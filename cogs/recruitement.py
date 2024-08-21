import disnake
from disnake.ext import commands


class RecruitementModal(disnake.ui.Modal):
    def __init__(self, arg):
        self.arg = arg  # arg - это аргумент, который передается в конструкторе класса RecruitementSelect
        components = [
            disnake.ui.TextInput(label="Ваше имя", placeholder="Введите ваше имя", custom_id="name"),
            disnake.ui.TextInput(label="Ваш возраст", placeholder="Введите ваш возраст", custom_id="age"),
            disnake.ui.TextInput(
                label="Расскажите о себе и почему именно вы?",
                placeholder="Расскажи о себе здесь",
                custom_id="info",
                style=disnake.TextInputStyle.paragraph,
                min_length=10,
                max_length=500,
            )
        ]
        if self.arg == "Designer":
            title = "Набор на должность Дизайнера"
        else:
            title = "Набор на должность разработчика"
        super().__init__(title=title, components=components, custom_id="recruitementModal")

    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        name = interaction.text_values["name"]
        age = interaction.text_values["age"]
        info = interaction.text_values["info"]
        embed = disnake.Embed(color=0x2F3136, title="Заявка отправлена!")
        embed.description = f"{interaction.author.mention}, Благодарим вас за **заявку**! " \
                            f"Если вы нам **подходите**, администрация **свяжется** с вами в ближайшее время."
        embed.set_thumbnail(url=interaction.author.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        channel = interaction.guild.get_channel(1047957934149226506)
        await channel.send(f"Заявка на должность {self.arg} от {name}\n"
                           f" {interaction.author.mention} ({age} лет). \n"
                           f" Также он указал информацию почему именно он должен стать {self.arg}: {info}")


class RecruitementSelect(disnake.ui.Select):
    def __init__(self):
        options = [
            disnake.SelectOption(label="Дезигнер", value="Designer", description="Если ты рисуешь или придумываешь"),
            disnake.SelectOption(label="Разработчик", value="Developer", description="Вы гений кажется"),
        ]
        super().__init__(
            placeholder="Выбери кем ты являешься", options=options, min_values=0, max_values=1, custom_id="recruitement"
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        if not interaction.values:
            await interaction.response.defer()
        else:
            await interaction.response.send_modal(RecruitementModal(interaction.values[0]))


class Recruitement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistents_views_added = False


    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Modal "Rec" connected')

    @commands.slash_command()
    async def recruit(self, ctx):
        view = disnake.ui.View()
        view.add_item(RecruitementSelect())
        # Тут можно добавть эмбед с описанием ролей
        await ctx.send('Выбери желаемую роль', view=view)

    @commands.Cog.listener()
    async def on_connect(self):
        if self.persistents_views_added:
            return

        view = disnake.ui.View(timeout=None)
        view.add_item(RecruitementSelect())
        self.bot.add_view(view,
                          message_id=1169004458278146078)  # Вставить ID сообщения, которое отправится после использования с команда !recruit


def setup(bot):
    bot.add_cog(Recruitement(bot))
