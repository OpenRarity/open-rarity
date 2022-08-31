from open_rarity.models.token import Token
from open_rarity.models.token_identifier import EVMContractTokenIdentifier
from open_rarity.models.token_metadata import (
    NumericAttribute,
    TokenMetadata,
    StringAttribute,
    AttributeName,
)
from open_rarity.models.collection import Collection
from open_rarity.models.token_standard import TokenStandard
from random import shuffle


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
    """Generate a Collection with every token except a single token has uniformly
    distributed attributes. The single rare token will be the only token that
    exhibits a unique attribute name/value combo for all attributes.
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
    tokens_traits: list[dict[str, str | int]]
) -> Collection:
    tokens = []
    attributes_frequency_counts = {}
    for idx, token_traits in enumerate(tokens_traits):
        token_string_attributes: dict[str, StringAttribute] = {}
        token_number_attributes: dict[str, NumericAttribute] = {}

        for attribute_name, attribute_value in token_traits.items():
            # Update collection attributes frequency based on tokens' traits
            attributes_frequency_counts.setdefault(
                attribute_name, {}
            ).setdefault(attribute_value, 0)
            attributes_frequency_counts[attribute_name][attribute_value] += 1

            # Create the string attributes for token
            if isinstance(attribute_value, str):
                token_string_attributes[attribute_name] = StringAttribute(
                    name=attribute_name, value=attribute_value
                )
            else:
                token_number_attributes[attribute_name] = NumericAttribute(
                    name=attribute_name, value=attribute_value
                )

        # Add the tokens
        tokens.append(
            Token(
                token_identifier=EVMContractTokenIdentifier(
                    contract_address="0x0", token_id=idx
                ),
                token_standard=TokenStandard.ERC721,
                metadata=TokenMetadata(
                    string_attributes=token_string_attributes,
                    numeric_attributes=token_number_attributes,
                ),
            )
        )

    return Collection(
        name="My collection",
        tokens=tokens,
        attributes_frequency_counts=attributes_frequency_counts,
    )


def get_mixed_trait_spread(
    max_total_supply: int = 10000,
) -> dict[str, dict[str, float]]:
    # dict[attribute name, dict[attribute value, % of max supply]]
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
       others none
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
            trait_name: get_trait_value(
                list(trait_value_to_percent.items()), idx
            )
            for trait_name, trait_value_to_percent in get_mixed_trait_spread().items()
        }

        token_ids_to_traits[token_id] = traits

    return generate_collection_with_token_traits(
        [token_ids_to_traits[token_id] for token_id in range(max_total_supply)]
    )
