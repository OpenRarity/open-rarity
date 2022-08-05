from open_rarity.models.token import Token
from open_rarity.models.token_identifier import EVMContractTokenIdentifier
from open_rarity.models.token_metadata import (
    TokenMetadata,
    StringAttributeValue,
    AttributeName,
)
from open_rarity.models.collection import Collection
from open_rarity.models.chain import Chain
from open_rarity.models.token_standard import TokenStandard


def generate_uniform_attributes_count(
    attribute_count: int = 5,
    values_per_attribute: int = 10,
    token_total_supply: int = 10000,
) -> dict[str, dict[str, int]]:
    """generate trait counts with uniformly distributed attributes"""

    if token_total_supply % values_per_attribute > 0:
        raise Exception(
            """token_total_supply must be divisible by values_per_attribute
            for uniform count metadata"""
        )

    return {
        str(i): {
            str(j): token_total_supply // values_per_attribute
            for j in range(values_per_attribute)
        }
        for i in range(attribute_count)
    }


def generate_uniform_rarity_collection(
    attribute_count: int = 5,
    values_per_attribute: int = 10,
    token_total_supply: int = 10000,
) -> Collection:
    """generate a Collection with uniformly distributed attributes"""

    collection_attributes_count = generate_uniform_attributes_count(
        attribute_count, values_per_attribute, token_total_supply
    )

    token_list = []
    for i in range(token_total_supply):
        string_attribute_dict = {}

        for j in range(attribute_count):
            string_attribute_dict[AttributeName(j)] = StringAttributeValue(
                attribute_name=AttributeName(j),
                attribute_value=str(
                    i // (token_total_supply // values_per_attribute)
                ),
                count=token_total_supply // values_per_attribute,
            )

        token_list.append(
            Token(
                token_identifier=EVMContractTokenIdentifier(
                    contract_address="0x0", token_id=i
                ),
                token_standard=TokenStandard.ERC721,
                metadata=TokenMetadata(string_attributes=string_attribute_dict),
            )
        )

    return Collection(
        name="Uniform Rarity Collection",
        tokens=token_list,
        attributes_frequency_counts=collection_attributes_count,
    )


# NOTE: Do not understand what this is trying to do and we need to overhaul tests so....
# Going to interpret it.
# TODO [vicky, dan] To overhaul/fix this whole thing
def generate_onerare_attributes_count(
    attribute_count: int = 5,
    values_per_attribute: int = 10,
    token_total_supply: int = 10000,
) -> dict[str, dict[str, int]]:
    """generate trait counts with a single token with one rare attribute;
    otherwise uniformly distributed"""

    if (token_total_supply - 1) % (values_per_attribute - 1) > 0:
        raise Exception(
            """token_total_supply-1 must be divisible by values_per_attribute-1
            for onerare count metadata"""
        )

    collection_attributes_count = generate_uniform_attributes_count(
        attribute_count, values_per_attribute - 1, token_total_supply - 1
    )

    # Make it such that this one rare token has a unique value for all attribute
    for i in range(attribute_count):
        collection_attributes_count[str(i)][str(values_per_attribute)] = 1

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

    for k in range(token_total_supply):
        string_attribute_dict = {}

        for i in range(attribute_count - 1):
            string_attribute_dict[AttributeName(i)] = StringAttributeValue(
                attribute_name=AttributeName(i),
                attribute_value=str(
                    k // (token_total_supply // values_per_attribute)
                ),
                count=token_total_supply // values_per_attribute,
            )

        if k < token_total_supply - 1:
            string_attribute_dict[
                AttributeName(attribute_count - 1)
            ] = StringAttributeValue(
                attribute_name=AttributeName(attribute_count - 1),
                attribute_value=str(
                    k
                    // ((token_total_supply - 1) // (values_per_attribute - 1))
                ),
                count=((token_total_supply - 1) // (values_per_attribute - 1)),
            )
        else:
            string_attribute_dict[
                AttributeName(attribute_count - 1)
            ] = StringAttributeValue(
                attribute_name=AttributeName(attribute_count - 1),
                attribute_value=str(values_per_attribute - 1),
                count=1,
            )

        token_list.append(
            Token(
                token_identifier=EVMContractTokenIdentifier(
                    contract_address="0x0", token_id=k
                ),
                token_standard=TokenStandard.ERC721,
                metadata=TokenMetadata(string_attributes=string_attribute_dict),
            )
        )

    return Collection(
        name="One Rare Rarity Collection",
        tokens=token_list,
        attributes_frequency_counts=collection_attributes_count,
    )
