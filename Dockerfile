FROM pre-harbor.webull.com/library/python:3.10.11-slim-buster

WORKDIR ./

COPY requirements.txt requirements.txt
RUN pip3 config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple/ &&\
    pip3 install -r requirements.txt

COPY . ./easy-automation-test

RUN pip3 install -e easy-automation-test