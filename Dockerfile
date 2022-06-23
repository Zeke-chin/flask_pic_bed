FROM python:3.8

WORKDIR ./docker_demo

ADD . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "server.py"]
