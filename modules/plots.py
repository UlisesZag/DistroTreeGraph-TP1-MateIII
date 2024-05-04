import matplotlib.pyplot as plt
import networkx as nx
import pandas

import modules.scraping as scraping
import modules.data as data

def graph(basedon = ""):
    table = data.load_distros_table() #Carga la tabla con todos los datos

    #Configura el matplotlib
    fig, ax = plt.subplots(figsize=(10,10))

    #Itera por toda la tabla y hace relaciones para el grafo
    print("Building graph...")
    relaciones = [] #Cual esta conectado a cual???

    names_map = {} #Diccionario para cambiar los nombres de los nodos
    sizes_array = []

    #Itera por la tabla para sacar las relaciones y los nombres reales
    for index, row in table.iterrows():
        name = row["UrlName"]
        complete_name = row["Name"]
        based_on = row["BasedOn"].split(";")

        #Filtra por basedon
        if basedon != "-- Todos --":
            if basedon.lower() != based_on[len(based_on)-1].lower():
                continue

        relaciones.append((based_on[len(based_on)-1].lower(), name.lower()))
        print(f"Appended '{name}' to '{based_on[len(based_on)-1]}'")

        #Añade el nombre a la lista
        names_map[name] = complete_name

    #Crea el grafo
    grafo = nx.DiGraph(relaciones)
    
    #Crea un arbol
    if basedon == "-- Todos --":
        grafo = nx.bfs_tree(grafo, source="independent") #Comentar si se quiere todos los nodos.
    else:
        grafo = nx.bfs_tree(grafo, basedon)

    #PARA HACER LOS TAMAÑOS
    # Toma el diccionario de basedons
    basedon_dict = data.get_property_quantity("BasedOn")
    for distro in nx.nodes(grafo):
        continuing = False
        for parent_distro in basedon_dict:
            if distro == parent_distro:
                nsize = 300 + basedon_dict[parent_distro] * 50 * (1 if basedon == "-- Todos --" else 2)
                nsize = min(nsize, 1000)
                sizes_array.append(float(nsize))
                continuing = True
                break
        
        if continuing:
            continue

        sizes_array.append(150)

    #Les da un mejor nobre que los IDs sacados de las urls
    grafo = nx.relabel_nodes(grafo, names_map)

    if basedon == "-- Todos --":
        pos = nx.planar_layout(grafo)
        pos = nx.rescale_layout_dict(pos, 2)
    
    else:
        #pos = nx.kamada_kawai_layout(grafo)
        #pos = nx.bfs_layout(grafo, start=basedon)
        pos = nx.spring_layout(grafo)
    
    draw_options = {
        "label": "Arbol de distribuciones de linux: ",
        "with_labels": True,
        "font_size": 7,
        "font_color": "#FFFFFF",
        "font_family": "monospace",
        "node_size": sizes_array,
        "node_color": "#003366"
    }

    nx.draw_networkx(grafo, pos, ax=ax, **draw_options)

    #Estilos,etc
    fig.tight_layout()
    ax.set_facecolor("#002244")

    plt.show()

def dict_stats(prop: str, title: str, ylabel: str):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    based_distros = data.get_property_quantity(prop)

    ax.bar(based_distros.keys(), based_distros.values())
    ax.tick_params(axis='x', labelrotation=90)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    plt.show()