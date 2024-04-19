# Use the Locust image as the base image
FROM locustio/locust:2.25.0

WORKDIR /home/locust

# TODO: pip install requirements without locust

# Copy the Locust files into the container
COPY locust-ui.conf locust.conf
COPY tests/ tests
COPY start-script.sh start-script.sh

# Expose the Locust web UI port
EXPOSE 8089
