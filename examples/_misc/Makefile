default: 00

SHELL := $(shell which bash)

# dataclasses support
00:
	# use class
	python $@*/useclass/main.py > $$(echo $@*/)useclass/got.yaml 2>&1
	dictknife diff $@*/want.yaml $@*/useclass/got.yaml > $$(echo $@*/)want-useclass.diff 2>&1

	# use dataclasses as member
	python $@*/usedataclass/main.py > $$(echo $@*/)usedataclass/got.yaml 2>&1
	dictknife diff $@*/want.yaml $@*/usedataclass/got.yaml > $$(echo $@*/)want-usedataclass.diff 2>&1
