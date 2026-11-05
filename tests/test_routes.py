def test_index_responds_200(client):
    response = client.get("/")
    print(response.get_data(as_text=True))
    assert response.status_code == 200
