import matplotlib.pyplot as plt
import networkx as nx
import re
import pandas as pd

import modules.data as data

def graph():
    table = data.load_distros_table() #Carga la tabla con todos los datos

    #Configura el matplotlib
    fig, ax = plt.subplots(figsize=(5,5))


    #Itera por toda la tabla y hace relaciones para el grafo
    print("Building graph...")
    relaciones = []
    for index, row in table.iterrows():
        name = row["Name"]
        based_on = row["BasedOn"].split(";")
        # for b in based_on:
        #     relaciones.append((name, b))
        relaciones.append((name, based_on[len(based_on)-1]))
        print(f"Appended '{name}' to '{based_on[len(based_on)-1]}'")

    #Crea el grafo
    grafo = nx.DiGraph(relaciones)
    pos = nx.planar_layout(grafo, 1)
    nx.draw(grafo, pos, with_labels=True)
    #Muestra el grafo
    plt.show()
