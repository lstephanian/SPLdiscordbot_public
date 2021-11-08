import discord
from discord.utils import get
from discord.ext import commands
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
import requests
 


#################### READ FROM GOOGLE SHEETS ####################
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'INSERT/PATH/TO/KEY.JSON' #add path to your google sheets key.json 

creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = 'INSERT SPREADSHEET ID'
service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range="Sheet1!A:B").execute()

rows = result.get('values')

# #################### READ WALLET BALANCES ####################
mint_address = "INSERT MINT ADDRESS" #this is the mint address for your SPL token
minimum_tokens = 10 #change this to minimum thresholds to become a member
members = []

for row in rows:
    discordId = row[0]
    address = row[1]


# find balance of wallet
    headers = {'Content-Type': 'application/json',}
    data = '{"jsonrpc":"2.0","id":1, "method":"getTokenAccountsByOwner", "params": ["' + address + '", {"mint":"' + mint_address + '"}, {"encoding":"jsonParsed"}]}';
    response = requests.post('https://api.mainnet-beta.solana.com/', headers=headers, data=data)
    json = response.json()
    balance = json['result']['value'][0]['account']['data']['parsed']['info']['tokenAmount']['amount']
    balance = int(balance)/1000000000
    
    if balance >= minimum_tokens:
        members.append(discordId)


#################### DISCORD BOT ASSIGN ROLES ####################
member = discordId
TOKEN = 'INSERT DISCORD TOKEN HERE' 
role_id = 'INSERT DISCORD ROLE ID HERE' 

# create the bot
client = commands.Bot(command_prefix = '.')

# ready the bot
@client.event
async def on_ready():
    print('Bot is ready.')

@client.event  
async def on_member_join(ctx):

    if member in members:
        role = discord.utils.get(ctx.guild.roles, id = role_id) 
        await ctx.add_roles(role)

@client.command(pass_context = True)
async def clear(ctx, amount=100):
    channel = ctx.messages.channel
    messages = []
    async for message in client.logs_from(channel, limit=int(amount) + 1):
        message.append(message)
    await client.delete_messages(messages)
    await client.say('Messages deleted.')

client.run(TOKEN)

