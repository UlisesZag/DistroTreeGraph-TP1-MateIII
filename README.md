# DistroTree Graph
DistroTree Graph - Ulises Zagare, 2024.
Desarrollado para la cursada de Matematica III para TPI en la Universidad Nacional de San Martin.

![Main Menu](https://github.com/UlisesZag/DistroTreeGraph-TP1-MateIII/blob/master/docs/main_menu.png?raw=true)

Esta aplicacion scrapea datos acerca de distribuciones linux a partir de distrowatch: https://distrowatch.com/
Luego crea un grafico de arbol de como se van derivando las distribuciones. Se uso NetworkX para poder crear el grafico.
Tambien muestra varias estadisticas con MatPlotLib.

## Scrapear Distros
Este menu es para scrapear todas las distros disponibles de distrowatch. Permite scrapear todo de nuevo.

![Scrape Menu](https://github.com/UlisesZag/DistroTreeGraph-TP1-MateIII/blob/master/docs/scrape_menu.png?raw=true)

## Arreglar Base de datos
Luego de scrapear la base de datos puede tener errores, con este menu el programa corrige los nombres de las distribuciones, y tambien obtiene las distribuciones base que no estan en la base de datos.

![Fix Menu](https://github.com/UlisesZag/DistroTreeGraph-TP1-MateIII/blob/master/docs/fix_menu.png?raw=true)

## Mostrar Grafico
Este menu permite generar el arbol completo de distribuciones linux. Tambien permite ver todas las distribuciones basadas en una distribucion en especifico, y poner un limite a la cantidad de distribuciones mostradas.

![Graph Menu](https://github.com/UlisesZag/DistroTreeGraph-TP1-MateIII/blob/master/docs/graph_menu.png?raw=true)

Tambien muestra estadisticas: Distros mas tomadas como base, y distros por arquitectura, categoria, entorno de escritorio y actividad.

### Formato del CSV
`distros.csv` es el archivo de tabla donde se almacenan los datos con las distribuciones Linux.
Cada columna de `distros.csv` esta separado por un tab (\t). Las columnas que tienen una lista de valores estan separadas por un punto y coma (;)