test:
	python setup.py test

format:
#	pip install -e .[dev]
	black metashape setup.py

lint:
#	pip install -e .[dev]
	flake8 metashape --ignore W503,E203,E501

typecheck:
#	pip install -e .[dev]
	mypy --strict metashape
# TODO: examples

build:
#	pip install wheel
	python setup.py bdist_wheel

upload:
#	pip install twine
	twine check dist/metashape-$(shell cat VERSION)*
	twine upload dist/metashape-$(shell cat VERSION)*

.PHONY: test format lint build upload
