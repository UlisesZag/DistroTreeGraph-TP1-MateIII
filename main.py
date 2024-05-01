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

print("DistroTree Graph v0.1dev")
print("1: Parsear distros. 2: 0: Mostrar grafo")
opcion = input(":")

if opcion == "1":
    scraping.distrowatch_alltocsv()
if opcion == "0":
    ui.graph()
if opcion == "2":
    while True: 
        distro = input("Ingrese una distro linux: ")
        ld = scraping.distrowatch_linuxdistro("https://distrowatch.com/table.php?language=EN&distribution="+distro)

        if ld == None:
            print("No se encontro su distro linux buscada.")
            continue

        data.print_linuxdistro(ld)
        data.save_linux_distro(ld)