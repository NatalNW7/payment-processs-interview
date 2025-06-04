from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Dict
from time import sleep
from uuid import uuid4
from threading import Thread, Lock
from dataclasses import dataclass


@dataclass
class PaymentRecord:
    payment_id: str
    user_id: str
    amount: int
    transaction_id: str
    status: str

payment_db: Dict[str, PaymentRecord] = {}
idempotency_cache: Dict[str, str] = {}

app = FastAPI()

class PaymentRequest(BaseModel):
    user_id: str
    amount: int

class MockPaymentGateway:
    def process_payment(self, user_id: str, amount: int):
        sleep(1) # simulate a payment process
        return f'tax_{uuid4()}'

payment_gateway = MockPaymentGateway()
lock = Lock()

@app.get('/payments')
def show_payments():
    return payment_db

@app.post('/payments', status_code=201)
def create_payment(
    payload: PaymentRequest,
    idempotency_key = Header(None)
):
    if not idempotency_key:
        raise HTTPException(
            status_code=400,
            detail='Idempotency-Key header is required'    
        )
    
    
    with lock:
        print(idempotency_cache)
        if idempotency_key in idempotency_cache:
            payment_id = idempotency_cache[idempotency_key]
            return payment_db[payment_id]

        payment_id = str(uuid4())
        txn_id = payment_gateway.process_payment(payload.user_id, payload.amount)

        payload_record = PaymentRecord(
            payment_id=payment_id,
            user_id=payload.user_id,
            amount=payload.amount,
            transaction_id=txn_id,
            status='paid'
        )

        payment_db[payment_id] = payload_record
        idempotency_cache[idempotency_key] = payment_id

        return payload_record



from fastapi.testclient import TestClient

def simulate_parallel_requets():
    def make_request():
        client = TestClient(app)
        response = client.post(
            '/payments',
            json={
                'user_id': 'user-123',
                'amount': 100
            },
            headers={'Idempotency-Key': 'key-123'}
        )
        print(response.json())

    threads = [Thread(target=make_request) for _ in range(5)]

    for t in threads:
        t.start()
    
    for t in threads:
        t.join()


if __name__ == '__main__':
    simulate_parallel_requets()

        


