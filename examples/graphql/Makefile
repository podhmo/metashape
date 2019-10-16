default: 00

typing:
	mypy --strict .

00:
	python $@*/main.py | tee `echo $@*`/schema.graphql
