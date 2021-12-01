.PHONY: release
release:
	rm -rf dist
	rm -rf build
	scripts/git_tag.sh
	python setup.py sdist bdist_wheel
	twine upload dist/*

.PHONY: docs
docs:
	@cd docs/source && rm -f androidtv*.rst
	@cd docs && sphinx-apidoc -f -e -o source/ ../androidtv/
	@cd docs && make html && make html

SYNCTESTS := $(shell cd tests && ls test*.py | grep -v async)

.PHONY: test
test:
	python --version 2>&1 | grep -q "Python 2" && (for synctest in $(SYNCTESTS); do python -m unittest discover -s tests/ -t . -p "$$synctest"; done) || true
	python --version 2>&1 | grep -q "Python 3" && python -m unittest discover -s tests/ -t . || true

.PHONY: coverage
coverage:
	coverage run --source androidtv -m unittest discover -s tests/ -t . && coverage html && coverage report -m

.PHONY: tdd
tdd:
	coverage run --source androidtv -m unittest discover -s tests/ -t . && coverage report -m

.PHONY: lint
lint:
	flake8 androidtv/ && pylint androidtv/

.PHONY: black
black:
	black --safe --line-length 120 --target-version py35 androidtv
	black --safe --line-length 120 --target-version py35 tests
	black --safe --line-length 120 --target-version py35 setup.py

.PHONY: lint-black
lint-black:
	black --check --safe --line-length 120 --target-version py35 androidtv
	black --check --safe --line-length 120 --target-version py35 tests
	black --check --safe --line-length 120 --target-version py35 setup.py

.PHONY: alltests
alltests:
	flake8 androidtv/ && pylint androidtv/ && coverage run --source androidtv -m unittest discover -s tests/ -t . && coverage report -m
