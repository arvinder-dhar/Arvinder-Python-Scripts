# import necessary packages
  
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# create message object instance
msg = MIMEMultipart()

message = "Welcome to World of Python"
  
# setup the parameters of the message
msg['From'] = "user@something.com"
msg['To'] = "user@something.com"
msg['Subject'] = "Python"

# add in the message body
msg.attach(MIMEText(message, 'plain'))
  
#create server
server = smtplib.SMTP('smtp.com')
  
# send the message via the server.
server.sendmail(msg['From'], msg['To'], msg.as_string())
