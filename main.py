import discord
import asyncio
import requests
from bs4 import BeautifulSoup

print("""
 ▒█████   ██▒   █▓
▒██▒  ██▒▓██░   █▒
▒██░  ██▒ ▓██  █▒░ has
▒██   ██░  ▒██ █░░  been
░ ████▓▒░   ▒▀█░     launched
░ ▒░▒░▒░    ░ ▐░  
  ░ ▒ ▒░    ░ ░░  
░ ░ ░ ▒       ░░  
    ░ ░        ░  
              ░
""")

target = input("> enter target: ").strip()

# Replace these with your actual Discord bot token and channel ID
TOKEN = "3rfEW"
CHANNEL_ID = 123456789

last_message = None

def scrape_message():
    url = "https://plancke.io/hypixel/player/stats/" + target
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        status_element = soup.select_one("body > div:nth-child(1) > div:nth-child(3) > div > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(3) > div > b")
        
        if status_element:
            status_text = status_element.get_text(strip=True)

            if status_text == "Offline":
                return "Offline"
            else:
                parent = status_element.parent
                
                if parent:
                    server_type = None
                    next_content = status_element.next_sibling
                    
                    if next_content and isinstance(next_content, str):
                        server_type = next_content.strip()
                    elif next_content and hasattr(next_content, 'get_text'):
                        server_type = next_content.get_text(strip=True)
                    
                    if server_type:
                        return f"Online, Server: {server_type}"
                return "Online"
        else:
            return "Online"
    else:
        return None

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def send_message_periodically():
    global last_message
    await client.wait_until_ready()

    while not client.is_closed():
        new_message = scrape_message()

        if new_message != last_message:
            if new_message:
                channel = client.get_channel(CHANNEL_ID)
                if new_message == "Offline":
                    await channel.send("`Status: Offline`")
                else:
                    await channel.send(f"`Status: {new_message}`")
                last_message = new_message
            else:
                print("No message data found.")
        else:
            print(f"Status hasn't changed. Current status: {new_message}")

        await asyncio.sleep(300)  # 300 seconds = checks every 5 mins. Plancke itself checks like every 5 mins so it's not always accurate

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("Bot is tracking", target + ".")

    initial_status = scrape_message()
    if initial_status:
        print(f"Initial Status: {initial_status}")
    else:
        print("Could not retrieve initial status.")

    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f"`Bot is now tracking {target}...`")
        

    client.loop.create_task(send_message_periodically())

client.run(TOKEN)
