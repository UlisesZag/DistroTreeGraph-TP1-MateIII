import requests
import re
import json
import os
import threading

from bs4 import BeautifulSoup
import pandas as pd

from modules.data import LinuxDistro

distrowatch_scrape_patterns = {
    "Name: ": "$$$$$0",
    "Last Update: ": "$$$$$1",
    "OS Type: ": "$$$$$2",
    "Based on: ": "$$$$$3",
    "Origin: ": "$$$$$4",
    "Architecture: ": "$$$$$5",
    "Desktop: ": "$$$$$6",
    "Category: ": "$$$$$7",
    "Status: ": "$$$$$8",
    "Popularity: ": "$$$$$9",
    "Popularity (hits per day)": "$$$$$B",
    "hits per day)": "$$$$$A",
    "Not ranked": "$$$$$A"
}

patterns_positions = {
    "$$0": 0,
    "$$1": 1,
    "$$2": 2,
    "$$3": 3,
    "$$4": 4,
    "$$5": 5,
    "$$6": 6,
    "$$7": 7,
    "$$8": 8,
    "$$9": 9,
    "$$A": 10,
    "$$B": 11
}

#Busca una distro por string y devuelve la distro que redirecciona la pagina
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

    #Si no encontro la pagina
    if soup is None:
        return None

    try:
        datos = soup.find("td", {"class": "TablesTitle"}).text
    except AttributeError:
        return None

    #Saca el nombre de distro de url como para usarlo de ID unica
    urlname = req.url.split("https://distrowatch.com/table.php?distribution=")[1]
    print("URL Name:",urlname)

    datos = datos.replace("\n", "")
    #Cambia cada texto por un ide ej $$1 $$2...
    for i in distrowatch_scrape_patterns.keys():
        datos = datos.replace(i, distrowatch_scrape_patterns[i])

    datos = "$$0"+datos
    datos = datos.split("$$$")#Parte el string

    #Saca los espacios en blanco
    for index, i in enumerate(datos):
        if re.match(r"^\s*$", i):
            datos[index] = ""

    #Vacia los elementos con ""
    while datos.count("") != 0:
        datos.remove("") 
    
    #Aca asigna todos los datos a una lista con todos sus valores inicializados en ""
    datos_org = ["" for i in range(0, 17)]
    for dat in datos:
        for i in distrowatch_scrape_patterns.values():
            patkey = i.replace("$$$", "")
            if dat.startswith(patkey):
                dat_append = dat.replace(patkey, "")
                datos_org[patterns_positions[patkey]] = dat_append
                break
    
    datos = datos_org
    
    #La convierte a un objeto LinuxDistro y devuelve
    ld = LinuxDistro(urlname, datos)
    return ld

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

#Convierte un objeto LinuxDistro a un Dataframe
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

#Este hilo scrapea todas las distros de distrowatch 
class ScrapeAllThread(threading.Thread):
    def __init__(self, stop_flag, enable_controls, scrape_allagain):
        super().__init__()
        self.stop_flag = stop_flag #Flag de cancelacion
        self.enable_controls = enable_controls #Funcion para reactivar los controles
        self.scrape_allagain = scrape_allagain #Scrapear todo de nuevo?

    def run(self):
        distributions_scraped = 0
        distributions_failed = 0
        already_in_database = 0

        #Renombra el csv
        if self.scrape_allagain:
            print("Scrapeando todo de nuevo...")
            if os.path.exists("distros_old.csv"):
                os.remove("distros_old.csv")
            if os.path.exists("distros.csv"):
                os.rename("distros.csv", "distros_old.csv")

        #Abre el csv
        if os.path.exists("distros.csv"):
            table = pd.read_csv("distros.csv", sep="\t") #Elegi el tabulador porque es el menos probable que se use
        else:
            table = pd.DataFrame(columns=["UrlName","Name", "LastUpdated", "OSType", "BasedOn", "Origin", "Architecture", "Desktop", "Category", "Status", "Popularity", "Description"])

        #OBTENCION DE LA LISTA DE DISTRIBUCIONES
        print("Obteniendo lista de distribuciones linux . . .")
        try:
            available_distros = distrowatch_list()
        except requests.exceptions.ConnectionError:
            print("ERROR: No se pudo conectar al sitio. Compruebe su conexion a internet.")
            self.enable_controls()
            return
        print("Numero de distribuciones linux disponible:", len(available_distros))

        #EXTRACCION DE CADA DISTRIBUCION
        for num, distro in enumerate(available_distros):
            if self.stop_flag.is_set(): #Cancela si el flag de cancelacion esta activado
                break

            #Si ya esta en la tabla lo saltea
            if distro in table["Name"].values:
                print(f"Salteando {distro} ya que ya esta en la base de datos.")
                already_in_database += 1
                continue

            #Intenta obtener una distribucion
            print(f"Obteniendo: {distro}... ({num+1}/{len(available_distros)})")
            try:
                ld = distrowatch_linuxdistro(distro)
            except requests.exceptions.ConnectionError:
                print("\nERROR: No se pudo conectar al sitio. Compruebe su conexion a internet.")
                self.enable_controls()
                return

            #Si no trata con otro nombre.
            if ld == None:
                print(f"No se encontro: {distro}.")
                alt_name = distro.split(" ")[0]
                print(f"Intentando con: {alt_name}")

                try:
                    ld = distrowatch_linuxdistro(alt_name)
                except requests.exceptions.ConnectionError:
                    print("\nERROR: No se pudo conectar al sitio. Compruebe su conexion a internet.")
                    self.enable_controls()
                    return

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

            #Convierte el objeto LinuxDistro a un dataframe y luego lo concatena al original
            new_row = distro_to_dataframe(ld)
            
            table = pd.concat([table, new_row], ignore_index=True)
            distributions_scraped += 1
            table.to_csv("distros.csv", sep="\t", index=False)
        
        print("--- Se detuvo el scrapping -------------------")
        print(f" Distros obtenidas exitosamente: {distributions_scraped}")
        print(f" Distros falladas: {distributions_failed}")
        print(f" Ya estaban en la base de datos: {already_in_database}")
        self.enable_controls()