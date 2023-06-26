from brownie import *
import json, math

# Deploy contracts, then deposit eth to cream, borrow cream, supply cream, send crCream to Manager contract
UNLOCK_ADDR = "0x98D9177187512E081aD0901Ea7DE4117AE553718"
FUSDC_ADDR = "0x465a5a630482f3abD6d3b84B39B29b07214d19e5"
FUSDC_DECIMALS = 8
MANTISSA = math.pow(10, FUSDC_DECIMALS)
def main():
    unlocked_account = accounts.at(UNLOCK_ADDR, force=True)
    a = accounts[0]
    _D = {'from':a, 'gas_price': "100 gwei"}
    
    print("** Deploying the fluxUSD contract")
    l = fluxUSDC.deploy( {'from':accounts[0], 'gas_price': "100 gwei"})
    
    print(f'Stored exchange rate of fUSDC tokens per 1USDC {l.getFTokenExchangeRateStored()/1e16}')
    
    l.fTokenExchangeRateCurrent(_D)
    print(f'Updating Stored Exch Rate. New rate is: {l.getFTokenExchangeRateStored()/1e16}')
    
    
    """
    Test Mint
    """
    print(); print(); print("TEST MINTING")
    
    #transfer some fUSDC tokens to this address; Use address 0x98D9177187512E081aD0901Ea7DE4117AE553718
    #must unlock it in ganache
    fusdc_k = interface.ICToken(FUSDC_ADDR)
    
    #make sure account[0] has zero fluxUSDC to start
    bal_fluxUSDC = l.balanceOf(a)
    if bal_fluxUSDC > 0:
        l.transfer(UNLOCK_ADDR, bal_fluxUSDC, _D)
        
    fusdc_k.transfer(a, int(10000 * math.pow(10, FUSDC_DECIMALS)), {'from':unlocked_account, 'gas_price': "100 gwei"})
    bal_fusdc = fusdc_k.balanceOf(a)
    bal_fluxUSDC = l.balanceOf(a)
    print(f'Pre-mint balances of fUSDC and fluxUSDC: {bal_fusdc/MANTISSA}   {bal_fluxUSDC/1e18}')
    fusdc_k.approve(l.address, bal_fusdc, _D)
    l.mint(bal_fusdc, _D)
    bal_fusdc = fusdc_k.balanceOf(a)
    bal_fluxUSDC1 = l.balanceOf(a)
    print(f'Post-mint balances of fUSDC and fluxUSDC: {bal_fusdc/MANTISSA}   {bal_fluxUSDC1/1e18}')  
    
    #Mint Again
    print(); print("MINTING AGAIN")
    fusdc_k.transfer(a, int(10000 * math.pow(10, FUSDC_DECIMALS)), {'from':unlocked_account, 'gas_price': "100 gwei"})
    bal_fusdc = fusdc_k.balanceOf(a)
    bal_fluxUSDC = l.balanceOf(a)
    print(f'Pre-mint balances of fUSDC and fluxUSDC: {bal_fusdc/MANTISSA}   {bal_fluxUSDC/1e18}')
    fusdc_k.approve(l.address, bal_fusdc, _D)
    l.mint(bal_fusdc, _D)
    bal_fusdc = fusdc_k.balanceOf(a)
    bal_fluxUSDC2 = l.balanceOf(a)
    print(f'Post-mint balances of fUSDC and fluxUSDC: {bal_fusdc/MANTISSA}   {bal_fluxUSDC2/1e18}')  
   
    #Rebase
    print(); print("TESTING REBASE")
    print(f'Pre-rebase balance of fluxUSDC: {l.balanceOf(a)/1e18}')    
    chain.sleep(50000)
    chain.mine()
    l.rebase(_D)
    print(f'Post-rebase balance of fluxUSDC: {l.balanceOf(a)/1e18}')    
    
    #Burn fluxUSDC
    print(); print("TESTING BURN")
    b1 = l.balanceOf(a)
    print(f'Pre-burn balance of fluxUSDC: {b1/1e18}. Pre-burn balance of fUSDC: {fusdc_k.balanceOf(a)/MANTISSA}')    
    print('Burning 25% of balance ...')
    amtToBurn = int(b1 * .25)
    print(amtToBurn, l.balanceOf(a))
    l.burn(amtToBurn, _D)
    b2 = l.balanceOf(a)
    print(f'Post-burn balance of fluxUSDC: {b2/1e18}. Post-burn balance of fUSDC: {fusdc_k.balanceOf(a)/MANTISSA}')     
    print('Burning rest of balance ...')
    amtToBurn = l.balanceOf(a)
    print(amtToBurn, l.balanceOf(a))
    l.burn(amtToBurn, _D)
    b2 = l.balanceOf(a)
    print(f'Post-burn balance of fluxUSDC: {b2/1e18}. Post-burn balance of fUSDC: {fusdc_k.balanceOf(a)/MANTISSA}')    
    
    print(); print(); print("TESTING Transfer of more fluxUSDC than present")
    bal_fusdc = fusdc_k.balanceOf(a)
    print(f"Attempting to mint with {bal_fusdc}")
    fusdc_k.approve(l.address, bal_fusdc, _D)
    l.mint(bal_fusdc, _D)
    b1 =  l.balanceOf(a)
    print(f'Balance of fluxUSDC is {b1/1e18}. Attempting to transfer 110% of that')
    print('begin transfer ...')
    transfer_amt = int(1.10 * b1)
    try:
        l.transfer(accounts[1], transfer_amt, _D)
        print("FAIL")
    except:
        print("TRANSFER FAIL ... SUCCESS")
        
    print(); print(); print("TESTING Transfer of more fluxUSDC Shares than present")
    shares = l.sharesOf(a)
    print(f'Account has {shares} shares')
    print('Transfering half of shares to account[2]')
    l.transferShares( accounts[2], int(shares/2), _D)
    b2 = l.sharesOf(accounts[2])
    print(f'Share balance of account2 is {b2}')
    print('Transfering again with too many shares.')
    try:
        l.transferShares( accounts[2], shares, _D)    
        print("FAIL")
    except:
        print("TRANSFER FAIL ... SUCCESS")        
   
    #try:
        #l.transfer(accounts[1], transfer_amt, _D)
        #print("FAIL")
    #except:
        #print("TRANSFER FAIL ... SUCCESS")    
    
    #TODO 
    #test approval/allowance, transfer etc. 
    
    #transfer - test that it fails if I try to transfer more than the balance
    # test transferShares in the same way
    #test approve
    
    
    