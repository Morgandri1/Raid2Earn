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

async def get_token_identifiers(tokens: list) -> dict:
    """
    example:
    {
        "HwzkXyX8B45LsaHXwY8su92NoRBS5GQC32HzjQRDqPnr": {
            "symbol": "SAMO",
            "name": "Samoyedcoin"
        }
    }
    """
    r = requests.post(
        f"https://rest-api.hellomoon.io/v0/nft/mint_information", 
        headers={
            "accept": "application/json", 
            'authorization': 'Bearer b4392ac7-dd14-4b9d-9b47-eb25dde52ebd', 
            "content-type": "application/json"
        }, 
        json={"nftMint": tokens}
    ).json()
    data = {}
    for index, token in enumerate(r["data"]):
        data[r["data"][index]["nftMint"]] = {"symbol": token["nftMetadataJson"]["symbol"], "name": token["nftMetadataJson"]["name"], "mint": token["nftMint"]}
    return data

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