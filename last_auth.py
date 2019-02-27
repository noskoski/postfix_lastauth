#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""last_auth.py: Postfix Daemon that saves last sasl auth date ."""

__author__      = "Leandro Abelin Noskoski"
__site__	= "www.alternativalinux.net"
__projectpage__ = "https://github.com/noskoski/postfix_smtpd_last_auth"
__copyright__   = "Copyright 2019, Alternativa Linux"
__license__ 	= "GPL"
__version__ 	= "1.0.1"
__maintainer__ 	= "Leandro Abelin Noskoski"
__email__ 	= "leandro@alternatialinux.net"
__status__ 	= "Production"

import socket,struct,sys,time, logging, re, MySQLdb, syslog, errno, signal, threading, unicodedata
from logging.handlers import SysLogHandler

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

_bind='127.0.0.1'
_bindport=10007
_myhost="localhost"
_myuser="dba"
_mypasswd="a9x3"
_mydb="mail"
_mytable="mailbox"
_mycolumn="last_auth"


logger = logging.getLogger()
syslog = SysLogHandler(address='/dev/log', facility='mail')
formatter = logging.Formatter('postfix/%(module)s[%(process)d]:%(message)s')
syslog.setFormatter(formatter)
logger.addHandler(syslog)

# Loglevel INFO
logger.setLevel(logging.INFO)
# Loglevel Debug
#logger.setLevel(logging.NOTSET)

syslog = SysLogHandler(address='/dev/log', facility='mail')
formatter = logging.Formatter('postfix/%(module)s[%(process)d]:%(message)s')
syslog.setFormatter(formatter)
logger.addHandler(syslog)

class Job(threading.Thread):

    def __init__(self,sock,name):
        threading.Thread.__init__(self)
        self.start = time.time()
        self.shutdown_flag = threading.Event()
        self.sock = sock
        self.name = name
        self.__sasl_username = ""
        self.__end='\n\n'
        self.__total_data = ""
        self.terminate = 0
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def recv_timeout(self):

        while not self.shutdown_flag.is_set():

            try:
                data=self.sock.recv(64)
                if data == b'':
                    break
                if data.decode("UTF-8") :
                    self.__total_data  = self.__total_data + data.decode("UTF-8")
                    if self.__end in data.decode("UTF-8") :
                        break
                else:
                    break
            except UnicodeDecodeError as e:
                logging.error(self.name + " unicode error: %s " % str(e) )
                break
            except KeyboardInterrupt:
                logging.error(self.name + ' CTRL-C HIT')
                break

            except socket.error as e:
                logging.error(self.name + " socket error: %s " % str(e) )
                break

        logging.debug(self.name + " end of recv: (" + str(len(self.__total_data)) + ")")

        if (len(str(self.__total_data))>10):
            for item in self.__total_data.split("\n"):
                if 'sasl_username' in item:
                    self.__sasl_username = item.split('=')[1]
        else :
            self.__sasl_username = ''

        if len(self.__sasl_username) < 5 :
            self.__sasl_username=''
        else:
            try:
                self.sock.sendall(b"action=OK\n\n")
                logging.debug(self.name + ' sending OK, go ahead')

            except socket.error as e:
                logging.error(self.name + " socket error: %s " % str(e) )

    def run(self):

        logging.debug('%s Thread  started' % self.name)
        self.recv_timeout()
        if len(self.__sasl_username) > 5 :
           try:
               logging.info(self.name + ' sasl_username:(' + self.__sasl_username + ')')
               _con = MySQLdb.connect(host=_myhost, user=_myuser, passwd=_mypasswd, db=_mydb)
               _cursor = _con.cursor()
               _s = "UPDATE %s set %s = date(now()) WHERE username=\"%s\" ; " % (_mytable,_mycolumn,str(self.__sasl_username))
               logging.debug("SQL: " + _s )
               _affected_rows = _cursor.execute(_s)
               _con.commit()
               logging.info(self.name + ' _affected_rows: ' + str(_affected_rows))
               _con.close()

           except MySQLdb.Error as e:
               _con.rollback()
               _con.close()
               logging.error(self.name + " mySQL Error: %s" % str(e))

        self.sock.close()
        self.terminate = 1
        logging.debug('%s Thread  stopped : (%.4f)' % (self.name, time.time() - self.start , ) )

class ServiceExit(Exception):
    pass

def service_shutdown(signum, frame):
    logging.debug('Caught signal %d' % signum)
    raise ServiceExit


def Main():

    socket.setdefaulttimeout(360)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)
    i = 1
    aThreads = []
    sockok=0

    while (not sockok):

        try:
            s.bind((_bind, _bindport))
            logging.debug(' socket binded to port: ' + str(_bindport))
            # put the socket into listening mode
            s.listen(128)
            logging.debug(' socket is listening')
            sockok=1

        except socket.error as e:
            logging.error(" socket error: %s " % str(e) )
            time.sleep(2)


    while True:

        try:
            c, addr = s.accept()
        except socket.error as e:
            logging.error(" socket error: %s " % str(e) )
            pass
        except ServiceExit:
            logging.warning(" ServiceExit : " )
            for th in aThreads:
                th.shutdown_flag.set()
                th.sock.close()
                th.join()

        if c:
            logging.debug(' connected to :' + str(addr[0]) + ':' + str(addr[1]))
            process = (Job(c,"[" + str(i) + "]"))
            process.daemon = True
            process.start
            aThreads.append(process)
            del process

        i += 1
        if (i > 99999):
            i = 0

        for th in aThreads:
                if th.terminate:
                    aThreads.remove(th)

        logging.debug("Thread count: " + str(len(aThreads)) )

    logging.debug(' close socket ')


    for process in aThreads:
        process.join()

    try:
        s.close()
    except:
        pass

    self.terminate = 1


if __name__ == '__main__':
    Main()
