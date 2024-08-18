import discord
import asyncio
import requests
import re

# SETTINGS #
TOKEN = 'MTI2ODY1NzQ5NTQ5NzUwNzAwMg.GTadsn.DKsruFemKdTMT83h7RCMMU0kDHTWngs8WJDI0w'
CHANNELS_URL = "https://github.com/yavuz360/GFVdzepF/raw/main/SNIPE_CHANNELS.txt"
SEARCH_TERMS_URL = "https://github.com/yavuz360/GFVdzepF/raw/main/SNIPE_KEYWORDS.txt"
TARGET_CHANNEL_ID = 1269522246511099935  # The channel to send the sniped message to
REFRESH_INTERVAL = 180
# SETTINGS END #

class SniperSelfbot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.snipe_channels = []
        self.search_terms = []

    async def on_ready(self):
        print(f'Selfbot is online as {self.user}.')
        await self.fetch_snipe_channels()
        await self.fetch_search_terms()
        self.loop.create_task(self.periodic_refresh())

    async def periodic_refresh(self):
        while True:
            await asyncio.sleep(REFRESH_INTERVAL)
            await self.fetch_snipe_channels()
            await self.fetch_search_terms()
            print("Refreshed channels and search terms.")

    async def fetch_snipe_channels(self):
        try:
            response = requests.get(CHANNELS_URL)
            if response.status_code == 200:
                self.snipe_channels = [int(line.strip()) for line in response.text.strip().split('\n') if line.strip()]
                print(f"Fetched {len(self.snipe_channels)} channels for sniping.")
            else:
                print(f"Failed to fetch snipe channels: {response.status_code}")
        except requests.RequestException as e:
            print(f"Failed to fetch snipe channels: {e}")

    async def fetch_search_terms(self):
        try:
            response = requests.get(SEARCH_TERMS_URL)
            if response.status_code == 200:
                self.search_terms = [line.strip().split(',') for line in response.text.strip().split('\n') if line.strip()]
                print(f"Fetched {len(self.search_terms)} search term pairs.")
            else:
                print(f"Failed to fetch search terms: {response.status_code}")
        except requests.RequestException as e:
            print(f"Failed to fetch search terms: {e}")

    async def on_message(self, message):
        if message.channel.id in self.snipe_channels:
            if self.snipe_message(message.content):
                await self.send_sniped_message(message)

    def snipe_message(self, message_content):
        for search_pair in self.search_terms:
            if len(search_pair) == 2:
                keyword, number = search_pair
                # Use regex to check if the keyword and number appear together in the same line
                pattern = rf'\b{re.escape(keyword)}\b.*\b{re.escape(number)}\b|\b{re.escape(number)}\b.*\b{re.escape(keyword)}\b'
                if re.search(pattern, message_content, re.IGNORECASE):
                    return True
        return False

    async def send_sniped_message(self, message):
        target_channel = self.get_channel(TARGET_CHANNEL_ID)
        if target_channel:
            message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
            beautified_content = "\n> ".join(message.content.split('\n'))
            await target_channel.send(
                f"Sniped Message ([Go to Message]({message_link}))\n\n"
                f"> {beautified_content}\n\n"
                f"-# made by Yavuz with ❤️"
            )

# Start the bot
client = SniperSelfbot()
client.run(TOKEN)
