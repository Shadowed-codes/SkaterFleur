from discord.ext import commands


class NotModmailChannel(commands.errors.CommandError):
    """Not an modmail ticket channel."""

    pass
