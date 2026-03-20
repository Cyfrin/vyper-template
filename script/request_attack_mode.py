"""
Step 3 (Protocol): Submit the attack mode request for DAO review.

Prerequisites:
    AGREEMENT_ADDRESS set in .env after running: just create-agreement

Usage:
    just request-attack-mode
    (or: mox run script/request_attack_mode.py --network battlechain)

After running, wait for DAO approval. Check state with:
    just check-state
    # 2 = ATTACK_REQUESTED, 3 = UNDER_ATTACK (approved)
"""

import json
import os

import boa

from script.abis import BC_ATTACK_REGISTRY, ATTACK_REGISTRY_ABI


def moccasin_main() -> None:
    agreement_address = os.environ.get("AGREEMENT_ADDRESS")
    if not agreement_address:
        raise ValueError("AGREEMENT_ADDRESS not set in .env")

    attack_registry = boa.loads_abi(
        json.dumps(ATTACK_REGISTRY_ABI), name="AttackRegistry"
    ).at(BC_ATTACK_REGISTRY)

    attack_registry.requestUnderAttack(agreement_address)

    print(f"Attack mode requested for agreement: {agreement_address}")
    print("State is now ATTACK_REQUESTED (2) — awaiting DAO approval.")
    print("Once approved, state moves to UNDER_ATTACK (3).")
