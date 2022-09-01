from enum import Enum


class TokenStandard(Enum):
    """Enum class representing the interface or standard that
    a token is respecting. Each chain may have their own token standards.
    """

    # -- Ethereum/EVM standards
    # https://eips.ethereum.org/EIPS/eip-721
    ERC721 = "erc721"
    # https://eips.ethereum.org/EIPS/eip-1155
    ERC1155 = "erc1155"

    # -- Solana token standards
    # https://docs.metaplex.com/programs/token-metadata/token-standard
    METAPLEX_NON_FUNGIBLE = "metaplex_non_fungible"
