default: 00

SHELL := $(shell which bash)

# dataclasses support
00:
	# use class
	python $(shell echo $@*/)useclass/main.py &> $(shell echo $@*/)useclass/got.yaml
	dictknife diff $(shell echo $@*/)want.yaml $@*/useclass/got.yaml &> $(shell echo $@*/)want-useclass.diff

	# use dataclasses as member
	python $(shell echo $@*/)usedataclass/main.py &> $(shell echo $@*/)usedataclass/got.yaml
	dictknife diff $(shell echo $@*/)want.yaml $@*/usedataclass/got.yaml &> $(shell echo $@*/)want-usedataclass.diff
