'''
Grant Flow -> Client Credentials
Packages -> msal(1.26.0), keyring(24.3.1), requests(2.31.0) , json

KB Articles
1. https://github.com/AzureAD/microsoft-authentication-library-for-python/tree/dev
2. https://github.com/AzureAD/microsoft-authentication-library-for-python/blob/1.22.0/sample/confidential_client_secret_sample.py
3. https://pypi.org/project/keyring/#description
4. https://www.nylas.com/blog/use-python-requests-module-rest-apis/
5. https://www.geeksforgeeks.org/python-difference-two-lists/
6. https://www.geeksforgeeks.org/read-a-file-line-by-line-in-python/
7. https://medium.com/nerd-for-tech/query-ms-graph-api-in-python-e8e04490b04e

Version : 2
Improvements :
    PRT can be revoked for Admin accounts too which was not possible in previous job
    Replaced Text file with csv file to include additional details
    Email body will contain success and failure count
    Delete Logs older than 45 days

'''

#############################
########### Start  ##########
#############################

### Get Token ###

## Import Modules
import msal
import requests
#import keyring
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from email.message import EmailMessage
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import sys
import shutil
import time
import csv

#print("Directory path")
#print(os.getcwd())
os.getcwd()

## Variables
tenant_id = sys.argv[1]
clientid = sys.argv[2]
key = sys.argv[3]
authority= "https://login.microsoftonline.com/"
authority += tenant_id
scope = ['https://graph.microsoft.com/.default']
inclusion_group_id = sys.argv[4]
exclusion_group_id = sys.argv[5]

## Create Confidential Client App Instance & Acquire Token
app = msal.ConfidentialClientApplication(client_id=clientid,authority=authority,client_credential=key)
result = app.acquire_token_for_client(scopes=scope)

## Function for Creating Empty CSV File
def Create_File(name):
    file_name = str(name)
    if os.path.exists(file_name):
        # Delete if file already present
        print("{} File is already present with the same name, deleting and re-creating empty".format(file_name))
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

## Use Token & Call the Graph API Endpoints
if "access_token" in result:
    print("Token Extracted")
    
    # Graph Endpoint for the Inclusion & Exclusion Groups
    graph_api = "https://graph.microsoft.com/v1.0/groups/"
    graph_api_inclusion = graph_api
    graph_api_exclusion = graph_api

    graph_api_inclusion += inclusion_group_id
    graph_api_exclusion += exclusion_group_id

    graph_api_inclusion += "/members"
    graph_api_exclusion += "/members"
    
    ## Call the Endpoints & get group members
    # Inclusion
    inclusion_members_raw = []
    inclusion_members = []
    graph_data_inclusion = requests.get(
        graph_api_inclusion,
        headers={'Authorization': 'Bearer ' + result['access_token']},).json()
    inclusion_members_raw = graph_data_inclusion['value']
    odata_next_link_inclusion = graph_data_inclusion['@odata.nextLink']

    while (odata_next_link_inclusion):
        try:
            graph_data_inclusion = requests.get(graph_data_inclusion['@odata.nextLink'],headers={'Authorization': 'Bearer ' + result['access_token']},).json()
            inclusion_members_raw += graph_data_inclusion['value']
        except:
            break

    for inclusion_member in inclusion_members_raw:
        inclusion_members.append(inclusion_member['id'])
    
    # Exclusion
    exclusion_members_raw = []
    exclusion_members = []
    graph_data_exclusion = requests.get(
        graph_api_exclusion,
        headers={'Authorization': 'Bearer ' + result['access_token']},).json()
    exclusion_members_raw = graph_data_exclusion['value']

    for exclusion_member in exclusion_members_raw:
        exclusion_members.append(exclusion_member['id'])

    ## First Revoke List
    first_revoke_users_list = []
    for i_member in inclusion_members:
        if i_member not in exclusion_members:
            first_revoke_users_list.append(i_member)
    print("First Revoke User List Count : {}".format(len(first_revoke_users_list)))

    ## Delete the Old Comparision file & Create New
    final_revoke_users_list = []
    print ("Current Working Directory is {}".format(os.getcwd()))
    if os.path.exists("compare_user_list.txt"):
        print("Comparison File Already Present, updating the file post comparison")
        with open("compare_user_list.txt","r") as old_file:
            old_contents = old_file.read().replace("\n"," ")
            old_file.close()
        for i_member in first_revoke_users_list:
            if i_member not in old_contents:
                final_revoke_users_list.append(i_member)
        print("Final Revoke User List Count : {}".format(len(final_revoke_users_list)))
        os.remove("compare_user_list.txt")
        file = open("compare_user_list.txt","x")
        for first_revoke_user in first_revoke_users_list:
            file.write("{}\n".format(first_revoke_user))
        file.close()
    else:
        print("Comparision File not present, creating new")
        file = open("compare_user_list.txt","x")
        for first_revoke_user in first_revoke_users_list:
            file.write("{}\n".format(first_revoke_user))
    file.close()

else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))  # You may need this when reporting a bug

    ## Send Email for Failure
    msg = EmailMessage()
    msg["Subject"] = "Users Token Revocation"
    msg["From"] = "reports@something.com"
    msg["To"] = "me@something.com"
    msg["X-Priority"] = "1"
    msg.set_content("""Failed to Retreive Token""")

    server = smtplib.SMTP('smtp.com')
    server.send_message(msg)

## Break Execution if no new user found
if not final_revoke_users_list:
    print("No New Users found for Token Revocation")

else:
    timestamp = datetime.now().strftime("%B-%d-%Y-%H-%M")
    Token_Revocation = "Report_Only_Token_Revocation-"
    Token_Revocation += timestamp
    file_name = str(Token_Revocation + ".csv")

    ## Create Empty File with headers
    Create_File(file_name)
    time.sleep(2)
    attachment_file = open(file_name,'w',newline='',encoding="utf-8")
    header = ['Object ID','UPN','Sign In Session Valid from (EST)','Status']
    csv.writer(attachment_file).writerow(header)
    success = int(0)
    failure = int(0)

    ## Revoke PRT for New Terminated Users
    for final_revoke_user in final_revoke_users_list:
        user_data_endpoint = None
        user_data_endpoint = "https://graph.microsoft.com/v1.0/users/"
        user_data_endpoint += final_revoke_user
        user_data_endpoint += "?$select=userPrincipalName,refreshTokensValidFromDateTime"
        user_data = requests.get(
            url=user_data_endpoint,
            headers={'Authorization': 'Bearer ' + result["access_token"]},).json()
        success += 1
        failure += 1
        ## Shift these two variables later in the Revoke logic
        '''
        token_revoke_endpoint = None
        token_revoke_endpoint = "https://graph.microsoft.com/v1.0/users/"
        token_revoke_endpoint += final_revoke_user
        token_revoke_endpoint += "/revokeSignInSessions"
    
        ## Token Revoke Logic
        try:
            revoke_call = requests.post(
                url=token_revoke_endpoint,
                headers={'Authorization': 'Bearer ' + result["access_token"]},).json()
            if revoke_call['value']:
                print("Token Revocation Successful for {}".format(final_revoke_user))
                success += 1
            else:
                print ("Token Revocation Failed for {}".format(final_revoke_user))
                failure += 1
        except:
            print("Token Revocation Failed as user {} couldn't be found".format(final_revoke_user))
        
    print("PRT Revoked for {} users".format(len(final_revoke_users_list)))
    '''
        # Parse the UTC time string into a datetime object
        utc_time = datetime.fromisoformat(user_data['refreshTokensValidFromDateTime'].replace('Z', '+00:00'))
       
       # Define the target time zone (America/New_York covers EST/EDT)
        est_timezone = ZoneInfo('America/New_York')

        # Convert the UTC datetime object to the target time zone
        est_time = utc_time.astimezone(est_timezone)
        est_time_formatted = None
        est_time_formatted = f"{est_time.date()}" + " " + f"{est_time.time()}"

        row_data = [final_revoke_user,user_data['userPrincipalName'],est_time_formatted,'Success']
        csv.writer(attachment_file).writerow(row_data)
    
    ## Close CSV File
    attachment_file.close()

    ## Send Email with Attachment
    ## Email Contents
    subject = "Users Token Revocation"
    body = str(len(final_revoke_users_list))
    body += " new users found"
    body += "\n"
    body += "Success : "
    body += str(success)
    body += "\n"
    body += "Failed : "
    body += str(failure)
    sender_email = "reports@something.com"
    recipient_email = "me@something.com"
    smtp_server = 'smtp.com'
    attachment = file_name

    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = recipient_email
    message.attach(MIMEText(body))

    ## Attachment
    with open(attachment, 'rb') as att:
        message.attach(MIMEApplication(att.read(), Name=attachment))

    with smtplib.SMTP('smtp.com') as server:
        server.sendmail(sender_email, recipient_email, message.as_string())

## Move the file to Logs Folder

if final_revoke_users_list:
    shutil.move(file_name,"Logs")

#############################
########### End  ###########
#############################
