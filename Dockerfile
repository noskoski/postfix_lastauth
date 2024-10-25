FROM python:3.9

RUN mkdir /postfix_lastauth/ -p && \
        apt-get update && \
        apt-get install -y --no-install-recommends  net-tools && \
        apt dist-upgrade -y && \
        rm -rf /var/lib/apt/lists/*

RUN     rm -f   /etc/localtime && \
        ln -fs /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime 

RUN useradd -ms /bin/bash www && \
        chown www: /postfix_lastauth
USER www

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
  _loglevel=INFO \
  _loghandler=stdout

RUN pip install mysql-connector-python
 	
HEALTHCHECK CMD netstat -an | grep ${_bindport} > /dev/null; if [ 0 != $? ]; then exit 1; fi;

#VOLUME ["/postfix_lastauth"]

CMD [ "python", "/postfix_lastauth/last_auth.py" ]
