import matplotlib.pyplot as plt
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout
import re
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import sys
import threading

import modules.scraping as scraping
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

class MainFrame(ttk.Frame):
    def __init__(self, container, root_scrape_distros, root_fix_database, root_draw_graph):
        super().__init__(container)

        self.root_scrape_distros = root_scrape_distros
        self.root_fix_database = root_fix_database
        self.root_draw_graph = root_draw_graph

        self.options = {'padx': 5, 'pady': 5}

        #################### OPCIONES DE SCRAPING ##################################
        self.scrape_labelframe = tk.LabelFrame(self, text="Opciones de scraping: ")
        self.scrape_labelframe.grid(row = 1, column = 0, padx=10, pady=10, ipadx=5, ipady=5, sticky=tk.NSEW)

        self.scrape_button = ttk.Button(self.scrape_labelframe, text="Scrapear Distros", command = self.scrape_distros)
        self.scrape_button.grid(row = 0, column = 0, sticky=tk.W, padx=5)

        self.scrape_label = ttk.Label(self.scrape_labelframe, justify=tk.LEFT, text="Scrapea distrowatch.com y guarda los datos de \ncada distribucion linux en la base de datos.")
        self.scrape_label.grid(row = 0, column = 1, sticky=tk.W, padx=10)

        self.fix_button = ttk.Button(self.scrape_labelframe, text="Arreglar Base de datos", command = self.fix_database)
        self.fix_button.grid(row = 1, column = 0, sticky=tk.W, padx=5)

        self.fix_label = ttk.Label(self.scrape_labelframe, justify=tk.LEFT, text="Arregla la base de datos. Si aparece varias veces la misma \ndistro en el grafico, se debe arreglar la base de datos.")
        self.fix_label.grid(row = 1, column = 1, sticky=tk.W, padx=10)

        #################### OPCIONES DE GRAFICADO ##################################
        self.graph_labelframe = tk.LabelFrame(self, text = "Opciones de graficado: ")
        self.graph_labelframe.grid(row = 2, column = 0, padx=10, pady=10, ipadx=5, ipady=5, sticky=tk.NSEW)

        self.graph_button = ttk.Button(self.graph_labelframe, text = "Mostrar Grafico", command = self.draw_graph)
        self.graph_button.grid(row=0, column=0, sticky=tk.W, padx=5)

        self.graph_label = ttk.Label(self.graph_labelframe, justify=tk.LEFT, text="Muestra el grafico de arbol con todas las distribuciones \nlinux en la base de datos.")
        self.graph_label.grid(row=0, column=1, sticky=tk.W, padx=5)

    def scrape_distros(self):
        self.root_scrape_distros()

    def fix_database(self):
        self.root_fix_database()

    def draw_graph(self):
        self.root_draw_graph()


# Completamente sacado de stackoverflow
# escribe el output de consola a un scrolledtext.
class PrintLogger(object):  # create file like object

    def __init__(self, textbox):  # pass reference to text widget
        self.textbox = textbox  # keep ref

    def write(self, text):
        self.textbox.configure(state="normal")  # make field editable
        self.textbox.insert("end", text)  # write text to textbox
        self.textbox.see("end")  # scroll to end
        self.textbox.configure(state="disabled")  # make field readonly

    def flush(self):  # needed for file like object
        pass



class ScrapeFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.scrape_thread = None
        self.scrape_thread_kill_event = threading.Event()

        self.allagain = tk.BooleanVar(self, False)

        self.scrape_labelframe = ttk.Labelframe(self, text = "Scrapear distros")
        self.scrape_labelframe.grid(row = 0, column = 0, padx=10, pady=10, ipadx=5, ipady=5, sticky=tk.NSEW)

        self.scrape_allagain_checkbutton = ttk.Checkbutton(self.scrape_labelframe, text="Descargar todo de nuevo?", variable = self.allagain)
        self.scrape_allagain_checkbutton.grid(row = 0, column = 0)

        self.scrape_button = ttk.Button(self.scrape_labelframe, text="Scrapear distros", command = lambda: self.scrape_distros(),)
        self.scrape_button.grid(row = 1, column = 0, padx=5)

        self.cancel_button = ttk.Button(self.scrape_labelframe, text="Cancelar", command = lambda: self.cancel_scrape_distros(),state=tk.DISABLED)
        self.cancel_button.grid(row = 1, column = 1, padx=5)

        self.back_button = ttk.Button(self.scrape_labelframe, text="Volver")
        self.back_button.grid(row = 1, column = 2, padx=5)

        self.log_widget = ScrolledText(self)
        self.log_widget.grid(row = 2, column = 0, rowspan=5, columnspan = 3)

        self.redirect_logging()

    def scrape_distros(self):
        #self.root_scrape_distros()
        self.scrape_thread_kill_event.clear()
        self.scrape_button["state"] = tk.DISABLED
        self.cancel_button["state"] = tk.NORMAL
        
        self.scrape_thread = scraping.ScrapeAllThread(
            self.scrape_thread_kill_event, 
            self.enable_scrape_button)
        self.scrape_thread.start()
    
    def cancel_scrape_distros(self):
        self.cancel_button["state"] = tk.DISABLED
        self.scrape_thread_kill_event.set()
        
    def enable_scrape_button(self):
        self.scrape_button["state"] = tk.NORMAL

    def reset_logging(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def redirect_logging(self):
        self.logger = PrintLogger(self.log_widget)

        sys.stdout = self.logger
        sys.stderr = self.logger

class App(tk.Tk):
    #Aca crea toda la GUI
    def __init__(self):
        super().__init__()

        self.menubar = tk.Menu(self)
        self.config(menu = self.menubar)
        self.menubar.add_command(label="DistroTree Graph v0.1dev")

        self.appframe = MainFrame(self, self.scrape_distros_menu, self.fix_database_menu, self.draw_graph_menu)
        self.appframe.pack()

        self.scrapeframe = ScrapeFrame(self)


    def scrape_distros_menu(self):
        self.appframe.pack_forget()
        self.scrapeframe.pack()

    def fix_database_menu(self):
        self.appframe.pack_forget()

    def draw_graph_menu(self):
        #self.appframe.pack_forget()
        graph()