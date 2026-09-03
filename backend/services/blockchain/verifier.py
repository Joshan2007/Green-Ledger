"""
GreenLedger - Blockchain & Sepolia Testnet Verifier Service
Provides ABI metadata, network constants, and transaction verification logic.
"""

import re
from typing import Dict, Any

SEPOLIA_CHAIN_ID = 11155111
SEPOLIA_EXPLORER_BASE = "https://sepolia.etherscan.io"

# GreenBadge ERC-1155 Minimal Interface ABI for Client-Side Minting
GREEN_BADGE_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "account", "type": "address"},
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "bytes", "name": "data", "type": "bytes"}
        ],
        "name": "mint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "account", "type": "address"},
            {"internalType": "uint256", "name": "id", "type": "uint256"}
        ],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "id", "type": "uint256"}],
        "name": "uri",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "operator", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "from", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "id", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}
        ],
        "name": "TransferSingle",
        "type": "event"
    }
]


def verify_ethereum_address(address: str) -> bool:
    """Validates basic standard Ethereum hex address format."""
    return bool(re.match(r"^0x[a-fA-F0-9]{40}$", address))


def verify_tx_hash(tx_hash: str) -> bool:
    """Validates Ethereum transaction hash format."""
    return bool(re.match(r"^0x[a-fA-F0-9]{64}$", tx_hash))


def get_blockchain_metadata() -> Dict[str, Any]:
    """Returns network config, contract ABI, and explorer links."""
    return {
        "network": "Ethereum Sepolia Testnet",
        "chain_id": SEPOLIA_CHAIN_ID,
        "token_standard": "ERC-1155 (Multi-Token Standard)",
        "explorer_url": SEPOLIA_EXPLORER_BASE,
        "contract_abi": GREEN_BADGE_ABI,
        "testnet_disclaimer": "Sepolia is an Ethereum testnet. Tokens and test ETH have no real-world monetary value."
    }
