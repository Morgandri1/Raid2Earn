import interactions
import json

def allow(guild_id: int, bot: interactions.Client):
    with open("paid.json", "r") as f:
        data: list = json.load(f)
    data.append(guild_id)
    with open("paid.json", "w") as f:
        json.dump(data, f)
    bot.reload("cogs.create")

def get_allowed():
    with open("paid.json", "r") as f:
        return json.load(f)