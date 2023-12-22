# serve-load-testing
Load testing for SciLifeLab Serve using the Python Locust library.

## Branch strategy

This repository contains two branches:

- main (default)
- develop

## Setup

    cd ./source
    python3 -m venv .venv
    source ./.venv/bin/activate
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt

    locust -V

## Configuration options

To configure the test runs, use the Locust configuration file ./source/locust.conf
For options, see https://docs.locust.io/en/stable/configuration.html

## Create tests

Create locust tests in the source/tests directory.

## Verify the setup by running a simple test

### At the command line, headlessly

Run the command:

    locust --headless -f ./tests/simple.py --users 1 --run-time 10s --html ./reports/locust-report-simple.html

Open the generated html report and verify that there are no errors and that the statistics look reasonable. The report is created under /source/reports/

### Using the Locust UI web client

Run the commands

    cd ./tests
    locust --modern-ui --class-picker -f simple.py

Open a browser tag at URL http://localhost:8089/

Paste in as host

    https://staging.serve-dev.scilifelab.se

## Running tests

If desired generate html reports by editing the report name in the below commands.

### Run tests headlessly

    cd ./source

### To run only the Website tests

    locust -f ./tests/website.py --html ./reports/locust-report-website.html

### To run only the API tests

    locust -f ./tests/api.py --html ./reports/locust-report-api.html

