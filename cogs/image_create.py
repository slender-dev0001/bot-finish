import discord
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image
import sqlite3
import os
import secrets
import string
import io

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
            image_data BLOB,
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
    async def imagecreate(self, ctx, *, title: str = "Image Tracker"):
        """+imagecreate [titre] — upload une image PNG et crée un tracker"""
        
        if not ctx.message.attachments:
            await ctx.send("❌ Veuillez joindre une image PNG/JPG à votre message.")
            return

        attachment = ctx.message.attachments[0]
        
        if not attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            await ctx.send("❌ Seules les images PNG/JPG sont acceptées.")
            return

        if attachment.size > 10 * 1024 * 1024:
            await ctx.send("❌ L'image ne doit pas dépasser 10 MB.")
            return

        async with ctx.typing():
            try:
                # Télécharger l'image
                image_data = await attachment.read()
                img = Image.open(io.BytesIO(image_data))
                
                # Vérifier et redimensionner si nécessaire (max 2000x2000)
                if img.size[0] > 2000 or img.size[1] > 2000:
                    img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
                
                # Convertir en RGB si nécessaire
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Sauvegarder en bytes
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                image_blob = img_bytes.getvalue()
                
                # Créer l'entrée en DB
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
                    INSERT INTO image_trackers (id, user_id, guild_id, title, image_data)
                    VALUES (?, ?, ?, ?, ?)
                ''', (short_id, ctx.author.id, ctx.guild.id if ctx.guild else 0, title, image_blob))
                conn.commit()
                conn.close()

                image_url = f"{BASE_URL.rstrip('/')}/image/{short_id}"

                try:
                    await ctx.author.send(
                        f"✅ Image tracker créée : {image_url}\n"
                        f"📸 Image: {title}\n"
                        "Quand quelqu'un charge cette URL, vous recevrez une notification avec l'IP."
                    )
                    await ctx.send("✅ Image tracker créée — lien envoyé en DM.")
                except discord.Forbidden:
                    await ctx.send(f"✅ Image tracker créée : {image_url}")
                except Exception as e:
                    await ctx.send(f"✅ Image tracker créée : {image_url}")

            except Exception as e:
                await ctx.send(f"❌ Erreur traitement image: {e}")

async def setup(bot):
    await bot.add_cog(ImageCreate(bot))