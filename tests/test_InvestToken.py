from brownie import InvestToken, accounts
import pytest


def test_deploy_totalSupply():
    # Arrange
    account = accounts[0]
    # Act
    inv_tok = InvestToken.deploy("InvestToken", "IT", {"from": account})
    starting_value = inv_tok.totalSupply()
    # Assert
    assert starting_value == 0


def test_owner():
    # Arrange
    account = accounts[0]
    inv_tok = InvestToken.deploy("InvestToken", "IT", {"from": account})
    # Act
    contract_owner = inv_tok.owner()
    # Assert
    assert contract_owner == account


def test_mint_balanceOf():
    # Arrange
    account = accounts[0]
    inv_tok = InvestToken.deploy("InvestToken", "IT", {"from": account})
    # Act
    account_invst = accounts[1]
    amount = 10
    inv_tok.mint(account_invst, amount, {"from": account})
    # Assert
    assert inv_tok.balanceOf(account_invst) == amount


def test_mint_disburse_one_acc_withdraw():
    # Arrange
    account = accounts[0]
    inv_tok = InvestToken.deploy("InvestToken", "IT", {"from": account})
    acc_invst = accounts[1]
    acc_balance_pre_withdraw = acc_invst.balance()
    inv_tok.mint(acc_invst, 10, {"from": account})
    # Act
    inv_tok.disburse({"from": account, "value": 10})
    inv_tok.withdraw({"from": acc_invst})
    acc_balance_with = acc_invst.balance()
    # Assert
    assert acc_balance_pre_withdraw + 10 == acc_balance_with


def test_transfer():
    # Arrange
    account = accounts[0]
    inv_tok = InvestToken.deploy("InvestToken", "IT", {"from": account})
    account_invst = accounts[1]
    amount_mint = 10
    inv_tok.mint(account_invst, amount_mint, {"from": account})

    # Act
    account_invst_new = accounts[2]
    inv_tok.transfer(account_invst_new, amount_mint, {"from": account_invst})

    # Assert
    assert inv_tok.balanceOf(account_invst_new) == amount_mint


def test_transfer_from():
    # Arrange
    account = accounts[0]
    inv_tok = InvestToken.deploy("InvestToken", "IT", {"from": account})
    account_invst = accounts[1]
    amount_mint = 10
    inv_tok.mint(account_invst, amount_mint, {"from": account})

    # Act
    account_invst_new = accounts[2]

    tx = inv_tok.approve(account, amount_mint, {"from": account_invst})
    tx.wait(1)
    inv_tok.transferFrom(
        account_invst, account_invst_new, amount_mint, {"from": account}
    )

    # Assert
    assert inv_tok.balanceOf(account_invst_new) == amount_mint


def test_disburse_transfer():
    # Arrane
    account = accounts[0]
    inv_token = InvestToken.deploy("InvestToken", "IT", {"from": account})
    account_invst = accounts[1]
    account_inv_balance_pre = account_invst.balance()
    ammount_mint = 234
    inv_token.mint(account_invst, ammount_mint, {"from": account})
    ammount_disburse = 9898398584975935
    inv_token.disburse({"from": account, "value": ammount_disburse})

    # Act
    account_invst_new = accounts[2]
    inv_token.transfer(account_invst_new, 1, {"from": account_invst})

    # Assert
    assert (
        account_inv_balance_pre + ammount_disburse >= account_invst.balance()
        and account_inv_balance_pre + ammount_disburse <= account_invst.balance() + 1
    )


def test_disburse_transferFrom():
    # Arrane
    account = accounts[0]
    inv_token = InvestToken.deploy("InvestToken", "IT", {"from": account})
    account_invst = accounts[1]
    account_inv_balance_pre = account_invst.balance()
    ammount_mint = 43567
    inv_token.mint(account_invst, ammount_mint, {"from": account})
    ammount_disburse = 987656789654
    inv_token.disburse({"from": account, "value": ammount_disburse})

    # Act
    account_invst_new = accounts[2]

    tx = inv_token.approve(account, ammount_mint, {"from": account_invst})
    tx.wait(1)
    inv_token.transferFrom(
        account_invst, account_invst_new, ammount_mint, {"from": account}
    )

    # Assert
    assert (
        account_inv_balance_pre + ammount_disburse >= account_invst.balance()
        and account_inv_balance_pre + ammount_disburse <= account_invst.balance() + 1
    )


@pytest.mark.parametrize(
    "j, weights",
    [
        (45657567745, [1, 2, 3, 4, 5, 6, 7, 8, 9]),
        (79000000000000, [10, 20, 35, 14, 15, 6, 77, 98, 900]),
        (75, [534, 345, 456, 45, 78, 987, 901, 1122, 1]),
        (500000, [927, 603, 25, 24, 86, 1, 2, 3, 1]),
        (98345098304985345, [1, 2, 3, 4, 5, 6, 7, 8, 9]),
        (10000000000000, [10, 20, 35, 14, 15, 6, 77, 98, 900]),
        (1000, [534, 345, 456, 45, 78, 987, 901, 1122, 1]),
        (1, [927, 603, 25, 24, 86, 1, 2, 3, 1]),
    ],
)
def test_mint_disburse_nine_acc_withdraw(j, weights):
    # Arrange
    account = accounts[0]
    inv_tok = InvestToken.deploy("InvestToken", "IT", {"from": account})
    acc_invst = [accounts[i] for i in range(1, 10)]
    acc_balance_pre_withdraw = [acc_invst[i].balance() for i in range(9)]
    for i, k in zip(range(9), weights):
        inv_tok.mint(acc_invst[i], k, {"from": account})
    # Act
    disburse_amm = j
    inv_tok.disburse({"from": account, "value": disburse_amm})
    for i in range(9):
        inv_tok.withdraw({"from": acc_invst[i]})
    acc_balance_with = [acc_invst[i].balance() for i in range(9)]
    # Assert
    for i, k in zip(range(9), weights):
        assert (
            acc_balance_pre_withdraw[i] + k * disburse_amm / sum(weights)
            >= acc_balance_with[i]
        ) and (
            acc_balance_pre_withdraw[i] + k * disburse_amm / sum(weights)
            <= acc_balance_with[i] + 2
        )


@pytest.mark.parametrize(
    "disb_1, disb_2, weights",
    [
        (45657567745, 1, [1, 2, 3, 4, 5, 6, 7, 8, 9]),
        (79000000000000, 1000, [10, 20, 35, 14, 15, 6, 77, 98, 900]),
        (75, 10000000000000, [534, 345, 456, 45, 78, 987, 901, 1122, 1]),
        (500000, 98345098304985345, [927, 603, 25, 24, 86, 1, 2, 3, 1]),
        (98345098304985345, 500000, [1, 2, 3, 4, 5, 6, 7, 8, 9]),
        (10000000000000, 75, [10, 20, 35, 14, 15, 6, 77, 98, 900]),
        (1000, 79000000000000, [534, 345, 456, 45, 78, 987, 901, 1122, 1]),
        (1, 45657567745, [927, 603, 25, 24, 86, 1, 2, 3, 1]),
    ],
)
def test_disburse_withdraw_withdraw_disburse_withdraw(disb_1, disb_2, weights):
    # Arrange
    account = accounts[0]
    inv_tok = InvestToken.deploy("InvestToken", "IT", {"from": account})
    acc_invst = [accounts[i] for i in range(1, 10)]
    acc_balance_pre_withdraw = [acc_invst[i].balance() for i in range(9)]
    for i, j in zip(range(9), weights):
        inv_tok.mint(acc_invst[i], j, {"from": account})
    # Act I
    disburse_amm = disb_1
    inv_tok.disburse({"from": account, "value": disburse_amm})
    for i in range(4):
        inv_tok.withdraw({"from": acc_invst[i]})
    for i in range(4):
        inv_tok.withdraw({"from": acc_invst[i]})
    acc_balance_with = [acc_invst[i].balance() for i in range(9)]
    # Assert I
    for i, k in zip(range(4), weights):
        assert (
            acc_balance_pre_withdraw[i] + k * disburse_amm / sum(weights)
            >= acc_balance_with[i]
        ) and (
            acc_balance_pre_withdraw[i] + k * disburse_amm / sum(weights)
            <= acc_balance_with[i] + 2
        )
    # Act II
    disburse_amm = disb_2
    inv_tok.disburse({"from": account, "value": disburse_amm})
    for i in range(9):
        inv_tok.withdraw({"from": acc_invst[i]})
    acc_balance_with = [acc_invst[i].balance() for i in range(9)]
    # Assert II
    for i, k in zip(range(9), weights):
        assert (
            acc_balance_pre_withdraw[i] + k * (disb_1 + disb_2) / sum(weights)
            >= acc_balance_with[i]
        ) and (
            acc_balance_pre_withdraw[i] + k * (disb_1 + disb_2) / sum(weights)
            <= acc_balance_with[i] + 2
        )
