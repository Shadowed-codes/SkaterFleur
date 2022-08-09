import discord
import os
import asyncio
import logging

from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


class SkaterFleur(commands.Bot):
    def __init__(self):
        super().__init__(
            status=discord.Status.do_not_disturb,
            intents=discord.Intents.all(),
            activity=discord.Game("DM me to contact staff."),
            owner_ids={767115163127906334, 925292379580268544},
            description="A bot for the server, 'Cosmo Control'",
            command_prefix=commands.when_mentioned_or("-"),
            case_insensitive=True,
            strip_after_prefix=True,
        )
        self.logger = logger

    async def setup_hook(self):
        print("Initally Loading all cogs...\n")
        await self.load_extension("jishaku")
        for f in os.listdir("./cogs"):
            if f.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{f[:-3]}")
                except commands.ExtensionFailed as e:
                    print(f"ExtentionFailed: {e.name}\n=> {str(e)}")
        print(f"=> Loaded {len(self.cogs)} cogs\n")

    async def reload_extension(self, *args, **kwargs) -> None:
        await super().reload_extension(*args, **kwargs)
        print(f"[!] Reloaded Cog {args[0]}")
        logger.info(f"[!] Reloaded Cog {args[0]}")

    async def load_extension(self, *args, **kwargs) -> None:
        await super().load_extension(*args, **kwargs)
        print(f"[!] Loaded Cog {args[0]}")
        logger.info(f"[!] Loaded Cog {args[0]}")

    async def unload_extension(self, *args, **kwargs) -> None:
        await super().unload_extension(*args, **kwargs)
        print(f"[!] Unloaded Cog {args[0]}")
        logger.info(f"[!] Unloaded Cog {args[0]}")

    async def start(self):
        await self.login(os.getenv("TOKEN"))
        print(f"Logged in as {self.user} [{self.user.id}]")
        await self.connect(reconnect=True)

    async def on_ready(self):
        print(f"Websocket connected, Listening to events.")
        pass

    async def close(self) -> None:
        print("Closing down bot...")
        return await super().close()


bot = SkaterFleur()


async def start():
    await bot.start()


if __name__ == "__main__":
    asyncio.run(start())
