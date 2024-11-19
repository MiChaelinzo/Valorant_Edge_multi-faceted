import discord
import boto3
import uuid
import asyncio
import logging

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

AGENT_ID = ''
AGENT_ALIAS_ID = ''
session_id = str(uuid.uuid4())

bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!ask'):
        query = message.content[5:].strip()
        await process_query(message, query)

async def process_query(message, query):
    try:
        ai_response = await invoke_agent(query)
        await send_long_message(message.channel, f"**Bedrock Agent says:**\n{ai_response}")
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        print(error_msg)
        await message.channel.send(error_msg)

async def invoke_agent(query):
    try:
        response = bedrock_agent.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=query
        )

        full_response = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    full_response += chunk['bytes'].decode('utf-8')

        return full_response
    except Exception as e:
        raise Exception(f"Error invoking agent: {str(e)}")

async def send_long_message(channel, message):
    if len(message) <= 2000:
        await channel.send(message)
    else:
        parts = [message[i:i+1900] for i in range(0, len(message), 1900)]
        for part in parts:
            await channel.send(part)
            await asyncio.sleep(1)  # To avoid rate limiting

def run_bot():
    while True:
        try:
            client.run('')
        except Exception as e:
            print(f"Bot disconnected. Reconnecting... Error: {str(e)}")
            asyncio.sleep(5)

logging.basicConfig(level=logging.DEBUG)
boto3.set_stream_logger('', logging.DEBUG)

if __name__ == "__main__":
    run_bot()
                                                                                                      