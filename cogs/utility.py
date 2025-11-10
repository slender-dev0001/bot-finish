import discord
from discord.ext import commands
from datetime import datetime
import requests
import json

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='serverinfo')
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(
            title=f"📊 {guild.name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="ID", value=guild.id, inline=True)
        embed.add_field(name="Membres", value=f"👥 {guild.member_count}", inline=True)
        embed.add_field(name="Salons", value=f"#️⃣ {len(guild.channels)}", inline=True)
        embed.add_field(name="Rôles", value=f"🏷️ {len(guild.roles)}", inline=True)
        embed.add_field(name="Créé le", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Propriétaire", value=guild.owner.mention, inline=True)
        embed.add_field(name="Niveau de vérification", value=str(guild.verification_level), inline=True)
        embed.add_field(name="Région", value=str(guild.region) if hasattr(guild, 'region') else "N/A", inline=True)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        await ctx.send(embed=embed)

    @commands.command(name='userinfo')
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(
            title=f"👤 {member}",
            color=member.color
        )
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Mention", value=member.mention, inline=True)
        embed.add_field(name="Compte créé", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Serveur rejoint", value=member.joined_at.strftime("%d/%m/%Y") if member.joined_at else "N/A", inline=True)
        embed.add_field(name="Bot?", value="✅ Oui" if member.bot else "❌ Non", inline=True)
        embed.add_field(name="Statut", value=str(member.status).upper(), inline=True)
        
        roles = [role.mention for role in member.roles if role != ctx.guild.default_role]
        if roles:
            embed.add_field(name=f"Rôles ({len(roles)})", value=", ".join(roles[:10]), inline=False)
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        await ctx.send(embed=embed)

    @commands.command(name='roleinfo')
    async def roleinfo(self, ctx, role: discord.Role):
        embed = discord.Embed(
            title=f"🏷️ {role.name}",
            color=role.color
        )
        embed.add_field(name="ID", value=role.id, inline=True)
        embed.add_field(name="Position", value=role.position, inline=True)
        embed.add_field(name="Créé le", value=role.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Mentalité", value="✅ Oui" if role.mentionable else "❌ Non", inline=True)
        embed.add_field(name="Géré par bot", value="✅ Oui" if role.managed else "❌ Non", inline=True)
        embed.add_field(name="Couleur", value=str(role.color), inline=True)
        embed.add_field(name="Membres", value=len(role.members), inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name='channelinfo')
    async def channelinfo(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        embed = discord.Embed(
            title=f"#️⃣ {channel.name}",
            color=discord.Color.purple()
        )
        embed.add_field(name="ID", value=channel.id, inline=True)
        embed.add_field(name="Type", value="Texte" if isinstance(channel, discord.TextChannel) else "Vocal", inline=True)
        embed.add_field(name="Créé le", value=channel.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Sujet", value=channel.topic or "Aucun", inline=False)
        embed.add_field(name="NSFW", value="✅ Oui" if channel.is_nsfw() else "❌ Non", inline=True)
        
        if channel.slowmode_delay > 0:
            embed.add_field(name="Mode lent", value=f"{channel.slowmode_delay}s", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name='stats')
    async def stats(self, ctx):
        embed = discord.Embed(
            title="📈 Statistiques du Bot",
            color=discord.Color.green()
        )
        embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Serveurs", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Utilisateurs", value=len(self.bot.users), inline=True)
        embed.add_field(name="Extensions chargées", value=len(self.bot.cogs), inline=True)
        embed.add_field(name="Version", value="1.0.0", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name='searchip')
    async def searchip(self, ctx, ip: str):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(f'http://ip-api.com/json/{ip}?lang=fr', timeout=5, headers=headers)
            
            if response.status_code != 200:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description=f"Erreur API (Status: {response.status_code})\nEssayez dans quelques secondes",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
            
            data = response.json()
            
            if data.get('status') != 'success':
                embed = discord.Embed(
                    title="❌ IP Invalide",
                    description=f"L'IP `{ip}` n'est pas valide ou introuvable",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"🔍 Résultats pour l'IP: {ip}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(name="🌍 Pays", value=f"{data.get('country', 'Inconnu')}", inline=True)
            embed.add_field(name="🏙️ Ville", value=f"{data.get('city', 'Inconnu')}", inline=True)
            embed.add_field(name="📍 Région", value=f"{data.get('regionName', 'Inconnu')}", inline=True)
            
            embed.add_field(name="🕐 Fuseau horaire", value=f"{data.get('timezone', 'Inconnu')}", inline=False)
            embed.add_field(name="📌 Coordonnées GPS", value=f"Latitude: {data.get('lat', 'N/A')}\nLongitude: {data.get('lon', 'N/A')}", inline=False)
            embed.add_field(name="🔗 FAI (Fournisseur)", value=f"{data.get('isp', 'Inconnu')}", inline=True)
            embed.add_field(name="🏢 Organisation", value=f"{data.get('org', 'Inconnu')}", inline=True)
            embed.add_field(name="💾 Code Pays", value=f"{data.get('countryCode', 'XX')}", inline=True)
            
            embed.set_footer(text="Recherche d'IP | Alimenté par ip-api.com")
            
            await ctx.send(embed=embed)
        
        except requests.exceptions.Timeout:
            embed = discord.Embed(
                title="❌ Timeout",
                description="La requête a pris trop de temps",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except requests.exceptions.ConnectionError:
            embed = discord.Embed(
                title="❌ Erreur Connexion",
                description="Impossible de se connecter à l'API",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name='searchname')
    async def searchname(self, ctx, firstname: str, lastname: str):
        try:
            await ctx.send("🔍 Recherche OSINT en cours... Les résultats vous seront envoyés en DM")
            
            results_found = False
            embed = discord.Embed(
                title=f"🔍 Résultats OSINT: {firstname} {lastname}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            try:
                email = f"{firstname.lower()}.{lastname.lower()}@"
                response = requests.get(
                    'https://api.holehe.com/email_exists',
                    params={'email': email},
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        embed.add_field(name="📧 Recherche par Email", value=f"Résultats trouvés", inline=False)
                        results_found = True
            except:
                pass
            
            try:
                response = requests.get(
                    f'https://api.epieos.com/email-finder?name={firstname}+{lastname}',
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('email'):
                        email_found = data.get('email')
                        confidence = data.get('confidence', 'N/A')
                        embed.add_field(
                            name="📧 Email Trouvé",
                            value=f"`{email_found}`\n**Confiance:** {confidence}%",
                            inline=False
                        )
                        results_found = True
                        
                        try:
                            hibp_response = requests.get(
                                f'https://haveibeenpwned.com/api/v3/breachedaccount/{email_found}',
                                headers={'User-Agent': 'Discord Bot'},
                                timeout=5
                            )
                            if hibp_response.status_code == 200:
                                breaches = hibp_response.json()
                                breach_names = [b['Name'] for b in breaches[:5]]
                                embed.add_field(
                                    name="⚠️ Fuites de Données",
                                    value=f"Trouvé dans {len(breaches)} fuite(s):\n" + "\n".join(breach_names),
                                    inline=False
                                )
                        except:
                            pass
            except:
                pass
            
            try:
                response = requests.get(
                    f'https://api.hunter.io/v2/domain-search?domain=linkedin.com&limit=10',
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get('data'):
                        similar_names = [p['value'] for p in data.get('data', [])[:3] if f"{firstname.lower()}" in p['value'].lower() or f"{lastname.lower()}" in p['value'].lower()]
                        if similar_names:
                            embed.add_field(
                                name="👤 Profils Similaires",
                                value="\n".join(similar_names[:3]),
                                inline=False
                            )
                            results_found = True
            except:
                pass
            
            try:
                response = requests.get(
                    f'https://nominatim.openstreetmap.org/search?q={firstname}+{lastname}&format=json&limit=5',
                    headers={'User-Agent': 'Discord Bot'},
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        locations = [f"{d.get('display_name', 'Unknown')}" for d in data[:3]]
                        if locations:
                            embed.add_field(
                                name="📍 Emplacements Publics",
                                value="\n".join(locations),
                                inline=False
                            )
                            results_found = True
            except:
                pass
            
            try:
                username_search = firstname.lower() + lastname.lower()
                found_accounts = []
                
                accounts_config = {
                    'twitter': f'https://twitter.com/search?q={firstname}%20{lastname}',
                    'instagram': f'https://instagram.com/{username_search}',
                    'github': f'https://github.com/{username_search}',
                    'reddit': f'https://reddit.com/user/{username_search}',
                    'tiktok': f'https://tiktok.com/@{username_search}',
                    'youtube': f'https://youtube.com/results?search_query={firstname}+{lastname}'
                }
                
                for site, url in accounts_config.items():
                    try:
                        if site == 'github':
                            response = requests.get(f'https://api.github.com/users/{username_search}', timeout=3)
                            if response.status_code == 200:
                                found_accounts.append(f'[{site.capitalize()}]({url})')
                        elif site in ['twitter', 'youtube']:
                            found_accounts.append(f'[{site.capitalize()}]({url})')
                        else:
                            response = requests.head(url, timeout=3, allow_redirects=True)
                            if response.status_code < 404:
                                found_accounts.append(f'[{site.capitalize()}]({url})')
                    except:
                        pass
                
                if found_accounts:
                    embed.add_field(
                        name="🌐 Comptes Trouvés",
                        value=" • ".join(found_accounts),
                        inline=False
                    )
                    results_found = True
            except:
                pass
            
            if not results_found:
                embed.add_field(
                    name="📭 Aucun Résultat",
                    value="Aucune information trouvée pour cette personne",
                    inline=False
                )
            
            embed.add_field(
                name="⚠️ Avertissement Légal",
                value="Ces données sont publiques. Respect de la vie privée obligatoire.",
                inline=False
            )
            embed.set_footer(text="OSINT Search | Données de sources publiques")
            
            await ctx.author.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur lors de la recherche: {str(e)}",
                color=discord.Color.red()
            )
            try:
                await ctx.author.send(embed=embed)
            except:
                await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
