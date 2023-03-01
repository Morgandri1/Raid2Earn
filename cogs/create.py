import interactions
import utils.allow as allow
from utils.base import get_token_opts, requirements
from solana.rpc.api import Client
import json
from datetime import timedelta, datetime
import os
from solders.pubkey import Pubkey

class create(interactions.Extension):
    def __init__(self, bot) -> None:
        self.bot: interactions.Client = bot
        self.client: Client = Client("https://api.mainnet-beta.solana.com")

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
                    interactions.Choice(name="Like + Follow + Retweet", value=7)
                ]
            )
        ]
    )
    async def create(self, ctx: interactions.CommandContext, info: str, duration: int, link: str, reward: int, requirement: int):
        embed = interactions.Embed(
            title="Bounty Builder",
            description="Please select a payout token to create a bounty."
        )
        await ctx.send(embeds=embed, components=[
            interactions.SelectMenu(
                custom_id="token",
                placeholder="Select a token",
                options=get_token_opts(int(ctx.guild_id), self.client)
                )
        ], ephemeral=True)
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
        }
        with open(f"bounties/{ctx.guild_id}/{ctx.message.id}.json", "w") as f:
            json.dump(data, f)

    @interactions.extension_component("token")
    async def token(self, ctx: interactions.ComponentContext, token: str):
        with open(f"bounties/{ctx.guild_id}/{ctx.message.id}.json", "r") as f:
            data = json.load(f)
        data["token"] = token
        data["address"] = json.loads(self.client.get_account_info_json_parsed(Pubkey.from_string(token[0])).to_json())["result"]["value"]["data"]["parsed"]["info"]["mint"] if token[0] != "SOL" else None
        data["ends"] = (datetime.utcnow() + timedelta(hours=data["duration"])).timestamp()
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
            description=f"Info: {data['info']}\nReward: {data['reward']} {data['token'] if data['token'] == 'SOL' else ' '}\nRequirement: {requirements[data['requirement']]}\nDuration: {data['duration']} hours\nEnds: {datetime.fromtimestamp(data['ends'])}"
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