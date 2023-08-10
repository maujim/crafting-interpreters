VENV ?= venv

repl: venv
	./$(VENV)/bin/python -m lox

./$(VENV)/bin/activate:
	python3.9 -m venv $(VENV)
	./$(VENV)/bin/pip install --editable .

venv: ./$(VENV)/bin/activate

test:
	ls tests/*.lox | xargs -I '{}' python -m lox {}
