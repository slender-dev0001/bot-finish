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
            description="Tous les outils de recherche OSINT disponibles",
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
            name="⚠️ **Rappel Important**",
            value="✅ Légal: Données publiques, vérification compromission\n❌ Illégal: Harcèlement, doxxing, menaces\n\n**Respect de la vie privée obligatoire**",
            inline=False
        )
        
        embed.set_footer(text="💡 Tapez +help pour les autres commandes • 🔐 Résultats en DM")
        
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
