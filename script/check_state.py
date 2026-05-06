"""
Utility: print the on-chain state of the signer's adopted Safe Harbor agreement.

Usage:
    just check-state
    (or: mox run script/check_state.py --network battlechain)

States:
    0 NOT_DEPLOYED        4 PROMOTION_REQUESTED
    1 NEW_DEPLOYMENT      5 PRODUCTION
    2 ATTACK_REQUESTED    6 CORRUPTED
    3 UNDER_ATTACK
"""

import json

import boa

import battlechain as bc
from battlechain.abi import REGISTRY_ABI


def moccasin_main() -> None:
    signer = boa.env.eoa
    registry = boa.loads_abi(json.dumps(REGISTRY_ABI), name="BCSafeHarborRegistry").at(
        bc.TESTNET_REGISTRY
    )
    agreement_address = registry.getAgreement(signer)
    if int(agreement_address, 16) == 0:
        raise RuntimeError(
            f"No Safe Harbor agreement adopted by {signer}. Run `just create-agreement` first."
        )

    state = bc.get_agreement_state(agreement_address)
    print(f"Agreement: {agreement_address}")
    print(f"State:     {state.name} ({int(state)})")
