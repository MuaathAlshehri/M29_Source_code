from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from web3 import Web3



app = FastAPI()



RPC_URL = "http://127.0.0.1:7545"

w3 = Web3(Web3.HTTPProvider(RPC_URL))



PRIVATE_KEY = "Your_Private_Key"

WALLET_ADDRESS = w3.eth.account.from_key(
    PRIVATE_KEY
).address



CONTRACT_ADDRESS = Web3.to_checksum_address(
    "Your_Contract_Address"
)

ABI = [
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "_timestamp",
        "type": "string"
      },
      {
        "internalType": "uint256",
        "name": "_fromBank",
        "type": "uint256"
      },
      {
        "internalType": "string",
        "name": "_account",
        "type": "string"
      },
      {
        "internalType": "uint256",
        "name": "_toBank",
        "type": "uint256"
      },
      {
        "internalType": "string",
        "name": "_account1",
        "type": "string"
      },
      {
        "internalType": "uint256",
        "name": "_amountReceived",
        "type": "uint256"
      },
      {
        "internalType": "string",
        "name": "_receivingCurrency",
        "type": "string"
      },
      {
        "internalType": "uint256",
        "name": "_amountPaid",
        "type": "uint256"
      },
      {
        "internalType": "string",
        "name": "_paymentCurrency",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "_paymentFormat",
        "type": "string"
      },
      {
        "internalType": "bool",
        "name": "_isSuspicious",
        "type": "bool"
      }
    ],
    "name": "addDecision",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  }
]

contract = w3.eth.contract(
    address=CONTRACT_ADDRESS,
    abi=ABI
)



class InputData(BaseModel):

    Timestamp: str

    From_Bank: int = Field(alias="From Bank")

    Account: str

    To_Bank: int = Field(alias="To Bank")

    Account_1: str = Field(alias="Account.1")

    Amount_Received: float = Field(alias="Amount Received")

    Receiving_Currency: str = Field(alias="Receiving Currency")

    Amount_Paid: float = Field(alias="Amount Paid")

    Payment_Currency: str = Field(alias="Payment Currency")

    Payment_Format: str = Field(alias="Payment Format")

    Is_Suspicious: bool = Field(alias="Is Suspicious")



def save_transaction(data: InputData):

    nonce = w3.eth.get_transaction_count(
        WALLET_ADDRESS
    )

    txn = contract.functions.addDecision(

        data.Timestamp,

        data.From_Bank,

        data.Account,

        data.To_Bank,

        data.Account_1,

        int(data.Amount_Received),

        data.Receiving_Currency,

        int(data.Amount_Paid),

        data.Payment_Currency,

        data.Payment_Format,

        data.Is_Suspicious

    ).build_transaction({

        "chainId": 1337,

        "gas": 3000000,

        "gasPrice": w3.eth.gas_price,

        "nonce": nonce

    })

    signed_txn = w3.eth.account.sign_transaction(
        txn,
        private_key=PRIVATE_KEY
    )

    tx_hash = w3.eth.send_raw_transaction(
        signed_txn.raw_transaction
    )

    receipt = w3.eth.wait_for_transaction_receipt(
        tx_hash
    )

    return receipt



@app.post("/save_transaction")

def save_transaction_api(data: InputData):

    try:

        receipt = save_transaction(data)

        return {

            "status": "success",

            "block_number": receipt.blockNumber,

            "transaction_hash": receipt.transactionHash.hex(),

            "saved_data": data.dict(by_alias=True)

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )