# ------------------------------------------------------------------------- #
# Husqy Discord Bot, see https://www.husqy.xyz for more info                #
#                                                                           #
# Copyright (C) Husqy - All Rights Reserved                                 #
# Unauthorized copying of this file, via any medium is strictly prohibited  #
# Proprietary and confidential                                              #
# Written by Luke Hendriks <luke@la-online.nl>, July 2021 (C)               #
# ------------------------------------------------------------------------- #
# START OF STAGE 1
# Set base image
FROM python:3.12.2-alpine3.19

ENV PYTHONDONTWRITEBYTECODE=1

# Copy all files
COPY . /Victreebot

# Initialize Git and install requirements
RUN cd /Victreebot && pip install --no-cache-dir --no-deps --no-compile -r /Victreebot/requirements.txt

# Start
CMD python3 -O /Victreebot/victreebot/__main__.py
# END OF STAGE 1