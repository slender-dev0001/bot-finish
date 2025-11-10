import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import secrets
import os
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import io

load_dotenv()
BASE_URL = os.getenv('BASE_URL', 'https://googg.up.railway.app')
if BASE_URL and not BASE_URL.startswith(('http://', 'https://')):
    BASE_URL = f'https://{BASE_URL}'

class ImageTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        try:
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            
            # Table pour les images tracker
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
            
            # Table pour les clics sur les images
            cursor.execute('''
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
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Erreur lors de l'initialisation de la DB image tracker: {e}")

    def generate_tracker_id(self):
        return secrets.token_urlsafe(6)

    def create_tracking_image(self, title):
        """Créer une image attractive pour le tracking"""
        # Dimensions de l'image
        width, height = 800, 400
        
        # Créer l'image avec un dégradé
        img = Image.new('RGB', (width, height), color=(88, 101, 242))
        draw = ImageDraw.Draw(img)
        
        # Dessiner un dégradé simple
        for i in range(height):
            color_value = int(88 + (i / height) * 50)
            draw.rectangle([(0, i), (width, i+1)], fill=(color_value, 101, 242))
        
        # Ajouter le texte
        try:
            # Essayer de charger une police système
            font_large = ImageFont.truetype("arial.ttf", 50)
            font_small = ImageFont.truetype("arial.ttf", 30)
        except:
            # Utiliser la police par défaut si arial n'est pas disponible
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Titre
        title_text = title if len(title) < 30 else title[:27] + "..."
        
        # Calculer la position centrée
        bbox = draw.textbbox((0, 0), title_text, font=font_large)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2 - 30
        
        # Dessiner le texte avec ombre
        draw.text((x + 2, y + 2), title_text, fill=(0, 0, 0, 128), font=font_large)
        draw.text((x, y), title_text, fill=(255, 255, 255), font=font_large)
        
        # Sous-titre
        subtitle = "🎁 Cliquez pour voir"
        bbox_sub = draw.textbbox((0, 0), subtitle, font=font_small)
        sub_width = bbox_sub[2] - bbox_sub[0]
        x_sub = (width - sub_width) // 2
        y_sub = y + text_height + 20
        
        draw.text((x_sub + 1, y_sub + 1), subtitle, fill=(0, 0, 0, 128), font=font_small)
        draw.text((x_sub, y_sub), subtitle, fill=(255, 255, 255), font=font_small)
        
        # Sauvegarder en bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes

    @app_commands.command(name="createimage", description="Créer une image qui track les clics avec l'IP")
    async def createimage(self, interaction: discord.Interaction, title: str):
        """Créer une image tracker qui envoie une notification avec l'IP quand quelqu'un clique"""
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Générer un ID unique
            tracker_id = self.generate_tracker_id()
            
            # Enregistrer dans la base de données
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO image_trackers (id, user_id, guild_id, title)
                VALUES (?, ?, ?, ?)
            ''', (tracker_id, interaction.user.id, interaction.guild.id if interaction.guild else 0, title))
            conn.commit()
            conn.close()
            
            # Créer l'image
            img_bytes = self.create_tracking_image(title)
            
            # URL de tracking
            tracking_url = f"{BASE_URL}/image/{tracker_id}"
            
            # Créer l'embed de confirmation
            embed = discord.Embed(
                title="✅ Image Tracker Créée !",
                description=f"Votre image tracker est prête !",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📋 Informations",
                value=f"**Titre:** {title}\n**ID:** `{tracker_id}`",
                inline=False
            )
            
            embed.add_field(
                name="🔗 URL de l'image",
                value=f"```{tracking_url}```",
                inline=False
            )
            
            embed.add_field(
                name="📊 Utilisation",
                value=(
                    "Partagez cette URL ou utilisez `/imageclick` pour voir les statistiques.\n"
                    "Quand quelqu'un clique sur l'image, vous recevrez une notification avec :\n"
                    "• 📍 Adresse IP\n"
                    "• 🌍 Localisation (pays, région, ville)\n"
                    "• 🖥️ Navigateur et appareil\n"
                    "• 🕐 Date et heure du clic"
                ),
                inline=False
            )
            
            embed.add_field(
                name="⚠️ Avertissement",
                value="Cette fonctionnalité est à utiliser de manière éthique et légale uniquement.",
                inline=False
            )
            
            embed.set_footer(text="Les notifications seront envoyées en DM")
            
            # Envoyer l'image en tant que fichier
            file = discord.File(img_bytes, filename=f"tracker_{tracker_id}.png")
            
            await interaction.followup.send(embed=embed, file=file, ephemeral=True)
            
            # Message public dans le salon
            public_embed = discord.Embed(
                title="🖼️ Nouvelle Image",
                description=f"**{title}**",
                color=discord.Color.blue()
            )
            public_embed.set_image(url=tracking_url)
            public_embed.set_footer(text=f"Créé par {interaction.user.name}")
            
            await interaction.channel.send(embed=public_embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la création de l'image : {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="imageclicks", description="Voir les statistiques de votre image tracker")
    async def imageclicks(self, interaction: discord.Interaction, tracker_id: str):
        """Afficher les statistiques d'une image tracker"""
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            
            # Vérifier que l'utilisateur est le propriétaire
            cursor.execute('''
                SELECT user_id, title, clicks, created_at
                FROM image_trackers
                WHERE id = ?
            ''', (tracker_id,))
            
            result = cursor.fetchone()
            
            if not result:
                embed = discord.Embed(
                    title="❌ Tracker non trouvé",
                    description=f"Aucune image tracker avec l'ID `{tracker_id}`",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                conn.close()
                return
            
            user_id, title, clicks, created_at = result
            
            if user_id != interaction.user.id:
                embed = discord.Embed(
                    title="❌ Accès refusé",
                    description="Vous n'êtes pas le propriétaire de cette image tracker",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                conn.close()
                return
            
            # Récupérer les clics
            cursor.execute('''
                SELECT ip_address, browser, device_type, country, region, city, clicked_at
                FROM image_clicks
                WHERE tracker_id = ?
                ORDER BY clicked_at DESC
                LIMIT 10
            ''', (tracker_id,))
            
            click_results = cursor.fetchall()
            conn.close()
            
            embed = discord.Embed(
                title=f"📊 Statistiques : {title}",
                description=f"**Total de clics :** {clicks}",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📋 Informations",
                value=f"**ID:** `{tracker_id}`\n**Créé le:** {created_at}",
                inline=False
            )
            
            if click_results:
                for idx, (ip, browser, device, country, region, city, clicked_at) in enumerate(click_results, 1):
                    location = f"{city}, {region}, {country}" if city != "Inconnu" else "Non disponible"
                    click_info = (
                        f"**IP:** `{ip}`\n"
                        f"📍 {location}\n"
                        f"🌐 {browser} | 📱 {device}\n"
                        f"🕐 {clicked_at}"
                    )
                    embed.add_field(
                        name=f"Clic #{idx}",
                        value=click_info,
                        inline=False
                    )
            else:
                embed.add_field(
                    name="📭 Aucun clic",
                    value="Cette image n'a pas encore été cliquée",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur : {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @commands.command(name='createimage')
    async def createimage_prefix(self, ctx, *, title: str):
        """Version prefix de la commande createimage"""
        
        try:
            # Générer un ID unique
            tracker_id = self.generate_tracker_id()
            
            # Enregistrer dans la base de données
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO image_trackers (id, user_id, guild_id, title)
                VALUES (?, ?, ?, ?)
            ''', (tracker_id, ctx.author.id, ctx.guild.id if ctx.guild else 0, title))
            conn.commit()
            conn.close()
            
            # Créer l'image
            img_bytes = self.create_tracking_image(title)
            
            # URL de tracking
            tracking_url = f"{BASE_URL}/image/{tracker_id}"
            
            # Créer l'embed
            embed = discord.Embed(
                title="✅ Image Tracker Créée !",
                description=f"Votre image tracker est prête !",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📋 Informations",
                value=f"**Titre:** {title}\n**ID:** `{tracker_id}`",
                inline=False
            )
            
            embed.add_field(
                name="🔗 URL de l'image",
                value=f"```{tracking_url}```",
                inline=False
            )
            
            embed.add_field(
                name="📊 Commandes",
                value=f"`+imageclicks {tracker_id}` - Voir les statistiques",
                inline=False
            )
            
            embed.set_footer(text="⚠️ À utiliser de manière éthique")
            
            # Envoyer l'image
            file = discord.File(img_bytes, filename=f"tracker_{tracker_id}.png")
            await ctx.send(embed=embed, file=file)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur : {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name='imageclicks')
    async def imageclicks_prefix(self, ctx, tracker_id: str):
        """Version prefix de imageclicks"""
        
        try:
            conn = sqlite3.connect("links.db")
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, title, clicks, created_at
                FROM image_trackers
                WHERE id = ?
            ''', (tracker_id,))
            
            result = cursor.fetchone()
            
            if not result:
                await ctx.send("❌ Tracker non trouvé")
                conn.close()
                return
            
            user_id, title, clicks, created_at = result
            
            if user_id != ctx.author.id:
                await ctx.send("❌ Accès refusé")
                conn.close()
                return
            
            cursor.execute('''
                SELECT ip_address, browser, device_type, country, region, city, clicked_at
                FROM image_clicks
                WHERE tracker_id = ?
                ORDER BY clicked_at DESC
                LIMIT 10
            ''', (tracker_id,))
            
            click_results = cursor.fetchall()
            conn.close()
            
            embed = discord.Embed(
                title=f"📊 Statistiques : {title}",
                description=f"**Total :** {clicks} clic(s)",
                color=discord.Color.blue()
            )
            
            if click_results:
                for idx, (ip, browser, device, country, region, city, clicked_at) in enumerate(click_results[:5], 1):
                    location = f"{city}, {region}, {country}"
                    embed.add_field(
                        name=f"Clic #{idx}",
                        value=f"`{ip}` | {location}\n{browser} | {device}",
                        inline=False
                    )
            else:
                embed.add_field(name="📭", value="Aucun clic", inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur : {str(e)}")

async def setup(bot):
    await bot.add_cog(ImageTracker(bot))