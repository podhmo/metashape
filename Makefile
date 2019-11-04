test:
	pytest -vv --show-capture=all
ci:
	pytest --show-capture=all --cov=metashape --no-cov-on-fail --cov-report term-missing
	$(MAKE) lint typing

format:
#	pip install -e .[dev]
	black metashape setup.py

lint:
#	pip install -e .[dev]
	flake8 metashape --ignore W503,E203,E501

typing:
#	pip install -e .[dev]
	mypy --strict --strict-equality --ignore-missing-imports metashape

examples:
	$(MAKE) -C examples/openapi

build:
#	pip install wheel
	python setup.py bdist_wheel

upload:
#	pip install twine
	twine check dist/metashape-$(shell cat VERSION)*
	twine upload dist/metashape-$(shell cat VERSION)*

.PHONY: test format lint build upload examples typing
