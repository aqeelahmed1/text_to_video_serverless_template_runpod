# Base image -> https://github.com/runpod/containers/blob/main/official-templates/base/Dockerfile
# DockerHub -> https://hub.docker.com/r/runpod/base/tags
# FROM runpod/base:0.4.0-cuda11.8.0
FROM runpod/pytorch:2.2.1-py3.10-cuda12.1.1-devel-ubuntu22.04

# The base image comes with many system dependencies pre-installed to help you get started quickly.
# Please refer to the base image's Dockerfile for more information before adding additional dependencies.
# IMPORTANT: The base image overrides the default huggingface cache location.


# --- Optional: System dependencies ---
# COPY builder/setup.sh /setup.sh
# RUN /bin/bash /setup.sh && \
#     rm /setup.sh


# Python dependencies
COPY builder/requirements.txt /requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install  --upgrade pip && \
    python-m pip install --default-timeout=100 --upgrade -r /requirements.txt --no-cache-dir && \
    rm /requirements.txt

# NOTE: The base image comes with multiple Python versions pre-installed.
#       It is reccommended to specify the version of Python when running your code.


# Add src files (Worker Template)
ADD src .

RUN --mount=type=cache,target=/root/.cache/pip python /handler.py --default-timeout=100

CMD python -u /handler.py
