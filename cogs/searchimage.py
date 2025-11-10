import discord
from discord.ext import commands
from bing_image_downloader import downloader
import os
import logging

logger = logging.getLogger(__name__)

class SearchImage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='searchimage')
    async def search_image(self, ctx, *, query):
        if not query or len(query.strip()) == 0:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Veuillez fournir un nom/prénom",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        loading_embed = discord.Embed(
            title="🔍 Recherche en cours...",
            description=f"Recherche d'images pour: **{query}**",
            color=discord.Color.blue()
        )
        loading_msg = await ctx.send(embed=loading_embed)

        try:
            download_dir = f"./image_downloads/{query.replace(' ', '_')}"
            
            downloader.download(
                query,
                limit=5,
                output_dir="image_downloads",
                adult_filter_off=False,
                force_replace=False,
                timeout=15
            )

            image_folder = os.path.join(download_dir)
            
            if os.path.exists(image_folder):
                images = [f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
                
                if images:
                    embed = discord.Embed(
                        title=f"🖼️ Images trouvées pour: {query}",
                        description=f"**{len(images)} image(s)** trouvée(s)",
                        color=discord.Color.green()
                    )
                    
                    for i, image in enumerate(images[:3], 1):
                        image_path = os.path.join(image_folder, image)
                        try:
                            await ctx.send(file=discord.File(image_path))
                        except:
                            pass
                    
                    await loading_msg.edit(embed=embed)
                else:
                    error_embed = discord.Embed(
                        title="❌ Aucune image trouvée",
                        description=f"Pas de résultats pour: **{query}**",
                        color=discord.Color.red()
                    )
                    await loading_msg.edit(embed=error_embed)
            else:
                error_embed = discord.Embed(
                    title="❌ Erreur",
                    description="Impossible de télécharger les images",
                    color=discord.Color.red()
                )
                await loading_msg.edit(embed=error_embed)

        except Exception as e:
            logger.error(f"Erreur searchimage: {e}")
            error_embed = discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur est survenue: {str(e)[:100]}",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=error_embed)

async def setup(bot):
    await bot.add_cog(SearchImage(bot))
