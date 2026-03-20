"""
Step 1 (Protocol): Deploy MockToken + VulnerableVault, seed the vault.

Prerequisites:
    mox wallet import deployer  (run once to import your private key)

Usage:
    just setup
    (or: mox run script/setup.py --network battlechain)
"""

import boa
import vyper

from src import MockToken, VulnerableVault
from script.verify_contract import verify_contract

SEED_AMOUNT = 1000 * 10**18  # 1000 tokens
VYPER_VERSION = vyper.__version__


def moccasin_main() -> None:
    # 1. Deploy MockToken
    token = MockToken.deploy()
    print(f"MockToken deployed: {token.address}")
    verify_contract(token.address, "src/MockToken.vy:MockToken", VYPER_VERSION)

    # 2. Deploy VulnerableVault
    vault = VulnerableVault.deploy(token.address)
    print(f"VulnerableVault deployed: {vault.address}")
    verify_contract(vault.address, "src/VulnerableVault.vy:VulnerableVault", VYPER_VERSION)

    # 3. Seed the vault with tokens to represent protocol liquidity
    token.mint(boa.env.eoa, SEED_AMOUNT)
    token.approve(vault.address, SEED_AMOUNT)
    vault.deposit(SEED_AMOUNT)
    print(f"Vault seeded with 1000.0 tokens")

    print("\n--- Add to your .env ---")
    print(f"TOKEN_ADDRESS={token.address}")
    print(f"VAULT_ADDRESS={vault.address}")
