FROM python:3

RUN apt update && apt install -y python3-pip iproute2 nmap iputils-ping
RUN pip3 install cryptography requests
RUN touch a_little_text_file_to_test_my_ransomware.txt
RUN echo "This is a brilliant way to test whether my ransomware works, isn't it? I guess I should do this more often #8^)" > a_little_text_file_to_test_my_ransomware.txt

