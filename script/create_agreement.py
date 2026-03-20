"""
Step 2 (Protocol): Create a Safe Harbor agreement and adopt it.

Prerequisites:
    VAULT_ADDRESS set in .env after running: just setup

Usage:
    just create-agreement
    (or: mox run script/create_agreement.py --network battlechain)
"""

import json
import os
import time

import boa
from eth_utils import keccak

from script.abis import (
    BC_AGREEMENT_FACTORY,
    BC_REGISTRY,
    BC_CAIP2_CHAIN_ID,
    BC_SAFE_HARBOR_URI,
    AGREEMENT_FACTORY_ABI,
    AGREEMENT_ABI,
    REGISTRY_ABI,
)

COMMITMENT_WINDOW_DAYS  = 30
CHILD_CONTRACT_SCOPE_ALL = 2   # ChildContractScope.All
IDENTITY_ANONYMOUS       = 0   # IdentityRequirements.Anonymous


def moccasin_main() -> None:
    vault_address = os.environ.get("VAULT_ADDRESS")
    if not vault_address:
        raise ValueError("VAULT_ADDRESS not set in .env")

    signer = boa.env.eoa

    factory  = boa.loads_abi(json.dumps(AGREEMENT_FACTORY_ABI), name="AgreementFactory").at(BC_AGREEMENT_FACTORY)
    registry = boa.loads_abi(json.dumps(REGISTRY_ABI), name="Registry").at(BC_REGISTRY)

    # Build AgreementDetails tuple
    details = (
        "BattleChain Starter Demo",
        [("Security Team", "security@example.com")],
        [(
            signer,
            [(vault_address, CHILD_CONTRACT_SCOPE_ALL)],
            BC_CAIP2_CHAIN_ID,
        )],
        (
            10,           # bountyPercentage
            5_000_000,    # bountyCapUsd
            True,         # retainable
            IDENTITY_ANONYMOUS,
            "",           # diligenceRequirements
            0,            # aggregateBountyCapUsd
        ),
        BC_SAFE_HARBOR_URI,
    )

    salt = keccak(b"agreement-v1" + bytes.fromhex(signer[2:]))

    # Simulate first (eth_call) to get the returned agreement address,
    # then the actual transaction is sent by boa automatically.
    agreement_address = factory.create(details, signer, salt)
    print(f"Agreement created: {agreement_address}")

    # Extend commitment window
    new_cant_change_until = int(time.time()) + COMMITMENT_WINDOW_DAYS * 24 * 60 * 60
    agreement = boa.loads_abi(json.dumps(AGREEMENT_ABI), name="Agreement").at(agreement_address)
    agreement.extendCommitmentWindow(new_cant_change_until)
    print(f"Commitment window extended {COMMITMENT_WINDOW_DAYS} days")

    # Adopt the agreement
    registry.adoptSafeHarbor(agreement_address)
    print("Safe Harbor adopted")

    print("\n--- Add to your .env ---")
    print(f"AGREEMENT_ADDRESS={agreement_address}")
