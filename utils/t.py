from __future__ import annotations
import json
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts, TokenAccountOpts
from solana.transaction import Transaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID
import requests

async def send_token(
    to: Pubkey,
    source: Keypair,
    decimal: int,
    token_account: Pubkey,
    token_mint_address: Pubkey,
    token_amount: int,
    client: AsyncClient,
    ) -> dict:
    token = AsyncToken(client, pubkey=token_mint_address, program_id=TOKEN_PROGRAM_ID, payer=source)

    print(to)

    destination = await _validate_token_account(client, token_mint_address, to, token)

    response = await token.transfer(
        source=token_account,
        dest=destination,
        owner=source,
        amount=int(token_amount*decimal),
        opts=TxOpts(skip_confirmation=True),
        multi_signers=[source]
    )
    print(response.to_json())
    return json.loads(response.to_json())

async def send_sol(
    to: Pubkey,
    source: Keypair,
    client: AsyncClient,
    amount: int,
    ) -> dict:
    tx = Transaction(
        instructions=[transfer(TransferParams(from_pubkey=(source.pubkey()), to_pubkey=(to), lamports=int(amount*1000000000)))],
        fee_payer=source.pubkey(),
    )

    result = await client.send_transaction(tx, source)

    return json.loads(result.to_json())

async def get_avalible_tokens(client: AsyncClient, pubkey: Pubkey) -> list:
    r = await client.get_token_accounts_by_owner_json_parsed(pubkey, TokenAccountOpts(program_id=TOKEN_PROGRAM_ID))
    return json.loads(r.to_json())["result"]["value"]

async def get_token_identifiers(token: Pubkey) -> dict:
    r = requests.get(f"https://public-api.solscan.io/token/meta?tokenAddress={token}", headers={"accept": "application/json", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkQXQiOjE2Nzc0Njk5MzA0OTMsImVtYWlsIjoibW9yZ2FuLm1ldHpAZXlla29uLnh5eiIsImFjdGlvbiI6InRva2VuLWFwaSIsImlhdCI6MTY3NzQ2OTkzMH0.aVkZR-fP2yNhG_6xjarBnGOiuDcU2AKJ-vAdX4mBot0"}).json()
    return {"symbol": r["symbol"], "name": r["name"], "decimals": r["decimals"], "mint": str(token)}

async def _validate_token_account(
        client: AsyncClient, 
        token: Pubkey, 
        dest: Pubkey, 
        program: AsyncToken
    ) -> Pubkey:
    """
    !internal use only!
    checks if the reciever has an attached token account, if not, creates one
    """
    raw_data = await client.get_token_accounts_by_owner_json_parsed(dest, opts=TokenAccountOpts(mint=token))
    data = json.loads(raw_data.to_json())

    for account in data["result"]["value"]:
        print(account)
        if account["account"]["data"]["parsed"]["info"]["mint"] == str(token):
            return Pubkey.from_string(account["pubkey"])
        else:
            return await program.create_account(dest)