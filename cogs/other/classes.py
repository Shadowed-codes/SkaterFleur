import discord

from discord.ui import View
from io import BytesIO, BufferedIOBase


class Transcript:
    def __init__(self, user: discord.User):
        self._messages = list()
        self._user = user

    def add_message(self, message: discord.Message, /):
        self._messages.append(message)

    def str_export(self) -> str:
        return (
            f"Ticket opened by {self._user} ({self._user.id})\nGenerated at: {discord.utils.utcnow().strftime('%d/%m/%Y %H:%M')}\n\n"
            + "\n".join(
                [
                    f'({m.created_at.strftime("%d/%m/%Y %H:%M")}) [{m.author.id}: {m.author}]: {m.content.replace("-ar", "[AR]")}'
                    for m in self._messages
                ]
            )
        )

    def buffer_export(self) -> BufferedIOBase:
        return BytesIO(bytes(self.str_export(), "utf-8"))

    def file_export(self) -> discord.File:
        return discord.File(self.buffer_export(), f"transcript_{self._user.id}.txt")


class InfoView(View):
    def __init__(self):
        super().__init__(timeout=20)

    @discord.ui.button(
        label="Rules",
        emoji="<:channel_rules:995606482240405514>",
        style=discord.ButtonStyle.gray,
        custom_id="P_Info:rules",
    )
    async def send_rules(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(embeds=[], ephemeral=True)
