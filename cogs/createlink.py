import discord
from discord.ext import commands
import sqlite3
import secrets
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5001')

class CreateLink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        try:
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_links (
                    id TEXT PRIMARY KEY,
                    original_url TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    clicks INTEGER DEFAULT 0
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erreur lors de l'initialisation de la DB: {e}")

    def is_valid_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except:
            return False

    def generate_short_id(self):
        return secrets.token_urlsafe(4)

    @commands.command(name='createlink')
    async def createlink(self, ctx, url: str):
        if not self.is_valid_url(url):
            embed = discord.Embed(
                title="❌ URL invalide",
                description="Veuillez fournir une URL HTTPS valide (ex: https://discord.com)",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        short_id = self.generate_short_id()
        
        try:
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO custom_links (id, original_url, user_id, guild_id)
                VALUES (?, ?, ?, ?)
            ''', (short_id, url, ctx.author.id, ctx.guild.id))
            conn.commit()
            conn.close()

            short_url = f"{BASE_URL}/link/{short_id}"
            embed = discord.Embed(
                title="✅ Lien créé avec succès",
                color=discord.Color.green()
            )
            embed.add_field(name="ID du lien", value=f"`{short_id}`", inline=False)
            embed.add_field(name="Lien court", value=f"`{short_url}`", inline=False)
            embed.add_field(name="URL originale", value=url, inline=False)
            embed.add_field(name="Créé par", value=ctx.author.mention, inline=True)
            embed.set_footer(text=f"Utilisez +getlink {short_id} pour accéder au lien")
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la création du lien: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name='getlink')
    async def getlink(self, ctx, short_id: str):
        try:
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            
            if ctx.guild:
                cursor.execute('''
                    SELECT original_url, user_id, created_at, clicks
                    FROM custom_links
                    WHERE id = ? AND guild_id = ?
                ''', (short_id, ctx.guild.id))
            else:
                cursor.execute('''
                    SELECT original_url, user_id, created_at, clicks
                    FROM custom_links
                    WHERE id = ?
                ''', (short_id,))
            
            result = cursor.fetchone()
            if not result:
                embed = discord.Embed(
                    title="❌ Lien non trouvé",
                    description=f"Le lien `{short_id}` n'existe pas",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                conn.close()
                return

            original_url, user_id, created_at, clicks = result
            
            cursor.execute('''
                UPDATE custom_links
                SET clicks = clicks + 1
                WHERE id = ?
            ''', (short_id,))
            conn.commit()
            conn.close()

            user = await self.bot.fetch_user(user_id)
            short_url = f"{BASE_URL}/link/{short_id}"
            embed = discord.Embed(
                title="🔗 Lien trouvé",
                color=discord.Color.blue()
            )
            embed.add_field(name="ID", value=f"`{short_id}`", inline=False)
            embed.add_field(name="Lien court", value=f"`{short_url}`", inline=False)
            embed.add_field(name="URL", value=original_url, inline=False)
            embed.add_field(name="Créé par", value=user.mention, inline=True)
            embed.add_field(name="Clics", value=clicks + 1, inline=True)
            embed.add_field(name="Créé le", value=created_at, inline=True)
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la récupération du lien: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name='mylinks')
    async def mylinks(self, ctx):
        try:
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            
            if ctx.guild:
                cursor.execute('''
                    SELECT id, original_url, clicks, created_at
                    FROM custom_links
                    WHERE user_id = ? AND guild_id = ?
                    ORDER BY created_at DESC
                ''', (ctx.author.id, ctx.guild.id))
                links_scope = "dans ce serveur"
            else:
                cursor.execute('''
                    SELECT id, original_url, clicks, created_at
                    FROM custom_links
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (ctx.author.id,))
                links_scope = "au total"
            
            links = cursor.fetchall()
            conn.close()

            if not links:
                embed = discord.Embed(
                    title="📭 Aucun lien",
                    description=f"Vous n'avez créé aucun lien {links_scope}",
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title="🔗 Vos liens",
                color=discord.Color.blue()
            )
            
            for short_id, url, clicks, created_at in links:
                short_url = f"{BASE_URL}/link/{short_id}"
                embed.add_field(
                    name=f"`{short_id}`",
                    value=f"**Lien:** {short_url}\n**Cible:** {url}\n**Clics:** {clicks}",
                    inline=False
                )
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la récupération de vos liens: {e}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CreateLink(bot))
