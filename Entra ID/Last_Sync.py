'''
KB Articles

https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.usernamepasswordcredential?view=azure-python
https://github.com/AzureAD/microsoft-authentication-library-for-python/blob/1.22.0/sample/username_password_sample.py
https://www.w3schools.com/python/ref_string_replace.asp
https://www.geeksforgeeks.org/how-to-convert-pythons-isoformat-string-back-into-datetime-object/
https://stackoverflow.com/questions/35351876/calculate-time-span-in-python
https://www.geeksforgeeks.org/how-to-send-beautiful-emails-in-python/

'''

##### Start #####

# Import Modules
import requests
from msal import PublicClientApplication
import json
from datetime import datetime, timezone
from email.message import EmailMessage
import smtplib
import sys

## Variables

tenant = sys.argv[1]
authority = "https://login.microsoftonline.com/"
authority += str(tenant)
clientid = sys.argv[2]
username = sys.argv[3]
password = sys.argv[4]
scope = ['https://graph.microsoft.com/.default']
endpoint = "https://graph.microsoft.com/v1.0//organization/"
endpoint += str(tenant)
endpoint = endpoint.rstrip()

app = PublicClientApplication(client_id=clientid, authority=authority)
result = app.acquire_token_by_username_password(username, password, scope)

if "access_token" in result:
    graph_data = requests.get(
        endpoint,
        headers={'Authorization': 'Bearer ' + result['access_token']},).json()

    last_sync_unformatted = 0 #Defined for JC only as the variable was not been recognized "Name error"
    last_sync_unformatted = graph_data['onPremisesLastSyncDateTime']
    last_sync_formatted_iso = last_sync_unformatted.replace("Z", ".000000")
    last_sync_formatted_iso_python = datetime.fromisoformat(last_sync_formatted_iso)

    utc_time_now = datetime.utcnow()

    time_span_seconds = utc_time_now-last_sync_formatted_iso_python
    time_span_minutes = time_span_seconds.total_seconds()/60
    print(time_span_minutes)


else:
    print("Failed to Retrieve Token")
    msg = EmailMessage()
    msg["Subject"] = "(ACTION REQUIRED) PROD : AAD Sync Delay (JC)"
    msg["From"] = "reports@something.com"
    msg["To"] = "me@something.com"
    # https://www.chilkatsoft.com/p/p_471.asp
    # https://stackoverflow.com/questions/11843148/smtp-sending-an-priority-email
    msg["X-Priority"] = '1'
    msg.set_content("""Failed to get token""")
    server = smtplib.SMTP('smtp.com')
    server.send_message(msg)

# Send Email if the Sync is more than 2 hours
if int(time_span_minutes) > 120:
    print("AAD Sync Delayed, please check manually")
    msg = EmailMessage()
    msg["Subject"] = "PROD : AAD Sync Delay"
    msg["From"] = "reports@something.com"
    msg["To"] = "me@something.com"

    msg.set_content("""<html>
    <font
        color=Red><font size='+2'><b>ALERT : Last AAD Export Sync Duration > 2 Hrs.</b><br>
        <font
        color=Black size='+1.5'><b>Please check the run cycles and confirm they are running correctly </b>
        <ul><li>
        <b>Primary Sync Server:</b> Graph Limitation</li>
        <li><b>LastDirsync Time(UTC):</b> """ + str(last_sync_unformatted) + """ </li>
        </ul>
        <p class=MsoNormal align=center style='text-align:left'><span
    style='font-family:'Arial',sans-serif'><img width=190 height=63 id='_x0000_i1025'
    src='https://someimage.png'
    style='height:1in;width:4.5in' alt=Image><o:p></o:p></span></p>
        </html>""", subtype='html')

    server = smtplib.SMTP('smtp.com')
    server.send_message(msg)

##### End #####
