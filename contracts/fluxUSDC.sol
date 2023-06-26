// SPDX-License-Identifier: MIT

/*
 * Simple wrapper contract around fUSDC to create a rebasing ERC20 token ("fluxUSDC")
 * that is equal to 1 USD. Rebasing oracle is the fUSDC to USDC exchange rate oracle.
 * Users may deposit fUSDC to mint fluxUSDC, and burn fluxUSDC to receive fUSDC.
 * A `rebase` function adjusts the fluxUSDC balance for each user based on the latest
 * fUSDC exchange rate.
 */

pragma solidity 0.8.19;

import "./Erc20RebaseBase.sol";

interface IfToken {
    function exchangeRateCurrent() external returns (uint256);

    function exchangeRateStored() external view returns (uint256);

    function balanceOf(address _account) external view returns (uint256);

    function transferFrom(
        address _sender,
        address _recipient,
        uint256 _amount
    ) external returns (bool);

    function transfer(
        address _recipient,
        uint256 _amount
    ) external returns (bool);
}

contract fluxUSDC is Erc20RebaseBase {
    using SafeMath for uint256;

    IfToken ftoken = IfToken(0x465a5a630482f3abD6d3b84B39B29b07214d19e5); //fUSDC

    uint256 public totalTokenAmt;

    mapping(address => uint256) public depositedFUSDC;

    //Events
    event Mint(
        address minter,
        uint256 mintAmount,
        uint256 fUSDCAmount,
        uint256 timestamp
    );
    event Burn(
        address burnAddress,
        uint256 amountFluxUSDCBurned,
        uint256 amountFUSDCReturned,
        uint256 timestamp
    );
    event Rebase(
        uint256 oldTotalTokenAmt,
        uint256 newTotalTokenAmt,
        uint256 timestamp
    );

    //constructor() {
    //}

    /**
     * @notice Deposit fUSD and mint fluxUSDC
     * Emits a `Mint` event.
     *
     */
    function mint(uint256 amountFUSDC) external {
        require(amountFUSDC > 0, "ZERO_MINT");

        uint256 exchRate = _fTokenExchangeRateCurrent();
        _rebase(exchRate);

        uint256 _amtToMint = (amountFUSDC * exchRate) / 1e6;
        ftoken.transferFrom(msg.sender, address(this), amountFUSDC);
        depositedFUSDC[msg.sender] += amountFUSDC;

        uint256 sharesAmount = getSharesByTokens(_amtToMint);
        if (sharesAmount == 0) {
            //fluxUSDC totalSupply is 0: assume that shares correspond to fluxUSDC 1-to-1
            sharesAmount = _amtToMint;
        }

        _mintShares(msg.sender, sharesAmount);

        totalTokenAmt += _amtToMint;
        emit Mint(msg.sender, _amtToMint, amountFUSDC, block.timestamp);
    }

    /**
     * @notice Burn the amount of fluxUSDC and payback the corresponding amount of fUSDC
     * Emits a `Burn` event.
     */
    function burn(uint256 amountFluxUSDC) external {
        require(amountFluxUSDC > 0, "ZERO_BURN");

        uint256 exchRate = _fTokenExchangeRateCurrent();
        _rebase(exchRate);

        require(
            amountFluxUSDC <= balanceOf(msg.sender),
            "User Balance Too Low"
        );
        uint256 _amtFUSDC = (amountFluxUSDC * 1e6) / exchRate;

        uint256 sharesAmount = getSharesByTokens(amountFluxUSDC);
        _burnShares(msg.sender, sharesAmount);

        totalTokenAmt = totalTokenAmt.sub(amountFluxUSDC);

        ftoken.transfer(msg.sender, _amtFUSDC);

        emit Burn(msg.sender, amountFluxUSDC, _amtFUSDC, block.timestamp);
    }

    /**
     * @dev adjust totalTokenAmt based on change in fUSDC exch rate
     */
    function rebase() external {
        uint256 exchRate = _fTokenExchangeRateCurrent();
        _rebase(exchRate);
    }

    /**
     * @dev adjust totalTokenSupply based on change in fUSDC exch rate
     */
    function _rebase(uint256 exchRate) internal {
        uint256 oldTotalTokenAmt = totalTokenAmt;
        totalTokenAmt = (ftoken.balanceOf(address(this)) * exchRate) / 1e6;
        emit Rebase(oldTotalTokenAmt, totalTokenAmt, block.timestamp);
    }

    /**
     * @dev total circulation of fluxUSDC
     */
    function _getTotalTokenSupply() internal view override returns (uint256) {
        return totalTokenAmt;
    }

    /**
     * @dev get fUSDC exchange rate
     * Performs an 'accrueInterest' call on the cToken before returning
     * Rate is scaled by 1e16
     * Returns updated exchange rate
     */
    function fTokenExchangeRateCurrent() external returns (uint256) {
        return _fTokenExchangeRateCurrent();
    }

    /**
     * @dev get the stored fUSDC exchange rate. Stored rate is unadjusted for interest accrued
     * Rate is scaled by 1e16
     */
    function getFTokenExchangeRateStored() external view returns (uint256) {
        return ftoken.exchangeRateStored();
    }

    /**
     * @dev get fUSDC exchange rate
     * Performs an 'accrueInterest' call on the cToken before returning
     * Rate is scaled by 1e16
     */
    function _fTokenExchangeRateCurrent() internal returns (uint256) {
        uint256 _rate = ftoken.exchangeRateCurrent();
        return _rate;
    }
}
