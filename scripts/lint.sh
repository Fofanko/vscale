#!/usr/bin/env bash

set -x

mypy app
black app --check