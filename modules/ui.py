import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import showerror as tk_showerror, showinfo as tk_showinfo
import sys
import threading
import os

import modules.scraping as scraping
import modules.data as data
import modules.plots as plots
import main

#Menu inicial
class MainFrame(ttk.Frame):
    def __init__(self, container, root_scrape_distros, root_fix_database, root_draw_graph):
        super().__init__(container)

        self.root_scrape_distros = root_scrape_distros
        self.root_fix_database = root_fix_database
        self.root_draw_graph = root_draw_graph

        self.options = {'padx': 5, 'pady': 5}

        #################### OPCIONES DE SCRAPING ##################################
        self.scrape_labelframe = ttk.Labelframe(self, text="Opciones de scraping: ")
        self.scrape_labelframe.grid(row = 1, column = 0, columnspan=2, padx=10, pady=10, ipadx=5, ipady=5, sticky=tk.NSEW)

        self.scrape_button = ttk.Button(self.scrape_labelframe, text="Scrapear Distros", command = self.scrape_distros)
        self.scrape_button.grid(row = 0, column = 0, sticky=tk.NSEW, padx=5)

        self.scrape_label = ttk.Label(self.scrape_labelframe, justify=tk.LEFT, text="Scrapea distrowatch.com y guarda los datos de \ncada distribucion linux en la base de datos.")
        self.scrape_label.grid(row = 0, column = 1, sticky=tk.W, padx=10)

        self.fix_button = ttk.Button(self.scrape_labelframe, text="Arreglar Base de datos", command = self.fix_database)
        self.fix_button.grid(row = 1, column = 0, sticky=tk.NSEW, padx=5)

        self.fix_label = ttk.Label(self.scrape_labelframe, justify=tk.LEFT, text="Arregla la base de datos. Si aparece varias veces la misma \ndistro en el grafico, se debe arreglar la base de datos.")
        self.fix_label.grid(row = 1, column = 1, sticky=tk.W, padx=10)

        #################### OPCIONES DE GRAFICADO ##################################
        self.graph_labelframe = ttk.Labelframe(self, text = "Opciones de graficado: ")
        self.graph_labelframe.grid(row = 2, column = 0, columnspan=2, padx=10, pady=10, ipadx=5, ipady=5, sticky=tk.NSEW)

        self.graph_button = ttk.Button(self.graph_labelframe, text = "Mostrar Grafico", command = self.draw_graph)
        self.graph_button.grid(row=0, column=0, sticky=tk.NSEW, padx=5)

        self.graph_label = ttk.Label(self.graph_labelframe, justify=tk.LEFT, text="Muestra el grafico de arbol con todas las distribuciones \nlinux en la base de datos.")
        self.graph_label.grid(row=0, column=1, sticky=tk.W, padx=5)

        #################### ETC ####################################################
        self.about_button = ttk.Button(self, text = "Acerca de...", command = self.about)
        self.about_button.grid(row = 3, column = 0, sticky = tk.NSEW, padx = 5, pady = 5)

    def scrape_distros(self):
        self.root_scrape_distros()

    def fix_database(self):
        self.root_fix_database()

    def draw_graph(self):
        self.root_draw_graph()
    
    def about(self):
        tk_showinfo(f"{main.program_name} - Acerca de...", 
f"""
{main.program_name} {main.program_version} - Ulises Zagare, 2024.
Desarrollado para la cursada de Matematica III para TPI en la Universidad Nacional de San Martin.

Esta aplicacion saca datos acerca de distribuciones linux a partir de distrowatch: https://distrowatch.com/
Luego crea un grafico de arbol de como se van derivando las distribuciones. Se uso NetworkX para poder crear el grafico.
Tambien muestra varias estadisticas con MatPlotLib.

Github: https://github.com/UlisesZag/DistroTreeGraph-TP1-MateIII
"""
                    )
    
    def salir(self):
        pass


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

class ConsoleLogger(ScrolledText):
    def __init__(self, container):
        super().__init__(container)
    
    def reset_logging(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def redirect_logging(self):
        self.logger = PrintLogger(self)

        sys.stdout = self.logger
        sys.stderr = self.logger

# Ventana de Scrapear las Distribuciones
class ScrapeFrame(ttk.Frame):
    def __init__(self, container, root_main_menu):
        super().__init__(container)

        self.container = container

        self.scrape_thread = None
        self.scrape_thread_kill_event = threading.Event()

        self.root_main_menu = root_main_menu

        self.allagain = tk.BooleanVar(self, False)

        self.scrape_labelframe = ttk.Labelframe(self, text = "Scrapear distros")
        self.scrape_labelframe.grid(row = 0, column = 0, columnspan = 3, padx=10, pady=10, ipadx=5, ipady=5, sticky=tk.NSEW)

        self.scrape_allagain_checkbutton = ttk.Checkbutton(self.scrape_labelframe, text="Descargar todo de nuevo?", variable = self.allagain)
        self.scrape_allagain_checkbutton.grid(row = 0, column = 0)

        self.scrape_button = ttk.Button(self.scrape_labelframe, text="Scrapear distros", command = lambda: self.scrape_distros(),)
        self.scrape_button.grid(row = 1, column = 0, padx=5)

        self.cancel_button = ttk.Button(self.scrape_labelframe, text="Cancelar", command = lambda: self.cancel_scrape_distros(),state=tk.DISABLED)
        self.cancel_button.grid(row = 1, column = 1, padx=5)

        self.back_button = ttk.Button(self.scrape_labelframe, text="Volver", command=lambda: self.main_menu())
        self.back_button.grid(row = 1, column = 2, padx=5)

        self.log_widget = ConsoleLogger(self)
        self.log_widget.grid(row = 2, column = 0, rowspan=5, columnspan = 3)

    def activate_frame(self):
        self.log_widget.redirect_logging()

    def scrape_distros(self):
        self.scrape_thread_kill_event.clear() #Flag de fin de hilo
        #Desactiva los botones
        self.scrape_button["state"] = tk.DISABLED
        self.back_button["state"] = tk.DISABLED
        self.cancel_button["state"] = tk.NORMAL

        self.container.busy = True #La aplicacion no puede cerrarse hasta que el hilo termine
        
        self.scrape_thread = scraping.ScrapeAllThread(
            self.scrape_thread_kill_event, 
            self.enable_controls,
            self.allagain.get()
            )
        self.scrape_thread.start()
    
    def cancel_scrape_distros(self):
        self.cancel_button["state"] = tk.DISABLED
        self.scrape_thread_kill_event.set()
        
    def enable_controls(self):
        self.scrape_button["state"] = tk.NORMAL
        self.back_button["state"] = tk.NORMAL
        self.cancel_button["state"] = tk.DISABLED
        self.container.busy = False #Habilita el cierre de la aplicacion
    
    def main_menu(self):
        self.log_widget.reset_logging()
        self.root_main_menu()

# Ventana de Scrapear las Distribuciones
class FixFrame(ttk.Frame):
    def __init__(self, container, root_main_menu):
        super().__init__(container)

        self.container = container

        self.fix_thread = None
        self.fix_thread_kill_event = threading.Event()

        self.root_main_menu = root_main_menu

        self.scrape_labelframe = ttk.Labelframe(self, text = "Arreglar base de datos")
        self.scrape_labelframe.grid(row = 0, column = 0, columnspan = 3, padx=10, pady=10, ipadx=5, ipady=5, sticky=tk.NSEW)

        self.fix_button = ttk.Button(self.scrape_labelframe, text="Arreglar base de datos", command = lambda: self.fix_database(),)
        self.fix_button.grid(row = 0, column = 0, padx=5)

        self.cancel_button = ttk.Button(self.scrape_labelframe, text="Cancelar", command = lambda: self.cancel(),state=tk.DISABLED)
        self.cancel_button.grid(row = 0, column = 1, padx=5)

        self.back_button = ttk.Button(self.scrape_labelframe, text="Volver", command=lambda: self.main_menu())
        self.back_button.grid(row = 0, column = 2, padx=5)

        self.log_widget = ConsoleLogger(self)
        self.log_widget.grid(row = 2, column = 0, rowspan=5, columnspan = 3)

    def activate_frame(self):
        self.log_widget.redirect_logging()

    #Desactiva los controles y crea el hilo de arreglado
    def fix_database(self):
        self.fix_thread_kill_event.clear()
        self.fix_button["state"] = tk.DISABLED
        self.back_button["state"] = tk.DISABLED
        self.cancel_button["state"] = tk.NORMAL

        self.container.busy = True #La aplicacion no puede cerrarse hasta que el hilo termine
        
        self.scrape_thread = data.FixTableThread(
            self.fix_thread_kill_event,
            self.enable_controls
            )
        self.scrape_thread.start()
    
    def cancel(self):
        self.cancel_button["state"] = tk.DISABLED
        self.fix_thread_kill_event.set()
    
    #Cuando el hilo finaliza reestablece los controles
    def enable_controls(self):
        self.fix_button["state"] = tk.NORMAL
        self.back_button["state"] = tk.NORMAL
        self.cancel_button["state"] = tk.DISABLED

        self.container.busy = False #Habilita el cierre de la aplicacion
    
    #Volver a menu principal
    def main_menu(self):
        self.log_widget.reset_logging()
        self.root_main_menu()
    

# Ventana de dibujar el grafo
class GraphFrame(ttk.Frame):
    def __init__(self, container, root_main_menu):
        super().__init__(container)
        
        self.root_main_menu = root_main_menu

        self.parentslist = None #Basado en . . .
        self.distros_in_table = 0

        self.basedon = tk.StringVar(self, "-- Todos --")
        self.first_elements = tk.StringVar(self, str(self.distros_in_table))

        #Diccionarios para generar estadisticas.
        self.gen_basedon = {
            "prop": "BasedOn",
            "title": "Distribuciones usadas como base",
            "ylabel": "Distribuciones linux"
        }
        self.gen_architecture = {
            "prop": "Architecture",
            "title": "Distribuciones por arquitectura",
            "ylabel": "Distribuciones linux"
        }
        self.gen_category = {
            "prop": "Category",
            "title": "Distribuciones por categoria",
            "ylabel": "Distribuciones linux"
        }
        self.gen_desktop = {
            "prop": "Desktop",
            "title": "Distribuciones por entorno de escritorio",
            "ylabel": "Distribuciones linux"
        }
        self.gen_status = {
            "prop": "Status",
            "title": "Distribuciones por actividad",
            "ylabel": "Distribuciones linux"
        }

        #Elementos de UI
        self.graph_labelframe = ttk.Labelframe(self, text = "Grafo")
        self.graph_labelframe.grid(row = 0, column = 0, columnspan = 3, padx=10, pady=10, ipadx=5, ipady=5, sticky=tk.NSEW)

        self.filter_label = ttk.Label(self.graph_labelframe, text = "Basado en:")
        self.filter_label.grid(row = 0, column = 0)

        self.filter_entry = ttk.Combobox(self.graph_labelframe, textvariable = self.basedon)
        self.filter_entry.grid(row = 0, column = 1)

        self.first_label = ttk.Label(self.graph_labelframe, text = "Los primeros:")
        self.first_label.grid(row = 1, column = 0)

        self.first_entry = ttk.Spinbox(self.graph_labelframe, textvariable = self.first_elements, from_=1, to=str(self.distros_in_table))
        self.first_entry.grid(row = 1, column = 1)

        self.graph_button = ttk.Button(self.graph_labelframe, text = "Generar grafo", command = lambda: self.generate_graph(),)
        self.graph_button.grid(row = 0, column = 2, padx=5)

        self.back_button = ttk.Button(self.graph_labelframe, text = "Volver", command=lambda: self.main_menu())
        self.back_button.grid(row = 0, column = 3, padx=5)

        self.stats_labelframe = ttk.Labelframe(self, text = "Estadisticas")
        self.stats_labelframe.grid(row = 1, column = 0, columnspan = 3, padx=10, pady=10, ipadx=5, ipady=5, sticky=tk.NSEW)

        self.basedon_button = ttk.Button(self.stats_labelframe, text = "Distros mas tomadas como base", command = lambda: self.generate_stats(**self.gen_basedon))
        self.basedon_button.grid(row = 0, column = 0, padx=5, sticky = tk.NSEW)

        self.arch_button = ttk.Button(self.stats_labelframe, text = "Distros por arquitectura", command = lambda: self.generate_stats(**self.gen_architecture))
        self.arch_button.grid(row = 0, column = 1, padx=5, sticky = tk.NSEW)

        self.cat_button = ttk.Button(self.stats_labelframe, text = "Distros por categoria", command = lambda: self.generate_stats(**self.gen_category))
        self.cat_button.grid(row = 1, column = 0, padx=5, sticky = tk.NSEW)

        self.cat_button = ttk.Button(self.stats_labelframe, text = "Distros por entorno de escritorio", command = lambda: self.generate_stats(**self.gen_desktop))
        self.cat_button.grid(row = 1, column = 1, padx=5, sticky = tk.NSEW)

        self.cat_button = ttk.Button(self.stats_labelframe, text = "Distros por actividad", command = lambda: self.generate_stats(**self.gen_status))
        self.cat_button.grid(row = 2, column = 0, padx=5, sticky = tk.NSEW)
        
    #Si entra al frame:
    def activate_frame(self):
        if os.path.exists("distros.csv"):
            self.basedon.set("-- Todos --")

            self.distros_in_table = data.number_distros_csv()
            self.first_elements.set(str(self.distros_in_table))
            self.first_entry["to"]=str(self.distros_in_table)

            self.parentslist = data.get_property_quantity("BasedOn")
            #Toma el diccionario de distros padre
            _todos_list = ["-- Todos --"]
            _p_list = []

            #Va poniendo cada key como valor de la lista
            for entry in self.parentslist:
                _p_list.append(entry)

            _p_list.sort()

            #Asigna los valores a la lista.
            self.filter_entry["values"] = _todos_list + _p_list
        else:
            self.filter_entry["values"] = ["NO EXISTE DISTROS.CSV"]
            self.basedon.set("NO EXISTE DISTROS.CSV")

    def main_menu(self):
        self.root_main_menu()

    #UI: Ejecuta la funcion que arma el grafo con los parametros del menu
    def generate_graph(self):
        if not os.path.exists("distros.csv"):
            tk_showerror("Error", "No se encuentra el archivo: distros.csv. Intente scrapear distros para crear la base de datos.")
            return    
        
        #Arma un diccionario con los argumentos para hacer el grafo
        options_dict = {
            "basedon": self.basedon.get(),
            "first": min(max(int(self.first_elements.get()), 1), self.distros_in_table)
        }
        self.first_elements.set(str(options_dict["first"]))

        plots.graph(options_dict)
    
    def generate_stats(self, prop, title, ylabel):
        if not os.path.exists("distros.csv"):
            tk_showerror("Error", "No se encuentra el archivo: distros.csv. Intente scrapear distros para crear la base de datos.")
            return
        
        plots.dict_stats(prop, title, ylabel)


class App(tk.Tk):
    #Aca crea toda la GUI
    def __init__(self):
        super().__init__()
        self.resizable(False, False)

        self.busy = False #Flag si la app esta ejecutando un tarea o no

        self.protocol("WM_DELETE_WINDOW", self.close_app)

        #Titulo
        self.menubar = tk.Menu(self)
        self.config(menu = self.menubar)
        self.menubar.add_command(label=f"{main.program_name} {main.program_version}")


        self.appframe = MainFrame(self, self.scrape_distros_menu, self.fix_database_menu, self.draw_graph_menu)
        self.appframe.pack()

        self.scrapeframe = ScrapeFrame(self, self.main_menu)

        self.fixframe = FixFrame(self, self.main_menu)

        self.graphframe = GraphFrame(self, self.main_menu)
    
    def main_menu(self):
        self.scrapeframe.pack_forget()
        self.fixframe.pack_forget()
        self.graphframe.pack_forget()
        self.appframe.pack()

    def scrape_distros_menu(self):
        self.appframe.pack_forget()
        self.scrapeframe.pack()
        self.scrapeframe.activate_frame()

    def fix_database_menu(self):
        self.appframe.pack_forget()
        self.fixframe.pack()
        self.fixframe.activate_frame()

    def draw_graph_menu(self):
        self.appframe.pack_forget()
        self.graphframe.pack()
        self.graphframe.activate_frame()

    def close_app(self):
        if not self.busy:
            self.quit()
        else:
            tk_showinfo(
                "Advertencia", 
                "La operacion se esta ejecutando. Espere a que termine o cancelela antes de cerrar la aplicacion."
                )