OUTFILE := data.py
OUTFILE2 := data-nested.py

default: 00 01 02 03 04 05

00:
	python -m metashape.inputs.python $(shell echo $@*)/data.json | tee `echo $(shell echo $@*)`/${OUTFILE}
	python -m metashape.inputs.python -s nested $(shell echo $@*)/data.json | tee `echo $(shell echo $@*)`/${OUTFILE2}
01:
	python -m metashape.inputs.python $(shell echo $@*)/data.json | tee `echo $(shell echo $@*)`/${OUTFILE}
	python -m metashape.inputs.python -s nested $(shell echo $@*)/data.json | tee `echo $(shell echo $@*)`/${OUTFILE2}
02:
	python -m metashape.inputs.python $(shell echo $@*)/data.json | tee `echo $(shell echo $@*)`/${OUTFILE}

03: 03jsonvat.com/data.json
	python -m metashape.inputs.python $(shell echo $@*)/data.json | tee `echo $(shell echo $@*)`/${OUTFILE}
	python -m metashape.inputs.python -s nested $(shell echo $@*)/data.json | tee `echo $(shell echo $@*)`/${OUTFILE2}
03jsonvat.com/data.json:
	wget https://jsonvat.com -O $@

04: 04pokeapi-pokemon/data.json
	python -m metashape.inputs.python $(shell echo $@*)/data.json | tee `echo $(shell echo $@*)`/${OUTFILE}
	python -m metashape.inputs.python -s nested $(shell echo $@*)/data.json | tee `echo $(shell echo $@*)`/${OUTFILE2}
04pokeapi-pokemon/data.json:
	wget https://pokeapi.co/api/v2/pokemon/151 -O $@

todo: support list
05: 05github-events/data.json
	jqfpy 'get()[0]' $(shell echo $@*)/data.json > $(shell echo $@*)/data.0.json
	python -m metashape.inputs.python $(shell echo $@*)/data.0.json | tee `echo $(shell echo $@*)`/${OUTFILE}
	python -m metashape.inputs.python -s nested $(shell echo $@*)/data.0.json | tee `echo $(shell echo $@*)`/${OUTFILE2}
05github-events/data.json:
	wget https://api.github.com/events -O $@
