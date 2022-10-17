from random import shuffle

from open_rarity.models.collection import Collection
from open_rarity.models.token import Token
from open_rarity.models.token_identifier import (
    EVMContractTokenIdentifier,
    SolanaMintAddressTokenIdentifier,
)
from open_rarity.models.token_metadata import (
    AttributeName,
    NumericAttribute,
    StringAttribute,
    TokenMetadata,
)
from open_rarity.models.token_standard import TokenStandard


def create_evm_token(
    token_id: int,
    contract_address: str = "0xaaa",
    token_standard: TokenStandard = TokenStandard.ERC721,
    metadata: TokenMetadata | None = None,
) -> Token:
    metadata = metadata or TokenMetadata()
    return Token(
        token_identifier=EVMContractTokenIdentifier(
            contract_address=contract_address, token_id=token_id
        ),
        token_standard=token_standard,
        metadata=metadata,
    )


def create_string_evm_token(
    token_id: int,
    contract_address: str = "0xaaa",
    token_standard: TokenStandard = TokenStandard.ERC721,
) -> Token:
    string_metadata = TokenMetadata(
        string_attributes={"test name": StringAttribute("test name", "test value")}
    )
    return create_evm_token(
        token_id=token_id,
        contract_address=contract_address,
        token_standard=token_standard,
        metadata=string_metadata,
    )


def create_numeric_evm_token(
    token_id: int,
    contract_address: str = "0xaaa",
    token_standard: TokenStandard = TokenStandard.ERC721,
) -> Token:
    numeric_metadata = TokenMetadata(
        numeric_attributes={"test": NumericAttribute("test", 1)}
    )
    return create_evm_token(
        token_id=token_id,
        contract_address=contract_address,
        token_standard=token_standard,
        metadata=numeric_metadata,
    )


def uniform_rarity_tokens(
    attribute_count: int = 5,
    values_per_attribute: int = 10,
    token_total_supply: int = 10000,
):
    tokens = []
    for token_id in range(token_total_supply):
        string_attribute_dict = {}

        # Construct attributes for the token such that the first bucket
        # gets the first possible value for every attribute, second bucket
        # gets the second possible value for every attribute, etc.
        for attr_name in range(attribute_count):
            string_attribute_dict[str(attr_name)] = StringAttribute(
                name=str(attr_name),
                value=str(token_id // (token_total_supply // values_per_attribute)),
            )

        tokens.append(
            Token(
                token_identifier=EVMContractTokenIdentifier(
                    contract_address="0x0", token_id=token_id
                ),
                token_standard=TokenStandard.ERC721,
                metadata=TokenMetadata(string_attributes=string_attribute_dict),
            )
        )
    return tokens


def generate_uniform_rarity_collection(
    attribute_count: int = 5,
    values_per_attribute: int = 10,
    token_total_supply: int = 10000,
) -> Collection:
    """generate a Collection with uniformly distributed attributes
    where each token gets <attribute_count> attributes.

    Every bucket of (token_total_supply // values_per_attribute) gets the same
    attributes.
    """
    tokens = uniform_rarity_tokens(
        token_total_supply=token_total_supply,
        attribute_count=attribute_count,
        values_per_attribute=values_per_attribute,
    )

    return Collection(name="Uniform Rarity Collection", tokens=tokens)


def onerare_rarity_tokens(
    attribute_count: int = 3,
    values_per_attribute: int = 10,
    token_total_supply: int = 10000,
) -> Collection:
    """generate a Collection with a single token with one rare attribute;
    otherwise uniformly distributed attributes.

    For default params:
        - every bundle of 1111 tokens have exactly the same attributes
        - the first 9,999 tokens all have attributes with the same probabilities
        - the last token has all unique attributes
    Collection attributes frequency:
    {
        '0': {
            '-1': 1111, '0': 1111, '1': 1111, '2': 1111, '3': 1111,
            '4': 1111, '5': 1111, '6': 1111, '7': 1111, '9': 1
        },
        '1': {
            '-1': 1111, '0': 1111, '1': 1111, '2': 1111, '3': 1111,
            '4': 1111, '5': 1111, '6': 1111, '7': 1111, '9': 1
        },
        '2': {
            '-1': 1111, '0': 1111, '1': 1111, '2': 1111, '3': 1111,
            '4': 1111, '5': 1111, '6': 1111, '7': 1111, '9': 1
        },
        'meta_trait:trait_count': {'3': 10000}
    }
    """
    tokens = []

    # Create attributes for all the uniform tokens
    for token_id in range(token_total_supply - 1):
        string_attribute_dict = {}

        for attr_name in range(attribute_count):
            string_attribute_dict[AttributeName(attr_name)] = StringAttribute(
                name=AttributeName(attr_name),
                value=str(
                    token_id // (token_total_supply // (values_per_attribute - 1)) - 1
                ),
            )

        tokens.append(
            Token(
                token_identifier=EVMContractTokenIdentifier(
                    contract_address="0x0", token_id=token_id
                ),
                token_standard=TokenStandard.ERC721,
                metadata=TokenMetadata(string_attributes=string_attribute_dict),
            )
        )

    # Create the attributes for the last rare token
    rare_token_string_attribute_dict = {}
    for attr_name in range(attribute_count):
        rare_token_string_attribute_dict[AttributeName(attr_name)] = StringAttribute(
            name=AttributeName(attr_name),
            value=str(values_per_attribute),
        )

    tokens.append(
        Token(
            token_identifier=EVMContractTokenIdentifier(
                contract_address="0x0", token_id=token_total_supply - 1
            ),
            token_standard=TokenStandard.ERC721,
            metadata=TokenMetadata(string_attributes=rare_token_string_attribute_dict),
        )
    )

    return tokens


def generate_onerare_rarity_collection(
    attribute_count: int = 3,
    values_per_attribute: int = 10,
    token_total_supply: int = 10000,
) -> Collection:
    """generate a Collection with a single token with one rare attribute;
    otherwise uniformly distributed attributes.

    For default params:
        - every bundle of 1111 tokens have exactly the same attributes
        - the first 9,999 tokens all have attributes with the same probabilities
        - the last token has all unique attributes
    Collection attributes frequency:
    {
        '0': {
            '-1': 1111, '0': 1111, '1': 1111, '2': 1111, '3': 1111,
            '4': 1111, '5': 1111, '6': 1111, '7': 1111, '9': 1
        },
        '1': {
            '-1': 1111, '0': 1111, '1': 1111, '2': 1111, '3': 1111,
            '4': 1111, '5': 1111, '6': 1111, '7': 1111, '9': 1
        },
        '2': {
            '-1': 1111, '0': 1111, '1': 1111, '2': 1111, '3': 1111,
            '4': 1111, '5': 1111, '6': 1111, '7': 1111, '9': 1
        },
        'meta_trait:trait_count': {'3': 10000}
    }
    """
    tokens = onerare_rarity_tokens(
        token_total_supply=token_total_supply,
        attribute_count=attribute_count,
        values_per_attribute=values_per_attribute,
    )

    return Collection(name="One Rare Rarity Collection", tokens=tokens)


def generate_collection_with_token_traits(
    tokens_traits: list[dict[str, str | int]],
    token_identifier_type: str = "evm_contract",
) -> Collection:
    tokens = []
    for idx, token_traits in enumerate(tokens_traits):
        match token_identifier_type:
            case EVMContractTokenIdentifier.identifier_type:
                identifier_type = EVMContractTokenIdentifier(
                    contract_address="0x0", token_id=idx
                )
                token_standard = TokenStandard.ERC721
            case SolanaMintAddressTokenIdentifier.identifier_type:
                identifier_type = SolanaMintAddressTokenIdentifier(
                    mint_address=f"Fake-Address-{idx}"
                )
                token_standard = TokenStandard.METAPLEX_NON_FUNGIBLE
            case _:
                raise ValueError(
                    f"Unexpected token identifier type: {token_identifier_type}"
                )

        tokens.append(
            Token(
                token_identifier=identifier_type,
                token_standard=token_standard,
                metadata=TokenMetadata.from_attributes(token_traits),
            )
        )

    return Collection(name="My collection", tokens=tokens)


def get_mixed_trait_spread(
    max_total_supply: int = 10000,
) -> dict[str, dict[str, float]]:
    # dict[attribute name, dict[attribute value, items with that attribute]]
    return {
        "hat": {
            "cap": int(max_total_supply * 0.2),
            "beanie": int(max_total_supply * 0.3),
            "hood": int(max_total_supply * 0.45),
            "visor": int(max_total_supply * 0.05),
        },
        "shirt": {
            "white-t": int(max_total_supply * 0.8),
            "vest": int(max_total_supply * 0.2),
        },
        "special": {
            "true": int(max_total_supply * 0.1),
            "null": int(max_total_supply * 0.9),
        },
    }


def generate_mixed_collection(max_total_supply: int = 10000):
    """Generates a collection such that the tokens have traits with
    get_mixed_trait_spread() spread of trait occurrences:
     "hat":
       20% have "cap",
       30% have "beanie",
       45% have "hood",
       5% have "visor"
     "shirt":
       80% have "white-t",
       20% have "vest"
     "special":
       1% have "special"
       others "null"
    Note: The token ids are shuffled and it is random order in terms of
    which trait/value combo they get.
    """
    if max_total_supply % 10 != 0 or max_total_supply < 100:
        raise Exception("only multiples of 10 and greater than 100 please.")

    token_ids = list(range(max_total_supply))
    shuffle(token_ids)

    def get_trait_value(trait_spread, idx):
        trait_value_idx = 0
        max_idx_for_trait_value = trait_spread[trait_value_idx][1]
        while idx >= max_idx_for_trait_value:
            trait_value_idx += 1
            max_idx_for_trait_value += trait_spread[trait_value_idx][1]
        return trait_spread[trait_value_idx][0]

    token_ids_to_traits = {}
    for idx, token_id in enumerate(token_ids):
        traits = {
            trait_name: get_trait_value(list(trait_value_to_percent.items()), idx)
            for trait_name, trait_value_to_percent in get_mixed_trait_spread().items()
        }

        token_ids_to_traits[token_id] = traits

    return generate_collection_with_token_traits(
        [token_ids_to_traits[token_id] for token_id in range(max_total_supply)]
    )
