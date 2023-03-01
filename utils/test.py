from solana.rpc.api import Client
from solders.pubkey import Pubkey

sol = Client("https://api.mainnet-beta.solana.com")

print(sol.get_account_info_json_parsed(Pubkey.from_string("")))