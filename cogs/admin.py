import interactions
import json
import database
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client

class Admin(interactions.Extension):
    def __init__(self, bot) -> None:
        self.bot: interactions.Client = bot
        self.client: Client = Client("https://api.devnet.solana.com")

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

        return await ctx.send(f"Your wallet address is ``{db.wallet_pubkey}``.\nit currently has ``{json.loads(self.client.get_balance(Pubkey.from_string(db.wallet_pubkey)).to_json())['result']['value']/1000000000}`` SOL.")

def setup(bot: interactions.Client):
    Admin(bot)