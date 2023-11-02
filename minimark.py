import disnake
from disnake.ext import commands


class MarketModal(disnake.ui.Modal):
    def __init__(self, arg):
        self.arg = arg  # arg - это аргумент, который передается в конструкторе класса RecruitementSelect
        components = [
            disnake.ui.TextInput(label="Ваше имя", placeholder="Введите ваше имя", custom_id="name"),
            disnake.ui.TextInput(label="как с вами связаться можно?", placeholder="Введите ТГ или оставьте прочерк",
                                 custom_id="info"),
        ]
        if self.arg == "Yapup(10000)":
            title = "купить Япупа"
        elif self.arg == "Mason(1000)":
            title = "Купить Масона"
        elif self.arg == "Black(100)":
            title = "Купить Чёрный ник"
        elif self.arg == "Yellow(100)":
            title = "Купить Жёлтый ник"
        else:
            title = "Купить Зелёный ник"
        super().__init__(title=title, components=components, custom_id="marketModal")

    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        name = interaction.text_values["name"]
        info = interaction.text_values["info"]
        embed = disnake.Embed(color=0x2F3136, title="Заявка отправлена!")
        embed.description = f"{interaction.author.mention}, Благодарим вас за **заявку**! " \
                            f"В ближайшее время мы рассмотрим вашу заявку на покупку роли и напишем вам по контактным данным."
        embed.set_thumbnail(url=interaction.author.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        channel = interaction.guild.get_channel(1169006637730779207)
        await channel.send(f"Заявка на покупку **{self.arg}** от **{name}**\n"
                           f" {interaction.author.mention}\n"
                           f" Также он указал информацию где с ним можно связаться: {info}")


class MarketSelect(disnake.ui.Select):
    def __init__(self):
        options = [
            disnake.SelectOption(label="Япуп(10000)", value="Yapup(10000)", description="Роль с правами, выделяет перед участниками"),
            disnake.SelectOption(label="Масон(1000)", value="Mason(1000)", description="Роль с правами, выдает закрытый доступ к каналу"),
            disnake.SelectOption(label="Чёрный цвет ника(100)", value="Black(100)", description="Изменяет цвет ника  на черный"),
            disnake.SelectOption(label="Жёлтый цвет ника(100)", value="Yellow(100)", description="Изменяет цвет ника на Жёлтый"),
            disnake.SelectOption(label="Зелёный цвет ника(100)", value="Green(100)", description="Изменяет цвет ника на зеленый"),
        ]
        super().__init__(
            placeholder="Выбери что ты хочешь купить", options=options, min_values=0, max_values=1, custom_id="market"
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        if not interaction.values:
            await interaction.response.defer()
        else:
            await interaction.response.send_modal(MarketModal(interaction.values[0]))


class Market(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistents_views_added = False

    @commands.slash_command()
    async def payment(self, ctx):
        view = disnake.ui.View()
        view.add_item(MarketSelect())
        embed = disnake.Embed(
            title="Выбери, что хочешь купить",
            color=disnake.Color.from_rgb(150, 86, 206)
        )
        await ctx.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_connect(self):
        if self.persistents_views_added:
            return

        view = disnake.ui.View(timeout=None)
        view.add_item(MarketSelect())
        self.bot.add_view(view,
                          message_id=1169012251739553994)  # Вставить ID сообщения, которое отправится после использования с команда !recruit


def setup(bot):
    bot.add_cog(Market(bot))
