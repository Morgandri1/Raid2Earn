import interactions
from utils.base import _transfer, parse, preflight
import user_db
import json
import os
import tweepy
from solana.rpc.api import Client

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
            data = tweepy.Paginator(self.client.get_users_followers, self.client.get_user(username=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).data.id)
        elif bounty["requirement"] == 3:
            data = tweepy.Paginator(self.client.get_retweeters, str(bounty["link"]).split("?")[0].split("/")[-1])
        elif bounty["requirement"] == 4:
            data = tweepy.Paginator(self.client.get_liking_users, str(bounty["link"]).split("?")[0].split("/")[-1])
            data2 = tweepy.Paginator(self.client.get_retweeters, str(bounty["link"]).split("?")[0].split("/")[-1])
        elif bounty["requirement"] == 5:
            data = tweepy.Paginator(self.client.get_users_followers, self.client.get_user(username=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).data.id)
            data2 = tweepy.Paginator(self.client.get_retweeters, str(bounty["link"]).split("?")[0].split("/")[-1])
        elif bounty["requirement"] == 6:
            data = tweepy.Paginator(self.client.get_users_followers, self.client.get_user(username=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).data.id)
            data2 = tweepy.Paginator(self.client.get_liking_users, str(bounty["link"]).split("?")[0].split("/")[-1])
        elif bounty["requirement"] == 7: # this is the only one with 3, so itll be handled independently
            followers = tweepy.Paginator(self.client.get_users_followers, self.client.get_user(username=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).data.id)
            likes = tweepy.Paginator(self.client.get_liking_users, str(bounty["link"]).split("?")[0].split("/")[-1])
            retweets = tweepy.Paginator(self.client.get_retweeters, str(bounty["link"]).split("?")[0].split("/")[-1])
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