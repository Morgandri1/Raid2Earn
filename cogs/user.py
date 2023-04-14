import interactions
import user_db
import tweepy

class User(interactions.Extension):
    def __init__(self, bot) -> None:
        self.bot: interactions.Client = bot
        self.client: tweepy.Client = tweepy.Client(bearer_token=r"AAAAAAAAAAAAAAAAAAAAAJDQfAEAAAAAunT6NcW8O8TdjpU1%2BhI%2F9kvSM68%3DkyCmgJCWkDnnm2wNHo6PWPYRWSaKNI6bAtwNa4QcRPEGZtb8lm")

    @interactions.extension_command(
        name="register",
        description="Register your account",
        options=[
            interactions.Option(
                name="username",
                description="Your twitter username",
                type=interactions.OptionType.STRING,
                required=True,
            ),
            interactions.Option(
                name="wallet",
                description="Your wallet address",
                type=interactions.OptionType.STRING,
                required=True,
            )
        ]
    )
    async def register(self, ctx: interactions.CommandContext, username: str, wallet: str):
        db = user_db.get_user(ctx.author.id)
        if db.Uid != "None":
            return await ctx.send("You are already registered!")
        data = self.client.get_user(username=username)
        db.Uid = data.data.id
        db.username = data.data.username
        db.Wallet = wallet
        await ctx.send("You have been registered!")
        return user_db.update()

    @interactions.extension_command(
        name="reg clear",
        description="Clear your registration so you can re-register",
    )
    async def reg_clear(self, ctx: interactions.CommandContext):
        db = user_db.get_user(ctx.author.id)
        if db.Uid == "None":
            return await ctx.send("You are not registered!")
        db.Uid = "None"
        db.username = "None"
        db.Wallet = "None"
        await ctx.send("You have been unregistered!")
        return user_db.update()

def setup(bot: interactions.Client):
    User(bot)