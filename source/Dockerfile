# Use the Locust image as the base image
# It in turn is based on python:3.11-slim
FROM locustio/locust:2.31.8

WORKDIR /home/locust

# Install the locust-plugins dashboards plugin etc
RUN pip3 install --no-cache-dir --upgrade pip==23.3.2 \
    && pip3 install --no-cache-dir lxml_html_clean>=0.2.2 \
    && pip3 install --no-cache-dir requests-html>=0.10.0 \
    && pip3 install --no-cache-dir locust-plugins[dashboards]==4.5.3

# Copy the Locust files into the container
COPY --chown=locust:locust locust-ui.conf locust.conf
COPY --chown=locust:locust tests/ tests
COPY --chown=locust:locust tests-dev/ tests-dev
COPY --chown=locust:locust start-script.sh start-script.sh
COPY --chown=locust:locust run_test_plan.sh run_test_plan.sh

RUN chmod ug+x start-script.sh
RUN chmod ug+x run_test_plan.sh

EXPOSE 8089 5557
