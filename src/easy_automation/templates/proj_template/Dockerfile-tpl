FROM python:3.9.20-slim

WORKDIR /test-agent

COPY requirements.txt requirements.txt
RUN pip3 config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple/ &&\
    pip3 install -r requirements.txt

COPY . .

EXPOSE 8839
CMD [ "gunicorn", "-w", "1", "-b", ":8839", "easy_test:create_app()"]