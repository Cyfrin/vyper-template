set dotenv-load

# Import your private key into Moccasin's encrypted keystore (run once)
import-key:
    mox wallet import deployer

# Compile contracts
build:
    mox compile

# Step 1: Deploy MockToken + VulnerableVault, seed the vault.
# Addresses are saved to moccasin's deployments.db automatically.
setup:
    mox run script/setup.py --network battlechain

# Step 2: Create Safe Harbor agreement (reads VulnerableVault from deployments.db)
# Copy AGREEMENT_ADDRESS from output into .env
create-agreement:
    mox run script/create_agreement.py --network battlechain

# Step 3: Request attack mode (transitions agreement to ATTACK_REQUESTED)
request-attack-mode:
    mox run script/request_attack_mode.py --network battlechain

# Step 3.5: Self-approve via the permissionless testnet MockRegistryModerator
# (transitions to UNDER_ATTACK). Testnet only; mainnet approval is real DAO governance.
approve-attack:
    mox run script/approve_attack.py --network battlechain

# Step 4: Execute the attack (requires the agreement to be UNDER_ATTACK; reads contracts from deployments.db)
attack:
    mox run script/attack.py --network battlechain

# Check agreement state (2=ATTACK_REQUESTED, 3=UNDER_ATTACK)
check-state:
    mox run script/check_state.py --network battlechain
