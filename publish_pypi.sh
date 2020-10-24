#!/bin/bash
python setup.py sdist bdist_wheel
twine upload dist/*
rm -rf aws_elemental_python_client.egg-info/
rm -rf build/
rm -rf dist/