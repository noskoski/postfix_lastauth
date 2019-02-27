last_auth.py

Objective:

Use Postfix access control to save the last sasl authentication (smtps or submission )  (date, not datetime ) of an user in mysql 



Instalation:

  1 - install needed packages 
  ubuntu/debain:
    apt install supervisor python3-mysqldb
    
  2 - copy and edit last_auth.conf
  
       cp last_auth.conf /etc/supervisor/conf.d/ 
  

  3 - edit those lines in /etc/postfix/last_auth.py    

  _bind='127.0.0.1'
  _bindport=10007
  _myhost="localhost"
  _myuser="last_access"
  _mypasswd="XXXXXXXX"
  _mydb="mail"
  _mytable="mailbox"
  _mycolumn="last_auth"

  4 - create column in mysql

        ALTER TABLE `mailbox` ADD `last_auth` DATE NULL DEFAULT NULL; 
 
  5 - Restart supervisord
    service supervisor restart
   
  6 - add line to /etc/postfix/main.cf
  
    smtpd_last_auth = check_policy_service inet:127.0.0.1:10008 #change to the value of _bindport 
  
  7 - modify you /etc/postfix/master.cf ( smtps or/and submission entry do not use this in smtp  )

     -o smtpd_end_of_data_restrictions=$smtpd_last_auth
  
  8 - service postfix reload   

 
 

Test:
 
  1 - verify if the daemon are listening:
        
        netstat -nl |grep 10007 ( user your _bindport value )
        
    
  2 - The test
 
      cat Testfile | netcat 127.0.0.1 10007
      
      response:
      action=OK 
      
      -----
      see the mail/syslog log too:
      
      Feb 27 11:36:29 mail postfix/last_auth[102313]:[410] sasl_username:(root@localhost)
      Feb 27 11:36:29 mail postfix/last_auth[102313]:[410] _affected_rows: 1
  
  3 - Try to send an email with an authenticated user and see the mail log
      

      


 
 
 
 
 
 










