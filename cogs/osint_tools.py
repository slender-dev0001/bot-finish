import discord
from discord.ext import commands
import requests
import logging
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)

class OSINTTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='reverseemail')
    async def reverse_email(self, ctx, email):
        if '@' not in email:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Format email invalide",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loading_embed = discord.Embed(
            title="🔍 Recherche en cours...",
            description=f"Recherche de comptes pour: **{email}**",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            email_encoded = email.replace('@', '%40')
            search_url = f"https://www.google.com/search?q={email_encoded}"
            response = requests.get(search_url, headers=headers, timeout=10)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            for result in soup.find_all('div', class_='yuRUbf'):
                link = result.find('a')
                if link:
                    results.append(link.get('href'))
            
            if not results:
                embed = discord.Embed(
                    title="❌ Aucun résultat",
                    description=f"Pas de comptes trouvés pour: **{email}**",
                    color=discord.Color.orange()
                )
                await loading_msg.edit(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"📧 Résultats pour: {email}",
                description=f"**{len(results[:5])} résultat(s)** trouvé(s)",
                color=discord.Color.green()
            )
            
            for i, link in enumerate(results[:5], 1):
                embed.add_field(
                    name=f"Résultat {i}",
                    value=f"[{link[:60]}...]({link})",
                    inline=False
                )
            
            await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur reverseemail: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur est survenue: {str(e)[:100]}",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)

    @commands.command(name='socialmedia')
    async def social_media(self, ctx, username):
        if not username or len(username) < 3:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Username minimum 3 caractères",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loading_embed = discord.Embed(
            title="🔍 Recherche en cours...",
            description=f"Recherche de **{username}** sur les réseaux",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            platforms = {
                "Twitter": f"https://twitter.com/{username}",
                "Instagram": f"https://instagram.com/{username}",
                "TikTok": f"https://tiktok.com/@{username}",
                "GitHub": f"https://github.com/{username}",
                "YouTube": f"https://youtube.com/@{username}",
                "Reddit": f"https://reddit.com/u/{username}",
                "LinkedIn": f"https://linkedin.com/in/{username}",
                "Twitch": f"https://twitch.tv/{username}",
                "Discord": f"https://discord.com/users/{username if username.isdigit() else 'search'}",
                "Snapchat": f"https://snapchat.com/add/{username}",
                "BeReal": f"https://bereal.com/user/{username}",
                "Bluesky": f"https://bsky.app/profile/{username}"
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            found = []
            for platform, url in platforms.items():
                try:
                    resp = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
                    if resp.status_code == 200:
                        found.append((platform, url))
                except:
                    pass
            
            if not found:
                embed = discord.Embed(
                    title="❌ Aucun compte trouvé",
                    description=f"Pas de compte trouvé pour: **{username}**",
                    color=discord.Color.orange()
                )
                await loading_msg.edit(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"📱 Comptes trouvés pour: {username}",
                description=f"**{len(found)}** compte(s) actif(s)",
                color=discord.Color.green()
            )
            
            for platform, url in found:
                embed.add_field(
                    name=f"✅ {platform}",
                    value=f"[Voir profil]({url})",
                    inline=True
                )
            
            await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur socialmedia: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur est survenue: {str(e)[:100]}",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)

    @commands.command(name='leaks')
    async def check_leaks(self, ctx, query):
        if '@' not in query and not query.isdigit():
            embed = discord.Embed(
                title="❌ Erreur",
                description="Entrez un email ou un téléphone",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loading_embed = discord.Embed(
            title="🔍 Vérification en cours...",
            description=f"Vérification de: **{query}**",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            if '@' in query:
                url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{query}"
            else:
                url = f"https://haveibeenpwned.com/api/v3/breachedaccount/+{query}"
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 404:
                embed = discord.Embed(
                    title="✅ Sécurisé",
                    description=f"**{query}** n'a pas été trouvé dans les fuites connues",
                    color=discord.Color.green()
                )
                await loading_msg.edit(embed=embed)
                return
            
            if response.status_code == 200:
                breaches = response.json()
                embed = discord.Embed(
                    title="⚠️ Données compromise!",
                    description=f"**{query}** a été trouvé dans **{len(breaches)}** fuite(s)",
                    color=discord.Color.red()
                )
                
                for i, breach in enumerate(breaches[:5], 1):
                    embed.add_field(
                        name=f"Fuite {i}: {breach['Name']}",
                        value=f"📅 {breach['BreachDate']}\n🔢 {breach['PwnCount']} comptes",
                        inline=False
                    )
                
                await loading_msg.edit(embed=embed)
                return
            
            embed = discord.Embed(
                title="❓ Résultat inconnu",
                description="Impossible de vérifier pour l'instant",
                color=discord.Color.yellow()
            )
            await loading_msg.edit(embed=embed)

        except Exception as e:
            logger.error(f"Erreur leaks: {e}")
            embed = discord.Embed(
                title="❌ Erreur",
                description="Impossible de vérifier les fuites",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=embed)

    @commands.command(name='googlehint')
    async def google_dorking(self, ctx):
        embed = discord.Embed(
            title="🔍 Google Dorking - Techniques Avancées",
            description="Techniques de recherche Google avancées",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📄 Rechercher par type de fichier",
            value="`filetype:pdf password`\n`filetype:xlsx secret`",
            inline=False
        )
        
        embed.add_field(
            name="🌐 Limiter à un site",
            value="`site:example.com password`\n`site:example.com admin`",
            inline=False
        )
        
        embed.add_field(
            name="🔗 Lien exact",
            value="`inurl:admin`\n`inurl:login`\n`inurl:config.php`",
            inline=False
        )
        
        embed.add_field(
            name="📝 Dans le titre",
            value="`intitle:index.of`\n`intitle:admin login`",
            inline=False
        )
        
        embed.add_field(
            name="🚫 Exclure",
            value="`password -site:wikipedia.org`",
            inline=False
        )
        
        embed.add_field(
            name="💬 Guillemets (exact)",
            value='`"admin@example.com"`\n`"API_KEY="`',
            inline=False
        )
        
        embed.add_field(
            name="🔢 Plage numérique",
            value="`age 18..65`",
            inline=False
        )
        
        embed.add_field(
            name="📧 Trouver emails",
            value="`"@example.com" "password"`",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Exemples classiques",
            value="`"index.of /" mp3`\n`"config.php" password`\n`inurl:admin inurl:login`",
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(OSINTTools(bot))
