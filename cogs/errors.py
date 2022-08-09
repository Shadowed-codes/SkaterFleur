import discord
from discord.ext import commands

from main import SkaterFleur


class ErrorHandler(commands.Cog, command_attrs={"hidden": True}):
    def __init__(self, bot: SkaterFleur):
        self.bot = bot

    @commands.Cog.listener("on_command_error")
    async def err_handler(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.errors.CommandNotFound):
            pass
        else:
            await ctx.send(
                embed=discord.Embed(
                    color=0x2F3136, description=f"```\n{str(error)}\n```"
                )
            )


async def setup(bot: SkaterFleur):
    await bot.add_cog(ErrorHandler(bot))
