import discord
from discord.ext import commands

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="📚 Bot Discord Complet - Commandes",
            description="**90+ Commandes Disponibles**",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎮 **Basiques**",
            value="`+hello` • `+ping` • `+say <msg>` • `+avatar [@user]`",
            inline=False
        )
        
        embed.add_field(
            name="📊 **Slash Commands** (Modernes avec /)",
            value="`/slashhelp` • `/ping` • `/usercard [@user]` • `/leaderboard` • `/about`",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ **Informations**",
            value="`+serverinfo` • `+userinfo [@u]` • `+roleinfo <role>` • `+channelinfo [channel]` • `+stats`",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ **Modération** (Admin)",
            value="`+clear <n>` • `+kick @user` • `+ban @user` • `+unban <name>` • `+mute @user` • `+unmute @user`",
            inline=False
        )
        
        embed.add_field(
            name="🎮 **Interactions Avancées**",
            value="`+buttons` • `+select` • `+modal` (Buttons, Menus, Modales)",
            inline=False
        )
        
        embed.add_field(
            name="🎭 **Événements & Rôles**",
            value="`+autoroles <role>` • `+reactionrole <id> <emoji> <role>` • `+welcome` • `+setuplogs`",
            inline=False
        )
        
        embed.add_field(
            name="👤 **Profils & XP**",
            value="`+profile [@u]` • `+setbio <bio>` • `+balance [@u]` • `+addbal @user <n>` • `+leaderboard`",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ **Customisation Serveur** (Admin)",
            value="`+prefix <new>` • `+setwelcome <msg>` • `+setleave <msg>` • `+setautorole <role>`",
            inline=False
        )
        
        embed.add_field(
            name="👥 **Invitations**",
            value="`+invites [@user]` • `+inviteleaderboard` (Tracker d'invitations)",
            inline=False
        )
        
        embed.add_field(
            name="🎫 **Support & Tickets** (Admin)",
            value="`+ticketsystem` - Créer la base de tickets",
            inline=False
        )
        
        embed.add_field(
            name="🔐 **Vérification** (Admin)",
            value="`+setupverification` - Captcha mathématique auto",
            inline=False
        )
        
        embed.add_field(
            name="🎉 **Giveaways** (Admin)",
            value="`+giveaway <durée> <winners> <prize>` • `+giveaways` • `+endgiveaway <id>`",
            inline=False
        )
        
        embed.add_field(
            name="🎨 **Outils Créatifs**",
            value="`+qrcode <texte>` (QR Code) • `+ascii <texte>` (ASCII Art)",
            inline=False
        )
        
        embed.add_field(
            name="🎲 **Jeux & Plaisir**",
            value="`+dice` • `+flip` • `+8ball <question>`",
            inline=False
        )
        
        embed.set_footer(text="✨ Réaction-rôles • Logs complets • XP système • BD SQLite • Prefix personnalisé • Tracker d'invitations")
        
        await ctx.send(embed=embed)

    @commands.command(name='hello')
    async def hello(self, ctx):
        await ctx.send(f'Bonjour {ctx.author.mention}! 👋')

    @commands.command(name='say')
    async def say(self, ctx, *, message):
        await ctx.send(message)

    @commands.command(name='ping')
    async def ping(self, ctx):
        latence = round(self.bot.latency * 1000)
        await ctx.send(f'🏓 Pong! Latence: {latence}ms')

    @commands.command(name='avatar')
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(
            title=f"Avatar de {member}",
            color=member.color
        )
        embed.set_image(url=member.avatar.url if member.avatar else None)
        await ctx.send(embed=embed)

    @commands.command(name='aide')
    async def aide(self, ctx):
        embed = discord.Embed(
            title="🔍 Outils OSINT - Recherche & Intelligence",
            description="**13+ Outils OSINT avancés** - Recherche, analyse, vérification",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="🌐 **Géolocalisation IP**",
            value="`+searchip <ip>` Informations géographiques d'une IP\n→ Pays, région, ville, FAI, coordonnées GPS",
            inline=False
        )
        
        embed.add_field(
            name="👤 **Recherche Personnelle**",
            value="`+searchname <prénom> <nom>` Recherche OSINT complète par nom\n→ Emails, fuites, comptes sociaux\n\n`+useroslint <id_discord>` Lookup utilisateur Discord\n→ Comptes sociaux, emails possibles, fuites",
            inline=False
        )
        
        embed.add_field(
            name="☎️ **Recherche Téléphone**",
            value="`+searchphone <numéro>` Recherche numéro de téléphone\n→ Fuites, localisation, annuaires\n\n`+searchphone_reverse <numéro>` Recherche inversée complète\n→ Apps, Truecaller, sites de lookup",
            inline=False
        )
        
        embed.add_field(
            name="📧 **Recherche Email**",
            value="`+searchemail <email>` Analyse complète d'une email\n→ Fuites, validation domaine, comptes sociaux",
            inline=False
        )
        
        embed.add_field(
            name="👥 **Recherche Username**",
            value="`+searchusername <username>` Trouve un username sur les réseaux\n→ 13+ plateformes (GitHub, Twitter, Discord, TikTok, etc)",
            inline=False
        )
        
        embed.add_field(
            name="🔗 **Recherche URL**",
            value="`+searchurl <url>` Analyse d'un site web\n→ Headers, DNS, titre, métadescription",
            inline=False
        )
        
        embed.add_field(
            name="📍 **Recherche Localisation**",
            value="`+searchlocation <lat> <lon>` Infos géographiques par coordonnées\n→ Adresse, ville, fuseau horaire, cartes",
            inline=False
        )
        
        embed.add_field(
            name="🔍 **Recherche Email Avancée**",
            value="`+reverseemail <email>` Trouve comptes associés à un email\n→ Résultats Google, comptes sociaux possibles",
            inline=False
        )
        
        embed.add_field(
            name="👥 **Recherche Username Multi-Plateformes**",
            value="`+socialmedia <username>` Cherche sur 12+ réseaux sociaux\n→ Twitter, Instagram, TikTok, GitHub, YouTube, Reddit, LinkedIn, Twitch, Discord, Snapchat, BeReal, Bluesky",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ **Vérifier les Fuites de Données**",
            value="`+leaks <email ou téléphone>` Vérifie Have I Been Pwned\n→ Fuites connues, services compromis, dates",
            inline=False
        )
        
        embed.add_field(
            name="🖼️ **Extraction Métadonnées Images**",
            value="`+metadata` (joindre une image) Extrait EXIF\n→ Localisation GPS, appareil, date de prise de vue, etc",
            inline=False
        )
        
        embed.add_field(
            name="🌐 **Google Dorking - Techniques Avancées**",
            value="`+googlehint` Guide complet du Google dorking\n→ Syntaxe site, filetype, inurl, intitle, etc",
            inline=False
        )
        
        embed.add_field(
            name="☎️ **Localisation Numéro Téléphone**",
            value="`+phonelocation <numéro>` Infos détaillées d'un téléphone\n→ Opérateur, type de ligne, localisation, nom",
            inline=False
        )
        
        embed.add_field(
            name="🌐 **Whois - Infos Domaine**",
            value="`+whois <domaine>` Infos complètes du domaine\n→ Registrar, dates création/expiration, Name Servers, propriétaire",
            inline=False
        )
        
        embed.add_field(
            name="🖼️ **Recherche Images**",
            value="`+searchimage <nom> <prénom>` Trouve images par nom\n→ Résultats Bing Image",
            inline=False
        )
        
        embed.add_field(
            name="🌐 **DNS & Records**",
            value="`+dnsrecords <domaine>` Récupère les records DNS\n→ A, AAAA, MX, CNAME, TXT",
            inline=False
        )
        
        embed.add_field(
            name="📧 **Vérification Email**",
            value="`+emailverify <email>` Vérifie la validité d'un email\n→ Format, domaine, MX records",
            inline=False
        )
        
        embed.add_field(
            name="🔐 **Crack Hash**",
            value="`+hashcrack <hash>` Analyse un hash\n→ Type (MD5, SHA-1, SHA-256, SHA-512) + liens crack",
            inline=False
        )
        
        embed.add_field(
            name="🔒 **Scanner Ports**",
            value="`+portscan <ip>` Scanne les ports courants\n→ HTTP, HTTPS, SSH, FTP, MySQL, etc",
            inline=False
        )
        
        embed.add_field(
            name="📊 **Plage IP**",
            value="`+iprange <ip_début> <ip_fin>` Infos d'une plage\n→ Calcule total IPs, première/dernière",
            inline=False
        )
        
        embed.add_field(
            name="🔄 **Générateur IP**",
            value="`+ipgen [nombre]` Génère IPs aléatoires\n→ Vérifie chaque IP générée (max 100)",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ **Rappel Important**",
            value="✅ Légal: Données publiques, vérification compromission\n❌ Illégal: Harcèlement, doxxing, menaces\n\n**Respect de la vie privée obligatoire**",
            inline=False
        )
        
        embed.set_footer(text="💡 Tapez +help pour les autres commandes • 🔐 Résultats en DM")
        
        await ctx.send(embed=embed)

    @commands.command(name='googlehint')
    async def googlehint(self, ctx):
        embed = discord.Embed(
            title="🔍 Google Dorking - Guide Complet",
            description="Techniques avancées de recherche Google pour l'OSINT",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="🎯 **Syntaxe de Base**",
            value="`site:` Limiter à un site\n`intitle:` Chercher dans le titre\n`inurl:` Chercher dans l'URL\n`intext:` Chercher dans le texte",
            inline=False
        )
        
        embed.add_field(
            name="📁 **Fichiers & Types**",
            value="`filetype:pdf` Documents PDF\n`filetype:doc` Documents Word\n`filetype:xls` Feuilles Excel\n`filetype:ppt` Présentations\n`filetype:zip` Archives\n`filetype:sql` Bases de données",
            inline=False
        )
        
        embed.add_field(
            name="🔗 **Opérateurs Avancés**",
            value="`\"exact phrase\"` Recherche exacte\n`word1 OR word2` Ou (OR)\n`word1 -word2` Exclure (NOT)\n`*` Joker (remplace des mots)",
            inline=False
        )
        
        embed.add_field(
            name="👤 **Recherche Personnelle**",
            value="`site:facebook.com \"prénom nom\"` Facebook\n`site:linkedin.com \"prénom nom\"` LinkedIn\n`site:twitter.com username` Twitter\n`site:instagram.com username` Instagram",
            inline=False
        )
        
        embed.add_field(
            name="📧 **Email & Contact**",
            value="`inurl:contact site:example.com` Pages de contact\n`\"email@example.com\"` Email spécifique\n`intext:\"@example.com\" filetype:pdf` Emails dans PDFs",
            inline=False
        )
        
        embed.add_field(
            name="🔐 **Configurations Dangereuses**",
            value="`intitle:\"index of\"` Répertoires non protégés\n`inurl:admin inurl:login` Pages admin\n`intitle:\"Apache\" \"Index of\"` Serveurs exposés\n`inurl:.git` Repos Git exposés",
            inline=False
        )
        
        embed.add_field(
            name="💾 **Données Sensibles**",
            value="`filetype:env` Fichiers .env (secrets)\n`filetype:sql intext:password` Bases de données\n`intext:\"password\" site:pastebin.com` Passwords leakés\n`filetype:conf` Fichiers de configuration",
            inline=False
        )
        
        embed.add_field(
            name="🌐 **Informations Techniques**",
            value="`inurl:robots.txt site:example.com` Fichier robots\n`inurl:sitemap.xml` Sitemaps\n`inurl:backup` Fichiers de backup\n`inurl:install.php` Scripts d'installation",
            inline=False
        )
        
        embed.add_field(
            name="📊 **Exemples Pratiques**",
            value="`site:linkedin.com \"CTO\" \"France\"` Trouver des CTOs\n`site:github.com \"api_key\"` Clés API exposées\n`\"@company.fr\" filetype:pdf` Documents de l'entreprise\n`inurl:webcam inurl:view.shtml` Webcams IoT",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ **Avertissement Légal**",
            value="✅ **Légal**: Données publiques, recherche responsable\n❌ **Illégal**: Accès non autorisé, exploitation malveillante\n\n**Utilisation éthique obligatoire**",
            inline=False
        )
        
        embed.set_footer(text="💡 Consultez +aide pour tous les outils OSINT")
        
        await ctx.send(embed=embed)

    @commands.command(name='helplink')
    async def helplink(self, ctx):
        embed = discord.Embed(
            title="📚 Guide Complet - Toutes les Commandes",
            description="Répertoire de toutes les commandes disponibles",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎮 **Commandes Basiques**",
            value="`+hello` Salutation\n`+ping` Latence du bot\n`+say <msg>` Répéter un message\n`+avatar [@user]` Afficher l'avatar",
            inline=False
        )
        
        embed.add_field(
            name="📊 **Informations Serveur & Utilisateur**",
            value="`+serverinfo` Info du serveur\n`+userinfo [@user]` Info utilisateur\n`+roleinfo <role>` Info du rôle\n`+channelinfo [salon]` Info du salon\n`+stats` Stats du bot",
            inline=False
        )
        
        embed.add_field(
            name="👤 **Profils & XP**",
            value="`+profile [@user]` Voir le profil\n`+setbio <bio>` Définir une bio\n`+balance [@user]` Voir le solde\n`+addbal @user <montant>` Ajouter des coins\n`+leaderboard` Top 10 utilisateurs",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ **Modération (Admin)**",
            value="`+clear <nombre>` Supprimer des messages\n`+kick @user [raison]` Expulser\n`+ban @user [raison]` Bannir\n`+unban <nom>` Débannir\n`+mute @user` Mute un utilisateur\n`+unmute @user` Unmute un utilisateur",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ **Configuration Serveur (Admin)**",
            value="`+prefix <nouveau>` Changer le prefix\n`+setwelcome <msg>` Message de bienvenue\n`+setleave <msg>` Message de départ\n`+setautorole <role>` Rôle automatique",
            inline=False
        )
        
        embed.add_field(
            name="🎮 **Interactions Avancées**",
            value="`+buttons` Boutons interactifs\n`+select` Menu déroulant\n`+modal` Formulaire avec modale",
            inline=False
        )
        
        embed.add_field(
            name="👥 **Invitations**",
            value="`+invites [@user]` Voir les invitations\n`+inviteleaderboard` Leaderboard des invitations",
            inline=False
        )
        
        embed.add_field(
            name="🔗 **Liens Courts & Suivi**",
            value="`+createlink <url>` Créer un lien court\n`+getlink <id>` Récupérer un lien\n`+mylinks` Voir vos liens\n`+linkvisits <id>` 📊 Voir les visiteurs authentifiés (OAuth2)",
            inline=False
        )
        
        embed.add_field(
            name="🔍 **OSINT & Recherche**",
            value="`+aide` 🔥 Tous les outils OSINT\n`+searchip <ip>` Géolocalisation d'une IP\n`+searchname <prénom> <nom>` Recherche OSINT par nom (résultats en DM)\n`/useroslint <id>` 🕵️ Lookup Discord → Infos OSINT en DM",
            inline=False
        )
        
        embed.add_field(
            name="🎨 **Outils Créatifs**",
            value="`+qrcode <texte>` Générer un QR Code\n`+ascii <texte>` Art ASCII\n`+asciistyles` Voir les styles ASCII",
            inline=False
        )
        
        embed.add_field(
            name="🎉 **Giveaways (Admin)**",
            value="`+giveaway <durée> <winners> <prix>` Créer un giveaway\n`+giveaways` Liste des giveaways actifs\n`+endgiveaway <id>` Terminer un giveaway",
            inline=False
        )
        
        embed.add_field(
            name="🔐 **Vérification (Admin)**",
            value="`+setupverification` Configurer la vérification\n`+verify` Se vérifier manuellement",
            inline=False
        )
        
        embed.add_field(
            name="🎫 **Support & Tickets (Admin)**",
            value="`+ticketsystem` Créer la base de tickets\n`+ticket` Info sur les tickets",
            inline=False
        )
        
        embed.add_field(
            name="📊 **Slash Commands Modernes** (Avec /)",
            value="`/help` Aide complète\n`/ping` Latence\n`/usercard [@user]` Carte de profil\n`/leaderboard` Top 10\n`/about` À propos\n`/hello` Salutation\n`/say <msg>` Répéter\n`/avatar [@user]` Avatar\n`/dice` Dé\n`/flip` Pile/Face\n`/8ball` Boule magique\n`/clear <n>` Supprimer messages\n`/kick` `/ban` `/unban` `/mute` `/unmute` (Modération)\n`/serverinfo` `/userinfo` `/roleinfo` `/channelinfo` `/stats` (Info)",
            inline=False
        )
        
        embed.set_footer(text="✨ 90+ Commandes • Prefix: + • Slash Commands: / • Support: +helplink")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Commands(bot))
