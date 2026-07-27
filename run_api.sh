#!/usr/bin/env bash

export PYTHONPATH=./src
uvicorn --app-dir ./src progsnap2.api.main:app --reload --reload-dir ./src/