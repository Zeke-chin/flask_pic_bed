FROM python:3.8

WORKDIR ./docker_demo

ADD . .

RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && pip install -r requirements.txt

EXPOSE 5000

RUN mkdir -p /var/log/supervisor
RUN mkdir -p /etc/supervisor/conf.d

RUN echo_supervisord_conf > /etc/supervisor/supervisord.conf
RUN echo "\
[program:server] \n\
command=/usr/local/bin/gunicorn server:app -w2 -b0.0.0.0:5000  --worker-class=gevent\n\
autorestart=true\n\
startretries=0\n\
redirect_stderr=true\n\
stdout_logfile=/var/log/server.log\n\
stdout_logfile_maxbytes=0\n\
" >> /etc/supervisor/supervisord.conf

CMD ["/usr/local/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]