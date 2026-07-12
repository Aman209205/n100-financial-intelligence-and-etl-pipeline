.PHONY: setup load test clean

setup:
	python -m venv venv
	./venv/Scripts/pip install -r requirements.txt  
	
	mkdir -p raw_data database output src/etl notebooks tests/etl
	touch src/etl/__init__.py

load:
	./venv/Scripts/python src/etl/loader.py

test:
	./venv/Scripts/pytest tests/

clean:
	rm -rf venv output/*.csv database/*.db