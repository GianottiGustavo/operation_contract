from brownie import InvestToken, accounts
import pytest


@pytest.fixture
def inv_tok() -> InvestToken:
    account = accounts[0]
    inv_tok = InvestToken.deploy("InvestToken", "IT", {"from": account})
    return inv_tok


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


def test_mint_balanceOf(inv_tok):
    # Arrange/Act
    account_invst = accounts[1]
    amount = 10
    inv_tok.mint(account_invst, amount, {"from": inv_tok.owner()})
    # Assert
    assert inv_tok.balanceOf(account_invst) == amount


def test_mint_disburse_one_acc_withdraw(inv_tok):
    # Arrange
    acc_invst = accounts[1]
    acc_balance_pre_withdraw = acc_invst.balance()
    inv_tok.mint(acc_invst, 10, {"from": inv_tok.owner()})
    # Act
    inv_tok.disburse({"from": inv_tok.owner(), "value": 10})
    inv_tok.withdraw({"from": acc_invst})
    acc_balance_with = acc_invst.balance()
    # Assert
    assert acc_balance_pre_withdraw + 10 == acc_balance_with


def test_transfer(inv_tok):
    # Arrange
    account_invst = accounts[1]
    amount_mint = 10
    inv_tok.mint(account_invst, amount_mint, {"from": inv_tok.owner()})

    # Act
    account_invst_new = accounts[2]
    inv_tok.transfer(account_invst_new, amount_mint, {"from": account_invst})

    # Assert
    assert inv_tok.balanceOf(account_invst_new) == amount_mint


def test_transfer_from(inv_tok):
    # Arrange
    account_invst = accounts[1]
    amount_mint = 10
    inv_tok.mint(account_invst, amount_mint, {"from": inv_tok.owner()})

    # Act
    account_invst_new = accounts[2]

    tx = inv_tok.approve(inv_tok.owner(), amount_mint, {"from": account_invst})
    tx.wait(1)
    inv_tok.transferFrom(
        account_invst, account_invst_new, amount_mint, {"from": inv_tok.owner()}
    )

    # Assert
    assert inv_tok.balanceOf(account_invst_new) == amount_mint


def test_disburse_transfer(inv_tok):
    # Arrane
    account_invst = accounts[1]
    account_inv_balance_pre = account_invst.balance()
    ammount_mint = 234
    inv_tok.mint(account_invst, ammount_mint, {"from": inv_tok.owner()})
    ammount_disburse = 9898398584975935
    inv_tok.disburse({"from": inv_tok.owner(), "value": ammount_disburse})

    # Act
    account_invst_new = accounts[2]
    inv_tok.transfer(account_invst_new, 1, {"from": account_invst})

    # Assert
    assert (
        account_inv_balance_pre + ammount_disburse >= account_invst.balance()
        and account_inv_balance_pre + ammount_disburse <= account_invst.balance() + 1
    )


def test_disburse_transferFrom(inv_tok):
    # Arrane
    account_invst = accounts[1]
    account_inv_balance_pre = account_invst.balance()
    ammount_mint = 43567
    inv_tok.mint(account_invst, ammount_mint, {"from": inv_tok.owner()})
    ammount_disburse = 987656789654
    inv_tok.disburse({"from": inv_tok.owner(), "value": ammount_disburse})

    # Act
    account_invst_new = accounts[2]

    tx = inv_tok.approve(inv_tok.owner(), ammount_mint, {"from": account_invst})
    tx.wait(1)
    inv_tok.transferFrom(
        account_invst, account_invst_new, ammount_mint, {"from": inv_tok.owner()}
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
def test_mint_disburse_nine_acc_withdraw(inv_tok, j, weights):
    # Arrange
    acc_invst = [accounts[i] for i in range(1, 10)]
    acc_balance_pre_withdraw = [acc_invst[i].balance() for i in range(9)]
    for i, k in zip(range(9), weights):
        inv_tok.mint(acc_invst[i], k, {"from": inv_tok.owner()})
    # Act
    disburse_amm = j
    inv_tok.disburse({"from": inv_tok.owner(), "value": disburse_amm})
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
def test_disburse_withdraw_withdraw_disburse_withdraw(inv_tok, disb_1, disb_2, weights):
    # Arrange
    acc_invst = [accounts[i] for i in range(1, 10)]
    acc_balance_pre_withdraw = [acc_invst[i].balance() for i in range(9)]
    for i, j in zip(range(9), weights):
        inv_tok.mint(acc_invst[i], j, {"from": inv_tok.owner()})
    # Act I
    disburse_amm = disb_1
    inv_tok.disburse({"from": inv_tok.owner(), "value": disburse_amm})
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
    inv_tok.disburse({"from": inv_tok.owner(), "value": disburse_amm})
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
