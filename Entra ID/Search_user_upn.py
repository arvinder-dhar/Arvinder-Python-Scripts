import asyncio
from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient

credential = ClientSecretCredential(
    'tenant_id',
    'client_id',
    'client_secret'
)
scopes = ['https://graph.microsoft.com/.default']   
client = GraphServiceClient(credentials=credential, scopes=scopes)

# GET /users/{id | userPrincipalName}
async def get_user():
    user = await client.users.by_user_id('userPrincipalName').get()
    if user:
        print(user.display_name)
asyncio.run(get_user())
