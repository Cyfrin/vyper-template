# pragma version ^0.4.0
"""
@title MockToken
@notice A mintable ERC20 where any user can register a transfer hook contract.

@dev When tokens are transferred to an address that has a registered hook,
     the token calls `onTokenTransfer` on that hook after the transfer
     completes. This lets users plug in arbitrary logic on receive —
     and is what makes the CEI violation in VulnerableVault exploitable
     via reentrancy.
"""

interface ITransferHook:
    def onTokenTransfer(from_: address, amount: uint256): nonpayable

# ERC20 state
name:        public(String[64])
symbol:      public(String[32])
decimals:    public(uint8)
totalSupply: public(uint256)
balanceOf:   public(HashMap[address, uint256])
allowance:   public(HashMap[address, HashMap[address, uint256]])

# Hook registry: recipient address → hook contract
transferHooks: public(HashMap[address, address])

event Transfer:
    sender:   indexed(address)
    receiver: indexed(address)
    value:    uint256

event Approval:
    owner:   indexed(address)
    spender: indexed(address)
    value:   uint256

event TransferHookSet:
    user: indexed(address)
    hook: indexed(address)


@deploy
def __init__():
    self.name     = "BattleChain Demo Token"
    self.symbol   = "BCDT"
    self.decimals = 18


@external
def mint(to: address, amount: uint256):
    """@notice Anyone can mint. Intentional for the tutorial."""
    self.totalSupply      += amount
    self.balanceOf[to]    += amount
    log Transfer(empty(address), to, amount)


@external
def setTransferHook(hook: address):
    """@notice Register a hook contract called when you receive tokens."""
    self.transferHooks[msg.sender] = hook
    log TransferHookSet(msg.sender, hook)


@external
def transfer(to: address, amount: uint256) -> bool:
    self._transfer(msg.sender, to, amount)
    hook: address = self.transferHooks[to]
    if hook != empty(address):
        extcall ITransferHook(hook).onTokenTransfer(msg.sender, amount)
    return True


@external
def transferFrom(owner: address, to: address, amount: uint256) -> bool:
    self.allowance[owner][msg.sender] -= amount
    self._transfer(owner, to, amount)
    return True


@external
def approve(spender: address, amount: uint256) -> bool:
    self.allowance[msg.sender][spender] = amount
    log Approval(msg.sender, spender, amount)
    return True


@internal
def _transfer(sender: address, to: address, amount: uint256):
    self.balanceOf[sender] -= amount
    self.balanceOf[to]     += amount
    log Transfer(sender, to, amount)
