'''
Author : Arvinder
Description : This Job will be used to track specific accounts in groups with certain prefix

'''

from ldap3 import Server, Connection, ObjectDef, Tls, ALL
import sys
import os
import ssl
from email.message import EmailMessage
import smtplib
from datetime import datetime

username=sys.argv[1] # in domain\user format
userpsd=sys.argv[2]

# Define the TLS configuration with only the CA certificate
tls_configuration = Tls(
    validate=ssl.CERT_REQUIRED,
    ca_certs_file=os.path.join(os.getcwd(),'cabundle.pem')
)

server = Server('something.com', use_ssl=True, tls=tls_configuration, get_info=ALL)
conn = Connection(server,user=username,password=userpsd)

## Define count variables
group1_count=0
group2_count=0

if conn.bind():
     print("Bind Successful")
     with open("Groups.txt","r") as groups_file:
          for line in groups_file:
               group = line.strip()
               #print(group)
               if not group:
                    continue # Skip empty lines
               search_filter = f'(samaccountname={group})'
               conn.search(
                    search_base='dc=something,dc=com',
                    search_filter=search_filter,
                    attributes=['name','member'] ## ['*','+'] to get all attributes run only this
                    )
               if conn.entries[0]['name'].value.lower().startswith('group1'.lower()):
                    for user in conn.entries[0]['member']:
                         if user.startswith('CN=some_prefix'):
                              group1 += 1

               if conn.entries[0]['name'].value.lower().startswith('group2'.lower()):
                    for user in conn.entries[0]['member']:
                         if user.startswith('CN=some_prefix'):
                              group2 += 1

     message = """
     <html><body>
     <h2 style='font-size:25px;font-family:Calibri;color:#6F9824''>Group Monitoring for prefix Accounts</h2><BR>
     <Table><TABLE style="font-size:11pt;font-family:Calibri" BORDER=1><tr bgcolor="#D5D5D4"><TD><B>Group</B></TD><TD><B>Count</B></TD></TR>
     <TD>group1</TD><TD> """ + str(group1_count) + """ </TD></TR>
     <TD>group2</TD><TD> """ + str(group2_count) +"""</TD></TR>
     </TABLE>
     <br>
     </body></html>
"""
          
     email = EmailMessage()
     sender = "reports@something.com"
     email["From"] = sender

     recipient = "me@something.com"
     email["To"] = recipient

     subject = ""
     subject += "Account Count - Groups - "
     subject += datetime.now().strftime("%m-%d-%Y")
     subject += " (automation)"
     email["Subject"] = subject

     email.set_content(message, subtype="html")

     smtp= ""
     smtp = smtplib.SMTP("smtp.com")

     smtp.sendmail(sender, recipient, email.as_string())
     smtp.quit()
     conn.unbind()
else:
     print("Failed to Bind",conn.result)
