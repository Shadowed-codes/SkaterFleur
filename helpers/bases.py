import discord

from inspect import iscoroutinefunction
from discord.ui import View


class ModmailEndView(discord.ui.View):
    def __init__(self, jump_url: str):
        super().__init__(timeout=0)
        self.add_item(discord.ui.Button(url=jump_url, label="Logs", emoji="📝"))

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red, emoji="🗑")
    async def _delete(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer()
        await interaction.channel.delete()


class BaseEmbed(discord.Embed):
    def __init__(self, **kwargs):
        super().__init__(color=0x2F3136, **kwargs)


class Confirmation(View):
    state: bool

    def __init__(self, callback=None, *clbk_args, **clbk_kwargs):
        super().__init__(timeout=20)
        self.action = callback
        self.args_ = clbk_args
        self.kwargs_ = clbk_kwargs

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes_(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Confirmed", ephemeral=True)
        self.state = True

        if not self.action:
            if iscoroutinefunction(self.action):
                await self.action(*self.args_, **self.kwargs_)
            else:
                self.action(*self.args_, **self.kwargs_)

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no_(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelled", ephemeral=True)
        self.state = False
