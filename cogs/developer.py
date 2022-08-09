import discord
import os

from helpers.bases import Confirmation
from main import SkaterFleur
from discord.ext import commands


class Developer(commands.Cog, command_attrs={"hidden": True}):
    def __init__(self, bot: SkaterFleur):
        self.bot: SkaterFleur = bot

    async def cog_before_invoke(self, ctx: commands.Context) -> bool:
        return ctx.author.id in self.bot.owner_ids

    @commands.group(name="dev", invoke_without_command=True)
    @commands.is_owner()
    async def dev(self, ctx: commands.Context):
        """Hidden developer only commands"""
        await ctx.send(
            f'Available: {", ".join([f"`{x.name}`" for x in self.dev.commands])}'
        )

    @dev.command("load", aliases=["l"])
    async def load(self, ctx: commands.Context, *exts: str):
        """Load cogs"""
        for ext in exts:
            try:
                await self.bot.load_extension(f"cogs.{ext}")
                await ctx.send(f"Loaded cogs.{ext}")
            except Exception as e:
                await ctx.send(
                    f"Error loading {e.name}" + "\n" + f"```py\n{str(e)}\n```"
                )
                continue

    @dev.command("unload", aliases=["u"])
    async def unload(self, ctx: commands.Context, *exts: str):
        """Unload cogs"""
        for ext in exts:
            try:
                if ext == "developer":
                    continue
                await self.bot.unload_extension(f"cogs.{ext}")
                await ctx.send(f"Loaded cogs.{ext}")
            except Exception as e:
                await ctx.send(
                    f"Error unloading {e.name}" + "\n" + f"```py\n{str(e)}\n```"
                )
                continue

    @dev.command("reload", aliases=["r"])
    async def reload(self, ctx: commands.Context, *exts: str):
        """Reload cogs"""
        for ext in exts:
            try:
                await self.bot.reload_extension(f"cogs.{ext}")
                await ctx.send(f"Reloaded cogs.{ext}")
            except Exception as e:
                await ctx.send(
                    f"Error reloading {e.name}" + "\n" + f"```py\n{str(e)}\n```"
                )
                continue

    @dev.command("reloadall", aliases=["ra"])
    async def reloadall(self, ctx: commands.Context):
        """Reload all cogs"""
        for ext in os.listdir("./cogs"):
            try:
                if ext.endswith(".py"):
                    await self.bot.reload_extension(f"cogs.{ext[:-3]}")
                    await ctx.send(f"Reloaded cogs.{ext}")
            except Exception as e:
                await ctx.send(
                    f"Error reloading {e.name}" + "\n" + f"```py\n{str(e)}\n```"
                )
                continue

    @dev.command("terminate", aliases=["shutdown", "kill", "t"])
    async def terminate(self, ctx: commands.Context):
        await ctx.send("Are you sure?", view=Confirmation(action=self.bot.close))


async def setup(bot: SkaterFleur):
    await bot.add_cog(Developer(bot))
