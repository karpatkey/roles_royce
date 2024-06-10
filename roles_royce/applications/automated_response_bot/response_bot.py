from roles_royce.applications.automated_response_bot.core import Alert
from roles_royce.applications.automated_response_bot.utils import validate_webhook,exit_strat
from roles_royce.applications.execution_app.stresstest import single_stresstest
from fastapi import FastAPI
import uvicorn
import json
from web3 import Web3

app = FastAPI()

w3 = Web3(Web3.HTTPProvider("https://rpc.gnosischain.com"))
public_key_hyp = "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEBgZAJk+OuOzp3sO6B+44gqLDzz/X1KloIQYkqefTYMv+URMIvN97gsoLYrZ9K08uQR0XHLXbB0RCTAt6BNFhzQ=="

@app.post("/webhook")
async def receive_webhook(data: dict):
    print("Received webhook message:")
    alert = Alert.from_webhook(data)
    print("received alert")
    if validate_webhook(data, public_key_hyp):
        print("Webhook message is valid")
        single_stresstest(percentage=50,
                      max_slippage=1,
                      dao="TestSafeDAO",
                      blockchain="gnosis",
                      protocol="Aura",
                      exec_config=exit_strat["positions"][0]["exec_config"][0],
                      web3=w3)
    
    # if alert.chain == "ethereum":
    #     print('lets exit')
    return {"cool stuff"}

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
