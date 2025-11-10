import discord
from discord.ext import commands
import sqlite3
import os
from dotenv import load_dotenv
import secrets
import string

load_dotenv()
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5001')
if BASE_URL and not BASE_URL.startswith(('http://', 'https://')):
    BASE_URL = f'http://{BASE_URL}'

def ensure_tables():
    conn = sqlite3.connect("links.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS image_trackers (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            guild_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            clicks INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def generate_id(length: int = 8) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

class ImageCreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        ensure_tables()

    @commands.command(name='imagecreate')
    async def imagecreate(self, ctx, *, url: str):
        """+imagecreate <url> — crée un tracker d'image et envoie le lien en DM"""
        if not url:
            await ctx.send("❌ Veuillez fournir une URL.")
            return

        if not (url.startswith("http://") or url.startswith("https://")):
            await ctx.send("❌ URL invalide — doit commencer par http:// ou https://")
            return

        # show typing while we create the tracker
        async with ctx.typing():
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()

            short_id = generate_id(8)
            tries = 0
            while tries < 10:
                cursor.execute('SELECT 1 FROM image_trackers WHERE id = ?', (short_id,))
                if not cursor.fetchone():
                    break
                short_id = generate_id(8)
                tries += 1

            cursor.execute('''
                INSERT OR REPLACE INTO image_trackers (id, user_id, guild_id, title)
                VALUES (?, ?, ?, ?)
            ''', (short_id, ctx.author.id, ctx.guild.id if ctx.guild else 0, url))
            conn.commit()
            conn.close()

            image_url = f"{BASE_URL.rstrip('/')}/image/{short_id}"

        try:
            await ctx.author.send(
                f"✅ Image tracker créée : {image_url}\n"
                "Intégrez cette URL comme image (pixel) ; quand quelqu'un la chargera, vous recevrez une notification avec l'IP."
            )
            await ctx.send("✅ Image tracker créée — lien envoyé en DM.")
        except discord.Forbidden:
            await ctx.send(f"✅ Image tracker créée : {image_url} (impossible d'envoyer un DM)")
        except Exception as e:
            await ctx.send(f"✅ Image tracker créée : {image_url} (erreur envoi DM: {e})")

async def setup(bot):
    await bot.add_cog(ImageCreate(bot))