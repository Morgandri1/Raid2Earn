import interactions
import user_db
import json
import os
from datetime import timedelta, datetime
import tweepy

def parse(data, bounty, db, ctx) -> bool:
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

class Events(interactions.Extension):
    def __init__(self, bot) -> None:
        # self.bot: interactions.Client = bot
        self.client: tweepy.Client = tweepy.Client(bearer_token=r"AAAAAAAAAAAAAAAAAAAAAJDQfAEAAAAAunT6NcW8O8TdjpU1%2BhI%2F9kvSM68%3DkyCmgJCWkDnnm2wNHo6PWPYRWSaKNI6bAtwNa4QcRPEGZtb8lm")

    @interactions.extension_component("claim")
    async def claim(self, ctx: interactions.ComponentContext):
        with open(f"bounties/{ctx.guild_id}/{ctx.message.id}.json", "r") as f:
            bounty = json.load(f)
        db = user_db.get_user(ctx.author.id)
        if db.Username == None:
            await ctx.send("You have not linked your twitter yet.", ephemeral=True)
            return
        elif ctx.author.id in bounty["claimed"]:
            await ctx.send("You have already claimed this bounty.", ephemeral=True)
            return
        
        data = None
        data2 = None # this is for multiple requirements, we'll use it for doubling up.

        if bounty["requirement"] == 1:
            data = self.client.get_liking_users(bounty["link"].split("/")[-1].split("?")[0]).json()["data"]
        elif bounty["requirement"] == 2:
            data = self.client.get_users_followers(self.client.get_user(id=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).json()["data"]["id"]).json()["data"]
        elif bounty["requirement"] == 3:
            data = self.client.get_retweeters(bounty["link"].split("/")[-1].split("?")[0]).json()["data"]
        elif bounty["requirement"] == 4:
            data = self.client.get_liking_users(self.client.get_user(id=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).json()["data"]["id"]).json()["data"]
            data2 = self.client.get_retweeters(self.client.get_user(id=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).json()["data"]["id"]).json()["data"]
        elif bounty["requirement"] == 5:
            data = self.client.get_users_followers(self.client.get_user(id=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).json()["data"]["id"]).json()["data"]
            data2 = self.client.get_retweeters(self.client.get_user(id=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).json()["data"]["id"]).json()["data"]
        elif bounty["requirement"] == 6:
            data = self.client.get_users_followers(bounty["link"].split("/")[-1].split("?")[0]).json()["data"]
            data2 = self.client.get_liking_users(self.client.get_user(id=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).json()["data"]["id"]).json()["data"]
        elif bounty["requirement"] == 7: # this is the only one with 3, so itll be handled independently
            followers = self.client.get_users_followers(self.client.get_user(id=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).json()["data"]["id"]).json()["data"]
            likes = self.client.get_liking_users(self.client.get_user(id=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).json()["data"]["id"]).json()["data"]
            retweets = self.client.get_retweeters(self.client.get_user(id=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).json()["data"]["id"]).json()["data"]
            if parse(followers, bounty, db, ctx) and parse(likes, bounty, db, ctx) and parse(retweets, bounty, db, ctx):
                return await ctx.send("You have claimed this bounty!", ephemeral=True)
            else:
                return await ctx.send("You have not fufilled the requirement(s).", ephemeral=True)

        if data2:
            if parse(data, bounty, db, ctx) and parse(data2, bounty, db, ctx):
                return await ctx.send("You have claimed this bounty!", ephemeral=True)
            return await ctx.send("You have not fufilled the requirement(s).", ephemeral=True)
        else:
            if parse(data, bounty, db, ctx):
                return await ctx.send("You have claimed this bounty!", ephemeral=True)
            return await ctx.send("You have not fufilled the requirement(s).", ephemeral=True)

def setup(bot):
    Events(bot)