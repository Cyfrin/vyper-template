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
from moccasin.config import get_active_network

import battlechain as bc
from src import MockToken, VulnerableVault

SEED_AMOUNT = 1000 * 10**18  # 1000 tokens
VYPER_VERSION = vyper.__version__


def moccasin_main() -> None:
    active_network = get_active_network()
    skip_verify = active_network.is_local_or_forked_network()

    # 1. Deploy MockToken
    token = MockToken.deploy()
    print(f"MockToken deployed: {token.address}")
    if not skip_verify:
        bc.verify_contract(token.address, "src/MockToken.vy:MockToken", VYPER_VERSION)

    # 2. Deploy VulnerableVault via BattleChainDeployer so it auto-registers
    #    with the AttackRegistry. The address is also persisted to
    #    .bc_deployments.json for create-agreement and attack to pick up.
    vault = bc.bc_deploy(VulnerableVault, token.address)
    print(f"VulnerableVault deployed: {vault.address}")
    if not skip_verify:
        bc.verify_contract(vault.address, "src/VulnerableVault.vy:VulnerableVault", VYPER_VERSION)

    # 3. Seed the vault with tokens to represent protocol liquidity
    token.mint(boa.env.eoa, SEED_AMOUNT)
    token.approve(vault.address, SEED_AMOUNT)
    vault.deposit(SEED_AMOUNT)
    print("Vault seeded with 1000.0 tokens")
