# 🔔 YouTube & Twitch Notifier Discord Bot

This Discord bot tracks YouTube uploads and Twitch livestreams for selected channels and sends automatic announcements to your server.

## 🌐 Invite the Bot (Ready-to-Use)
Click below to invite the official hosted version to your server:

👉 [Invite Bot](https://discord.com/oauth2/authorize?client_id=1391635902194782289&permissions=2147699712&integration_type=0&scope=bot+applications.commands)

---

## 🚀 Features
- Track multiple YouTube channels for new uploads.
- Track Twitch channels for going live.
- Send alerts to a configured channel with optional role pings.
- Simple slash commands to manage everything.

---

## 🛠️ Setup (Host the Bot Yourself)

### 1. Clone the Repo
```bash
git clone https://github.com/vihaanvp/UploadNotifier.git
cd discord-notifier-bot
```
  
### 2. Create and Activate Virtual Environment
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```
  
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
  
### 4. Create the .env file with all the API keys and Bot Token
Click [here](https://github.com/vihaanvp/UploadNotifier/blob/main/.env.example) for the .env file template  

---

## 🔑 How to Get API Keys
### Discord Bot Token
1. Go to Discord Developer Portal.
2. Create a new application and add a bot under the "Bot" section.
3. Copy the token and paste it into your .env file as DISCORD_TOKEN.

### YouTube API Key
1. Go to Google Cloud Console.
2. Create a project.
3. Go to APIs & Services > Library → Enable YouTube Data API v3.
4. Go to Credentials → Create API Key.

### Twitch Client ID & Secret
1. Go to Twitch Developer Console.
2. Click "Register Your Application":
   - Redirect URI: http://localhost
   - Category: Application Integration
3. Copy the Client ID and Client Secret into your .env.

---

## ▶️ Running the Bot
```bash
python main.py
```

---

## 🧪 Available Slash Commands
- `/setup` – Set the notification channel and ping role.
- `/add_youtube` – Add a YouTube channel to track.
- `/remove_youtube` – Remove a tracked YouTube channel.
- `/add_twitch` – Add a Twitch channel to track.
- `/remove_twitch` – Remove a tracked Twitch channel.
- `/list_channels` – List all tracked YouTube/Twitch channels.
- `/ping` – Show bot latency.

---

## 📁 Recommended `.gitignore`

```gitignore
.venv/
__pycache__/
.env
guild_configs.json
```

---

## 📜 License
MIT License – free to use and modify. (but please give credit)