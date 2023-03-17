from web3 import Web3, HTTPProvider
from web3.contract import Contract
from explorer_utils import fmt_hash, fmt_hash_str
import requests

# class Explorer
#
# usage:
# explorer = Explorer()
# explorer.get_transactions_nft(block_id)
# # returns a list of transactions that are NFT transfers, returns details of the transactions including the nft pictures
# explorer.get_transactions_erc20(block_id)
# # returns a list of transactions that are ERC20 transfers, returns details of the transactions including the token symbol and amount transfered

INFURA_API_KEY = open('./api_secret.txt', 'r').read().strip()

ABI_ERC721 = open('./abi_erc721.json', 'r').read().strip()
ABI_ERC20 = open('./abi_erc20.json', 'r').read().strip()

# note: the addresses need to be checksum formatted
NFT_COLLECTION_ADDRESS = "0x7D8820FA92EB1584636f4F5b8515B5476B75171a" # Murakami flowers

# Aeternity - but any erc20 token would do
ERC20_ADDRESS = "0x5CA9a71B1d01849C0a95490Cc00559717fCF0D1d"

RPC_URL = f"https://mainnet.infura.io/v3/{INFURA_API_KEY}"

WEB3 = Web3(HTTPProvider(RPC_URL))

if WEB3.isConnected():
  print("ETH node connection ok")

class Explorer:
  def __init__(self):
    self.eth = WEB3.eth
    self.web3 = WEB3
    self.contract_nft = self.eth.contract(
        address=NFT_COLLECTION_ADDRESS, abi=ABI_ERC721
    )
    self.contract_erc20 = self.eth.contract(
        address=ERC20_ADDRESS, abi=ABI_ERC20
    )
    self.block_latest = self.eth.get_block('latest')
    self.block_latest_number = self.block_latest.number

  def get_transactions_nft(self, block_num):
    block = self.eth.get_block(block_num)
    transactions = block.transactions
    txs_data = self.filter_transactions_nft(transactions)
    return txs_data

  def get_transactions_erc20(self, block_num):
    block = self.eth.get_block(block_num)
    transactions = block.transactions
    txs_data = self.filter_transactions_erc20(transactions)
    return txs_data

  def get_nft_data(self, transaction_input):
    function_input = self.contract_nft.decode_function_input(transaction_input)
    function_input = function_input[1]
    # print("function_input:", function_input)
    nft_id = function_input["tokenId"]
    nft_transfer_address_to = function_input["to"]
    nft_transfer_address_to = fmt_hash_str(nft_transfer_address_to)
    metadata_url = self.contract_nft.functions.tokenURI(nft_id).call()
    nft_image_url = self.get_nft_image_url(metadata_url)
    nft_data = {
      "nft_id": nft_id,
      "nft_image_url": nft_image_url,
      "nft_transfer_address_to": nft_transfer_address_to,
    }
    return nft_data

  def get_erc20_data(self, transaction_input):
    function_input = self.contract_erc20.decode_function_input(transaction_input)
    function_input = function_input[1]
    print("function_input:", function_input)
    erc20_transfer_address_to = function_input["to"]
    erc20_transfer_value = function_input["value"]
    erc20_ticker_symbol = self.contract_erc20.functions.symbol().call()
    erc20_transfer_value = self.web3.fromWei(erc20_transfer_value, "ether") # usually the decimals are 18 but this is not true for all the contracts
    erc20_data = {
      "erc20_transfer_address_to": erc20_transfer_address_to,
      "erc20_transfer_value": erc20_transfer_value,
      "erc20_ticker_symbol": erc20_ticker_symbol,
    }
    return erc20_data

  def get_nft_image_url(self, metadata_url):
    resp = requests.get(metadata_url)
    resp = resp.json()
    nft_image_url = resp['image']
    return nft_image_url

  def filter_transactions_erc20(self, transactions):
    txs_data = []
    print("transactions:", len(transactions))
    for idx, tx_id in enumerate(transactions):
      if idx > 16: return txs_data
      print("tx_id:", tx_id.hex())
      tx = self.eth.get_transaction(tx_id)
      transaction_input = tx.input
      tx_id_hex = tx_id.hex()
      tx_id = fmt_hash(tx_id)
      address_from = tx['from']
      address_from = fmt_hash_str(address_from)
      address_to = tx['to']
      print("TO:", address_to)
      # address_to = fmt_hash_str(address_to)
      tx_data = {
          "tx_id": tx_id,
          "address_from": address_from,
          "address_to": address_to,  # this is the smart contract address
          "explorer_url": f"https://etherscan.io/tx/{tx_id_hex}",
      }
      if tx["to"] == ERC20_ADDRESS:
        erc20_data = self.get_erc20_data(transaction_input)
        tx_data["erc20_transfer_value"] = erc20_data["erc20_transfer_value"]
        erc20_transfer_address_to = erc20_data["erc20_transfer_address_to"]
        erc20_transfer_address_to = fmt_hash_str(erc20_transfer_address_to)
        tx_data["erc20_transfer_address_to"] = erc20_transfer_address_to
        tx_data["erc20_ticker_symbol"] = erc20_data["erc20_ticker_symbol"]
        txs_data.append(tx_data)
    return txs_data

  def filter_transactions_nft(self, transactions):
    txs_data = []
    print("transactions:", len(transactions))
    for idx, tx_id in enumerate(transactions):
      if idx > 16: return txs_data
      print("tx_id:", tx_id.hex())
      tx = self.eth.get_transaction(tx_id)
      transaction_input = tx.input
      tx_id_hex = tx_id.hex()
      tx_id = fmt_hash(tx_id)
      address_from = tx['from']
      address_from = fmt_hash_str(address_from)
      address_to = tx['to']
      address_to = fmt_hash_str(address_to)
      tx_data = {
        "tx_id": tx_id,
        "address_from": address_from,
        "address_to": address_to, # this is the smart contract address
        "explorer_url": f"https://etherscan.io/tx/{tx_id_hex}",
      }
      if tx["to"] == NFT_COLLECTION_ADDRESS:
        nft_data = self.get_nft_data(transaction_input)
        tx_data["nft_id"] = nft_data["nft_id"]
        tx_data["nft_image_url"] = nft_data["nft_image_url"]
        tx_data["nft_transfer_address_to"] = nft_data["nft_transfer_address_to"] # this is the recipient address of the NFT
        txs_data.append(tx_data)

    return txs_data