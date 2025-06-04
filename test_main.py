from fastapi.testclient import TestClient
from main import app, payment_gateway, payment_db, idempotency_cache
from unittest import mock

client = TestClient(app)

def test_payment_idempotency():
    with mock.patch.object(payment_gateway, 'process_payment', return_value='txn_123'):
        headers={'Idempotency-Key': 'key-123'}
        json={'user_id': 'user-123', 'amount': 100}

        response = client.post('/payments', json=json, headers=headers)
        assert response.status_code == 200
        data1 = response.json()

        response = client.post('/payments', json=json, headers=headers)
        assert response.status_code == 200
        data2 = response.json()

        assert data1 == data2