# serve-load-testing
Load testing for SciLifeLab Serve using the Python Locust library.

## Branch strategy

This repository contains two branches:

- main (default)
- develop

Make changes in the develop branch, commit and submit pull requests to merge to main.

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

Create locust tests in the /source/tests directory.

## Verify the setup by running a simple test

These tests do not need access to a host (URL) to test against.

### Running tests using the command line (headlessly)

Run the command:

    locust --headless -f ./tests/test_verify_setup.py --users 1 --run-time 10s --html ./reports/locust-report-verify-setup.html

Open the generated html report and verify that there are no errors and that the statistics look reasonable. The report is created under /source/reports/

### Using the Locust UI web client

Run the command

    locust --config locust-ui.conf --modern-ui --class-picker -f ./tests/test_verify_setup.py --html ./reports/locust-report-verify-setup-ui.html

Open a browser tab at URL http://localhost:8089/

Paste in as host

    https://staging.serve-dev.scilifelab.se

## Verify the setup and access to a host (URL)

Run the command:

    locust --headless -f ./tests/test_verify_host.py --users 1 --run-time 10s --html ./reports/locust-report-verify-host.html

Open the generated html report and verify that there are no errors and that the statistics look reasonable. The report is created under /source/reports/


## Running tests

If desired then generate html reports by editing the report name in the below commands.

Move into the source directory if not already there:

    cd ./source

### To run the Normal test plan/scenario

Before running this, run scripts to pre-create test users "locust_test_user_"*
Use minimum 10 users for the Normal test plan

    locust --headless -f ./tests/test_plan_normal.py --html ./reports/locust-report-normal.html --users 10 --run-time 30s


## Tests under development

These tests are not yet ready to be used in a load testing session.
The tests are located under directory /source/tests-dev/

### To run only the AppViewer tests

This test uses a non-authenticated user

    locust --headless -f ./tests-dev/appviewer.py --html ./reports/locust-report-appviewer.html --users 1 --run-time 20s

### To run only the test class requiring authentication

These tests require a user account in Serve and a protected page such as a project page.

- Copy the template environment file .env.template as .env
- Edit the values in the .env file

Set the environment values from the file

    set -o allexport; source .env; set +o allexport

Run the tests

    locust --headless -f ./tests-dev/authenticated.py --html ./reports/locust-report-authenticated.html --users 1 --run-time 10s


## To run tests using a Docker base image

Using provided Locust base image. To select which tests to execute, edit the file parameter -f as shown above.

    cd ./source

    docker run -p 8089:8089 -v $PWD:/mnt/locust locustio/locust -f /mnt/locust/tests/simple.py --config /mnt/locust/locust.conf --html /mnt/locust/reports/locust-report-from-docker.html
