from solders.pubkey import Pubkey
from .t import *
import json
import os
import database
import user_db
from solana.rpc.async_api import AsyncClient
from datetime import datetime
import interactions

notation = {
    2: 10e2,
    3: 10e3,
    4: 10e4,
    5: 10e5,
    6: 10e6,
    7: 10e7,
    8: 10e8,
    9: 10e9
}

requirements = {
            1: "Like",
            2: "Follow",
            3: "Retweet",
            4: "Like + Retweet",
            5: "Follow + Retweet",
            6: "Like + Follow",
            7: "Like + Follow + Retweet",
            8: "Like + Comment",
            9: "Follow + Comment",
            10: "Like + Retweet + Comment",
            11: "Follow + Retweet + Comment",
            12: "Like + Follow + Retweet + Comment"
        }

def make_integer_smaller(big_integer, power_of_ten):
    return big_integer // (10 ** power_of_ten)

async def parse(data, bounty, db: user_db.User, ctx) -> bool:
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

async def _transfer(amount, wallet, guild, sol: AsyncClient, token: Pubkey | None = None, token_address: Pubkey | None = None):
    _from = Keypair.from_json(json.loads(database.get_guild(guild).wallet_secret))
    _to = Pubkey.from_string(wallet)
    print("defined and compiled _to, _from")
    if token is None or token_address is None:
        return await send_sol(_to, _from, sol, amount)
    else:
        print("tokens caught")
        decimals = int(requests.get(f"https://public-api.solscan.io/token/meta?tokenAddress={token_address}", headers={"accept": "application/json", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE2Nzc0Njk5MzA0OTMsImVtYWlsIjoibW9yZ2FuLm1ldHpAZXlla29uLnh5eiIsImFjdGlvbiI6InRva2VuLWFwaSIsImlhdCI6MTY3NzQ2OTkzMH0.aVkZR-fP2yNhG_6xjarBnGOiuDcU2AKJ-vAdX4mBot0"}).json()["decimals"])
        return await send_token(_to, _from, 10**decimals, token, token_address, amount, sol)

async def preflight(cls, ctx, guild, account: str | None = None):
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
    bal = await cls.sol.get_balance(Pubkey.from_string(db.wallet_pubkey))
    bal = int(json.loads(bal.to_json())["result"]["value"])
    print(bal)
    with open(f"bounties/{guild.id}/{ctx.message.id}.json", "r") as f:
        bounty = json.load(f)
    if datetime.now() >= datetime.fromtimestamp(bounty["ends"]):
        os.remove(f"bounties/{guild.id}/{ctx.message.id}.json")
        return 2
    if bounty["token"][0] == "SOL":
        if bal / 1000000000 < bounty["reward"]:
            return 1
    else:
        balance = requests.get(f"https://public-api.solscan.io/token/meta?tokenAddress={account}", headers={"accept": "application/json", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE2Nzc0Njk5MzA0OTMsImVtYWlsIjoibW9yZ2FuLm1ldHpAZXlla29uLnh5eiIsImFjdGlvbiI6InRva2VuLWFwaSIsImlhdCI6MTY3NzQ2OTkzMH0.aVkZR-fP2yNhG_6xjarBnGOiuDcU2AKJ-vAdX4mBot0"}).json()
        if balance == {'status': 400, 'error': {'message': 'missing or invalid tokenAddress'}}:
            return 3 # token not found on secondary checks. ignore. 
        balance = int(balance["tokenAmount"]["uiAmount"])
        if balance < int(bounty["reward"]):
            return 1
    return 3

async def get_allowed_guilds():
    with open("test.json", "r") as f:
        data = json.load(f)
    return data

async def get_token_opts(guild, c: AsyncClient):
    db = database.get_guild(guild)
    aTokens = await get_avalible_tokens(c, Pubkey.from_string(db.wallet_pubkey))
    print(aTokens)
    tokens = await get_token_identifiers([token['account']['data']['parsed']['info']["mint"] for token in aTokens])
    opts = [interactions.SelectOption(label="SOL", value="SOL")]
    for token in tokens:
        opts.append(interactions.SelectOption(label=(f"{tokens[token]['name']} - {tokens[token]['symbol']}"), value=aTokens[get_index(aTokens, token)]["pubkey"]))
    return opts

async def get_token_opts_universal(guild, c: AsyncClient) -> list[dict]:
    db = database.get_guild(guild)
    aTokens = await get_avalible_tokens(c, Pubkey.from_string(db.wallet_pubkey))
    print(aTokens)
    tokens = await get_token_identifiers([token['account']['data']['parsed']['info']["mint"] for token in aTokens])
    output = []
    for token in tokens:
        output.append(f'``{make_integer_smaller(int(aTokens[get_index(aTokens, token)]["account"]["data"]["parsed"]["info"]["tokenAmount"]["amount"]), int(aTokens[get_index(aTokens, token)]["account"]["data"]["parsed"]["info"]["tokenAmount"]["decimals"]))} {tokens[token]["symbol"]},``')
    return output

def get_index(data: list, item):
    for index, i in enumerate(data):
        if i["account"]["data"]["parsed"]["info"]["mint"] == item:
            return index
        
def get_index_dict(data: dict, item):
    for key in data:
        if data[key] == item:
            return key
    raise IndexError("Item not found in dict")
        

"""
/notation[int(aTokens[get_index(aTokens, token)]["account"]["data"]["parsed"]["info"]["tokenAmount"]["decimals"])]
"""
"""
{'account': {'data': {'parsed': {'info': {'tokenAmount': {'amount': '10000000', 'decimals': 5, 'uiAmount': 100.0, 'uiAmountString': '100'}}, 'type': 'account'}, 'space': 165}, 'owner': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'executable': False, 'rentEpoch': 0}}
"""