import ldap3
from ldap3 import Server, Connection, ObjectDef, Tls, ALL
import sys
import os
import ssl
import keyring

username=keyring.get_password('AAD_Id','User')  # in domain\user format
userpsd=keyring.get_password('AAD_Password','Password')

# Define the TLS configuration with only the CA certificate
tls_configuration = Tls(
    validate=ssl.CERT_REQUIRED,
    ca_certs_file=os.path.join(os.getcwd(),'cabundle.pem')
)


server = Server('something.com', use_ssl=True, tls=tls_configuration, get_info=ALL)
conn = Connection(server,user=username,password=userpsd)

if conn.bind():
     print("Bind Successful")
     obj_person = ObjectDef('person', conn)
     conn.search(
          search_base='dc=something,dc=com',
          search_filter='(samaccountname=userid)',
          search_scope='SUBTREE',
          attributes=[
               'displayName',
               'userAccountControl',
               'pwdLastSet',
               'lastLogonTimeStamp',
               'userPrincipalName',
               'sAMAccountName'
               ]
          )
     print(conn.entries)
     conn.unbind()
else:
     print("Failed to Bind",conn.result)
