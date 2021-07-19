FROM python:3.9

MAINTAINER "leandro@alternativalinux.net"

RUN mkdir /postfix_lastauth/ -p

WORKDIR /postfix_lastauth

RUN git clone --progress --verbose  https://github.com/noskoski/postfix_lastauth /postfix_lastauth

ENV _bind=0.0.0.0 \
  _bindport=10007 \
  _bindtimeout=120 \
  _myhost=mysql \
  _myuser=mail \
  _mypasswd=1a2b3c \
  _mydb=mail \
  _logfacility=mail \
  _logaddress=172.17.0.1 \
  _logport=514 \
  _loglevel=INFO

RUN pip install mysql-connector-python

VOLUME ["/postfix_lastauth"]

CMD [ "python", "/postfix_lastauth/last_auth.py" ]
