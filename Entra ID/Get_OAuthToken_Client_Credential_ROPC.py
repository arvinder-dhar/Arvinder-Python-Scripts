## ROPC

def ROPC(tenantid,clientid,username,password):
        
    ## Import PublicClientApplication Module
    from msal import PublicClientApplication

    authority = "https://login.microsoftonline.com/"
    authority += str(tenantid)
    scopes = ["https://graph.microsoft.com/.default"] ## Update the Scope based on preference

    app = PublicClientApplication(client_id=clientid,authority=authority)
    result = app.acquire_token_by_username_password(username,password,scopes)
    return result


# Client Credential Grant flow

def Client_Credential(tenantid,clientid,secret):

    ## Import ConfidentialClientApplication Module
    from msal import ConfidentialClientApplication

    authority = "https://login.microsoftonline.com/"
    authority += str(tenantid)
    scopes = ['https://graph.microsoft.com/.default'] ## Update the Scope based on preference

    ## Create Confidential Client App Instance & Acquire Token
    app = ConfidentialClientApplication(client_id=clientid,authority=authority,client_credential=secret)
    result = app.acquire_token_for_client(scopes=scopes)
    return result
