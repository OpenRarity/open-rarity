from dataclasses import dataclass


@dataclass
class Chain:
    """Class represents the blockchain and it's specific properties.

    Attributes
    ----------
        chain_id (int): internal indeitifer of the chain
        chain_name (str): name of the chain
    """

    chain_id: int
    chain_name: str
