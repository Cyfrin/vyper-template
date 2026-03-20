# Battlechain Starter — Moccasin

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
- [Python](https://www.python.org/) >= 3.11
- [moccasin](https://github.com/Cyfrin/moccasin) — `pip install moccasin`
- [just](https://github.com/casey/just) *(optional — all commands can be run with `mox` directly)*

## Installation

```bash
git clone <MY_REPO>
cd <MY_REPO>
pip install moccasin
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
# Step 1: Deploy MockToken + VulnerableVault, seed the vault
# Copy TOKEN_ADDRESS and VAULT_ADDRESS from output into .env
just setup

# Step 2: Create Safe Harbor agreement (requires VAULT_ADDRESS in .env)
# Copy AGREEMENT_ADDRESS from output into .env
just create-agreement

# Step 3: Request attack mode (requires AGREEMENT_ADDRESS in .env)
just request-attack-mode
```

## Whitehat Role

```bash
# Step 4: Execute the attack (requires DAO approval first)
# Requires TOKEN_ADDRESS, VAULT_ADDRESS, RECOVERY_ADDRESS in .env
just attack
```

## Utilities

```bash
# Check agreement state (2=ATTACK_REQUESTED, 3=UNDER_ATTACK)
just check-state
```
