from dotenv import load_dotenv
import discord
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged in as ', str(self.user), "!")

    async def on_message(self, message):
        if message.content.startswith('!') and message.author != self.user:
            if message.content.startswith('!ping'):
                await message.channel.send('!pong')

        print('Received message from ', message.author, ' reading ', message.content)

    async def ping(self, ctx):
        await ctx.send('Pong!')

intents = discord.Intents.default()
intents.message_content = True # You need to enable Message Content Intent in the Discord Developer Portal

client = MyClient(intents=intents)
client.run(token)