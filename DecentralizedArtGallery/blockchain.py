# import web3 module to interact with ethereum blockchain
from web3 import Web3

ganache_server_url = "http://127.0.0.1:7545"

def connect_to_server(http_url):
    return Web3(Web3.HTTPProvider(http_url)) # return web3 object after connecting to ganache at the given http_url

def get_balance(w3obj, address):
    balance_wei = w3obj.eth.get_balance(address)
    return w3obj.from_wei(balance_wei, "ether")

def get_contract(w3obj, contract_address, abi):
    return w3obj.eth.contract(address=contract_address, abi=abi)

def add_nft(w3obj, marketplace_contract, name, description, price, artist_account):
    price = w3obj.to_wei(price, 'ether')
    tx_hash = marketplace_contract.functions.addNft(name, description, price).transact({'from': artist_account})
    w3obj.eth.wait_for_transaction_receipt(tx_hash)
    return w3obj.eth.get_transaction_receipt(tx_hash)

def buy_nft(w3obj, marketplace_contract, nft_id, buyer_account, price):
    price = w3obj.to_wei(price, 'ether')
    tx_hash = marketplace_contract.functions.buyNft(nft_id).transact({'from': buyer_account, 'value': price})
    w3obj.eth.wait_for_transaction_receipt(tx_hash)
    return w3obj.eth.get_transaction_receipt(tx_hash)

if __name__ == "__main__":
    w3 = connect_to_server(ganache_server_url)
    if w3.is_connected():
        print("Connected to ethereum blockchain. Network ID: {}".format(w3.net.version))
    else:
        print("Could not connect to server. Please restart your server application and retry")


