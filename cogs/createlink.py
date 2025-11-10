import discord
from discord.ext import commands
import sqlite3
import secrets
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
from shortlink_server import click_codes

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

    @commands.command(name='linkclick')
    async def linkclick(self, ctx, code: str):
        if code not in click_codes:
            embed = discord.Embed(
                title="❌ Code Invalide",
                description=f"Le code `{code}` n'existe pas ou a expiré",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        data = click_codes[code]
        creator_id = data['user_id']
        short_id = data['short_id']
        ip_address = data['ip_address']
        browser = data['browser']
        device_type = data['device_type']
        user_agent_str = data['user_agent_str']
        
        embed = discord.Embed(
            title="✅ Visite Enregistrée!",
            description=f"Votre visite sur le lien **{short_id}** a été enregistrée",
            color=discord.Color.green()
        )
        embed.add_field(name="👤 Utilisateur", value=ctx.author.mention, inline=True)
        embed.add_field(name="📱 Appareil", value=device_type, inline=True)
        embed.add_field(name="🌐 Navigateur", value=browser, inline=True)
        embed.add_field(name="🔗 Code", value=f"`{code}`", inline=False)
        embed.add_field(name="⏰ Heure", value=f"<t:{int(data['timestamp'].timestamp())}:F>", inline=False)
        
        await ctx.send(embed=embed)
        
        try:
            creator = await self.bot.fetch_user(creator_id)
            notification = discord.Embed(
                title="📊 Nouvelle Visite Enregistrée!",
                description=f"{ctx.author.mention} a cliqué sur ton lien!",
                color=discord.Color.blue()
            )
            notification.add_field(name="🔗 ID du lien", value=f"`{short_id}`", inline=False)
            notification.add_field(name="👤 Visiteur", value=f"{ctx.author.name}#{ctx.author.discriminator}", inline=True)
            notification.add_field(name="📱 Appareil", value=device_type, inline=True)
            notification.add_field(name="🌐 Navigateur", value=browser, inline=True)
            notification.add_field(name="🔍 Adresse IP", value=f"```{ip_address}```", inline=False)
            notification.add_field(name="⏰ Heure", value=f"<t:{int(data['timestamp'].timestamp())}:F>", inline=False)
            
            await creator.send(embed=notification)
        except:
            pass
        
        del click_codes[code]

    @commands.command(name='linkvisits')
    async def linkvisits(self, ctx, short_id: str):
        try:
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id FROM custom_links WHERE id = ?
            ''', (short_id,))
            
            link_result = cursor.fetchone()
            if not link_result:
                embed = discord.Embed(
                    title="❌ Lien non trouvé",
                    description=f"Le lien `{short_id}` n'existe pas",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                conn.close()
                return
            
            link_owner_id = link_result[0]
            if link_owner_id != ctx.author.id and ctx.author.id != 817179893256192020:
                embed = discord.Embed(
                    title="❌ Accès refusé",
                    description="Vous n'êtes pas le propriétaire de ce lien",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                conn.close()
                return
            
            cursor.execute('''
                SELECT visitor_id, visitor_name, ip_address, browser, device_type, country, region, city, timestamp
                FROM link_visits
                WHERE short_id = ?
                ORDER BY timestamp DESC
            ''', (short_id,))
            
            visits = cursor.fetchall()
            conn.close()
            
            if not visits:
                embed = discord.Embed(
                    title="📭 Aucune visite",
                    description=f"Le lien `{short_id}` n'a pas encore reçu de visite authentifiée",
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"📊 Visites du lien `{short_id}`",
                description=f"Total: {len(visits)} visite(s)",
                color=discord.Color.blue()
            )
            
            for idx, (visitor_id, visitor_name, ip_address, browser, device_type, country, region, city, timestamp) in enumerate(visits[:10], 1):
                visitor_info = f"**{visitor_name}** (`{visitor_id}`)\n"
                visitor_info += f"📱 {device_type} | 🌐 {browser}\n"
                visitor_info += f"📍 {city}, {region}, {country}\n"
                visitor_info += f"🔗 {ip_address}"
                
                embed.add_field(
                    name=f"Visite #{idx}",
                    value=visitor_info,
                    inline=False
                )
            
            if len(visits) > 10:
                embed.set_footer(text=f"Affichage des 10 premières visites sur {len(visits)}")
            
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la récupération des visites: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CreateLink(bot))
