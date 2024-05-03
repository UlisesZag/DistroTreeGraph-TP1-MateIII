create_exe:
	pyinstaller --onefile main.py

setup:
	pip install matplotlib
	pip install networkx
	pip install pandas
	pip install beautifulsoup4

run:
	python ./main.py