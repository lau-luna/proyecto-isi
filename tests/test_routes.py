def test_register_responds_200(client):
    response = client.get("/user/register")
    assert response.status_code == 200
