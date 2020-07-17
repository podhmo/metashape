default: 00

# dataclasses support
00:
	# use class
	python $@*/useclass/main.py > $$(echo $@*)/useclass/got.yaml
	dictknife diff $@*/want.yaml $@*/useclass/got.yaml | tee $$(echo $@*)/want-useclass.diff

	# use dataclasses as member
	python $@*/usedataclass/main.py > $$(echo $@*)/usedataclass/got.yaml
	dictknife diff $@*/want.yaml $@*/usedataclass/got.yaml | tee $$(echo $@*)/want-usedataclass.diff
