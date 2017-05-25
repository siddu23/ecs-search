FROM ubuntu:16.04

# Install dependencies
RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

RUN apt-get install -y git curl
RUN git clone https://github.com/Pratilipi/search

WORKDIR search

RUN pip install -r requirements.txt

EXPOSE 8080

CMD python src/main.py

