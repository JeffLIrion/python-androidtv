.PHONY: release
release:
	rm -rf dist
	scripts/git_tag.sh
	python setup.py sdist bdist_wheel
	twine upload dist/*

.PHONY: docs
docs:
	@cd docs/source && rm -f aio_androidtv*.rst
	@cd docs && sphinx-apidoc -f -e -o source/ ../aio_androidtv/
	@cd docs && make html && make html

.PHONY: test
test:
	python setup.py test

.PHONY: coverage
coverage:
	coverage run --source aio_androidtv setup.py test && coverage html && coverage report -m

.PHONY: tdd
tdd:
	coverage run --source aio_androidtv setup.py test && coverage report -m

.PHONY: lint
lint:
	flake8 aio_androidtv/ && pylint aio_androidtv/

.PHONY: alltests
alltests:
	flake8 aio_androidtv/ && pylint aio_androidtv/ && coverage run --source aio_androidtv setup.py test && coverage report -m
