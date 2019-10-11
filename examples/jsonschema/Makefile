default: 00 01 02 03 04

typing:
	mypy --strict .

00:
	python $@*/main.py | tee `echo $@*`/output.json
01:
	python -m metashape $@*/*.py | tee `echo $@*`/output.json
	dictknife diff `echo 00*`/output.json `echo $@*`/output.json | tee `echo $@*`/a.diff
02:
	python -m metashape --aggressive $@*/*.py | tee `echo $@*`/output.json
	dictknife diff `echo 00*`/output.json `echo $@*`/output.json | tee `echo $@*`/a.diff
03:
	python -m metashape --aggressive $@*/*.py | tee `echo $@*`/output.json
	dictknife diff `echo 00*`/output.json `echo $@*`/output.json | tee `echo $@*`/a.diff
04:
	python -m metashape --aggressive $@*/*.py | tee `echo $@*`/output.json
	dictknife diff `echo 00*`/output.json `echo $@*`/output.json | tee `echo $@*`/a.diff
