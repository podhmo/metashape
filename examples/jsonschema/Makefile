default: 00 01 02 03

typing:
	mypy --strict .

00:
	python $@*/main.py | tee `echo $@*`/output.json
01:
	python -m metashape $@*/*.py | tee `echo $@*`/output.json
02:
	python -m metashape --aggressive $@*/*.py | tee `echo $@*`/output.json
03:
	python -m metashape --aggressive $@*/*.py | tee `echo $@*`/output.json
