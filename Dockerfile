FROM ubuntu:16.04

# Install dependencies
RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

RUN apt-get install -y git curl
RUN git clone https://github.com/Pratilipi/search

EXPOSE 2579

WORKDIR search

RUN pip install -r requirements.txt

CMD python src/main.py localhost 2579

