"""
Step 3.5 (Testnet only): Self-approve the pending attack request.

On the live testnet the `MockRegistryModerator` is permissionless, so an adopter
can approve their own request — moving the agreement from ATTACK_REQUESTED (2) to
UNDER_ATTACK (3) without waiting on real DAO governance. On mainnet this is a real
governance action and `bc.approve_attack_request` will raise.

Prerequisites:
    Attack mode requested via: just request-attack-mode

Usage:
    just approve-attack
    (or: mox run script/approve_attack.py --network battlechain)
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

    bc.approve_attack_request(agreement_address)

    print(f"Attack request approved for agreement: {agreement_address}")
    print("State is now UNDER_ATTACK (3) — whitehats may attack under Safe Harbor.")
