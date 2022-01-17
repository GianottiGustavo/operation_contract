// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
import "@openzeppelin/contracts/utils/Context.sol";

contract InvestToken is Context, IERC20, IERC20Metadata {
    address private _owner;
    uint256 private _totalSupply;
    string private _name;
    string private _symbol;
    uint256 _totalDividendPoints = 0;
    uint256 _unclaimedDividends = 0;
    uint256 _pointMultiplier = 1000000000000000000;

    mapping(address => uint256) private _lastDividendPoints;
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;

    constructor(string memory name_, string memory symbol_) {
        _name = name_;
        _symbol = symbol_;
        _owner = _msgSender();
    }

    function name() public view virtual override returns (string memory) {
        return _name;
    }

    function symbol() public view virtual override returns (string memory) {
        return _symbol;
    }

    function decimals() public view virtual override returns (uint8) {
        return 0;
    }

    function totalSupply() public view virtual override returns (uint256) {
        return _totalSupply;
    }

    function owner() public view virtual returns (address) {
        return _owner;
    }

    function balanceOf(address account)
        public
        view
        virtual
        override
        returns (uint256)
    {
        return _balances[account];
    }

    event DividendPayed(address indexed from, uint256 value);

    function transfer(address recipient, uint256 amount)
        public
        virtual
        override
        returns (bool)
    {
        _transfer(_msgSender(), recipient, amount);
        return true;
    }

    function allowance(address owner_ad, address spender)
        public
        view
        virtual
        override
        returns (uint256)
    {
        return _allowances[owner_ad][spender];
    }

    function approve(address spender, uint256 amount)
        public
        virtual
        override
        returns (bool)
    {
        _approve(_msgSender(), spender, amount);
        return true;
    }

    function transferFrom(
        address sender,
        address recipient,
        uint256 amount
    ) public virtual override returns (bool) {
        uint256 currentAllowance = _allowances[sender][_msgSender()];
        if (currentAllowance != type(uint256).max) {
            require(
                currentAllowance >= amount,
                "ERC20: transfer amount exceeds allowance"
            );
            unchecked {
                _approve(sender, _msgSender(), currentAllowance - amount);
            }
        }

        _transfer(sender, recipient, amount);

        return true;
    }

    function decreaseAllowance(address spender, uint256 subtractedValue)
        public
        virtual
        returns (bool)
    {
        uint256 currentAllowance = _allowances[_msgSender()][spender];
        require(
            currentAllowance >= subtractedValue,
            "ERC20: decreased allowance below zero"
        );
        unchecked {
            _approve(_msgSender(), spender, currentAllowance - subtractedValue);
        }

        return true;
    }

    function _transfer(
        address sender,
        address recipient,
        uint256 amount
    ) internal virtual {
        require(sender != address(0), "ERC20: transfer from the zero address");
        require(recipient != address(0), "ERC20: transfer to the zero address");

        _beforeTokenTransfer(sender, recipient, amount);

        uint256 senderBalance = _balances[sender];
        require(
            senderBalance >= amount,
            "ERC20: transfer amount exceeds balance"
        );
        unchecked {
            _balances[sender] = senderBalance - amount;
        }
        _balances[recipient] += amount;

        emit Transfer(sender, recipient, amount);

        _afterTokenTransfer(sender, recipient, amount);
    }

    function _mint(address account, uint256 amount)
        internal
        virtual
        updateAndSendDividend(account)
    {
        require(account != address(0), "ERC20: mint to the zero address");

        _totalSupply += amount;
        _balances[account] += amount;
        _lastDividendPoints[account] = _totalDividendPoints;
        emit Transfer(address(0), account, amount);
    }

    function _burn(address account, uint256 amount) internal virtual {
        require(account != address(0), "ERC20: burn from the zero address");

        _beforeTokenTransfer(account, address(0), amount);

        uint256 accountBalance = _balances[account];
        require(accountBalance >= amount, "ERC20: burn amount exceeds balance");
        unchecked {
            _balances[account] = accountBalance - amount;
        }
        _totalSupply -= amount;

        emit Transfer(account, address(0), amount);

        _afterTokenTransfer(account, address(0), amount);
    }

    function _approve(
        address owner_ad,
        address spender,
        uint256 amount
    ) internal virtual {
        require(owner_ad != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");

        _allowances[owner_ad][spender] = amount;
        emit Approval(owner_ad, spender, amount);
    }

    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal virtual updateAndSendDividend(from) updateAndSendDividend(to) {}

    function _afterTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal virtual {}

    /** 
    This function will update the dividends and send them to the investor.
    **/
    modifier updateAndSendDividend(address investor) {
        require(
            investor != address(0),
            "ERC20: transfer from the zero address"
        );
        uint256 owing = dividendsOwing(investor);
        if (owing > 0) {
            _unclaimedDividends = _unclaimedDividends - owing;
            _lastDividendPoints[investor] = _totalDividendPoints;
            payable(investor).transfer(owing);
        }
        _;
    }

    modifier onlyOwner() {
        require(_msgSender() == _owner);
        _;
    }

    /**
    This function has our main logic to calculate dividends.
     new dividend = _totalDividendPoints - investor's lastDividnedPoint
     ( balance * new dividend ) / points multiplier
    
    **/
    function dividendsOwing(address investor) public view returns (uint256) {
        uint256 newDividendPoints = _totalDividendPoints -
            _lastDividendPoints[investor];
        return (_balances[investor] * newDividendPoints) / _pointMultiplier;
    }

    /**
    This function will be called to pay dividends to the contract
    _totalDividendPoints += (amount * _pointMultiplier ) / _totalSupply
    **/
    function disburse() public payable {
        uint256 amount = msg.value;
        _totalDividendPoints =
            _totalDividendPoints +
            (amount * _pointMultiplier) /
            _totalSupply;
        _unclaimedDividends = _unclaimedDividends + amount;
        emit DividendPayed(_msgSender(), amount);
    }

    /**
    This function will be let the messege sender withdraw their dividends.
    **/
    function withdraw() public payable updateAndSendDividend(_msgSender()) {}

    /*
        External mint function only  called by owner
     */
    function mint(address account, uint256 amount) public payable onlyOwner {
        require(account != _owner);
        _mint(account, amount);
    }
}
