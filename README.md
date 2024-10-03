# serve-load-testing
Load testing for SciLifeLab Serve using the Python Locust library.

## Branch strategy

This repository contains two branches:

- main (default)
- develop

Make changes in the develop branch, commit and submit pull requests to merge to main.

## Setup for local development

### Using virtual environments with venv

    cd ./source
    python3 -m venv .venv
    source ./.venv/bin/activate
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt

### Using pyenv

    cd ./source
    pyenv virtualenv 3.12.2 locust-3.12.2
    pyenv local locust-3.12.2
    pyenv version
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt

### Check the Locust version

    locust -V

## Configuration options

To configure the test runs, use the Locust configuration file ./source/locust.conf
For options, see the [Locust docs](https://docs.locust.io/en/stable/configuration.html)

You can override all of the settings set in the configuration file by setting the same
on the command line. For example, to override the log level settings use --loglevel as in example:

    locust --headless -f ./tests/test_verify_setup.py --loglevel debug


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

    locust --config locust-ui.conf --class-picker -f ./tests/test_verify_setup.py --html ./reports/locust-report-verify-setup-ui.html

Open a browser tab at URL http://localhost:8089/

Paste in as host

    https://serve-dev.scilifelab.se

## Verify the setup and access to a host (URL)

Run the command:

    locust --headless -f ./tests/test_verify_host.py --users 1 --run-time 10s --html ./reports/locust-report-verify-host.html

Open the generated html report and verify that there are no errors and that the statistics look reasonable. The report is created under /source/reports/


## Running tests

### Prepare for running tests

Some of the tests require pre-existing test users that are named with the format "locust_test_user_"*
Therefore, before running the tests, run the script to create them in the test environment. This can be performed using the Django manage module while connected to the Serve studio pod. For example to add 10 test users, run:

    python3 manage.py add_locust_users 10

When the tests are completed, you can remove the test users by running:

    python3 manage.py remove_locust_users

Move into the source directory if not already there:

    cd ./source

- Copy the template environment file .env.template as .env

    cp ./.env.template .env

- Edit the following values in the .env file according to your needs.

    - SERVE_LOCUST_TEST_USER_PASS=(The password of the test locust users)
    - SERVE_LOCUST_DO_CREATE_OBJECTS=(A boolean indicating whether to create objects in Serve such as projects and apps)

Set the environment values from the file

    set -o allexport; source .env; set +o allexport

If desired then generate html reports by editing the report name in the below commands.

### To run the Normal test plan/scenario

Use minimum 10 users for the Normal test plan

    locust --headless -f ./tests/test_plan_normal.py --html ./reports/locust-report-normal.html --users 10 --run-time 30s

Or using the Web UI

    locust --config locust-ui.conf --class-picker -f ./tests/test_plan_normal.py --html ./reports/locust-report-normal-ui.html --users 10 --run-time 30s


### To run the Classroom test plan/scenario

    locust --headless -f ./tests/test_plan_classroom.py --html ./reports/locust-report-classroom.html --users 1 --run-time 30s

## Tests under development

These tests are not yet ready to be used in a load testing session.
The tests are located under directory /source/tests-dev/

### To run only the AppViewer tests

This test uses a non-authenticated user

    locust --headless -f ./tests-dev/appviewer.py --html ./reports/locust-report-appviewer.html --users 1 --run-time 20s

### To run only the test class requiring authentication

These tests require a user account in Serve and a protected page such as a project page.

Run the tests

    locust --headless -f ./tests-dev/authenticated.py --html ./reports/locust-report-authenticated.html --users 1 --run-time 10s


## To run tests using a Docker base image

Using provided Locust base image. To select which tests to execute, edit the file parameter -f as shown above.

    cd ./source

    docker run -p 8089:8089 -v $PWD:/mnt/locust locustio/locust -f /mnt/locust/tests/simple.py --config /mnt/locust/locust.conf --html /mnt/locust/reports/locust-report-from-docker.html


## To run k8s pod-creating tests

The Locust app-viewer tests do not currently create pods on the cluster. In order to run such tests, configure and execute appviewer_requestshtml.py

    python3 ./tests-dev/appviewer_requestshtml.py


## Use the shell script to run tests

The shell script can be used to execute multiple simultaneous types of tests (such as Locust plus a scripted test).

Edit the configuration in locust.conf and in .env. If running the appviewer_requestshtml.py module, then also configure settings in this file.

```
$ cd ./source
$ chmod +x run_test_plan.sh
$ ./run_test_plan.sh
```

## Use a custom built docker image

Copy the environment variables template file to .env and edit as needed. Then run:

    cd ./source

    docker build -t serve-load-testing .

    docker run -p 8089:8089 --env-file ./.env serve-load-testing


## Deploy to a kubernetes cluster in a production environment

The repository is setup for deployment to a kubernetes cluster using ArgoCD.
This is however beyond the scope of this document.


## Deploy to a local kubernetes clusing for local development

You might want to do this to troubleshoot a kubernetes deployment.
Manifests for a local deployment are provided using Kustomize.
Use togetehr with the CLI kubectl.

Create a deployment named locust-deployment in a new namespace locust:

    kustomize build ./manifests/overlays/development | kubectl apply -f - --force

To delete the deployments created:

    kubectl -n locust delete deployment locust-deployment
    kubectl -n locust delete deployment postgres-deployment


## Integrate locust-plugins

locust-plugins is an add on to locust that adds functionality such as persisting test restults to a database.
More specifically, we use the dashboards feature or locust-plugins. See

https://github.com/SvenskaSpel/locust-plugins/tree/master/locust_plugins/dashboards

To setup locust-plugins, there is an option to use locust-compose or manually setup. We use manual setup so that the
dashboards can always be running.

locust-plugins is integrated in the production version of this project (deployed to kubernetes using k8s manifests and a built docker image) but not used in local development. However the dashboards can be installed locally using:

    pip3 install locust-plugins[dashboards]

Or use a docker image

    docker run cyberw/locust-timescale:6
