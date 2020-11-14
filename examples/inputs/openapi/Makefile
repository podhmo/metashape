DIR = $(shell echo $@*/)

default: $(shell cat Makefile | grep -o '^[0-9][0-9]*:' | tr : "\n")

00:
	python -m metashape.inputs.openapi $(DIR)openapi.json | tee $(DIR)shapes.py
