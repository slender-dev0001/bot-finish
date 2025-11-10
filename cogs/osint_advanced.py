import discord
from discord.ext import commands
import requests
import logging
import whois
from datetime import datetime

logger = logging.getLogger(__name__)

class OSINTAdvanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='metadata')
    async def metadata(self, ctx):
        if not ctx.message.attachments:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Joignez une image à votre message",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loading_embed = discord.Embed(
            title="🔍 Analyse en cours...",
            description="Extraction des métadonnées",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            attachment = ctx.message.attachments[0]
            
            if not attachment.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Format d'image invalide",
                    color=discord.Color.red()
                )
                await loading_msg.edit(embed=embed)
                return
            
            image_data = await attachment.read()
            
            try:
                from PIL import Image
                from PIL.ExifTags import TAGS
                import io
                
                img = Image.open(io.BytesIO(image_data))
                exif_data = img._getexif()
                
                embed = discord.Embed(
                    title=f"🖼️ Métadonnées: {attachment.filename}",
                    description=f"Dimensions: {img.width}x{img.height}px",
                    color=discord.Color.green()
                )
                
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        if tag_name not in ['MakerNote', 'UserComment']:
                            embed.add_field(
                                name=tag_name,
                                value=str(value)[:100],
                                inline=True
                            )
                else:
                    embed.add_field(
                        name="EXIF",
                        value="Aucune données EXIF trouvée",
                        inline=False
                    )
                
                embed.add_field(
                    name="Format",
                    value=img.format,
                    inline=True
                )
                
                await loading_msg.edit(embed=embed)
                
            except Exception as e:
                logger.error(f"Erreur parsing EXIF: {e}")
                embed = discord.Embed(
                    title="⚠️ Info basique",
                    description=f"Fichier: **{attachment.filename}**\nTaille: **{attachment.size}** bytes",
                    color=discord.Color.yellow()
                )
                await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur metadata: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur est survenue: {str(e)[:100]}",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)

    @commands.command(name='phonelocation')
    async def phone_location(self, ctx, phone_number):
        phone = phone_number.replace('+', '').replace('-', '').replace(' ', '')
        
        if not phone.isdigit() or len(phone) < 10:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Numéro de téléphone invalide",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loading_embed = discord.Embed(
            title="🔍 Recherche en cours...",
            description=f"Localisation de: **{phone_number}**",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            phone_prefix = phone[:2]
            country_codes = {
                '33': 'France 🇫🇷',
                '32': 'Belgique 🇧🇪',
                '41': 'Suisse 🇨🇭',
                '49': 'Allemagne 🇩🇪',
                '44': 'Royaume-Uni 🇬🇧',
                '39': 'Italie 🇮🇹',
                '34': 'Espagne 🇪🇸',
                '31': 'Pays-Bas 🇳🇱',
                '43': 'Autriche 🇦🇹',
                '45': 'Danemark 🇩🇰',
            }
            
            country = country_codes.get(phone_prefix, 'Pays inconnu')
            
            search_url = f"https://www.google.com/search?q={phone_number}"
            response = requests.get(search_url, headers=headers, timeout=10)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = soup.find_all('div', class_='yuRUbf')
            
            embed = discord.Embed(
                title=f"☎️ Infos pour: {phone_number}",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="Format",
                value=f"+{phone[:2]} {phone[2:]}",
                inline=True
            )
            
            embed.add_field(
                name="Pays",
                value=country,
                inline=True
            )
            
            embed.add_field(
                name="Longueur",
                value=f"{len(phone)} chiffres",
                inline=True
            )
            
            if results:
                embed.add_field(
                    name="Résultats Google",
                    value=f"🔗 {len(results)} résultats trouvés",
                    inline=False
                )
            
            embed.add_field(
                name="ℹ️ Informations",
                value="Recherche sur données publiques\nPour plus de détails, utilisez Truecaller ou numlookup.com",
                inline=False
            )
            
            await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur phonelocation: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur est survenue",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)

    @commands.command(name='whois')
    async def whois_lookup(self, ctx, domain):
        domain = domain.lower().replace('http://', '').replace('https://', '').split('/')[0]
        
        if '.' not in domain:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Domaine invalide",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loading_embed = discord.Embed(
            title="🔍 Recherche WHOIS en cours...",
            description=f"Infos pour: **{domain}**",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            whois_data = whois.whois(domain)
            
            embed = discord.Embed(
                title=f"🌐 WHOIS: {domain}",
                color=discord.Color.green()
            )
            
            if whois_data.registrar:
                embed.add_field(
                    name="Registrar",
                    value=whois_data.registrar,
                    inline=True
                )
            
            if whois_data.creation_date:
                date = whois_data.creation_date
                if isinstance(date, list):
                    date = date[0]
                embed.add_field(
                    name="Date de création",
                    value=date.strftime("%d/%m/%Y") if hasattr(date, 'strftime') else str(date),
                    inline=True
                )
            
            if whois_data.expiration_date:
                date = whois_data.expiration_date
                if isinstance(date, list):
                    date = date[0]
                embed.add_field(
                    name="Date d'expiration",
                    value=date.strftime("%d/%m/%Y") if hasattr(date, 'strftime') else str(date),
                    inline=True
                )
            
            if whois_data.name_servers:
                ns = whois_data.name_servers
                if isinstance(ns, list):
                    ns = ', '.join(ns[:3])
                embed.add_field(
                    name="Name Servers",
                    value=ns,
                    inline=False
                )
            
            if whois_data.registrant:
                embed.add_field(
                    name="Propriétaire",
                    value=str(whois_data.registrant)[:100],
                    inline=False
                )
            
            if whois_data.emails:
                emails = whois_data.emails
                if isinstance(emails, list):
                    emails = ', '.join(emails[:2])
                embed.add_field(
                    name="Emails",
                    value=emails,
                    inline=False
                )
            
            await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur whois: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Domaine non trouvé ou erreur: {str(e)[:100]}",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(OSINTAdvanced(bot))
