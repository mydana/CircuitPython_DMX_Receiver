# SPDX-FileCopyrightText: Copyright (c) 2024 Dana Runge
#
# SPDX-License-Identifier: Unlicense
install:
	python3 -m venv .venv; \
	source .venv/bin/activate; \
	pip install -Ur requirements.txt; \
	pip install -Ur requirements/dev.txt;

.PHONY: docs
docs:
	source .venv/bin/activate; \
	cd docs; \
	sphinx-build -E -W -b html . _build/html;

check:
	source .venv/bin/activate; \
	pre-commit run --all-files;

deploy:
	source .venv/bin/activate; \
	python3 deploy.py --code=examples/dmx_receiver_simpletest.py \
	--pin=board.D3 dmx_receiver.py

clean:
	rm -rf .venv
	find -iname "*.pyc" -delete
	rm -rf docs/_build/html
