OUTFILE := output.json
SHELL := $(shell which bash)

GREP := $(shell which ggrep || which grep)
ALLS := $(shell cat Makefile| $(GREP) -Po '^\d+')

default: $(ALLS)

typing:
	mypy --strict .

00:
	python $@*/main.py | tee `echo $@*`/${OUTFILE}
01:
	python -m metashape.outputs.openapi $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} |& tee `echo $@*`/a.diff
02:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} |& tee `echo $@*`/a.diff
03:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} |& tee `echo $@*`/a.diff
04:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} |& tee `echo $@*`/a.diff
05:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} |& tee `echo $@*`/a.diff
06:
	python $@*/main.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} |& tee `echo $@*`/a.diff
07:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} |& tee `echo $@*`/a.diff
08:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} |& tee `echo $@*`/a.diff
09:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} |& tee `echo $@*`/a.diff
10:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
11:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
12:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
13:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
14:
	python $@*/main.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 00*`/${OUTFILE} `echo $@*`/${OUTFILE} |& tee `echo $@*`/a.diff
15:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
# newtype
16:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
17:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
18:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
19:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
20:
	python -m metashape.outputs.openapi --aggressive $@*/shape.py | tee `echo $@*`/${OUTFILE}
21:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 08*`/${OUTFILE} `echo $@*`/${OUTFILE} |& tee `echo $@*`/a.diff
22:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
23:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
24:
	python -m metashape.outputs.openapi --aggressive $@*/*.py | tee `echo $@*`/${OUTFILE}
	dictknife diff `echo 09*`/${OUTFILE} `echo $@*`/${OUTFILE} |& tee `echo $@*`/a.diff
