'''
Grant Flow -> ROPC
Packages -> msal(1.26.0), keyring(24.3.1)

KB Articles
1. https://github.com/AzureAD/microsoft-authentication-library-for-python/tree/dev
2. https://github.com/AzureAD/microsoft-authentication-library-for-python/blob/1.22.0/sample/username_password_sample.py
3. https://pypi.org/project/keyring/#description

'''

## Import Modules
from msal import PublicClientApplication
import keyring

## Variables
clientid = "{client-id}"
authority= "https://login.microsoftonline.com/{tenant-id}"
scopes = ['https://graph.microsoft.com/.default']
username=keyring.get_password("user","user") # pragma: allowlist secret
password=keyring.get_password("key","key") # pragma: allowlist secret

# Create Public Client App Instance
app = PublicClientApplication(client_id=clientid,authority=authority)

## Get Token
result=app.acquire_token_by_username_password(username=username,password=password,scopes=scopes) # pragma: allowlist secret

## Use Token & Call the Graph API Endpoint
if "access_token" in result:
    print("Token Extracted")
    print (result["access_token"])

else:
    print(result.get("error"))
    print(result.get("error_description"))
    print(result.get("correlation_id"))  # You may need this when reporting a bug
