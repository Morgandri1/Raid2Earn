import interactions
import user_db
# import database 
import os
import json
from datetime import timedelta, datetime, date 
import database
from solathon import Keypair, Client

class Admin(interactions.Extension):
    def __init__(self, bot) -> None:
        self.bot: interactions.Client = bot
        self.requirements = {
            1: "Like",
            2: "Follow",
            3: "Retweet",
            4: "Like + Retweet",
            5: "Follow + Retweet",
            6: "Like + Follow",
            7: "Like + Follow + Retweet"
        }
        self.client: Client = Client("https://api.devnet.solana.com")

    @interactions.extension_command(
        name="create",
        description="Create a new bounty",
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        options=[
            interactions.Option(
                name="info",
                description="The info of the bounty in a short blurb",
                type=interactions.OptionType.STRING,
                required=True,
            ),
            interactions.Option(
                name="requirement",
                description="The required steps to claim the bounty",
                type=interactions.OptionType.INTEGER,
                required=True,
                choices=[
                    interactions.Choice(name="Like", value=1),
                    interactions.Choice(name="Follow", value=2),
                    interactions.Choice(name="Retweet", value=3),
                    interactions.Choice(name="Like + Retweet", value=4),
                    interactions.Choice(name="Follow + Retweet", value=5),
                    interactions.Choice(name="Like + Follow", value=6),
                    interactions.Choice(name="Like + Follow + Retweet", value=7)
                ]
            ),
            interactions.Option(
                name="reward",
                description="SOL reward amount",
                type=interactions.OptionType.NUMBER,
                required=True,
            ),
            interactions.Option(
                name="duration",
                description="Duration of the bounty in hours",
                type=interactions.OptionType.NUMBER,
                required=True, 
            ),
            interactions.Option(
                name="link",
                description="Link to the bounty",
                type=interactions.OptionType.STRING,
                required=True,
            )
        ]
    )
    async def create(self, ctx: interactions.CommandContext, info: str, requirement: int, reward: int, duration: int, link: str):
        embed = interactions.Embed(
            title="New Bounty",
            description=f"{info}\nReward: {reward} SOL\nDuration: {duration} hours\nRequirement: {self.requirements[requirement]}",
            color=0x00FF00,
        )
        message = await ctx.send(embeds=embed, components=[interactions.Button(style=interactions.ButtonStyle.LINK, label="Start", url=link), interactions.Button(style=interactions.ButtonStyle.SUCCESS, label="Claim", custom_id="claim")])
        data = {
            "link": link,
            "reward": reward,
            "duration": duration,
            "ends": int((datetime.now() + timedelta(hours=duration)).timestamp()),
            "message": int(message.id),
            "requirement": requirement,
            "claimed": [],
        }
        if not os.path.exists(f"bounties/{ctx.guild_id}"):
            os.mkdir(f"bounties/{ctx.guild_id}")
        with open(f"bounties/{ctx.guild_id}/{message.id}.json", "w") as f:
            json.dump(data, fp=f)
        return

    @interactions.extension_command(
        name="wallet",
        description="manage the wallet for the server's bounty payouts",
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    )
    async def wallet(self, ctx: interactions.CommandContext):
        db = database.get_guild(ctx.guild_id)
        if db.wallet_secret == "None":
            keypair = Keypair()
            db.wallet_secret = str(keypair.private_key)
            db.wallet_pubkey = str(keypair.public_key)
            database.update()
            keypair = None
            return await ctx.send(f"Your wallet has been created! Your address is `{db.wallet_pubkey}`.")

        return await ctx.send(f"Your wallet address is ``{db.wallet_pubkey}``.\nit currently has ``{self.client.get_balance(db.wallet_pubkey)['result']['value']/1000000000}`` SOL.")

def setup(bot: interactions.Client):
    Admin(bot)