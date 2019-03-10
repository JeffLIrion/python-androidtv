.PHONY: release
release:
	rm -rf dist
	python setup.py sdist bdist_wheel
	twine upload dist/*
	
.PHONY: docs
docs:
	@cd docs && sphinx-apidoc -f -e -o source/ ../androidtv/
	@cd docs && make html && make html
