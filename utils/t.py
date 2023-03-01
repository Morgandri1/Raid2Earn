from __future__ import annotations
import json
from solana.rpc.api import Client
from solana.rpc.types import TxOpts, TokenAccountOpts
from solana.transaction import Transaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.system_program import TransferParams, transfer
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
import requests

def send_token(
    to: Pubkey,
    source: Keypair,
    decimal: int,
    token_account: Pubkey,
    token_mint_address: Pubkey,
    token_amount: int,
    client: Client,
    ) -> dict:
    token = Token(client, pubkey=token_mint_address, program_id=TOKEN_PROGRAM_ID, payer=source)

    print(to)

    destination = token.create_account(to)
    send_sol(destination, source, client, 0.02040280)
    response = token.transfer(
        source=token_account,
        dest=destination,
        owner=source,
        amount=int(token_amount*decimal),
        opts=TxOpts(skip_confirmation=True),
        multi_signers=[source]
    )
    print(response.to_json())
    return json.loads(response.to_json())

def send_sol(
    to: Pubkey,
    source: Keypair,
    client: Client,
    amount: int,
    ) -> dict:
    tx = Transaction(
        instructions=[transfer(TransferParams(from_pubkey=(source.pubkey()), to_pubkey=(to), lamports=int(amount*1000000000)))],
        fee_payer=source.pubkey(),
    )

    result = client.send_transaction(tx, source)

    return json.loads(result.to_json())

def get_avalible_tokens(client: Client, pubkey: Pubkey) -> list:
    return json.loads(client.get_token_accounts_by_owner_json_parsed(pubkey, TokenAccountOpts(program_id=TOKEN_PROGRAM_ID)).to_json())["result"]["value"]

def get_token_identifiers(token: Pubkey) -> dict:
    r = requests.get(f"https://public-api.solscan.io/token/meta?tokenAddress={token}", headers={"accept": "application/json", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE2Nzc0Njk5MzA0OTMsImVtYWlsIjoibW9yZ2FuLm1ldHpAZXlla29uLnh5eiIsImFjdGlvbiI6InRva2VuLWFwaSIsImlhdCI6MTY3NzQ2OTkzMH0.aVkZR-fP2yNhG_6xjarBnGOiuDcU2AKJ-vAdX4mBot0"}).json()
    return {"symbol": r["symbol"], "name": r["name"], "decimals": r["decimals"], "mint": str(token)}