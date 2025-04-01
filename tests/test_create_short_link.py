import pytest

@pytest.mark.asyncio
async def test_create_short_link(client):
    response = await client.post("/links/shorten", json={
        "original_url": "https://example.com",
        "custom_alias": "testalias"
    })

    assert response.status_code == 201
    assert response.json()["short_code"] == "testalias"
