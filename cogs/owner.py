import discord

from discord.ext import commands
from .other.classes import InfoView


class Owner(commands.Cog, command_attrs={"hidden": True}):
    def __init__(self, bot):
        self.bot = bot

    async def cog_before_invoke(self, ctx) -> None:
        return ctx.author.id in self.bot.owner_ids

    @commands.command()
    @commands.is_owner()
    async def setup_persistent_info(
        self, ctx: commands.Context, chnl: discord.TextChannel
    ):
        em1 = discord.Embed(color=0x2F3136).set_image(
            url="https://cdn.discordapp.com/attachments/928172511135416370/990506764229308426/image03.jpg?width=1247&height=701"
        )
        em2 = (
            discord.Embed(
                color=0x2F3136,
                title="Welcome!",
                description="Thank you so much for joining Cosmo Control!\n> Hope you will have a great time here!\n> Click the buttons below to view the rules and information\n\n> If you've read the rules, then head over to <#927971790926532621> to chat!!\n\n<:reply:928200570936897608>`Note:` We follow Discord [ToS](https://discord.com/terms) and [Guidelines](https://discord.com/guidelines) and so should you! ;)",
            )
            .set_author(
                name="Cosmo Control",
                icon_url="https://cdn.discordapp.com/attachments/928172511135416370/990506763918921788/image02.gif",
            )
            .set_footer(text="- Cosmo Control Staff")
        )
        await chnl.send(embeds=[em1, em2], view=InfoView())

    @commands.command()
    async def test_em(self, ctx: commands.Context):

        a = "ec" - 3
        await ctx.send("done")


async def setup(bot):
    await bot.add_cog(Owner(bot))
