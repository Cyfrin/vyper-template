"""
Step 2 (Protocol): Create a Safe Harbor agreement and adopt it.

Prerequisites:
    VulnerableVault deployed via: just setup

Usage:
    just create-agreement
    (or: mox run script/create_agreement.py --network battlechain)
"""

import boa
from eth_utils import keccak

import battlechain as bc

COMMITMENT_WINDOW_DAYS = 30
BOUNTY_CAP_USD = 5_000_000


def moccasin_main() -> None:
    vault_address = bc.get_tracked_address("VulnerableVault")
    if vault_address is None:
        raise RuntimeError(
            "VulnerableVault address not tracked — run `just setup` first."
        )

    signer = boa.env.eoa

    bounty_terms = bc.BountyTerms(
        bounty_percentage=10,
        bounty_cap_usd=BOUNTY_CAP_USD,
        retainable=True,
    )
    details = bc.default_agreement_details(
        protocol_name="BattleChain Starter Demo",
        contacts=[bc.Contact(name="Security Team", contact="security@example.com")],
        contracts=[vault_address],
        recovery_address=signer,
        chain_id=bc.TESTNET_CHAIN_ID,
        bounty_terms=bounty_terms,
    )

    salt = keccak(b"agreement-v1" + bytes.fromhex(signer[2:]))

    agreement_address = bc.create_and_adopt_agreement(
        details,
        owner=signer,
        salt=salt,
        commitment_days=COMMITMENT_WINDOW_DAYS,
    )
    print(f"Agreement created: {agreement_address}")
    print(f"Commitment window extended {COMMITMENT_WINDOW_DAYS} days")
    print("Safe Harbor adopted — registered on-chain to your adopter address.")
