import disnake
from disnake.ext import commands
from config import settings

intents = disnake.Intents.all()

bot = commands.Bot(command_prefix=settings['PREFIX'], intents=intents)


@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready!")

bot.load_extension('cogs.secret_santa')
bot.load_extension('cogs.recruitement')

bot.run(settings['TOKEN'])
