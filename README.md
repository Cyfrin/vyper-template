# Battlechain Starter — Moccasin

- [Battlechain Starter — Moccasin](#battlechain-starter--moccasin)
- [About](#about)
- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Quickstart](#quickstart)
- [Usage](#usage)
  - [Protocol Role](#protocol-role)
  - [Whitehat Role](#whitehat-role)
  - [Utilities](#utilities)

# About

A starter repo for interacting with the Battlechain Safe Harbor protocol using Moccasin. Includes scripts for deploying a vulnerable vault, creating a Safe Harbor agreement, requesting attack mode, and executing a whitehat rescue.

# Getting Started

## Requirements

- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [moccasin](https://github.com/Cyfrin/moccasin) — `uv tool install moccasin`
- [just](https://github.com/casey/just) *(optional — all commands can be run with `mox` directly)*

## Installation

```bash
git clone https://github.com/Cyfrin/vyper-template
cd vyper-template
# If not already installed:
uv tool install moccasin
```

Import your private key into the encrypted keystore (once):
```bash
just import-key
# prompts for a master password, then your private key — never stored in plaintext
```

## Quickstart

```bash
just build
```

# Usage

## Protocol Role

```bash
# Step 1: Deploy MockToken + VulnerableVault, seed the vault.
just setup

# Step 2: Create Safe Harbor agreement and adopt it.
just create-agreement

# Step 3: Request attack mode.
just request-attack-mode
```

## Whitehat Role

```bash
# Step 4: Execute the attack (requires DAO approval first; RECOVERY_ADDRESS in .env)
just attack
```

## Utilities

```bash
# Check agreement state (2=ATTACK_REQUESTED, 3=UNDER_ATTACK)
just check-state
```

## Address tracking

This repo deliberately avoids copy-pasting addresses between steps. Three
mechanisms cover three different kinds of addresses:

- **`MockToken` and `Attacker`** are deployed via vanilla
  `MockToken.deploy(...)` / `Attacker.deploy(...)`, so they land in moccasin's
  `deployments.db` automatically. Downstream scripts read them with
  `active_network.get_latest_contract_unchecked("MockToken")`. See the
  [moccasin docs on deployments](https://cyfrin.github.io/moccasin/core_concepts/deployments_db.html).
- **`VulnerableVault`** must be deployed through `BattleChainDeployer` so the
  AttackRegistry recognizes it as a top-level contract (otherwise
  `requestUnderAttack` reverts). The starter uses
  [`bc.bc_deploy(VulnerableVault, token.address)`](https://github.com/Cyfrin/battlechain-lib-py),
  which routes through BCDeployer and persists the address to a per-chain
  `.bc_deployments.json` file. Downstream scripts read it back with
  `bc.get_tracked_address("VulnerableVault")` or `bc.get_tracked_contract(VulnerableVault)`.
  This file exists because BCDeployer performs the CREATE inside its own call
  context — moccasin's `deployments.db` only sees top-level boa deploys.
- **Safe Harbor agreement** isn't a moccasin-deployed contract either (it
  comes back from a factory call), so scripts look it up on-chain via
  `BCSafeHarborRegistry.getAgreement(adopter)`, where `adopter` is `boa.env.eoa`.
- **`RECOVERY_ADDRESS`** is the only address that lives in `.env` — it's the
  user's own wallet, not something a script can derive.
