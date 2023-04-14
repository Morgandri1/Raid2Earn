import interactions
import json

def allow(guild_id: int, bot: interactions.Client) -> None:
    """Adds a guild ID to the scope of the create command, if it is not found.

    Args:
        guild_id (int): The guild ID to add to the scope.
        bot (interactions.Client): The bot object.

    Returns:
        None
    """
    with open("paid.json", "r") as f:
        data: list = json.load(f)
    if not guild_id in data:
        data.append(guild_id)
        with open("paid.json", "w") as f:
            json.dump(data, f, indent=4)
    bot.reload("cogs.create")

def disallow(guild_id: int, bot: interactions.Client) -> None:
    """Removes a guild ID from the scope of the create command, if it is found.
    
    Args:
        guild_id (int): The guild ID to remove from the scope.
        bot (interactions.Client): The bot object.

    Returns:
        None
    """
    with open("paid.json", "r") as f:
        data: list = json.load(f)
    if guild_id in data:
        data.remove(guild_id)
        with open("paid.json", "w") as f:
            json.dump(data, f, indent=4)
    bot.reload("cogs.create")

def get_allowed() -> list:
    """Gets the list of guild IDs that are allowed to use the create command.
    
    Returns:
        list: The list of guild IDs that are allowed to use the create command.
    """
    with open("paid.json", "r") as f:
        return json.load(f)
    
def is_allowed(guild_id: int) -> bool:
    """Checks if a guild ID is allowed to use the create command.

    Args:
        guild_id (int): The guild ID to check.

    Returns:
        bool: Guild is on allowlist.
    """
    with open("paid.json", "r") as f:
        data: list = json.load(f)
    return guild_id in data