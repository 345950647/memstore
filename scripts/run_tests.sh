#!/usr/bin/env bash

export PYTHONPATH=./src

echo "Running tests..."
coverage run -m pytest

echo "Generating coverage report..."
coverage report

echo "Generating HTML coverage report..."
coverage html

echo "Done! Check the coverage report in htmlcov/index.html"