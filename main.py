# Importing needed libraries
import discord
import os
import httpx
import json

# Import needed modules
from datetime import datetime, timezone
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

# Load the secrets from env file
load_dotenv()

# Assign variables to the env secrets
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')

# Name of Database File
CONFIG_FILE = 'guild_configs.json'

# Load or initialize the configuration file
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        guild_configs = json.load(f)
else:
    guild_configs = {}

# Initialize bot with default intents and addon the guilds intent
intents = discord.Intents.default()
intents.guilds = True

# Initialize Bot commands (ignore the command prefix, use only / commands)
bot = commands.Bot(command_prefix='!', intents=intents)

# Cache for tracking
video_cache = {}
stream_cache = {}


def save_configs():
    """Save the current guild configurations to the JSON file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(guild_configs, f, indent=4)


@bot.tree.command(name='setup', description='Set up notification channel and ping role')
@app_commands.describe(channel='Channel to send notifications', role='Role to ping (optional)')
@app_commands.checks.has_permissions(administrator=True)
async def setup_notification(interaction: discord.Interaction,
                             channel: discord.TextChannel,
                             role: discord.Role = None):
    guild_id = str(interaction.guild.id)
    guild_configs[guild_id] = {
        "notification_channel": channel.id,
        "ping_role": role.id if role else None,
        "youtube_channels": {},
        "twitch_channels": {}
    }
    save_configs()
    await interaction.response.send_message(
        f"✅ Notifications will be sent to {channel.mention} with ping role {role.mention if role else 'None'}",
        ephemeral=True
    )


@bot.tree.command(name='add_youtube', description='Add a YouTube channel to track')
@app_commands.describe(channel_id='YouTube channel ID', channel_name='Display name')
@app_commands.checks.has_permissions(administrator=True)
async def add_youtube(interaction: discord.Interaction,
                      channel_id: str, channel_name: str):
    guild_id = str(interaction.guild.id)
    if guild_id not in guild_configs:
        guild_configs[guild_id] = {"youtube_channels": {}, "twitch_channels": {}}

    guild_configs[guild_id]["youtube_channels"][channel_id] = {"name": channel_name}
    save_configs()
    await interaction.response.send_message(
        f"✅ Added YouTube channel: {channel_name}", ephemeral=True
    )
    print("Added YouTube channel", channel_name)


@bot.tree.command(name='remove_youtube', description='Remove a YouTube channel')
@app_commands.describe(channel_id='YouTube channel ID to remove')
@app_commands.checks.has_permissions(administrator=True)
async def remove_youtube(interaction: discord.Interaction, channel_id: str):
    guild_id = str(interaction.guild.id)
    if guild_id in guild_configs and channel_id in guild_configs[guild_id]["youtube_channels"]:
        del guild_configs[guild_id]["youtube_channels"][channel_id]
        save_configs()
        await interaction.response.send_message(
            f"✅ Removed YouTube channel ID: {channel_id}", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "ℹ️ Channel not found or was already removed", ephemeral=True
        )


@bot.tree.command(name='add_twitch', description='Add a Twitch channel to track')
@app_commands.describe(channel_name='Twitch username', display_name='Display name')
@app_commands.checks.has_permissions(administrator=True)
async def add_twitch(interaction: discord.Interaction,
                     channel_name: str, display_name: str):
    guild_id = str(interaction.guild.id)
    if guild_id not in guild_configs:
        guild_configs[guild_id] = {"youtube_channels": {}, "twitch_channels": {}}

    guild_configs[guild_id]["twitch_channels"][channel_name] = {"name": display_name}
    save_configs()
    await interaction.response.send_message(
        f"✅ Added Twitch channel: {display_name}", ephemeral=True
    )


@bot.tree.command(name='remove_twitch', description='Remove a Twitch channel')
@app_commands.describe(channel_name='Twitch username to remove')
@app_commands.checks.has_permissions(administrator=True)
async def remove_twitch(interaction: discord.Interaction, channel_name: str):
    guild_id = str(interaction.guild.id)
    if guild_id in guild_configs and channel_name in guild_configs[guild_id]["twitch_channels"]:
        del guild_configs[guild_id]["twitch_channels"][channel_name]
        save_configs()
        await interaction.response.send_message(
            f"✅ Removed Twitch channel: {channel_name}", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "ℹ️ Channel not found or was already removed", ephemeral=True
        )


@bot.tree.command(name='list_channels', description='List all tracked channels')
@app_commands.checks.has_permissions(administrator=True)
async def list_channels(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    if guild_id not in guild_configs:
        await interaction.response.send_message("No configuration found for this server")
        return

    youtube_channels = guild_configs[guild_id].get("youtube_channels", {})
    twitch_channels = guild_configs[guild_id].get("twitch_channels", {})

    embed = discord.Embed(title="Tracked Channels", color=0x7289da)

    if youtube_channels:
        yt_list = "\n".join([f"• **{info['name']}** (`{id}`)" for id, info in youtube_channels.items()])
        embed.add_field(name="YouTube Channels", value=yt_list, inline=False)

    if twitch_channels:
        tw_list = "\n".join([f"• **{info['name']}** (`{name}`)" for name, info in twitch_channels.items()])
        embed.add_field(name="Twitch Channels", value=tw_list, inline=False)

    if not youtube_channels and not twitch_channels:
        embed.description = "No channels are currently being tracked."

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name='ping', description='Check bot latency')
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Latency: {latency}ms", ephemeral=True)


# Background tasks
@tasks.loop(minutes=5)
async def youtube_check():
    """Check YouTube for new uploads"""
    await bot.wait_until_ready()
    try:
        for guild_id, config in guild_configs.items():
            if 'youtube_channels' not in config or not config['youtube_channels']:
                continue

            notification_channel = bot.get_channel(config.get('notification_channel'))
            if not notification_channel:
                continue

            ping_role = config.get('ping_role')
            role = notification_channel.guild.get_role(ping_role) if ping_role else None

            for channel_id, channel_info in config['youtube_channels'].items():
                video = await get_youtube_video(channel_id)
                if not video:
                    continue

                video_id = video['id']['videoId']
                cached_video = video_cache.get(channel_id)

                if cached_video != video_id:
                    video_cache[channel_id] = video_id

                    embed = discord.Embed(
                        title=video['snippet']['title'],
                        url=f"https://youtube.com/watch?v={video_id}",
                        description=f"New video from {channel_info['name']}!",
                        color=0xff0000,
                        timestamp=datetime.now(timezone.utc)
                    )
                    embed.set_thumbnail(url=video['snippet']['thumbnails']['high']['url'])

                    message = f"{role.mention if role else ''} New video from {channel_info['name']}!"
                    await notification_channel.send(message, embed=embed)
    except Exception as e:
        print(f"Error in youtube_check: {e}")


@tasks.loop(minutes=3)
async def twitch_check():
    """Check Twitch for live streams"""
    await bot.wait_until_ready()
    try:
        access_token = await get_twitch_access_token()
        if not access_token:
            return

        for guild_id, config in guild_configs.items():
            if 'twitch_channels' not in config or not config['twitch_channels']:
                continue

            notification_channel = bot.get_channel(config.get('notification_channel'))
            if not notification_channel:
                continue

            ping_role = config.get('ping_role')
            role = notification_channel.guild.get_role(ping_role) if ping_role else None

            for channel_name, channel_info in config['twitch_channels'].items():
                stream = await get_twitch_stream(channel_name, access_token)

                if stream:
                    stream_id = stream['id']
                    cached_stream = stream_cache.get(channel_name)

                    if cached_stream != stream_id:
                        stream_cache[channel_name] = stream_id

                        embed = discord.Embed(
                            title=stream['title'],
                            url=f"https://twitch.tv/{channel_name}",
                            description=f"{channel_info['name']} is now live!",
                            color=0x9147ff,
                            timestamp=datetime.now(timezone.utc)
                        )
                        embed.add_field(name="Game", value=stream['game_name'])
                        embed.add_field(name="Viewers", value=stream['viewer_count'])
                        embed.set_thumbnail(url=stream['thumbnail_url'].format(width=1920, height=1080))

                        message = f"{role.mention if role else ''} {channel_info['name']} is live on Twitch!"
                        await notification_channel.send(message, embed=embed)
                elif channel_name in stream_cache:
                    del stream_cache[channel_name]
    except Exception as e:
        print(f"Error in twitch_check: {e}")


async def get_twitch_access_token():
    """Get Twitch OAuth token"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            'https://id.twitch.tv/oauth2/token',
            params={
                'client_id': TWITCH_CLIENT_ID,
                'client_secret': TWITCH_CLIENT_SECRET,
                'grant_type': 'client_credentials'
            }
        )
        return resp.json().get('access_token')


async def get_youtube_video(channel_id: str):
    """Get latest YouTube video"""
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'channelId': channel_id,
        'maxResults': 1,
        'order': 'date',
        'type': 'video',
        'key': YOUTUBE_API_KEY
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        if resp.status_code == 200:
            items = resp.json().get('items', [])
            return items[0] if items else None
    return None


async def get_twitch_stream(channel_name: str, access_token: str):
    """Check Twitch stream status"""
    url = "https://api.twitch.tv/helix/streams"
    headers = {
        'Client-ID': TWITCH_CLIENT_ID,
        'Authorization': f'Bearer {access_token}'
    }
    params = {'user_login': channel_name}

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, params=params)
        if resp.status_code == 200:
            data = resp.json().get('data', [])
            return data[0] if data else None
    return None


@bot.event
async def on_ready():
    print(f'{bot.user.name} is ready!')

    # Start background tasks
    youtube_check.start()
    twitch_check.start()


# Run the bot
bot.run(DISCORD_TOKEN)
