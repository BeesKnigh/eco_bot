import disnake
from disnake.ext import commands
import random


class GiftModal(disnake.ui.Modal):
    def __init__(self, recipient):
        self.recipient = recipient
        components = [
            disnake.ui.TextInput(label="Ваш подарок", custom_id="gift_message", style=disnake.TextInputStyle.paragraph)
        ]
        super().__init__(title="Отправка подарка", custom_id="send_gift_modal", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        gift_message = inter.text_values["gift_message"]
        await self.recipient.send(f"Вы получили подарок от вашего Тайного Санты: {gift_message}")
        await inter.send("Ваш подарок был отправлен!", ephemeral=True)


class SecretSanta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.participants = []
        self.santa_pairs = {}
        self.waiting_for_gift = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Modal "Santa" connected')

    @commands.slash_command(description='Присоединиться к "Тайному Санте"')
    async def join_santa(self, inter):
        if inter.author not in self.participants:
            self.participants.append(inter.author)
            embed = disnake.Embed(title="Тайный Санта", description=f"{inter.author.mention} присоединился к Тайному Санте!", color=0x00ff00)
            await inter.send(embed=embed)
        else:
            embed = disnake.Embed(title="Тайный Санта", description=f"{inter.author.mention}, вы уже участвуете!", color=0xff0000)
            await inter.send(embed=embed)

    @commands.slash_command()
    async def draw_santa(self, inter):
        if len(self.participants) < 2:
            embed = disnake.Embed(title="Тайный Санта", description="Недостаточно участников для Тайного Санты!", color=0xff0000)
            await inter.send(embed=embed)
            return

        random.shuffle(self.participants)
        for i in range(len(self.participants)):
            self.santa_pairs[self.participants[i]] = self.participants[(i + 1) % len(self.participants)]

        embed = disnake.Embed(title="Тайный Санта", description="Пары для Тайного Санты были распределены!", color=0x00ff00)
        await inter.send(embed=embed)
        for santa, recipient in self.santa_pairs.items():
            await santa.send(f"Вы Тайный Санта для {recipient.name}!")

    @commands.slash_command()
    async def send_gift(self, inter, recipient: disnake.Member):
        if inter.author in self.santa_pairs and self.santa_pairs[inter.author] == recipient:
            self.waiting_for_gift[inter.author.id] = recipient.id
            embed = disnake.Embed(title="Тайный Санта", description="Пожалуйста, отправьте ваш подарок (фотографию) в личные сообщения боту.", color=0x00ff00)
            await inter.send(embed=embed, ephemeral=True)
        else:
            embed = disnake.Embed(title="Тайный Санта", description="Вы не Тайный Санта для этого пользователя или вы не участвуете в Тайном Санте.", color=0xff0000)
            await inter.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None and message.author.id in self.waiting_for_gift:
            recipient_id = self.waiting_for_gift.pop(message.author.id)
            recipient = self.bot.get_user(recipient_id)
            if message.attachments:
                for attachment in message.attachments:
                    if attachment.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
                        await recipient.send(f"Вы получили подарок от вашего Тайного Санты:", file=await attachment.to_file())
                        embed = disnake.Embed(title="Тайный Санта", description="Ваш подарок был отправлен!", color=0x00ff00)
                        await message.author.send(embed=embed)
                        return
            await message.author.send("Пожалуйста, отправьте фотографию в правильном формате (png, jpg, jpeg, gif).")

    @commands.slash_command()
    async def participants_list(self, inter):
        if self.participants:
            participant_names = "\n".join([p.name for p in self.participants])
            embed = disnake.Embed(title="Участники Тайного Санты", description=participant_names, color=0x00ff00)
            await inter.send(embed=embed)
        else:
            embed = disnake.Embed(title="Тайный Санта", description="Нет участников для Тайного Санты.", color=0xff0000)
            await inter.send(embed=embed)

    @commands.slash_command()
    async def send_gift_modal(self, inter, recipient: disnake.Member):
        if inter.author in self.santa_pairs and self.santa_pairs[inter.author] == recipient:
            modal = GiftModal(recipient)
            await inter.send_modal(modal)
        else:
            embed = disnake.Embed(title="Тайный Санта", description="Вы не Тайный Санта для этого пользователя или вы не участвуете в Тайном Санте.", color=0xff0000)
            await inter.send(embed=embed)


def setup(bot):
    bot.add_cog(SecretSanta(bot))
