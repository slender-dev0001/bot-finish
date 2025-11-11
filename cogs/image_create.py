import asyncio
import io
import os
import secrets
import sqlite3
import string
from pathlib import Path
from urllib.parse import urlparse

import discord
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError

load_dotenv()
DB_PATH = Path("links.db")

def resolve_base_url() -> str:
    raw_url = os.getenv("BASE_URL", "googg.up.railway.app")
    if not raw_url:
        return "googg.up.railway.app"
    parsed = urlparse(raw_url)
    if not parsed.scheme:
        return f"http://{raw_url}".rstrip("/")
    return raw_url.rstrip("/")

BASE_URL = resolve_base_url()

def ensure_tables() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS image_trackers (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                clicks INTEGER DEFAULT 0
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS image_clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracker_id TEXT NOT NULL,
                ip_address TEXT,
                browser TEXT,
                device_type TEXT,
                country TEXT,
                region TEXT,
                city TEXT,
                user_agent TEXT,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(tracker_id) REFERENCES image_trackers(id)
            )
            """
        )
        columns = {row[1] for row in cursor.execute("PRAGMA table_info(image_trackers)")}
        if "image_data" not in columns:
            cursor.execute("ALTER TABLE image_trackers ADD COLUMN image_data BLOB")

def generate_id(length: int = 8) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))

def get_unique_id(cursor: sqlite3.Cursor, max_attempts: int = 20) -> str:
    for _ in range(max_attempts):
        candidate = generate_id()
        cursor.execute("SELECT 1 FROM image_trackers WHERE id = ?", (candidate,))
        if cursor.fetchone() is None:
            return candidate
    raise RuntimeError("Impossible de générer un identifiant unique")

def prepare_image(data: bytes) -> bytes:
    with Image.open(io.BytesIO(data)) as img:
        if max(img.size) > 2000:
            img.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
        if img.mode != "RGB":
            img = img.convert("RGB")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

class ImageCreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        ensure_tables()

    @commands.command(name="imagecreate")
    async def imagecreate(self, ctx, *, title: str = "Image Tracker") -> None:
        if not ctx.message.attachments:
            await ctx.send("❌ Veuillez joindre une image PNG/JPG à votre message.")
            return
        attachment = ctx.message.attachments[0]
        if not attachment.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            await ctx.send("❌ Seules les images PNG/JPG sont acceptées.")
            return
        if attachment.size > 10 * 1024 * 1024:
            await ctx.send("❌ L'image ne doit pas dépasser 10 MB.")
            return
        async with ctx.typing():
            try:
                image_bytes = await attachment.read()
                processed_image = await asyncio.to_thread(prepare_image, image_bytes)
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    tracker_id = get_unique_id(cursor)
                    cursor.execute(
                        """
                        INSERT INTO image_trackers (id, user_id, guild_id, title, image_data)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            tracker_id,
                            ctx.author.id,
                            ctx.guild.id if ctx.guild else 0,
                            title,
                            processed_image,
                        ),
                    )
                image_url = f"{BASE_URL}/image/{tracker_id}"
                message = (
                    f"✅ Image tracker créée : {image_url}\n"
                    f"📸 Image: {title}\n"
                    "Quand quelqu'un charge cette URL, vous recevrez une notification avec l'IP."
                )
                try:
                    await ctx.author.send(message)
                    await ctx.send("✅ Image tracker créée — lien envoyé en DM.")
                except discord.Forbidden:
                    await ctx.send(f"✅ Image tracker créée : {image_url}")
            except UnidentifiedImageError:
                await ctx.send("❌ Impossible de lire cette image.")
            except RuntimeError as error:
                await ctx.send(f"❌ {error}")
            except Exception as error:
                await ctx.send(f"❌ Erreur traitement image: {error}")

async def setup(bot) -> None:
    await bot.add_cog(ImageCreate(bot))
