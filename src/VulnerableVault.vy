# pragma version ^0.4.0
"""
@title VulnerableVault
@notice A simple token vault with a deliberate CEI (Checks-Effects-Interactions) violation.

@dev THE VULNERABILITY
     `withdrawAll()` performs the token transfer (Interaction) BEFORE zeroing
     the caller's balance (Effect). If the token triggers a callback on the
     recipient during transfer, an attacker can re-enter `withdrawAll()`
     before the balance is cleared — draining the entire vault.

     The correct pattern (CEI) would be:
         self.balances[msg.sender] = 0                   # Effect first
         extcall IERC20(TOKEN).transfer(msg.sender, amt) # Interaction second
"""

interface IERC20:
    def transfer(to: address, amount: uint256) -> bool: nonpayable
    def transferFrom(owner: address, to: address, amount: uint256) -> bool: nonpayable

TOKEN:    public(immutable(address))
balances: public(HashMap[address, uint256])

event Deposited:
    user:   indexed(address)
    amount: uint256

event Withdrawn:
    user:   indexed(address)
    amount: uint256


@deploy
def __init__(token: address):
    TOKEN = token


@external
def deposit(amount: uint256):
    extcall IERC20(TOKEN).transferFrom(msg.sender, self, amount)
    self.balances[msg.sender] += amount
    log Deposited(msg.sender, amount)


@external
def withdrawAll():
    amount: uint256 = self.balances[msg.sender]
    assert amount > 0, "nothing to withdraw"

    # ❌ INTERACTION before EFFECT
    extcall IERC20(TOKEN).transfer(msg.sender, amount)

    # ❌ Effect happens here — re-entrant calls already passed the check above
    self.balances[msg.sender] = 0

    log Withdrawn(msg.sender, amount)


@external
@view
def getBalance(user: address) -> uint256:
    return self.balances[user]
