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
