default: 00 01

00:
	python $@*/main.py > $$(echo $@*)/output.yaml
	dictknife diff $@*/mkdocs.yml $@*/output.yaml | tee $$(echo $@*)/a.diff
01:
	python $@*/main.py > $$(echo $@*)/output.yaml
	python 00*/main.py $$(echo $@*)/conf.py:toplevel > $$(echo $@*)/00-output.yaml
	dictknife diff $@*/00-output.yaml $@*/output.yaml | tee $$(echo $@*)/a.diff
