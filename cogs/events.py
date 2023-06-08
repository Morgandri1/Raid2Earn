import interactions
from utils.base import _transfer, parse, preflight
import user_db
import json
import os
import tweepy
from solana.rpc.async_api import AsyncClient as Client
from solders.pubkey import Pubkey

class Events(interactions.Extension):
    def __init__(self, bot) -> None:
        # self.bot: interactions.Client = bot
        self.client: tweepy.Client = tweepy.Client(bearer_token=r"AAAAAAAAAAAAAAAAAAAAAJDQfAEAAAAAunT6NcW8O8TdjpU1%2BhI%2F9kvSM68%3DkyCmgJCWkDnnm2wNHo6PWPYRWSaKNI6bAtwNa4QcRPEGZtb8lm")
        self.sol: Client = Client("https://api.mainnet-beta.solana.com")

    def check_replies(self, tweet_ID, author: str, query: str = None):
        """
        author should be username, not user id.
        """
        if not query.startswith('"'):
            '"' + query
        if not query.endswith('"'):
            query + '"'  
        query = f'conversation_id:{tweet_ID} from:{author} ("{query if query != None else " "}") is:reply'
        print(query)
        replies = self.client.search_recent_tweets(query=query)
        return replies

    @interactions.extension_component("claim")
    async def claim(self, ctx: interactions.ComponentContext):
        await ctx.defer(ephemeral=True)
        try:
            with open(f"bounties/{ctx.guild_id}/{ctx.message.id}.json", "r") as f:
                bounty = json.load(f)
        except FileNotFoundError:
            await ctx.message.delete()
            return await ctx.send("this bounty does not exist.", ephemeral=True)

        if await preflight(self, ctx, ctx.guild, bounty["token"][0]) == 1:
            return await ctx.send("The wallet does not have enough SOL to pay the bounty. please alert an admin, and check back later.", ephemeral=True)
        elif await preflight(self, ctx, ctx.guild, bounty["token"][0]) == 2:
            os.remove(f"bounties/{ctx.guild_id}/{ctx.message.id}.json")
            await ctx.edit("``This bounty has ended.``")
            await ctx.disable_all_components()
            return await ctx.send("The bounty has expired.", ephemeral=True)

        db = user_db.get_user(ctx.author.id)
        if db.Uid == "None":
            await ctx.send("You have not linked your twitter yet.", ephemeral=True)
            return
        elif ctx.author.id in bounty["claimed"]:
            await ctx.send("You have already claimed this bounty.", ephemeral=True)
            return
        
        data = None
        data2 = None # this is for multiple requirements, we'll use it for doubling up.
        comments = None

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
        elif bounty["requirement"] == 8:
            data = tweepy.Paginator(self.client.get_liking_users, str(bounty["link"]).split("?")[0].split("/")[-1])
            comments = self.check_replies(str(bounty["link"]).split("?")[0].split("/")[-1], db.username, bounty["hashtag"] if bounty["hashtag"] != None else None)
        elif bounty["requirement"] == 9:
            data = tweepy.Paginator(self.client.get_users_followers, self.client.get_user(username=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).data.id)
            comments = self.check_replies(str(bounty["link"]).split("?")[0].split("/")[-1], db.username, bounty["hashtag"] if bounty["hashtag"] != None else None)
        elif bounty["requirement"] == 10:
            data = tweepy.Paginator(self.client.get_liking_users, str(bounty["link"]).split("?")[0].split("/")[-1])
            data2 = tweepy.Paginator(self.client.get_retweeters, str(bounty["link"]).split("?")[0].split("/")[-1])
            comments = self.check_replies(str(bounty["link"]).split("?")[0].split("/")[-1], db.username, bounty["hashtag"] if bounty["hashtag"] != None else None)
        elif bounty["requirement"] == 11:
            data = tweepy.Paginator(self.client.get_users_followers, self.client.get_user(username=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).data.id)
            data2 = tweepy.Paginator(self.client.get_retweeters, str(bounty["link"]).split("?")[0].split("/")[-1])
            comments = self.check_replies(str(bounty["link"]).split("?")[0].split("/")[-1], db.username, bounty["hashtag"] if bounty["hashtag"] != None else None)
        elif bounty["requirement"] == 7: # this is the only one with 3, so itll be handled independently
            followers = tweepy.Paginator(self.client.get_users_followers, self.client.get_user(username=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).data.id)
            likes = tweepy.Paginator(self.client.get_liking_users, str(bounty["link"]).split("?")[0].split("/")[-1])
            retweets = tweepy.Paginator(self.client.get_retweeters, str(bounty["link"]).split("?")[0].split("/")[-1])
            if await parse(followers, bounty, db, ctx) and await parse(likes, bounty, db, ctx) and await parse(retweets, bounty, db, ctx):
                await _transfer(bounty["reward"], db.Wallet, ctx.guild.id, self.sol, token=Pubkey.from_string(bounty["token"][0]) if bounty["token"][0] != "SOL" else None, token_address=Pubkey.from_string(bounty["address"]) if bounty["address"] != None else None)
                return await ctx.send("You have claimed this bounty!", ephemeral=True)
            else:
                return await ctx.send("You have not fufilled the requirement(s).", ephemeral=True)
        elif bounty["requirement"] == 12: # this is the only one with 4, so it'll also be handled independently
            followers = tweepy.Paginator(self.client.get_users_followers, self.client.get_user(username=(bounty["link"].split("twitter.com/")[-1].split("/")[0])).data.id)
            likes = tweepy.Paginator(self.client.get_liking_users, str(bounty["link"]).split("?")[0].split("/")[-1])
            retweets = tweepy.Paginator(self.client.get_retweeters, str(bounty["link"]).split("?")[0].split("/")[-1])
            comments = self.check_replies(str(bounty["link"]).split("?")[0].split("/")[-1], db.username, bounty["hashtag"] if bounty["hashtag"] != None else None)
            if await parse(followers, bounty, db, ctx) and await parse(likes, bounty, db, ctx) and await parse(retweets, bounty, db, ctx) and (comments.meta.get("result_count", 0) >= 1):
                await _transfer(bounty["reward"], db.Wallet, ctx.guild.id, self.sol, token=Pubkey.from_string(bounty["token"][0]) if bounty["token"][0] != "SOL" else None, token_address=Pubkey.from_string(bounty["address"]) if bounty["address"] != None else None)
                return await ctx.send("You have claimed this bounty!", ephemeral=True)
            else:
                return await ctx.send("You have not fufilled the requirement(s).", ephemeral=True)


        if data and not data2:
            if not await parse(data, bounty, db, ctx):
                return await ctx.send("You have not fufilled the requirement(s).", ephemeral=True)
        if data2 and data:
            if not any([await parse(data, bounty, db, ctx), await parse(data2, bounty, db, ctx)]): 
                return await ctx.send("You have not fufilled the requirement(s).", ephemeral=True)
        if comments and data and not data2:
            if not any([await parse(data, bounty, db, ctx), (comments.meta.get("result_count", 0) >= 1)]):
                return await ctx.send("You have not fufilled the requirement(s).", ephemeral=True)
        if comments and data2 and data:
            if not any([await parse(data, bounty, db, ctx), await parse(data2, bounty, db, ctx), (comments.meta.get("result_count", 0) >= 1)]):
                return await ctx.send("You have not fufilled the requirement(s).", ephemeral=True)
        
        await _transfer(bounty["reward"], db.Wallet, ctx.guild.id, self.sol, token=Pubkey.from_string(bounty["token"][0]) if bounty["token"][0] != "SOL" else None, token_address=Pubkey.from_string(bounty["address"]) if bounty["address"] != None else None)
        return await ctx.send("You have claimed this bounty!", ephemeral=True)

"https://twitter.com/eyekonnft/status/1627968700589436930"

def setup(bot):
    Events(bot)