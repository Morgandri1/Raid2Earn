import interactions
import json
import database
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from utils import allow
import interactions.ext.checks as checks
from utils.base import get_token_opts_universal

class Admin(interactions.Extension):
    def __init__(self, bot) -> None:
        self.bot: interactions.Client = bot
        self.client: AsyncClient = AsyncClient("https://api.mainnet-beta.solana.com")

    @interactions.extension_command(
        name="wallet",
        description="manage the wallet for the server's bounty payouts",
        default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    )
    async def wallet(self, ctx: interactions.CommandContext):
        db = database.get_guild(ctx.guild_id)
        if db.wallet_secret == "None":
            keypair: Keypair = Keypair()
            db.wallet_secret = json.dumps(keypair.to_json())
            db.wallet_pubkey = str(keypair.pubkey())
            database.update()
            keypair = None
            return await ctx.send(f"Your wallet has been created! Your address is `{db.wallet_pubkey}`.")
        bal = await self.client.get_balance(Pubkey.from_string(db.wallet_pubkey))
        bal = bal.to_json()
        d = await get_token_opts_universal(ctx.guild.id, self.client)
        d = "\n".join(d)
        return await ctx.send(f"Your wallet address is ``{db.wallet_pubkey}``.\nit currently has: \n``{json.loads(bal)['result']['value']/1000000000} SOL``,\n"+d)
    
    # @interactions.extension_command(
    #     name="billing",
    #     description="manage the billing for the server's bounty payouts and get info",
    #     default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    # )
    # async def billing(self, ctx: interactions.CommandContext):
    #     db = database.get_guild(ctx.guild_id)
    #     if allow.get_allowed(int(ctx.guild_id)):
    #         return await ctx.send("This server is currently on the paid plan.", ephemeral=True)
    #     else:
    #         return await ctx.send(f"This server is currently not on the paid plan. this is usually caused by too little SOL in your guild wallet on your billing date. your billing date is {}. if you put {} in your guild wallet (you can find the pubkey using ``/wallet``) and using ``/start``.", ephemeral=True) #todo: add billing date, price
        
    # @interactions.extension_command(
    #     name="start",
    #     description="start the billing for the server's bounty payouts",
    #     default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    #     scope=929905854734565397
    # )
    # async def start(self, ctx: interactions.CommandContext):
    #     db = database.get_guild(ctx.guild_id)
    #     if allow.get_allowed(int(ctx.guild_id)):
    #         return await ctx.send("This server is already on the paid plan.", ephemeral=True)
    #     else:
    #         allow.allow(int(ctx.guild_id))
    #         return await ctx.send("This server is now on the paid plan.", ephemeral=True)

    # @checks.is_owner()
    # @interactions.extension_command(
    #     name="allow",
    #     description="allow a user to use the bot",
    #     default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    #     options=[
    #         interactions.Option(
    #             name="guild",
    #             description="The guild to allow",
    #             type=interactions.OptionType.INTEGER,
    #             required=True
    #         ),
    #     ]
    # )
    # async def allow(self, ctx: interactions.CommandContext, guild: int):
    #     allow.allow(guild)
    #     return await ctx.send(f"Guild {guild} is now allowed to use the bot.", ephemeral=True)

def setup(bot: interactions.Client):
    Admin(bot)