"""
Contract verification helper for the BattleChain block explorer.

Submits Vyper source code for verification via the Etherscan-compatible API,
then polls until the result is known. Mirrors verifyContract.ts from
battlechain-starter-hardhat but uses vyper-json format.
"""

import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

EXPLORER_API = "https://block-explorer-api.testnet.battlechain.com/api"
CHAIN_ID = "627"
API_KEY = "not-required"


def _sleep(seconds: float) -> None:
    time.sleep(seconds)


def _wait_for_indexing(address: str) -> None:
    """Poll until the explorer has indexed the contract."""
    deadline = time.time() + 60
    while time.time() < deadline:
        params = urllib.parse.urlencode({
            "module": "contract",
            "action": "getabi",
            "address": address,
            "chainId": CHAIN_ID,
            "apikey": API_KEY,
        })
        with urllib.request.urlopen(f"{EXPLORER_API}?{params}") as resp:
            data = json.loads(resp.read())
        if data.get("result") == "Contract source code not verified":
            return
        _sleep(3)
    print("  ⚠ Timed out waiting for indexer — submitting verification anyway")


def _poll_verification(guid: str) -> str:
    deadline = time.time() + 120
    while time.time() < deadline:
        _sleep(5)
        params = urllib.parse.urlencode({
            "module": "contract",
            "action": "checkverifystatus",
            "guid": guid,
            "chainId": CHAIN_ID,
            "apikey": API_KEY,
        })
        with urllib.request.urlopen(f"{EXPLORER_API}?{params}") as resp:
            data = json.loads(resp.read())
        result = data.get("result", "")
        if result not in ("Pending in queue", "In progress"):
            return result
    return "Timed out waiting for verification result"


def verify_contract(
    address: str,
    contract_fqn: str,
    compiler_version: str,
) -> None:
    """
    Verify a deployed Vyper contract on the BattleChain explorer.

    Args:
        address:          Deployed contract address.
        contract_fqn:     File path and contract name, e.g. "src/MockToken.vy:MockToken".
        compiler_version: Vyper version string, e.g. "0.4.0".
    """
    contract_file, contract_name = contract_fqn.split(":")
    source_path = Path(contract_file)
    if not source_path.exists():
        print(f"  ⚠ Source file not found: {contract_file} — skipping verification")
        return

    source_code = source_path.read_text()

    std_json = {
        "language": "Vyper",
        "sources": {
            contract_file: {"content": source_code},
        },
        "settings": {
            "outputSelection": {
                "*": ["evm.bytecode", "evm.deployedBytecode", "abi"],
            },
        },
    }

    print(f"  ⏳ Waiting for explorer to index {address}...")
    _wait_for_indexing(address)

    body = urllib.parse.urlencode({
        "contractaddress": address,
        "sourceCode": json.dumps(std_json),
        "codeformat": "vyper-json",
        "contractname": contract_fqn,
        "compilerversion": f"v{compiler_version}",
    }).encode()

    submit_url = (
        f"{EXPLORER_API}?module=contract&action=verifysourcecode"
        f"&chainId={CHAIN_ID}&apikey={API_KEY}"
    )
    req = urllib.request.Request(
        submit_url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        submit_data = json.loads(resp.read())

    if submit_data.get("status") != "1":
        print(f"  ✗ Verification submission failed: {submit_data.get('result')}")
        return

    print(f"  📤 Submitted for verification: {contract_fqn} at {address}")
    result = _poll_verification(submit_data["result"])

    if "already verified" in result.lower() or "pass" in result.lower():
        print(f"  ✅ Verified: {address}")
    else:
        print(f"  ✗ Verification failed: {result}")
