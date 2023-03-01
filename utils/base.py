from solders.pubkey import Pubkey
from .t import *
import json
import os
import database
import user_db
from solana.rpc.api import Client
from datetime import datetime
import interactions

requirements = {
            1: "Like",
            2: "Follow",
            3: "Retweet",
            4: "Like + Retweet",
            5: "Follow + Retweet",
            6: "Like + Follow",
            7: "Like + Follow + Retweet"
        }

def parse(data, bounty, db: user_db.User, ctx) -> bool:
    """parses twitter Users list"""
    for sub in data:
        for user in sub:
            if isinstance(user, dict | None):
                continue
            for u in user:
                print(u)
                if db.username == str(u):
                    bounty["claimed"].append(int(ctx.author.id))
                    with open(f"bounties/{ctx.guild_id}/{ctx.message.id}.json", "w") as f:
                        json.dump(bounty, f)
                    return True
                else:
                    continue
    return False

def _transfer(amount, wallet, guild, sol: Client, token: Pubkey | None = None, token_address: Pubkey | None = None):
    _from = Keypair.from_json(json.loads(database.get_guild(guild).wallet_secret))
    _to = Pubkey.from_string(wallet)
    print("defined and compiled _to, _from")
    if token is None or token_address is None:
        return send_sol(_to, _from, sol, amount)
    else:
        print("tokens caught")
        decimals = int(requests.get(f"https://public-api.solscan.io/token/meta?tokenAddress={token_address}", headers={"accept": "application/json", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE2Nzc0Njk5MzA0OTMsImVtYWlsIjoibW9yZ2FuLm1ldHpAZXlla29uLnh5eiIsImFjdGlvbiI6InRva2VuLWFwaSIsImlhdCI6MTY3NzQ2OTkzMH0.aVkZR-fP2yNhG_6xjarBnGOiuDcU2AKJ-vAdX4mBot0"}).json()["decimals"])
        return send_token(_to, _from, 10**decimals, token, token_address, amount, sol)

def preflight(cls, ctx, guild, account: str | None = None):
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
    bal = int(json.loads(cls.sol.get_balance(Pubkey.from_string(db.wallet_pubkey)).to_json())["result"]["value"])
    print(bal)
    with open(f"bounties/{guild.id}/{ctx.message.id}.json", "r") as f:
        bounty = json.load(f)
    if datetime.now() >= datetime.fromtimestamp(bounty["ends"]):
        os.remove(f"bounties/{guild.id}/{ctx.message.id}.json")
        return 2
    if bounty["token"][0] == "SOL":
        if bal / 1000000000 < bounty["reward"]:
            return 1
    elif account is not "SOL":
        balance = int(requests.get(f"https://public-api.solscan.io/token/meta?tokenAddress={account}", headers={"accept": "application/json", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE2Nzc0Njk5MzA0OTMsImVtYWlsIjoibW9yZ2FuLm1ldHpAZXlla29uLnh5eiIsImFjdGlvbiI6InRva2VuLWFwaSIsImlhdCI6MTY3NzQ2OTkzMH0.aVkZR-fP2yNhG_6xjarBnGOiuDcU2AKJ-vAdX4mBot0"}).json()["tokenAmount"]["uiAmount"])
        if balance < int(bounty["reward"]):
            return 1
    return 3

def get_allowed_guilds():
    with open("test.json", "r") as f:
        data = json.load(f)
    return data

def get_token_opts(guild, c: Client):
    db = database.get_guild(guild)
    tokens = get_avalible_tokens(c, Pubkey.from_string(db.wallet_pubkey))
    opts = [interactions.SelectOption(label="SOL", value="SOL")]
    for token in tokens:
        opts.append(interactions.SelectOption(label=(token['account']['data']['parsed']['info']["mint"]), value=token["pubkey"]))
    return opts