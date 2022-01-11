.PHONY: all
all:
	make requirements
	make install


.PHONY: install
install:
	pip install -e .


.PHONY: uninstall
uninstall:
	pip uninstall pad_configuration


.PHONY: requirements
requirements:
	pip install -r requirements.txt
