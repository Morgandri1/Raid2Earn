import t
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID

print(t._validate_token_account(
    AsyncClient("https://api.mainnet-beta.solana.com"),
    Pubkey.from_string("QHPMKes2Fj8kWrRneZC8vpahBf2zgRYXgTFoWqWiUVj"),
    Pubkey.from_string("Fpa2S13a82aBu9YGscAEqttXJaCZb5TVzhscmUApnzhP"),
    AsyncToken(AsyncClient, Pubkey.from_string("QHPMKes2Fj8kWrRneZC8vpahBf2zgRYXgTFoWqWiUVj"), TOKEN_PROGRAM_ID, payer)
))