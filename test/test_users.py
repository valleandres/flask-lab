def test_create_user(create_user):
    data = create_user("Andrés")
    assert "id" in data
    assert data["name"] == "Andrés"


def test_get_users(client, create_users):
    create_users("Ana", "Bruno")

    res = client.get("/api/users")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["data"]) == 2


def test_get_all_users_json(client, create_users):
    create_users("Ana", "Bruno")

    res = client.get("/users")
    assert res.status_code == 200
    data = res.get_json()
    assert data == [
        {"id": 1, "name": "Ana"},
        {"id": 2, "name": "Bruno"},
    ]
