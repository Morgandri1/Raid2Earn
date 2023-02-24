import interactions
import user_db
import json
import os
from datetime import timedelta, datetime
import tweepy
import database
from solathon.core.instructions import transfer
from solathon import Client, Transaction, PublicKey, Keypair

def parse(data, bounty, db: user_db.User, ctx, sol: Client) -> bool:
    """parses twitter Users list"""
    for user in data:
        if user["id"] == db.Uid:
            bounty["claimed"].append(ctx.author.id)
            db.Points += bounty["reward"]
            user_db.update()
            with open(f"bounties/{ctx.guild_id}/{ctx.message.id}.json", "w") as f:
                json.dump(bounty, f)
            return True
        else:
            continue
    return False

def _transfer(amount, wallet, guild, sol: Client):
    headers = [transfer(from_public_key=PublicKey(database.get_guild(guild).wallet_pubkey), to_public_key=PublicKey(wallet), lamports=int(amount*1000000000))]
    transaction = Transaction(instructions=headers, signers=[Keypair.from_private_key(database.get_guild(guild).wallet_secret)])
    result = sol.send_transaction(transaction)  
    return result

class Events(interactions.Extension):
    def __init__(self, bot) -> None:
        # self.bot: interactions.Client = bot
        self.client: tweepy.Client = tweepy.Client(bearer_token=r"AAAAAAAAAAAAAAAAAAAAAJDQfAEAAAAAunT6NcW8O8TdjpU1%2BhI%2F9kvSM68%3DkyCmgJCWkDnnm2wNHo6PWPYRWSaKNI6bAtwNa4QcRPEGZtb8lm")
        self.sol: Client = Client("https://api.devnet.solana.com")

    @interactions.extension_component("claim")
    async def claim(self, ctx: interactions.ComponentContext):
        if preflight(self, ctx, ctx.guild) == 1:
            return await ctx.send("The wallet does not have enough SOL to pay the bounty. please alert an admin, and check back later.", ephemeral=True)
        elif preflight(self, ctx, ctx.guild) == 2:
            os.remove(f"bounties/{ctx.guild_id}/{ctx.message.id}.json")
            await ctx.edit("``This bounty has ended.``")
            await ctx.disable_all_components()
            return await ctx.send("The bounty has expired.", ephemeral=True)
        elif preflight(self, ctx, ctx.guild) == 0:
            await ctx.message.delete()
            return await ctx.send("this bounty does not exist.", ephemeral=True)

        with open(f"bounties/{ctx.guild_id}/{ctx.message.id}.json", "r") as f:
            bounty = json.load(f)
        db = user_db.get_user(ctx.author.id)
        if db.Uid == "None":
            await ctx.send("You have not linked your twitter yet.", ephemeral=True)
            return
        elif ctx.author.id in bounty["claimed"]:
            await ctx.send("You have already claimed this bounty.", ephemeral=True)
            return
        
        data = None
        data2 = None # this is for multiple requirements, we'll use it for doubling up.

        if bounty["requirement"] == 1:
            data = tweepy.Paginator(self.client.get_liking_users, str(bounty["link"]).split("?")[0].split("/")[-1])
        elif bounty["requirement"] == 2:
            data = self.client.get_users_followers(self.client.get_user(username=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).data.id).data
        elif bounty["requirement"] == 3:
            data = self.client.get_retweeters(str(bounty["link"]).split("?")[0].split("/")[-1]).data
        elif bounty["requirement"] == 4:
            data = self.client.get_liking_users(str(bounty["link"]).split("?")[0].split("/")[-1]).data
            data2 = self.client.get_retweeters(str(bounty["link"]).split("?")[0].split("/")[-1]).data
        elif bounty["requirement"] == 5:
            data = self.client.get_users_followers(self.client.get_user(username=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).data.id).data
            data2 = self.client.get_retweeters(str(bounty["link"]).split("?")[0].split("/")[-1]).data
        elif bounty["requirement"] == 6:
            data = self.client.get_users_followers(self.client.get_user(username=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).data.id).data
            data2 = self.client.get_liking_users(str(bounty["link"]).split("?")[0].split("/")[-1]).data
        elif bounty["requirement"] == 7: # this is the only one with 3, so itll be handled independently
            followers = self.client.get_users_followers(self.client.get_user(username=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).data.id).data
            likes = self.client.get_liking_users(str(bounty["link"]).split("?")[0].split("/")[-1]).data
            retweets = self.client.get_retweeters(str(bounty["link"]).split("?")[0].split("/")[-1]).data
            if parse(followers, bounty, db, ctx, self.sol) and parse(likes, bounty, db, ctx, self.sol) and parse(retweets, bounty, db, ctx, self.sol):
                _transfer(bounty["reward"], db.Wallet, ctx.guild.id, self.sol)
                return await ctx.send("You have claimed this bounty!", ephemeral=True)
            else:
                return await ctx.send("You have not fufilled the requirement(s).", ephemeral=True)

        if data2:
            if parse(data, bounty, db, ctx, self.sol) and parse(data2, bounty, db, ctx, self.sol):
                _transfer(bounty["reward"], db.Wallet, ctx.guild.id, self.sol)
                return await ctx.send("You have claimed this bounty!", ephemeral=True)
            return await ctx.send("You have not fufilled the requirement(s).", ephemeral=True)
        else:
            if parse(data, bounty, db, ctx, self.sol):
                _transfer(bounty["reward"], db.Wallet, ctx.guild.id, self.sol)
                return await ctx.send("You have claimed this bounty!", ephemeral=True)
            return await ctx.send("You have not fufilled the requirement(s).", ephemeral=True)

"https://twitter.com/eyekonnft/status/1627968700589436930"

def setup(bot):
    Events(bot)

def preflight(cls: Events, ctx: interactions.ComponentContext, guild: interactions.Guild):
    """checks if the message is a bounty message
    
    codes:
    0: not found
    1: Not enough SOL in payout wallet
    2: Bounty expired
    3: go
    """
    if not os.path.exists(f"bounties/{guild.id}/{ctx.message.id}.json"):
        return 0
    db = database.get_guild(guild.id)
    bal = int(cls.sol.get_balance(PublicKey(db.wallet_pubkey))["result"]["value"])
    print(bal)
    with open(f"bounties/{guild.id}/{ctx.message.id}.json", "r") as f:
        bounty = json.load(f)
    if datetime.now() >= datetime.fromtimestamp(bounty["ends"]):
        os.remove(f"bounties/{guild.id}/{ctx.message.id}.json")
        return 2
    if bal / 1000000000 < bounty["reward"]:
        return 1
    return 3