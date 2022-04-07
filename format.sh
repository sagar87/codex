#!/bin/bash

black .
isort --profile black .
flake8 . 