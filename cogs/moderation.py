import discord
from discord.ext import commands
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='clear')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount <= 0:
            await ctx.send("❌ Spécifie un nombre positif!")
            return
        if amount > 100:
            await ctx.send("❌ Maximum 100 messages à la fois!")
            return
        
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'✅ **{len(deleted) - 1}** messages supprimés!', delete_after=3)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Tu n'as pas la permission!")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Spécifie un nombre valide!")

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if member == ctx.author:
            await ctx.send("❌ Tu ne peux pas t'expulser toi-même!")
            return
        
        reason = reason or "Aucune raison spécifiée"
        embed = discord.Embed(
            title="⚠️ Expulsion",
            description=f"{member.mention} a été expulsé",
            color=discord.Color.orange()
        )
        embed.add_field(name="Raison", value=reason)
        embed.add_field(name="Modérateur", value=ctx.author.mention)
        
        await member.kick(reason=reason)
        await ctx.send(embed=embed)

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Tu n'as pas la permission de kick!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Mentionne un utilisateur!")

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        if member == ctx.author:
            await ctx.send("❌ Tu ne peux pas te bannir toi-même!")
            return
        
        reason = reason or "Aucune raison spécifiée"
        embed = discord.Embed(
            title="🚫 Bannissement",
            description=f"{member.mention} a été banni",
            color=discord.Color.red()
        )
        embed.add_field(name="Raison", value=reason)
        embed.add_field(name="Modérateur", value=ctx.author.mention)
        
        await member.ban(reason=reason)
        await ctx.send(embed=embed)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Tu n'as pas la permission de bannir!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Mentionne un utilisateur!")

    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member_name):
        bans = [entry async for entry in ctx.guild.audit_logs(action=discord.AuditLogAction.ban)]
        
        for entry in bans:
            if entry.target.name.lower() == member_name.lower():
                await ctx.guild.unban(entry.target)
                await ctx.send(f"✅ {entry.target.mention} a été débanni!")
                return
        
        await ctx.send("❌ Utilisateur non trouvé dans les bannissements!")

    @commands.command(name='mute')
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: int = None):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")
        
        await member.add_roles(muted_role)
        embed = discord.Embed(
            title="🔇 Mute",
            description=f"{member.mention} a été mute",
            color=discord.Color.greyple()
        )
        if duration:
            embed.add_field(name="Durée", value=f"{duration} secondes")
        
        await ctx.send(embed=embed)

    @commands.command(name='unmute')
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.send(f"✅ {member.mention} a été unmute!")
        else:
            await ctx.send(f"❌ {member.mention} n'est pas mute!")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
