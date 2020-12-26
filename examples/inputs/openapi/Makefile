DIR = $(shell echo $@*/)

default: $(shell cat Makefile | grep -o '^[0-9][0-9]*:' | tr : "\n")

00:
	python -m metashape.inputs.openapi $(DIR)openapi.json | tee $(DIR)shapes.py
01:
	python -m metashape.inputs.openapi $(DIR)openapi.json | tee $(DIR)shapes.py
02:
	python -m metashape.inputs.openapi $(DIR)openapi.json | tee $(DIR)shapes.py
03:
	python -m metashape.inputs.openapi $(DIR)openapi.json | tee $(DIR)shapes.py
04:
	python -m metashape.inputs.openapi $(DIR)openapi.json | tee $(DIR)shapes.py
05:
	python -m metashape.inputs.openapi $(DIR)openapi.json | tee $(DIR)shapes.py
06:
	python -m metashape.inputs.openapi $(DIR)openapi.json | tee $(DIR)shapes.py
07:
	python -m metashape.inputs.openapi $(DIR)openapi.json | tee $(DIR)shapes.py
08:
	python -m metashape.inputs.openapi $(DIR)openapi.json | tee $(DIR)shapes.py
09:
	python -m metashape.inputs.openapi $(DIR)openapi.json | tee $(DIR)shapes.py
10:
	python -m metashape.inputs.openapi $(DIR)openapi.json | tee $(DIR)shapes.py
11:
	python -m metashape.inputs.openapi --verbose $(DIR)openapi.json | tee $(DIR)shapes.py
12:
	python -m metashape.inputs.openapi $(DIR)openapi.json | tee $(DIR)shapes.py

lint:
	flake8 --ignore E501 .
