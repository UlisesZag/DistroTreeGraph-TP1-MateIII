import requests
import re
import json
import os
import threading

from bs4 import BeautifulSoup
import pandas as pd

from modules.data import LinuxDistro

distrowatch_scrape_patterns = [
    "\n",
    "Last Update: ",
    "OS Type: ",
    "Based on: ",
    "Origin: ",
    "Architecture: ",
    "Desktop: ",
    "Category: ",
    "Status: ",
    "Popularity: ",
    "Popularity (hits per day): 12 months: ",
    ", 6 months: ",
    ", 3 months: ",
    ", 4 weeks: ",
    ", 1 week: ",
    "Average visitor rating: "
]

def distrowatch_getrealname(distro):
    req = requests.get("https://distrowatch.com/table.php?distribution="+distro)
    try:
        urlname = req.url.split("https://distrowatch.com/table.php?distribution=")[1]
    except IndexError: #Si pasa esto es porque lo mando a una pagina invalida. debe retornar lo mismo que dio el usuario
        return distro
    return urlname

# Scrapea una pagina de distrowatch y devuelve un LinuxDistro con informacion
def distrowatch_linuxdistro(distro):
    req = requests.get("https://distrowatch.com/table.php?distribution="+distro)
    soup = BeautifulSoup(req.text, features="html.parser")

    if soup is None:
        return None

    try:
        datos = soup.find("td", {"class": "TablesTitle"}).text
    except AttributeError:
        return None

    urlname = req.url.split("https://distrowatch.com/table.php?distribution=")[1]
    print("URL Name:",urlname)

    for i in distrowatch_scrape_patterns:
        datos = datos.replace(i, "$$$")

    datos = datos.split("$$$")

    for index, i in enumerate(datos):
        if re.match(r"^\s*$", i):
            datos[index] = ""

    #Vacia los elementos con ""
    while datos.count("") != 0:
        datos.remove("") 
    
    ld = LinuxDistro(urlname, datos)
    return ld

def distrowatch_numberdistros():
    req = requests.get("https://distrowatch.com/weekly.php?issue=current")
    soup = BeautifulSoup(req.text, features="html.parser")

    alldistributions = soup(text=re.compile(r"all distributions"))
    text = alldistributions[0].parent.parent.text
    alldtext = re.search(r"Number of all distributions in the database: \d*", text)
    num = int(re.sub(r"Number of all distributions in the database: ", "", alldtext.group()))
    return num

# Obtiene una lista con los nombres de cada distribucion linux disponible
def distrowatch_list():
    distros = []
    # Saca la tabla con todas las distribuciones linux
    req = requests.get("https://distrowatch.com/search.php?status=All")
    soup = BeautifulSoup(req.text, features="html.parser")

    #Busca el texto para ubicar donde estan los links
    pop_link = soup(text=re.compile(r"The following distributions match your criteria \(sorted by"))
    section_with_distro_links = pop_link[0].parent.parent #Aca estan los links
    pop_link[0].parent.clear() #Borra el mensaje para que no moleste 
    annoying_table = section_with_distro_links.table #Borra la tabla de busqueda porque molesta
    annoying_table.clear()
    links = section_with_distro_links.find_all("a") #Busca todos los tags "a" que son los nombres de las distribuciones linux

    for ld in links:
        distros.append(ld.text)

    while distros.count("") > 0:
        distros.remove("")

    return distros

def distro_to_dataframe(ld):
    new_row = {
        "UrlName": ld.urlname,
        "Name": ld.name,
        "LastUpdated": ld.last_updated,
        "OSType": ld.os_type,
        "BasedOn": ";".join(ld.based_on),
        "Origin": ";".join(ld.origin),
        "Architecture": ";".join(ld.architecture),
        "Desktop": ";".join(ld.desktop),
        "Category": ";".join(ld.category),
        "Status": ld.status,
        "Popularity": ld.popularity,
        "Description": ld.description
    }

    new_dataframe = pd.DataFrame([new_row])
    return new_dataframe

class ScrapeAllThread(threading.Thread):
    def __init__(self, stop_flag, enable_scrape_button, scrape_allagain):
        super().__init__()
        self.stop_flag = stop_flag
        self.enable_scrape_button = enable_scrape_button
        self.scrape_allagain = scrape_allagain

    def run(self):
        distributions_scraped = 0
        distributions_failed = 0
        already_in_database = 0

        if self.scrape_allagain:
            print("Scrapeando todo de nuevo...")
            if os.path.exists("distros_old.csv"):
                os.remove("distros_old.csv")
            if os.path.exists("distros.csv"):
                os.rename("distros.csv", "distros_old.csv")

        if os.path.exists("distros.csv"):
            table = pd.read_csv("distros.csv", sep="\t") #Elegi el tabulador porque es el menos probable que se use
        else:
            table = pd.DataFrame(columns=["UrlName","Name", "LastUpdated", "OSType", "BasedOn", "Origin", "Architecture", "Desktop", "Category", "Status", "Popularity", "Description"])

        print("Obteniendo lista de distribuciones linux . . .")
        available_distros = distrowatch_list()
        print("Numero de distribuciones linux disponible:", len(available_distros))

        for num, distro in enumerate(available_distros):
            if self.stop_flag.is_set():
                break

            if distro in table["Name"].values:
                print(f"Salteando {distro} ya que ya esta en la base de datos.")
                already_in_database += 1
                continue

            print(f"Obteniendo: {distro}... ({num+1}/{len(available_distros)})")
            ld = distrowatch_linuxdistro(distro)

            if ld == None:
                print(f"No se encontro: {distro}.")
                alt_name = distro.split(" ")[0]
                print(f"Intentando con: {alt_name}")

                ld = distrowatch_linuxdistro(alt_name)

                if ld == None:
                    print(f"Fallo al intentar obtener: {distro} or {alt_name}. Salteando...")
                    distributions_failed += 1
                    continue
                else:
                    print(f"Se encontro {alt_name}! Obteniendo...")

            if ld.urlname in table["UrlName"].values:
                print(f"Salteando {distro} ya que ya esta en la base de datos.")
                already_in_database += 1
                continue

            new_row = distro_to_dataframe(ld)
            
            table = pd.concat([table, new_row], ignore_index=True)
            distributions_scraped += 1
            table.to_csv("distros.csv", sep="\t", index=False)
        
        print("--- Se detuvo el scrapping -------------------")
        print(f" Distros obtenidas exitosamente: {distributions_scraped}")
        print(f" Distros falladas: {distributions_failed}")
        print(f" Ya estaban en la base de datos: {already_in_database}")
        self.enable_scrape_button()