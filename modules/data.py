import pandas as pd
import modules.scraping

#Clase con los datos de una distribucion linux
#Creado a partir de scrapear una pagina de distrowatch
class LinuxDistro():
    def __init__(self, datos):
        self.name = datos[0]
        self.last_updated = datos[1]
        self.os_type = datos[2]
        self.based_on = datos[3].split(", ")
        self.origin = datos[4].split(", ")
        self.architecture = datos[5].split(", ")
        self.desktop = datos[6].split(", ")
        self.category = datos[7].split(", ")
        self.status = datos[8]
        self.popularity = datos[9]
        self.description = datos[10]

def print_linuxdistro(ld: LinuxDistro):
    print(f"""

============================================
Nombre: {ld.name}
Tipo de OS: {ld.os_type}
Basado en: {ld.based_on}
Origen: {ld.origin}
Arquitectura(s): {ld.architecture}
Escritorio(s): {ld.desktop}
Categoria: {ld.category}
Popularidad: {ld.popularity}
Descripction: {ld.description}
""")

def load_distros_table():
    table = pd.read_csv("distros.csv", sep="\t") #Elegi el tabulador porque es el menos probable que se use
    table["BasedOn"] = table["BasedOn"].str.replace(r"\w*\(.*\)",r"",regex=True) #Saca los parentesis como (Stable) (LTS) (Testing) (+18 version) etc
    table["BasedOn"] = table["BasedOn"].str.replace(r"^(.*)(\s)$", r"\1", regex=True)
    return table

def save_linux_distro(ld):
    table = pd.read_csv("distros.csv", sep="\t")
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