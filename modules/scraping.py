import requests
import re
import json
import os

from bs4 import BeautifulSoup
import pandas as pd

from modules.data import LinuxDistro

# Toma un link, busca en webarchive el link, y lo devuelve.
def webarchive_getlink(url):
    req = requests.get("https://archive.org/wayback/available?url="+url)
    req = json.loads(req.content.decode("utf-8"))
    newurl = req["archived_snapshots"]["closest"]["url"]
    return newurl

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

# Scrapea una pagina de distrowatch y devuelve un LinuxDistro con informacion
def distrowatch_linuxdistro(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, features="html.parser")

    if soup is None:
        return None

    try:
        datos = soup.find("td", {"class": "TablesTitle"}).text
    except AttributeError:
        return None

    for i in distrowatch_scrape_patterns:
        datos = datos.replace(i, "$$$")

    datos = datos.split("$$$")

    for index, i in enumerate(datos):
        if re.match(r"^\s*$", i):
            datos[index] = ""

    #Vacia los elementos con ""
    while datos.count("") != 0:
        datos.remove("") 
    
    ld = LinuxDistro(datos)
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

def distrowatch_alltocsv():
    if os.path.exists("distros.csv"):
        table = pd.read_csv("distros.csv", sep="\t") #Elegi el tabulador porque es el menos probable que se use
    else:
        table = pd.DataFrame(columns=["Name", "LastUpdated", "OSType", "BasedOn", "Origin", "Architecture", "Desktop", "Category", "Status", "Popularity", "Description"])

    print("Getting list of linux distributions")
    available_distros = distrowatch_list()
    print("Number of linux distros available:", len(available_distros))

    for num, distro in enumerate(available_distros):
        if distro in table["Name"].values:
            print(f"Skipping {distro} as it is already in the database.")
            continue

        print(f"Scraping: {distro}... ({num+1}/{len(available_distros)})")
        ld = distrowatch_linuxdistro("https://distrowatch.com/table.php?distribution="+distro)

        if ld == None:
            print(f"No se encontro: {distro}.")
            alt_name = distro.split(" ")[0]
            print(f"Trying with: {alt_name}")

            ld = distrowatch_linuxdistro("https://distrowatch.com/table.php?distribution="+alt_name)

            if ld == None:
                print(f"Failed to scrape: {distro} or {alt_name}. Skipping...")
                continue
            else:
                print(f"Found {alt_name}! Scrapping...")

        new_row = {
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
        
        table = pd.concat([table, pd.DataFrame([new_row])], ignore_index=True)

        table.to_csv("distros.csv", sep="\t", index=False)
