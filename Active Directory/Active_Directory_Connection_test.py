import ldap3
from ldap3 import Server, Connection, ObjectDef, Tls, ALL
import sys
import os
import ssl

username=sys.argv[1] # in domain\user format
userpsd=sys.argv[2]

# Define the TLS configuration with only the CA certificate
tls_configuration = Tls(
    validate=ssl.CERT_REQUIRED,
    ca_certs_file=os.path.join(os.getcwd(),'cabundle.pem')
)

print("TLS Configuration")
print(tls_configuration)

server = Server('server.com', use_ssl=True, tls=tls_configuration, get_info=ALL)
conn = Connection(server,user=username,password=userpsd)

if conn.bind():
     print("Bind Successful")
     obj_person = ObjectDef('person', conn)
     #print(conn.extend.standard.who_am_i()) ## I used this to print username and it is in netbios format.. domain\samaccountname
     conn.search(search_base='dc=server,dc=com',
          search_filter='(samaccountname=userid)')
     print(conn.entries)
     conn.unbind()
else:
     print("Failed to Bind",conn.result)
