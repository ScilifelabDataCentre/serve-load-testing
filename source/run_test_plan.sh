#!/bin/bash

set -o errexit

# Activate the virtual env
source ./.venv/bin/activate

# Set the env variables from this project
set -o allexport; source .env; set +o allexport

# Run 2 sets of tests in parallel: the non-locust user apps and the locust test plan

python3 ./tests-dev/appviewer_requestshtml.py & \
locust --headless -f ./tests/test_plan_normal.py --users 10 --run-time 60s --html ./reports/locust-report-normal.html
