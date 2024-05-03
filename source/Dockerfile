# Use the Locust image as the base image
FROM locustio/locust:2.25.0

WORKDIR /home/locust

# Install the locust-plugins dashboards plugin
RUN pip3 install --no-cache-dir locust-plugins[dashboards]==4.4.2

# Copy the Locust files into the container
COPY --chown=locust:locust locust-ui.conf locust.conf
COPY --chown=locust:locust tests/ tests
COPY --chown=locust:locust start-script.sh start-script.sh

RUN chmod ug+x start-script.sh

EXPOSE 8089 5557
