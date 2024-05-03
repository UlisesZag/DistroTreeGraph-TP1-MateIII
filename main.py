"""
DISTROTREE GRAPH v0.1dev
Hecho por Ulises Zagare, para el curso de Matematica III de la carrera TPI en la Universidad Nacional de San Martin.

Archivos fuente:
main.py #Archivo main. Llama a la aplicacion.
modules/data.py #Modulo con varias funciones de procesado de la base de datos.
modules/plots.py #Modulo con funciones para crear graficos con matplotlib y networkx.
modules/scraping.py #Modulo con funciones para sacar datos de distrowatch.
modules/ui.py #Modulo con la interfaz de usuario.
"""

#Librerias de progama
import modules.ui as ui

if __name__ == "__main__":
    print("--- DistroTree Graph v0.1dev ---")

    app = ui.App()
    app.mainloop()