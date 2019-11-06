OUTFILE := schema.graphql
DIFF := diff -u --label left --label right

default: 00 01 02 03 04 05

typing:
	mypy --strict .

00:
	python $@*/main.py | tee `echo $@*`/${OUTFILE}

01:
	python -m metashape.outputs.graphql $@*/*.py | tee `echo $@*`/${OUTFILE}
	${DIFF} `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
02:
	python -m metashape.outputs.graphql --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	${DIFF} `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
03:
	python -m metashape.outputs.graphql --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	${DIFF} `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
04:
	python -m metashape.outputs.graphql --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	${DIFF} `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
05:
	python -m metashape.outputs.graphql --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	${DIFF} `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
