.PHONY: release
release:
	rm -rf dist
	scripts/git_tag.sh
	python setup.py sdist bdist_wheel
	twine upload dist/*

.PHONY: docs
docs:
	@cd docs/source && rm -f androidtv*.rst
	@cd docs && sphinx-apidoc -f -e -o source/ ../androidtv/
	@cd docs && make html && make html

.PHONY: test
test:
	python setup.py test

.PHONY: coverage
coverage:
	coverage run --source androidtv setup.py test && coverage html && coverage report -m

.PHONY: tdd
tdd:
	coverage run --source androidtv setup.py test && coverage report -m

.PHONY: lint
lint:
	flake8 androidtv/ && pylint androidtv/

.PHONY: alltests
alltests:
	flake8 androidtv/ && pylint androidtv/ && coverage run --source androidtv setup.py test && coverage report -m
