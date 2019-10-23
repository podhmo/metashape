OUTFILE := schema.graphql

default: 00 01 02 03 04 05

typing:
	mypy --strict .

00:
	python $@*/main.py | tee `echo $@*`/${OUTFILE}

01:
	python -m metashape.drivers.graphql $@*/*.py | tee `echo $@*`/${OUTFILE}
	diff -u `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
02:
	python -m metashape.drivers.graphql --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	diff -u `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
03:
	python -m metashape.drivers.graphql --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	diff -u `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
04:
	python -m metashape.drivers.graphql --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	diff -u `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
05:
	python -m metashape.drivers.graphql --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	diff -u `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
