def test_create_user(client):
    res = client.post("/api/users", json={"name": "Andrés"})
    assert res.status_code == 201
    data = res.get_json()
    assert "id" in data
    assert data["name"] == "Andrés"

def test_get_users(client):
    client.post("/api/users", json={"name": "Ana"})
    client.post("/api/users", json={"name": "Bruno"})

    res = client.get("/api/users")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["data"]) == 2


def test_get_all_users_json(client):
    client.post("/api/users", json={"name": "Ana"})
    client.post("/api/users", json={"name": "Bruno"})

    res = client.get("/users")
    assert res.status_code == 200
    data = res.get_json()
    assert data == [
        {"id": 1, "name": "Ana"},
        {"id": 2, "name": "Bruno"},
    ]
