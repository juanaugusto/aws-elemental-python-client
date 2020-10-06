PWD:=$(shell pwd)


debug:
	docker run -it --rm -e PYTHONPATH="/app" -v $(PWD):/app -w /app python:3.8 /bin/bash -c 'pip install -r requirements.txt && /bin/bash'
