"""
Step 3 (Protocol): Submit the attack mode request for DAO review.

Prerequisites:
    Safe Harbor agreement adopted via: just create-agreement

Usage:
    just request-attack-mode
    (or: mox run script/request_attack_mode.py --network battlechain)

After running, wait for DAO approval. Check state with:
    just check-state
    # 2 = ATTACK_REQUESTED, 3 = UNDER_ATTACK (approved)
"""

import json

import boa

import battlechain as bc
from battlechain.abi import REGISTRY_ABI


def _adopter_agreement(adopter: str) -> str:
    registry = boa.loads_abi(json.dumps(REGISTRY_ABI), name="BCSafeHarborRegistry").at(
        bc.TESTNET_REGISTRY
    )
    address = registry.getAgreement(adopter)
    if int(address, 16) == 0:
        raise RuntimeError(
            f"No Safe Harbor agreement adopted by {adopter}. Run `just create-agreement` first."
        )
    return address


def moccasin_main() -> None:
    signer = boa.env.eoa
    agreement_address = _adopter_agreement(signer)

    bc.request_attack_mode(agreement_address)

    print(f"Attack mode requested for agreement: {agreement_address}")
    print("State is now ATTACK_REQUESTED (2) — awaiting DAO approval.")
    print("Once approved, state moves to UNDER_ATTACK (3).")
