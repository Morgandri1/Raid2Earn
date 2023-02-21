import interactions
import user_db
import tweepy
from requests import Response

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
            )
        ]
    )
    async def register(self, ctx: interactions.CommandContext, username: str):
        db = user_db.get_user(ctx.author.id)
        if db.Uid != "None":
            return await ctx.send("You are already registered!")
        data = self.client.get_user(username=username).json()["data"]["id"]
        db.Uid = data
        await ctx.send("You have been registered!")
        return user_db.update()

def setup(bot: interactions.Client):
    User(bot)