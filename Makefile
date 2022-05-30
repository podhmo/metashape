test:
	pytest -vv --show-capture=all
ci:
	pytest --show-capture=all --cov=metashape --no-cov-on-fail --cov-report term-missing
	$(MAKE) lint typing
	$(MAKE) examples
	git diff

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
	$(MAKE) -C examples

build:
#	pip install wheel
	python setup.py sdist bdist_wheel

upload:
#	pip install twine
	twine check dist/metashape-$(shell cat VERSION)*
	twine upload dist/metashape-$(shell cat VERSION)*.gz
	twine upload dist/metashape-$(shell cat VERSION)*.whl

local-tox:
	docker run -v `pwd`:/app --rm -it quay.io/pypa/manylinux_2_24_x86_64:latest bash 
	# python3.11 -m pip install --user
	# cd /app
	# ~/.local/bin/tox .



.PHONY: test format lint build upload examples typing
