OUTFILE := schema.graphql

default: 00 01

typing:
	mypy --strict .

00:
	python $@*/main.py | tee `echo $@*`/${OUTFILE}

01:
	python -m metashape.drivers.graphql $@*/*.py | tee `echo $@*`/${OUTFILE}
	diff -u `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
