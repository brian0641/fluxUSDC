# Overview

A "wrapper" contract for fUSDC from [Flux Finance](https://fluxfinance.com/) through which users may deposit fUSDC and receive back a rebasing stablecoin (called "fluxUSDC" here) where each fluxUSDC is redeemable for an amount of fUSDC equal to 1 USDC. FluxUSDC inhereits the underlying yield of fUSDC (currenlty ~4.0% APR), but unlike fUSDC, each fluxUSDC token should have a stable value of 1 USDC.

Flux Finance is a decentralized lending protocol built by the Ondo Finance team. The protocol is a fork of Compound V2 with additional functionality to support both permissionless (e.g. USDC) and permissioned (e.g. OUSG) tokens. Permissions are enforced on a per-asset basis. For example, a USDC lender receives the fUSDC token as a deposit receipt, which does not have any transfer restrictions. But a USDC borrower using OUSG as collateral will need to satisfy OUSG's permissions.

The yield of fUSDC is reflected in a changing exchange rate between fUSDC and USDC, and historically has been about 80bp below the OUSG yield. OUSG provides exposure to short term US Treasuries (UST). The UST market is extremely liquid and deep and can therefore support a practically infinite fUSDC/fluxUSDC supply. 

## Use Case

fluxUSDC is a yield-bearing (through rebasing) stablecoin where one fluxUSDC is worth 1 USDC. Users' may wish to hold USDC in their wallet or use it in other defi applications, such as an LP in a fluxUSDC/ETH pool. In either case, in contrast to USDC which does not receive yield, the user would receive the the fluxUSDC rebasing yield.

## Contract Details

The `fluxUSDC.sol` contract implements an ERC20 token. The main additional functions are:

* `mint()`: User transfers fUSDC to the contract and receives back an amount of fluxUSDC according to the current exchange rate obtained from the fUSDC oracle.
* `burn()`: The reverse of mint. User transfers fluxUSDC to the contract and receives back equivalent amount of fUSDC.
* `rebase()`: Get the latest fUSDC oracle rate and increase the token balances of the fluxUSDC token in all wallets if the oracle rate has increased since the last `rebase()` call. `Rebase()` is automatically called before `mint()` and `burn()` operations.

