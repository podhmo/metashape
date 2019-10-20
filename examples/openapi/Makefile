OUTFILE := output.json

default: 00 01 02 03 04 05 06 07 08 09

typing:
	mypy --strict .

00:
	python $@*/main.py | tee `echo $@*`/${OUTFILE}
01:
	python -m metashape.drivers.openapi $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
02:
	python -m metashape.drivers.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
03:
	python -m metashape.drivers.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
04:
	python -m metashape.drivers.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
05:
	python -m metashape.drivers.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
06:
	python $@*/main.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
07:
	python -m metashape.drivers.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
08:
	python -m metashape.drivers.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
09:
	python -m metashape.drivers.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} | tee `echo $@*`/a.diff
