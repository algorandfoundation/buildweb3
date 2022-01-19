# This example is provided for informational purposes only and has not been audited for security.

from pyteal import *

# Address of the seller of the asset
seller = Addr("4O6BRAPVLX5ID23AZWV33TICD35TI6JWOHXVLPGO4VRJATO6MZZQRKC7RI")
asset_id = 14035004  # ID of the official buildweb3 asset
asset_price = 4200000  # price of 1 asset = 4.2 Algos


def smart_contract(tmpl_seller=seller,
                   tmpl_asset_id=asset_id,
                   tmpl_asset_price=asset_price,
                   tmpl_max_fee=1000):
    # Check that the fee is not too high
    # otherwise an attacker could burn all the Algos of the seller
    # by choosing an abusive fee
    fee_cond = Txn.fee() <= Int(tmpl_max_fee)

    # Check that the approved transaction is the second one
    # of a group of two transactions
    group_cond = And(
        Global.group_size() == Int(2),
        Txn.group_index() == Int(1)
    )

    # Check that the first transaction is a payment
    # of tmpl_asset_price Algos to the seller
    first_txn_cond = And(
        Gtxn[0].type_enum() == TxnType.Payment,
        Gtxn[0].amount() == Int(tmpl_asset_price),
        Gtxn[0].receiver() == tmpl_seller
    )

    # Check that the second transaction (i.e., the one being approved)
    # is a transfer of 1 unit of asset
    second_txn_cond = And(
        Txn.type_enum() == TxnType.AssetTransfer,
        Txn.asset_amount() == Int(1),
        Txn.xfer_asset() == Int(tmpl_asset_id),
        # Check that the remaining assets are not sent anywhere
        Txn.asset_close_to() == Global.zero_address(),
        # Check that the account is not rekeyed
        # see https://developer.algorand.org/docs/features/accounts/rekey
        Txn.rekey_to() == Global.zero_address(),
    )

    return And(
        fee_cond,
        group_cond,
        first_txn_cond,
        second_txn_cond
    )


if __name__ == "__main__":
    print(compileTeal(smart_contract(), Mode.Signature))
