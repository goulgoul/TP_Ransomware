FROM python:3

RUN apt update && apt install -y python3-pip iproute2 nmap iputils-ping

RUN pip3 install cryptography requests