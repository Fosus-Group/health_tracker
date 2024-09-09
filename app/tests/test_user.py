import pytest


@pytest.mark.asyncio(scope="session")
async def test_get_all_shops(client):
    data = {
        "phone_number": "+79183394882"
    }
    response = await client.post("/api/user/call", json=data)
    data = response.json()
    assert response.status_code == 200
    assert data["success"] == True
