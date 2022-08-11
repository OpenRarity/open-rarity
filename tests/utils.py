from open_rarity.models.token import Token
from open_rarity.models.token_identifier import EVMContractTokenIdentifier
from open_rarity.models.token_metadata import (
    TokenMetadata,
    StringAttribute,
    AttributeName,
)
from open_rarity.models.collection import Collection
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


def generate_uniform_attributes_count(
    attribute_count: int = 5,
    values_per_attribute: int = 10,
    token_total_supply: int = 10000,
) -> dict[str, dict[str, int]]:
    """Generate trait counts with uniformly distributed attributes
    Example output(with default inputs):
    {
        "0": {"0": 1,000, "1": 1,000, "2": 1,000, ... "9": 1,000},
        ...
        "4": {"0": 1,000, "1": 1,000, "2": 1,000, ... "9": 1,000},
    }
    This means every token in the 10,000 collection will have exactly
    <attribute_count> traits.

    """

    if token_total_supply % values_per_attribute > 0:
        raise Exception(
            """token_total_supply must be divisible by values_per_attribute
            for uniform count metadata"""
        )

    return {
        str(attr_name): {
            str(attr_value): token_total_supply // values_per_attribute
            for attr_value in range(values_per_attribute)
        }
        for attr_name in range(attribute_count)
    }


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

    collection_attributes_count = generate_uniform_attributes_count(
        attribute_count, values_per_attribute, token_total_supply
    )

    token_list = []
    for token_id in range(token_total_supply):
        string_attribute_dict = {}

        # Construct attributes for the token such that the first bucket
        # gets the first possible value for every attribute, second bucket
        # gets the second possible value for every attribute, etc.
        for attr_name in range(attribute_count):
            string_attribute_dict[str(attr_name)] = StringAttribute(
                name=str(attr_name),
                value=str(
                    token_id // (token_total_supply // values_per_attribute)
                ),
            )

        token_list.append(
            Token(
                token_identifier=EVMContractTokenIdentifier(
                    contract_address="0x0", token_id=token_id
                ),
                token_standard=TokenStandard.ERC721,
                metadata=TokenMetadata(
                    string_attributes=string_attribute_dict
                ),
            )
        )

    return Collection(
        name="Uniform Rarity Collection",
        tokens=token_list,
        attributes_frequency_counts=collection_attributes_count,
    )


def generate_onerare_attributes_count(
    attribute_count: int = 5,
    values_per_attribute: int = 10,
    token_total_supply: int = 10000,
) -> dict[str, dict[str, int]]:
    """Generate a Collection with every token except a single token has uniformly distributed
    attributes. The single rare token will be the only token that exhibits a unique attribute name/value
    combo for all attributes.
    """

    if (token_total_supply - 1) % (values_per_attribute - 1) > 0:
        raise Exception(
            """token_total_supply-1 must be divisible by values_per_attribute-1
            for onerare count metadata"""
        )

    # Start with a uniform distribution for the entire token supply minus one token.
    collection_attributes_count = generate_uniform_attributes_count(
        attribute_count, values_per_attribute - 1, token_total_supply - 1
    )

    # Make it such that this last token is a rare token with a unique value for
    # all attributes.
    for attr_name in range(attribute_count):
        attr_value = str(values_per_attribute - 1)
        collection_attributes_count[str(attr_name)][attr_value] = 1

    return collection_attributes_count


def generate_onerare_rarity_collection(
    attribute_count: int = 5,
    values_per_attribute: int = 10,
    token_total_supply: int = 10000,
) -> Collection:
    """generate a Collection with a single token with one rare attribute;
    otherwise uniformly distributed attributes"""

    collection_attributes_count = generate_onerare_attributes_count(
        attribute_count, values_per_attribute, token_total_supply
    )

    token_list = []

    # Create attributes for all the uniform tokens
    for token_id in range(token_total_supply - 1):
        string_attribute_dict = {}

        for attr_name in range(attribute_count):
            string_attribute_dict[AttributeName(attr_name)] = StringAttribute(
                name=AttributeName(attr_name),
                value=str(
                    token_id
                    // (token_total_supply - 1 // values_per_attribute - 1)
                ),
            )

        token_list.append(
            Token(
                token_identifier=EVMContractTokenIdentifier(
                    contract_address="0x0", token_id=token_id
                ),
                token_standard=TokenStandard.ERC721,
                metadata=TokenMetadata(
                    string_attributes=string_attribute_dict
                ),
            )
        )

    # Create the attributes for the last rare token
    rare_token_string_attribute_dict = {}
    for attr_name in range(attribute_count):
        rare_token_string_attribute_dict[
            AttributeName(attr_name)
        ] = StringAttribute(
            name=AttributeName(attr_name),
            value=str(values_per_attribute - 1),
        )

    token_list.append(
        Token(
            token_identifier=EVMContractTokenIdentifier(
                contract_address="0x0", token_id=token_total_supply - 1
            ),
            token_standard=TokenStandard.ERC721,
            metadata=TokenMetadata(
                string_attributes=rare_token_string_attribute_dict
            ),
        )
    )

    return Collection(
        name="One Rare Rarity Collection",
        tokens=token_list,
        attributes_frequency_counts=collection_attributes_count,
    )


def generate_collection_with_token_traits(
    tokens_traits: list[dict[str, str]]
) -> Collection:
    tokens = []
    attributes_frequency_counts = {}
    for idx, token_traits in enumerate(tokens_traits):
        token_attributes: dict[str, StringAttribute] = {}
        for attribute_name, attribute_value in token_traits.items():
            # Update collection attributes frequency based on tokens' traits
            attributes_frequency_counts.setdefault(
                attribute_name, {}
            ).setdefault(attribute_value, 0)
            attributes_frequency_counts[attribute_name][attribute_value] += 1

            # Create the string attributes for token
            token_attributes[attribute_name] = StringAttribute(
                name=attribute_name, value=attribute_value
            )

        # Add the tokens
        tokens.append(
            Token(
                token_identifier=EVMContractTokenIdentifier(
                    contract_address="0x0", token_id=idx
                ),
                token_standard=TokenStandard.ERC721,
                metadata=TokenMetadata(string_attributes=token_attributes),
            )
        )

    return Collection(
        name="My collection",
        tokens=tokens,
        attributes_frequency_counts=attributes_frequency_counts,
    )
