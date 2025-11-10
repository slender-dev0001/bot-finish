import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import random

class AllSlashCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hello", description="Salut!")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Bonjour {interaction.user.mention}! 👋', ephemeral=True)

    @app_commands.command(name="say", description="Répéter un message")
    async def say(self, interaction: discord.Interaction, message: str):
        await interaction.response.send_message(message)

    @app_commands.command(name="avatar", description="Afficher l'avatar d'un utilisateur")
    async def avatar(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user
        embed = discord.Embed(
            title=f"Avatar de {user}",
            color=discord.Color.blue()
        )
        embed.set_image(url=user.avatar.url if user.avatar else None)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="clear", description="Supprimer des messages (Admin)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        if amount <= 0:
            await interaction.response.send_message("❌ Spécifie un nombre positif!", ephemeral=True)
            return
        if amount > 100:
            await interaction.response.send_message("❌ Maximum 100 messages à la fois!", ephemeral=True)
            return
        
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f'✅ **{len(deleted)}** messages supprimés!', ephemeral=True)

    @app_commands.command(name="kick", description="Expulser un utilisateur (Admin)")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        if member == interaction.user:
            await interaction.response.send_message("❌ Tu ne peux pas t'expulser toi-même!", ephemeral=True)
            return
        
        reason = reason or "Aucune raison spécifiée"
        embed = discord.Embed(
            title="⚠️ Expulsion",
            description=f"{member.mention} a été expulsé",
            color=discord.Color.orange()
        )
        embed.add_field(name="Raison", value=reason)
        embed.add_field(name="Modérateur", value=interaction.user.mention)
        
        await member.kick(reason=reason)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ban", description="Bannir un utilisateur (Admin)")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        if member == interaction.user:
            await interaction.response.send_message("❌ Tu ne peux pas te bannir toi-même!", ephemeral=True)
            return
        
        reason = reason or "Aucune raison spécifiée"
        embed = discord.Embed(
            title="🚫 Bannissement",
            description=f"{member.mention} a été banni",
            color=discord.Color.red()
        )
        embed.add_field(name="Raison", value=reason)
        embed.add_field(name="Modérateur", value=interaction.user.mention)
        
        await member.ban(reason=reason)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unban", description="Débannir un utilisateur (Admin)")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, member_name: str):
        bans = [entry async for entry in interaction.guild.audit_logs(action=discord.AuditLogAction.ban)]
        
        for entry in bans:
            if entry.target.name.lower() == member_name.lower():
                await interaction.guild.unban(entry.target)
                await interaction.response.send_message(f"✅ {entry.target.mention} a été débanni!", ephemeral=True)
                return
        
        await interaction.response.send_message("❌ Utilisateur non trouvé dans les bannissements!", ephemeral=True)

    @app_commands.command(name="mute", description="Rendre muet un utilisateur (Admin)")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: int = None):
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        
        if not muted_role:
            muted_role = await interaction.guild.create_role(name="Muted")
        
        await member.add_roles(muted_role)
        embed = discord.Embed(
            title="🔇 Mute",
            description=f"{member.mention} a été mute",
            color=discord.Color.greyple()
        )
        if duration:
            embed.add_field(name="Durée", value=f"{duration} secondes")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="unmute", description="Retirer le mute d'un utilisateur (Admin)")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        
        if muted_role and muted_role in member.roles:
            await member.remove_roles(muted_role)
            await interaction.response.send_message(f"✅ {member.mention} a été unmute!", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ {member.mention} n'est pas mute!", ephemeral=True)

    @app_commands.command(name="serverinfo", description="Informations du serveur")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
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
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="userinfo", description="Informations d'un utilisateur")
    async def userinfo(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user
        embed = discord.Embed(
            title=f"👤 {user}",
            color=discord.Color.blue()
        )
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Mention", value=user.mention, inline=True)
        embed.add_field(name="Compte créé", value=user.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Bot?", value="✅ Oui" if user.bot else "❌ Non", inline=True)
        
        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="roleinfo", description="Informations d'un rôle")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
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
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="channelinfo", description="Informations d'un salon")
    async def channelinfo(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        channel = channel or interaction.channel
        embed = discord.Embed(
            title=f"#️⃣ {channel.name}",
            color=discord.Color.purple()
        )
        embed.add_field(name="ID", value=channel.id, inline=True)
        embed.add_field(name="Type", value="Texte", inline=True)
        embed.add_field(name="Créé le", value=channel.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Sujet", value=channel.topic or "Aucun", inline=False)
        embed.add_field(name="NSFW", value="✅ Oui" if channel.is_nsfw() else "❌ Non", inline=True)
        
        if channel.slowmode_delay > 0:
            embed.add_field(name="Mode lent", value=f"{channel.slowmode_delay}s", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="stats", description="Statistiques du bot")
    async def stats(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📈 Statistiques du Bot",
            color=discord.Color.green()
        )
        embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Serveurs", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Utilisateurs", value=len(self.bot.users), inline=True)
        embed.add_field(name="Extensions chargées", value=len(self.bot.cogs), inline=True)
        embed.add_field(name="Version", value="1.0.0", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)



async def setup(bot):
    await bot.add_cog(AllSlashCommands(bot))
