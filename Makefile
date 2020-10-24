PWD:=$(shell pwd)

build:
	docker build -t aws-elemental-python-client .

debug:
	docker run -it --rm -e PYTHONPATH="/app" -v $(PWD):/app -w /app python:3.8 /bin/bash -c 'pip install -r requirements.txt && /bin/bash'

publish_package: build
	docker run -it --rm -v $(PWD):/app -w /app aws-elemental-python-client /app/publish_pypi.sh
