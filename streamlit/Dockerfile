# pull official base image
FROM python:3.10.12-slim-buster

# set work directory
WORKDIR /streamlit

# Set bash as the default shell
ENV SHELL=/bin/bash
    
RUN apt-get update && apt-get install -y \
    python3-pip \
    apt-utils \
    vim \
    git

# alias python='python3'
RUN ln -s /usr/bin/python3 /usr/bin/python

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt


CMD streamlit run main.py --server.port 8501

# copy project
COPY . .
