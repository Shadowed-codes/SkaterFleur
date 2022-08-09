import helpers.constants as constants
import discord

from io import BytesIO
from main import SkaterFleur
from datetime import datetime
from discord.ext import commands
from helpers.bases import ModmailEndView
from .other.errors import NotModmailChannel
from .other.classes import Transcript


class Modmail(commands.Cog):
    def __init__(self, bot: SkaterFleur):
        self.bot = bot

    async def cog_load(self) -> None:
        if not getattr(self.bot, "modmail_tickets", None):
            setattr(self.bot, "modmail_tickets", dict())
        if not getattr(self.bot, "modmail_transcripts", None):
            setattr(self.bot, "modmail_transcripts", dict())

    async def user_in_session(self, user: discord.User) -> bool:
        """Checks if user has a modmail session running."""
        return user.id in self.bot.modmail_tickets.keys()

    async def create_new_session(
        self, user: discord.User, initial_msg: discord.Message
    ) -> None:
        """Creates a new channel thread"""
        # *  create transcript
        self.bot.modmail_transcripts[user.id] = Transcript(user)
        tr = self.get_user_transcript(user)
        tr.add_message(initial_msg)

        # *  create a channel
        cat: discord.CategoryChannel = discord.utils.find(
            lambda m: m.id == constants._MODMAIL_CATEGORY_ID,
            self.bot.get_all_channels(),
        )
        ticket_chnl: discord.TextChannel = await cat.create_text_channel(
            name=f"{user.id}-ticket"
        )
        self.bot.modmail_tickets[user.id] = ticket_chnl.id

        await user.send(
            embed=discord.Embed(
                title="Modmail ticket created",
                color=0x2F3136,
                description=f"A modmail ticket has been created for you, the staff team will get back to you as soon as possible, please be patient.\n\n**Your Message**: {initial_msg.content}",
                timestamp=discord.utils.utcnow(),
            ).set_footer(text="Your messages will be logged, be nice!")
        )

        await ticket_chnl.send(
            embed=discord.Embed(
                title=f"New modmail from {user}",
                description=initial_msg.content,
                color=0x2F3136,
                timestamp=discord.utils.utcnow(),
            ).set_footer(text="Your messages will be logged, be nice!")
        )

    def get_session_channel(self, user: discord.User) -> discord.TextChannel:
        return self.bot.get_channel(self.bot.modmail_tickets[user.id])

    async def generate_end_logs(
        self,
        user: discord.User,
        reason: str,
        closing_time: datetime,
    ) -> discord.Message:
        # * get the transcript
        tr: Transcript = self.get_user_transcript(user)

        tr_file = tr.file_export()

        em = discord.Embed(title="Ticket Closed", color=0x2F3136)
        em.add_field(name="Author", value=user, inline=True)
        em.add_field(name="Reason", value=reason, inline=True)
        em.add_field(
            name="Closing Time",
            value=discord.utils.format_dt(closing_time, "f"),
            inline=True,
        )

        ch = self.bot.get_channel(constants._MODMAIL_LOGS_ID)
        return await ch.send(embed=em, file=tr_file)

    def get_user_transcript(self, user: discord.User) -> Transcript:
        tr: Transcript = self.bot.modmail_transcripts[user.id]
        return tr

    async def clear_user_tickets(self, user: discord.User) -> None:
        try:
            del self.bot.modmail_tickets[user.id]
        except:
            pass
        try:
            del self.bot.modmail_transcripts[user.id]
        except:
            pass

    @commands.Cog.listener("on_message")
    async def modmail_(self, message: discord.Message):
        if message.author.bot:
            return
        if message.guild:
            if message.channel.id in self.bot.modmail_tickets.values():
                if message.content.startswith("-"):
                    return
                for k, v in self.bot.modmail_tickets.items():
                    if v == message.channel.id:

                        # * adds to transcript
                        receiver: discord.User = self.bot.get_user(k)
                        tr: Transcript = self.get_user_transcript(receiver)
                        tr.add_message(message)

                        # * dms the user
                        await receiver.send(
                            "**Atachments below:**" if message.attachments else "",
                            embed=discord.Embed(
                                description=message.content,
                                color=0x2F3136,
                                timestamp=discord.utils.utcnow(),
                            ).set_author(
                                name=message.author,
                                icon_url=message.author.avatar.url
                                if message.author.avatar.url
                                else "",
                            ),
                            files=[
                                discord.File(BytesIO(await m.read()), m.filename)
                                for m in message.attachments
                            ],
                        )
                        await message.add_reaction("📨")
                        return
            else:
                return

        if not await self.user_in_session(message.author):
            await self.create_new_session(message.author, message)
        else:
            # * add to transcript
            tr: Transcript = self.get_user_transcript(message.author)
            tr.add_message(message)

            # * send to bound channel
            ch = self.get_session_channel(message.author)
            await ch.send(
                "**Atachments below:**" if message.attachments else "",
                embed=discord.Embed(
                    timestamp=discord.utils.utcnow(),
                    description=message.content,
                    color=0x2F3136,
                ).set_author(
                    name=message.author,
                    icon_url=message.author.avatar.url
                    if message.author.avatar.url
                    else "",
                ),
                files=[
                    discord.File(BytesIO(await m.read()), m.filename)
                    for m in message.attachments
                ],
            )
            await message.add_reaction("📨")

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def close(self, ctx: commands.Context, *, reason: str = "Resolved"):
        """Close a modmail ticket."""
        if (
            ctx.channel.id in ctx.bot.modmail_tickets.values()
            and ctx.channel.name.endswith("-ticket")
        ):
            usr_id = int(ctx.channel.name.rstrip("-ticket"))
            usr = self.bot.get_user(usr_id)

            logs = await self.generate_end_logs(usr, reason, discord.utils.utcnow())
            # * cleanup
            await self.clear_user_tickets(usr)

            await usr.send(
                embed=discord.Embed(
                    title="Modmail ticket closed",
                    description=f"The modmail ticket has been closed by a moderator.\n\n**Reason**: {reason}",
                    color=0x2F3136,
                    timestamp=discord.utils.utcnow(),
                )
            )

            em = discord.Embed(
                title="Support Team Controls",
                description="The ticket has been closed successfully.",
                color=0x2F3136,
            )

            await ctx.send(embed=em, view=ModmailEndView(logs.jump_url))

        else:
            raise NotModmailChannel(
                "This command can only be used in a modmail ticket channel."
            )

    @commands.command("anonymous-reply", aliases=["areply", "ar"])
    @commands.has_permissions(manage_channels=True)
    @commands.guild_only()
    async def areply(self, ctx: commands.Context, *, content: str):
        """Anonymously reply to the modmail ticket"""
        if (
            ctx.channel.id in ctx.bot.modmail_tickets.values()
            and ctx.channel.name.endswith("-ticket")
        ):
            usr_id = int(ctx.channel.name.rstrip("-ticket"))
            usr = self.bot.get_user(usr_id)
            tr = self.get_user_transcript(usr)

            tr.add_message(ctx.message)
            await usr.send(
                embed=discord.Embed(
                    description=content,
                    color=0x2F3136,
                    timestamp=discord.utils.utcnow(),
                ).set_author(
                    name="Anonymous#0000",
                    icon_url=constants.DISCORD_ICON_URL,
                )
            )
            await ctx.message.add_reaction("📨")

        else:
            raise NotModmailChannel(
                "This command can only be used in a modmail ticket channel."
            )

    @commands.command()
    @commands.is_owner()
    async def mmtd(self, ctx: commands.Context):
        """Check modmail ticket dict"""
        await ctx.send(str(self.bot.modmail_tickets))


async def setup(bot: SkaterFleur):
    await bot.add_cog(Modmail(bot))
