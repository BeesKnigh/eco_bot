import disnake
from disnake.ext import commands
from recruitement import Recruitement  # Путь к вашему файлу с когами
from config import settings
from minimark import Market
from register import Register
from blockchain import BlockchainCog

intents = disnake.Intents.all()

bot = commands.Bot(command_prefix=settings['PREFIX'], intents=intents)


@bot.event
async def on_ready():
    print(f"Bot {bot.user}, is ready!")
bot.add_cog(Register(bot))
bot.add_cog(Recruitement(bot))
bot.add_cog(Market(bot))
bot.add_cog(BlockchainCog(bot))

bot.run(settings['TOKEN'])
