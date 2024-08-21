import disnake
from disnake.ext import commands
from config import settings

intents = disnake.Intents.all()

bot = commands.Bot(command_prefix=settings['PREFIX'], intents=intents)


@bot.event
async def on_ready():
    print(f"Bot {settings['NAME_BOT']}, is ready!")
bot.load_extension('cogs.SecretSanta')
bot.load_extension('cogs.Recruitement')
bot.load_extension('blockchain_old.BlockchainCog')

bot.run(settings['TOKEN'])
