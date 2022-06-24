FROM python:3.8

WORKDIR ./docker_demo

ADD . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["supervisord", "-n"]

RUN echo "\
[program:server] \n\
command=/usr/sbin/sshd -D\n\
autorestart=True\n\
autostart=True\n\
redirect_stderr = true\n\
" > /etc/supervisor/conf.d/server.conf


CMD ["python", "server.py"]

