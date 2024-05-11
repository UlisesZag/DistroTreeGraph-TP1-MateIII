create_exe:
	pyinstaller --onefile main.py

setup:
	pip install matplotlib
	pip install networkx
	pip install pandas
	pip install beautifulsoup4
	pip install requests

setuplinux:
	sudo apt install python3-tk
	sudo apt install python3-pil.imagetk
	
run:
	python ./main.py