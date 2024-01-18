#!/bin/bash

set -o errexit

source ./.venv/bin/activate

# Start user app tests
python3 ./tests-dev/appviewer_requestshtml.py

# Start locust tests
locust --headless -f ./tests/test_verify_setup.py --users 1 --run-time 10s --html ./reports/locust-report-verify-setup.html
