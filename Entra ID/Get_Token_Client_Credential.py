import sys
from msal import ConfidentialClientApplication

from msal import ConfidentialClientApplication

def gettoken(tenantid, clientid, key):
    authority = f"https://login.microsoftonline.com/{tenantid}"
    scope = ['https://graph.microsoft.com/.default']

    app = ConfidentialClientApplication(
        client_id=clientid,
        client_credential=key,
        authority=authority
    )
    result = app.acquire_token_for_client(scopes=scope)
    return result

if __name__ == "__main__":
    import sys
    token = gettoken(sys.argv[1], sys.argv[2], sys.argv[3])
    #print(token)
