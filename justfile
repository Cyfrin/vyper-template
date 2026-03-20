set dotenv-load

# Import your private key into Moccasin's encrypted keystore (run once)
import-key:
    mox wallet import deployer

# Compile contracts
build:
    mox compile

# Step 1: Deploy MockToken + VulnerableVault, seed the vault
# Copy TOKEN_ADDRESS and VAULT_ADDRESS from output into .env
setup:
    mox run script/setup.py --network battlechain

# Step 2: Create Safe Harbor agreement (requires VAULT_ADDRESS in .env)
# Copy AGREEMENT_ADDRESS from output into .env
create-agreement:
    mox run script/create_agreement.py --network battlechain

# Step 3: Request attack mode (requires AGREEMENT_ADDRESS in .env)
request-attack-mode:
    mox run script/request_attack_mode.py --network battlechain

# Step 4: Execute the attack (requires DAO approval first)
attack:
    mox run script/attack.py --network battlechain

# Check agreement state (2=ATTACK_REQUESTED, 3=UNDER_ATTACK)
check-state:
    cast call $ATTACK_REGISTRY "getAgreementState(address)(uint8)" $AGREEMENT_ADDRESS \
        --rpc-url https://testnet.battlechain.com:3051
