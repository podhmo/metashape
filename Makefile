test:
	pytest --show-capture=all

format:
#	pip install -e .[dev]
	black metashape setup.py

lint:
#	pip install -e .[dev]
	flake8 metashape --ignore W503,E203,E501

typing:
#	pip install -e .[dev]
	mypy --strict --ignore-missing-imports metashape

examples:
	$(MAKE) -C examples/jsonschema

build:
#	pip install wheel
	python setup.py bdist_wheel

upload:
#	pip install twine
	twine check dist/metashape-$(shell cat VERSION)*
	twine upload dist/metashape-$(shell cat VERSION)*

.PHONY: test format lint build upload examples typing
