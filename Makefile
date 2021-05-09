unit:
	@echo "Running unit tests..."
	python -m unittest tests/*py

egg:
	@echo "Building egg..."
	python setup.py bdist_egg

upload:
	@echo "Uploading egg..."
	twine upload dist/*

.PHONY: unit egg upload