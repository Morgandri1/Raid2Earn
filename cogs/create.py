import interactions
import utils.allow as allow
from utils.base import get_token_opts, requirements
from utils.t import get_token_identifiers
from solana.rpc.async_api import AsyncClient
import json
from datetime import timedelta, datetime
import os
from solders.pubkey import Pubkey
import database

class create(interactions.Extension):
    def __init__(self, bot) -> None:
        self.bot: interactions.Client = bot
        self.client: AsyncClient = AsyncClient("https://api.mainnet-beta.solana.com")

    async def step_3(self, ctx: interactions.ComponentContext):
        embed = interactions.Embed(
            title="Bounty Builder",
            description="Please select a payout token to create a bounty."
        )
        return await ctx.send(embeds=embed, components=[
            interactions.SelectMenu(
                custom_id="token",
                placeholder="Select a token",
                options=await get_token_opts(int(ctx.guild_id), self.client)
                )
        ], ephemeral=True)

    @interactions.extension_command(
        name="create",
        description="Create a new bounty",
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
        scope=allow.get_allowed(),
        options=[
            interactions.Option(
                name="info",
                description="The info of the bounty in a short blurb",
                type=interactions.OptionType.STRING,
                required=True
            ),
            interactions.Option(
                name="duration",
                description="The duration of the bounty in hours",
                type=interactions.OptionType.NUMBER,
                required=True
            ),
            interactions.Option(
                name="link",
                description="The link to the tweet",
                type=interactions.OptionType.STRING,
                required=True
            ),
            interactions.Option(
                name="reward",
                description="The number of the given token to reward",
                type=interactions.OptionType.NUMBER,
                required=True
            ),
            interactions.Option(
                name="requirement",
                description="The requirement for the bounty",
                type=interactions.OptionType.INTEGER,
                required=True,
                choices=[
                    interactions.Choice(name="Like", value=1),
                    interactions.Choice(name="Follow", value=2),
                    interactions.Choice(name="Retweet", value=3),
                    interactions.Choice(name="Like + Retweet", value=4),
                    interactions.Choice(name="Follow + Retweet", value=5),
                    interactions.Choice(name="Like + Follow", value=6),
                    interactions.Choice(name="Like + Follow + Retweet", value=7),
                    interactions.Choice(name="Like + Comment", value=8),
                    interactions.Choice(name="Follow + Comment", value=9),
                    interactions.Choice(name="Like + Retweet + Comment", value=10),
                    interactions.Choice(name="Follow + Retweet + Comment", value=11),
                    interactions.Choice(name="Like + Follow + Retweet + Comment", value=12),
                ]
            ),
            interactions.Option(
                name="query",
                description="The query to search for in the replies",
                type=interactions.OptionType.STRING,
                required=False,
            )
        ]
    )
    async def create(self, ctx: interactions.CommandContext, info: str, duration: int, link: str, reward: int, requirement: int, query: str = None):
        if not os.path.exists(f"bounties/{ctx.guild_id}"):
            os.mkdir(f"bounties/{ctx.guild_id}")
        db = database.get_guild(ctx.guild_id)
        if db.wallet_pubkey == "None":
            return await ctx.send("Please create a wallet first with `/wallet`.", ephemeral=True)
        message = await self.step_3(ctx)
        data = {
            "info": info,
            "link": link,
            "reward": reward,
            "duration": duration,
            "ends": None,
            "message": None,
            "requirement": requirement,
            "token": None,
            "claimed": [],
            "symbol": None,
            "hashtag": query
        }
        with open(f"bounties/{ctx.guild_id}/{message.id}.json", "w") as f:
            json.dump(data, f)
        print(message.id)
        print("cum")
        return 

    @interactions.extension_component("token")
    async def token(self, ctx: interactions.ComponentContext, token: str):
        print(token)

        with open(f"bounties/{ctx.guild_id}/{ctx.message.id}.json", "r") as f:
            data = json.load(f)
        info = await self.client.get_account_info_json_parsed(Pubkey.from_string(token[0])) if token[0] != "SOL" else None
        mint = json.loads(info.to_json())["result"]["value"]["data"]["parsed"]["info"]["mint"]
        symbol = await get_token_identifiers(mint) if info else "SOL"
        data["token"] = token
        data["address"] = json.loads(info.to_json())["result"]["value"]["data"]["parsed"]["info"]["mint"] if info else "SOL"
        data["ends"] = (datetime.utcnow() + timedelta(hours=data["duration"])).timestamp()
        data["symbol"] = str(symbol[mint]["symbol"])
        with open(f"bounties/{ctx.guild_id}/{ctx.message.id}.json", "w") as f:
            json.dump(data, f)
        await ctx.edit(
            embeds=interactions.Embed(
                title="Bounty Builder",
                description="Would you like to publish this bounty?"
        ),
            components=[
                interactions.Button(
                    label="Publish",
                    custom_id="publish",
                    style=interactions.ButtonStyle.SUCCESS
                ),
                interactions.Button(
                    label="Cancel",
                    custom_id="cancel",
                    style=interactions.ButtonStyle.DANGER
                )
            ]
        )
    
    @interactions.extension_component("publish")
    async def publish(self, ctx: interactions.ComponentContext):
        with open(f"bounties/{ctx.guild_id}/{ctx.message.id}.json", "r") as f:
            data = json.load(f)
        embed = interactions.Embed(
            title="New bounty!",
            description=f"Info: {data['info']}\nReward: {data['reward']} {data['symbol']}\nRequirement: {requirements[data['requirement']]}\nDuration: {data['duration']} hours\nEnds: {datetime.fromtimestamp(data['ends'])}" + (f"\nComment: {data['hashtag']}" if data["hashtag"] else "")
        )
        old = ctx.message.id
        message = await ctx.send(
            embeds=embed,
            components=[
                interactions.Button(
                    label="Start",
                    style=interactions.ButtonStyle.LINK,
                    url=data["link"]
                ),
                interactions.Button(
                    label="Claim",
                    custom_id="claim",
                    style=interactions.ButtonStyle.SUCCESS
                )
            ]
        )
        os.rename(f"bounties/{ctx.guild_id}/{old}.json", f"bounties/{ctx.guild_id}/{message.id}.json")
        print(message.id)
        print(ctx.message.id)
        data["message"] = int(message.id)
        with open(f"bounties/{ctx.guild_id}/{message.id}.json", "w") as f:
            json.dump(data, f)

def setup(bot):
    create(bot)

"""
Twitter auth:
API key: 6S95rFVeMrTrujpRzNwtm0H2R
API Key Secret: I523YG6LyaCS8tvBK0Nc2fAT4WlJ9Uqyr8g9Pe7pl4HzoIXjCH
Access token: 1489800636954812422-AJ43VA2dcKa1CkICu6F6n3m51ZaGok
Access token Secret: jPwcIWHrGL1QdT2R1tmt5Op8ZT4IPJouQUBSDlandfDad
Client Secret: -b7tOVzUSyy7p2KtZI45YQAvm5IUlprh1WaAA4uE6Bj9Vz3-Ei
Client ID: SVMteXNrMFRIUHdxM0k2VFZmOHU6MTpjaQ

"""