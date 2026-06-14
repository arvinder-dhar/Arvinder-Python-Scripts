'''
Author : Arvinder
Description : This Job will be used to track
    1. Cloud only accounts
    2. Newly Created Cloud Accounts
    3. On-prem synced accounts with Cloud UPN

KB's
    1. https://www.itsolutionstuff.com/post/how-to-add-header-in-csv-file-using-pythonexample.html
    2. https://pythonassets.com/posts/send-html-email-with-attachments-via-smtp/
'''

#### Start ####

## Import Modules
from msal import PublicClientApplication
import sys
import requests
import os
import time
import csv
from datetime import datetime
from email.message import EmailMessage
import smtplib
import pandas

print("Start Time")
print(datetime.now().strftime("%B-%d-%Y-%H-%M"))

## Variables
tenant = sys.argv[1]
clientid = sys.argv[2]
username = sys.argv[3]
password = sys.argv[4]

authority = "https://login.microsoftonline.com/"
authority += str(tenant)
scopes = ["https://graph.microsoft.com/.default"]

app = PublicClientApplication(client_id=clientid,authority=authority)
result = app.acquire_token_by_username_password(username,password,scopes)

graph_api = "https://graph.microsoft.com/beta/users/"

## Function to get all Cloud Users

## Function to check if
# 1. File exists > delete > create empty
# 2. No File present > create empty
# 3. In any of the above, add Column headers

def Create_File(name):
    file_name = str(name + ".csv")
    if os.path.exists(file_name):
        # Delete if file already present
        print("{} File is present, deleting and re-creating empty".format(file_name))
        os.remove(file_name)
        # Induce Delay
        time.sleep(3)
        # Create New File
        new_file = open(file_name,"x")
        csv.writer(new_file)
        new_file.close()
   
    else:
        print("{} File is not present, creating new & empty".format(file_name))
        # Create New File
        new_file = open(file_name,"x")
        csv.writer(new_file)
        new_file.close()

## If access token is retreived, iterate through all Organization Users
if "access_token" in result:
    print("Token Acquired")
    ## Get All Users in the Organization
    users = []
    graph_data = requests.get(
            graph_api,
            headers={'Authorization': 'Bearer ' + result['access_token']},).json()
    users = graph_data['value']
    odata_next_link = graph_data['@odata.nextLink']
    while (odata_next_link):
        try:
            #print(graph_data['@odata.nextLink'])
            graph_data = requests.get(graph_data['@odata.nextLink'],headers={'Authorization': 'Bearer ' + result['access_token']},).json()
            users += graph_data['value']
            #time.sleep(3) ## Induce Delay

        except:
            break

    print("User Count {}".format(len(users)))

    ## Call the API again if the data is not extracted properly
    # Get All User Count in the Organization
    all_users = requests.get(
            "https://graph.microsoft.com/v1.0/users/$count",
            headers={ "ConsistencyLevel" : "eventual",
                'Authorization': 'Bearer ' + result['access_token']}).json()
    print("Total Users in the Organization {}".format(all_users))
    if len(users) < (all_users - 1000):
        print('Retrying as the Previous User Count was low, User Count {}'.format(len(users)))
        print("Token Acquired")
        users = []
        graph_data = requests.get(
                graph_api,
                headers={'Authorization': 'Bearer ' + result['access_token']},).json()
        users = graph_data['value']
        odata_next_link = graph_data['@odata.nextLink']
        while (odata_next_link):
            try:
                #print(graph_data['@odata.nextLink'])
                graph_data = requests.get(graph_data['@odata.nextLink'],headers={'Authorization': 'Bearer ' + result['access_token']},).json()
                users += graph_data['value']

            except:
                break
    
        print("New User Count {}".format(len(users)))

    ## Create Empty Files
    Create_File("CloudOnlyUser")
    Create_File("UPNIssue")

    ## Open Files & Add Headers

    # Cloud Only File
    CloudOnlyUser = open("CloudOnlyUser.csv",'w', newline='')
    # Add headers
    print("Adding Headers on Cloud Only User File")
    header = ['ObjectID','UserPrincipalName','CreatedDateTime','onPremisesSyncEnabled','OnPremisesLastSyncDateTime','OnPremisesImmutableId','AccountEnabled','OnPremisesProvisioningErrors']
    # Write headers with csv writer
    csv.writer(CloudOnlyUser).writerow(header)

    # UPN Issue File
    UPNIssue = open("UPNIssue.csv",'w', newline='')
    # Add headers
    print("Adding Headers on UPN Issue File")
    header = ['ObjectID','UserPrincipalName','CreatedDateTime','onPremisesSyncEnabled','OnPremisesLastSyncDateTime','OnPremisesImmutableId','AccountEnabled','OnPremisesProvisioningErrors']
    # Write headers with csv writer
    csv.writer(UPNIssue).writerow(header)
    
    for user in users:
        # Write to CloudOnlyUser File
        if user['onPremisesSyncEnabled'] == None:
            if user['onPremisesProvisioningErrors']:
               onPremisesProvisioningErrors = user['onPremisesProvisioningErrors'][0]['category']
            else:
               onPremisesProvisioningErrors = "None"
            cloudonlyuser_data = [user['id'],user['userPrincipalName'],user['createdDateTime'],user['onPremisesSyncEnabled'],user['onPremisesLastSyncDateTime'],user['onPremisesImmutableId'],user['accountEnabled'],onPremisesProvisioningErrors]
            csv.writer(CloudOnlyUser).writerow(cloudonlyuser_data)

        # Write to UPN Issue File
        if (user['onPremisesSyncEnabled'] == True and
            not(user['userPrincipalName'].startswith("Sync_connectserver1")) and # this will change in latest aadc versions as the sync will happen via app instead of user accounts
            not(user['userPrincipalName'].startswith("Sync_connectserver2")) and
            not(user['userPrincipalName'].startswith("Sync_connectserver3"))) :
            if user['onPremisesProvisioningErrors']:
               onPremisesProvisioningErrors = user['onPremisesProvisioningErrors'][0]['category']
            else:
               onPremisesProvisioningErrors = "None"
            upnissue_data = [user['id'],user['userPrincipalName'],user['createdDateTime'],user['onPremisesSyncEnabled'],user['onPremisesLastSyncDateTime'],user['onPremisesImmutableId'],user['accountEnabled'],onPremisesProvisioningErrors]
            csv.writer(UPNIssue).writerow(upnissue_data)
      
    # Closing Files Post Write
    print("Closing Files Post Write")
    CloudOnlyUser.close()
    UPNIssue.close()

else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))  # You may need this when reporting a bug
    ## Send Email for Failure
    print("Failed to Retrieve Token")
    msg = EmailMessage()
    msg["Subject"] = "(ACTION REQUIRED) PROD : Azure Object Level Report"
    msg["From"] = "reports@something.com"
    msg["To"] = "me@something.com"
    # https://www.chilkatsoft.com/p/p_471.asp
    # https://stackoverflow.com/questions/11843148/smtp-sending-an-priority-email
    msg["X-Priority"] = '1'
    msg.set_content("""Failed to get token""")
    server = smtplib.SMTP('smtp.com')
    server.send_message(msg)

###########
## Email ##
###########

data_cloudonlyuser = pandas.read_csv("CloudOnlyUser.csv")
cloudonlyuser_count = data_cloudonlyuser.shape[0] # 1st Body Variable

data_upnissue = pandas.read_csv("UPNIssue.csv")
onprem_accounts_with_cloudupn_count = data_upnissue.shape[0] # 2nd Body Variable

utc_time_now = datetime.utcnow()

count = 0
cloudonlyuser_createdlast24hours_count = 0
while count < cloudonlyuser_count:
    time_csv_unformatted = data_cloudonlyuser.iloc[count,2]
    time_csv_formatted = time_csv_unformatted.replace("Z",".000000")
    time_csv_formatted = datetime.fromisoformat(time_csv_formatted)
    time_span = utc_time_now-time_csv_formatted
    if time_span.days == 0:
        cloudonlyuser_createdlast24hours_count = cloudonlyuser_createdlast24hours_count + 1
        print(data_cloudonlyuser.iloc[count,1])
    count = count+1

count = 0
onprem_accounts_with_cloudupn_createdlast24hours = 0
while count < onprem_accounts_with_cloudupn_count:
    time_csv_unformatted = data_upnissue.iloc[count,2]
    time_csv_formatted = time_csv_unformatted.replace("Z",".000000")
    time_csv_formatted = datetime.fromisoformat(time_csv_formatted)
    time_span = utc_time_now-time_csv_formatted
    if time_span.days == 0:
        onprem_accounts_with_cloudupn_createdlast24hours = onprem_accounts_with_cloudupn_createdlast24hours + 1
    count = count+1

message = """
<html><body>
<h2 style='font-size:25px;font-family:Calibri;color:#6F9824''>Azure Object Level Report - """ + str(datetime.now().strftime("%m-%d-%Y")) + """</h2><BR>
<Table><TABLE style="font-size:11pt;font-family:Calibri" BORDER=1><tr bgcolor="#D5D5D4"><TD><B>Category</B></TD><TD><B>Count</B></TD></TR>
    <TD>Cloud Only Accounts</TD><TD> """ + str(cloudonlyuser_count) + """ </TD></TR>
    <TD>New Cloud only Accounts created in last 24 hrs.</TD><TD> """ + str(cloudonlyuser_createdlast24hours_count) +"""</TD></TR>
    <TD>Sync'd accounts with Cloud UPN</TD><TD> """ + str(onprem_accounts_with_cloudupn_count) + """ </TD></TR>
    <TD>New Sync'd accounts with Cloud UPN in last 24 hrs.</TD><TD> """ + str(onprem_accounts_with_cloudupn_createdlast24hours) + """ </TD></TR>
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
subject += "Azure Object Level Report - "
subject += datetime.now().strftime("%m-%d-%Y")
subject += " (JC)"
email["Subject"] = subject

email.set_content(message, subtype="html")

files = ["CloudOnlyUser.csv","UPNIssue.csv"]
for file in files:
    with open(file, "rb") as att:
        email.add_attachment(
            att.read(),
            filename=file,
            maintype="application",
            subtype="csv"
    )

smtp= ""
smtp = smtplib.SMTP("smtp.com")

smtp.sendmail(sender, recipient, email.as_string())
smtp.quit()

print("End Time")
print(datetime.now().strftime("%B-%d-%Y-%H-%M"))

#### End ####
