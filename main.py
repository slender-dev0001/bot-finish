import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
import sqlite3

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

def get_prefix(bot, message):
    if not message.guild:
        return '+'
    
    try:
        conn = sqlite3.connect("server_config.db")
        cursor = conn.cursor()
        cursor.execute('SELECT prefix FROM server_config WHERE guild_id = ?', (message.guild.id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else '+'
    except:
        return '+'

def get_user_email(user_id, guild_id):
    try:
        conn = sqlite3.connect("email_system.db")
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM user_emails WHERE user_id = ? AND guild_id = ?', (user_id, guild_id))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except:
        return None

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@bot.event
async def on_ready():
    logger.info(f'✅ Bot connecté: {bot.user}')
    await bot.change_presence(activity=discord.Game(name="+help pour l'aide"))

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name="bienvenue")
    if channel:
        email = get_user_email(member.id, member.guild.id)
        embed = discord.Embed(
            title=f"👋 Bienvenue {member.name}!",
            description=f"{member.mention} a rejoint le serveur!",
            color=discord.Color.green()
        )
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Compte créé le", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="Bot?", value="✅ Oui" if member.bot else "❌ Non", inline=True)
        embed.add_field(name="Pseudo", value=member.display_name, inline=True)
        if email:
            embed.add_field(name="Email", value=email, inline=True)
        embed.add_field(name="Nombre de membres", value=f"👥 {member.guild.member_count}", inline=True)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.set_footer(text=f"Serveur: {member.guild.name}")
        await channel.send(embed=embed)

async def load_cogs():
    cogs_path = os.path.join(os.path.dirname(__file__), 'cogs')
    if not os.path.exists(cogs_path):
        os.makedirs(cogs_path)
    
    for filename in os.listdir(cogs_path):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            logger.info(f'✅ Cog chargé: {filename[:-3]}')

@bot.event
async def setup_hook():
    await load_cogs()
    try:
        synced = await bot.tree.sync()
        logger.info(f'✅ {len(synced)} slash commands synchronisés')
        for cmd in synced:
            logger.info(f'   - /{cmd.name}')
    except Exception as e:
        logger.error(f'❌ Erreur lors de la synchronisation: {e}')

def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("❌ DISCORD_TOKEN non trouvé dans .env")
    bot.run(token)

if __name__ == '__main__':
    main()
