# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2022-2024 S. K. Medlock, E. K. Herman, K. M. Shaw

SHELL=/bin/bash

.PHONY: default
default: run

python-venv/bin/activate: requirements.txt
	rm -rf python-venv
	python3 -m venv python-venv
	source python-venv/bin/activate && \
	 pip3 install --upgrade pip
	source python-venv/bin/activate && \
	 pip3 install -r requirements.txt

.PHONY: run
run: heartmodel.py python-venv/bin/activate
	source python-venv/bin/activate && \
	 python3 $<

.PHONY: clean
clean:
	rm -rf python-venv
