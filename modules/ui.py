import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout
import re
import pandas as pd

import modules.data as data

def graph(basedon = ""):
    table = data.load_distros_table() #Carga la tabla con todos los datos

    #Configura el matplotlib
    fig, ax = plt.subplots(figsize=(15,20))


    #Itera por toda la tabla y hace relaciones para el grafo
    print("Building graph...")
    relaciones = [] #Cual esta conectado a cual???

    names_map = {} #Diccionario para cambiar los nombres de los nodos
    sizes_map = {}
    sizes_array = []

    for index, row in table.iterrows():
        name = row["UrlName"]
        complete_name = row["Name"]
        based_on = row["BasedOn"].split(";")
        # for b in based_on:
        #     relaciones.append((name, b))

        if basedon != "":
            if basedon.lower() != based_on[len(based_on)-1].lower():
                continue
        relaciones.append((based_on[len(based_on)-1].lower(), name.lower()))
        print(f"Appended '{name}' to '{based_on[len(based_on)-1]}'")

        #Añade el nombre a la lista
        names_map[name] = complete_name

    #Crea el grafo
    grafo = nx.MultiDiGraph(relaciones)
    grafo = nx.relabel_nodes(grafo, names_map)

    if basedon == "":
        pos = nx.planar_layout(grafo)
    else:
        pos = nx.kamada_kawai_layout(grafo)

    nx.draw_networkx(grafo, pos, with_labels=True, font_size=10)
    #Muestra el grafo
    plt.show()
