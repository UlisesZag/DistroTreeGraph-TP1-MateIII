#Librerias standard
import requests
import json
import re

#Librerias pip
import matplotlib.pyplot as plt
import networkx
from bs4 import BeautifulSoup

#Librerias de progama
import modules.scraping as scraping
import modules.data as data
import modules.ui as ui

if __name__ == "__main__":
    print("DistroTree Graph v0.1dev")

    # print("1: Parsear distros. 2: Buscar y guardar distros individuales. 0: Mostrar grafo")
    # opcion = input(":")

    # if opcion == "1":
    #     scraping.distrowatch_alltocsv()
    # if opcion == "0": 
    #     b = input("Basados en: ").lower()
    #     #data.fix_table()
    #     ui.graph(b)
    # if opcion == "2":
    #     while True: 
    #         distro = input("Ingrese una distro linux: ")
    #         ld = scraping.distrowatch_linuxdistro(distro)

    #         if ld == None:
    #             print("No se encontro su distro linux buscada.")
    #             continue

    #         data.print_linuxdistro(ld)
    #         data.save_linux_distro(ld)

    app = ui.App()
    app.mainloop()