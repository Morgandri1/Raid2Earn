import interactions
import user_db
# import database 
import os
import json
from datetime import timedelta, datetime

class Admin(interactions.Extension):
    def __init__(self, bot) -> None:
        self.bot: interactions.Client = bot

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
            description=f"{info}\nReward: {reward} SOL\nDuration: {duration} hours",
            color=0x00FF00,
        )
        message = await ctx.send(embeds=embed, components=[interactions.Button(style=interactions.ButtonStyle.PRIMARY, label="Start", url=link), interactions.Button(style=interactions.ButtonStyle.DANGER, label="Claim", custom_id="claim")])
        data = {
            "link": link,
            "reward": reward,
            "duration": duration,
            "ends": datetime.now() + timedelta(hours=duration),
            "message": message.id,
            "requirement": requirement,
            "claimed": [],
        }
        with open(f"bounties/{ctx.guild_id}/{message.id}.json", "w") as f:
            json.dump(data, fp=f)
        return
        
def setup(bot: interactions.Client):
    Admin(bot)