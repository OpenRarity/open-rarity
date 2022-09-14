from open_rarity.models.token_identifier import (
    EVMContractTokenIdentifier,
    SolanaMintAddressTokenIdentifier,
)


class TestTokenIdentifier:
    def test_evm_token_identifier_hashable(self):
        address = "evm_address"
        tid_1 = EVMContractTokenIdentifier(contract_address=address, token_id=1)
        tid_2 = EVMContractTokenIdentifier(contract_address=address, token_id=2)
        dup_tid_1 = EVMContractTokenIdentifier(contract_address=address, token_id=1)
        assert {tid_1, tid_2, dup_tid_1} == {tid_1, tid_2}

        tid_dict = {tid_1: "value1", tid_2: "value2"}
        tid_dict.update({dup_tid_1: "updated_value1"})
        assert tid_dict == {tid_1: "updated_value1", tid_2: "value2"}

    def test_solana_token_identifier_hashable(self):
        tid_1 = SolanaMintAddressTokenIdentifier(mint_address="address1")
        tid_2 = SolanaMintAddressTokenIdentifier(mint_address="address2")
        dup_tid_1 = SolanaMintAddressTokenIdentifier(mint_address="address1")
        assert {tid_1, tid_2, dup_tid_1} == {tid_1, tid_2}

        tid_dict = {tid_1: "value1", tid_2: "value2"}
        tid_dict.update({dup_tid_1: "updated_value1"})
        assert tid_dict == {tid_1: "updated_value1", tid_2: "value2"}
