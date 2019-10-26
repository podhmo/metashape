OUTFILE := schema.json

default: 00 01

typing:
	mypy --strict .

00:
	python $@*/main.py | tee `echo $@*`/${OUTFILE}
01:
	python -m metashape.outputs.jsonschema $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
