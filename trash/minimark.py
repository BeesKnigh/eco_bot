import disnake
from disnake.ext import commands
import mysql.connector

# Определение функции для списания средств с баланса пользователя
def deduct_balance_from_db(user_id, cost):
    try:
        # Подключение к базе данных и создание курсора
        db_connection = mysql.connector.connect(
            host="127.0.0.1",
            user="beesknight",
            password="12341234",
            database="discord_jb",
            charset="utf8mb4"
        )
        cursor = db_connection.cursor()

        # Получить текущий баланс пользователя
        cursor.execute("SELECT balance FROM user WHERE iduser = %s", (user_id,))
        current_balance = cursor.fetchone()

        if current_balance is not None and current_balance[0] >= cost:
            # Если средств достаточно, списать средства
            new_balance = current_balance[0] - cost
            cursor.execute("UPDATE user SET balance = %s WHERE iduser = %s", (new_balance, user_id))
            db_connection.commit()
            return True
        else:
            # Недостаточно средств на балансе
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    finally:
        cursor.close()
        db_connection.close()


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
        user_id = interaction.author.id
        name = interaction.text_values["name"]
        info = interaction.text_values["info"]
        selected_option = interaction.custom_id  # Обновлено здесь
        cost = 0

        if selected_option == "Yapup(10000)":
            cost = 10000
            title = "купить Япупа"
        elif selected_option == "Mason(1000)":
            title = "Купить Масона"
            cost = 1000
        elif selected_option == "Black(100)":
            title = "Купить Чёрный ник"
            cost = 100
        elif selected_option == "Yellow(100)":
            title = "Купить Жёлтый ник"
            cost = 100
        elif selected_option == "Green(100)":
            title = "Купить Зелёный ник"
            cost = 100

        if cost > 0:
            if deduct_balance_from_db(user_id, cost):
                # Успешно списаны деньги, можно отправить сообщение об успешной заявке
                embed = disnake.Embed(color=0x2F3136, title="Заявка отправлена!")
                embed.description = f"{interaction.author.mention}, Благодарим вас за **заявку** на покупку {title}! " \
                                    f"В ближайшее время мы рассмотрим вашу заявку и напишем вам по контактным данным."
            else:
                # Недостаточно средств на балансе
                embed = disnake.Embed(color=0xFF0000, title="Ошибка при снятии средств")
                embed.description = f"{interaction.author.mention}, у вас недостаточно средств на балансе для покупки {title}."
        else:
            # Неизвестная опция
            embed = disnake.Embed(color=0xFF0000, title="Ошибка при снятии средств")
            embed.description = "Неизвестная опция."

        await interaction.response.send_message(embed=embed, ephemeral=True)
        channel = interaction.guild.get_channel(1169006637730779207)
        await channel.send(f"Заявка на покупку **{title}** от **{name}**\n"
                           f" {interaction.author.mention}\n"
                           f" Также он указал информацию, где с ним можно связаться: {info}")


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
