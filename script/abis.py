# BattleChain protocol contract addresses and ABI fragments (chain ID 627 = testnet).
# Mirror of abis.ts from battlechain-starter-hardhat.

BC_DEPLOYER          = "0x8f57054CBa2021bEE15631067dd7B7E0B43F17Dc"
BC_AGREEMENT_FACTORY = "0x0EbBEeB3aBeF51801a53Fdd1fb263Ac0f2E3Ed36"
BC_REGISTRY          = "0xCb2A561395118895e2572A04C2D8AB8eCA8d7E5D"
BC_ATTACK_REGISTRY   = "0x9E62988ccA776ff6613Fa68D34c9AB5431Ce57e1"
BC_CAIP2_CHAIN_ID    = "eip155:627"
BC_SAFE_HARBOR_URI   = "ipfs://bafkreifgln3ir67woluatpwn3b65gjkrbmoq6jgzzotm3anas3vvq4yp4m"

AGREEMENT_FACTORY_ABI = [
    {
        "name": "create",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {
                "name": "details",
                "type": "tuple",
                "components": [
                    {"name": "protocolName", "type": "string"},
                    {
                        "name": "contactDetails",
                        "type": "tuple[]",
                        "components": [
                            {"name": "name", "type": "string"},
                            {"name": "contact", "type": "string"},
                        ],
                    },
                    {
                        "name": "chains",
                        "type": "tuple[]",
                        "components": [
                            {"name": "assetRecoveryAddress", "type": "string"},
                            {
                                "name": "accounts",
                                "type": "tuple[]",
                                "components": [
                                    {"name": "accountAddress", "type": "string"},
                                    {"name": "childContractScope", "type": "uint8"},
                                ],
                            },
                            {"name": "caip2ChainId", "type": "string"},
                        ],
                    },
                    {
                        "name": "bountyTerms",
                        "type": "tuple",
                        "components": [
                            {"name": "bountyPercentage", "type": "uint256"},
                            {"name": "bountyCapUsd", "type": "uint256"},
                            {"name": "retainable", "type": "bool"},
                            {"name": "identity", "type": "uint8"},
                            {"name": "diligenceRequirements", "type": "string"},
                            {"name": "aggregateBountyCapUsd", "type": "uint256"},
                        ],
                    },
                    {"name": "agreementURI", "type": "string"},
                ],
            },
            {"name": "owner", "type": "address"},
            {"name": "salt", "type": "bytes32"},
        ],
        "outputs": [{"name": "agreementAddress", "type": "address"}],
    },
]

AGREEMENT_ABI = [
    {
        "name": "extendCommitmentWindow",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [{"name": "newCantChangeUntil", "type": "uint256"}],
        "outputs": [],
    },
]

REGISTRY_ABI = [
    {
        "name": "adoptSafeHarbor",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [{"name": "agreementAddress", "type": "address"}],
        "outputs": [],
    },
]

ATTACK_REGISTRY_ABI = [
    {
        "name": "requestUnderAttack",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [{"name": "agreementAddress", "type": "address"}],
        "outputs": [],
    },
]
