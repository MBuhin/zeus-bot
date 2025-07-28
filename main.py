import discord
import gspread
import asyncio
import os
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIG ---
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
SHEET_ID = os.getenv("SHEET_ID")
TAB_NAME = "ZeusRP"
CHECK_INTERVAL = 900  # u sekundama (15 minuta)
WL_ROLE_ID = int(os.getenv("WL_ROLE_ID"))
BEZWL_ROLE_ID = int(os.getenv("BEZWL_ROLE_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
# ---------------

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(SHEET_ID).worksheet(TAB_NAME)

@client.event
async def on_ready():
    print(f"Bot je online kao {client.user}")
    while True:
        try:
            await check_wl()
        except Exception as e:
            print(f"Greška prilikom provjere: {e}")
        await asyncio.sleep(CHECK_INTERVAL)

async def check_wl():
    rows = sheet.get_all_values()
    guild = client.guilds[0]
    channel = guild.get_channel(CHANNEL_ID)
    wl_role = guild.get_role(WL_ROLE_ID)
    bezwl_role = guild.get_role(BEZWL_ROLE_ID)

    for i, row in enumerate(rows[1:], start=2):
        try:
            rezultat = row[2]
            discord_id = row[3]
            status = row[36] if len(row) > 36 else ""

            if status in ["Pao WL", "Dobio WL"]:
                continue

            broj_bodova = int(rezultat.split('/')[0])
            member = guild.get_member(int(discord_id))
            if not member:
                print(f"Korisnik s ID {discord_id} nije pronađen na serveru.")
                continue

            if broj_bodova >= 24:
                await member.add_roles(wl_role)
                await member.remove_roles(bezwl_role)
                await channel.send(f"✅ **<@{discord_id}> je PROŠAO pismenu WL. Imao je {rezultat} bodova.**")
                sheet.update_cell(i, 37, "Dobio WL")
            else:
                await channel.send(f"❌ **<@{discord_id}> je PAO pismenu WL. Imao je {rezultat} bodova.**")
                sheet.update_cell(i, 37, "Pao WL")

        except Exception as e:
            print(f"Greška kod reda {i}: {e}")

client.run(TOKEN)