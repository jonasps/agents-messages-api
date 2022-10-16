import json


def test_get_agents(test_app):
    response = test_app.get("/agents")
    assert response.status_code == 200


def test_create_agents(test_app, generate_test_name):
    name = generate_test_name()
    response = test_app.post("/agents", data=json.dumps({"name": name}))
    assert response.status_code == 200


def test_create_agents_with_duplicate_name_not_allowed(test_app, generate_test_name):
    name = generate_test_name()
    response = test_app.post("/agents", data=json.dumps({"name": name}))
    assert response.status_code == 200

    response = test_app.post("/agents", data=json.dumps({"name": name}))
    assert response.status_code == 400


def test_send_message_between_agents(test_app, generate_test_name):
    name_one = generate_test_name()
    name_two = generate_test_name()

    response = test_app.post("/agents", data=json.dumps({"name": name_one}))
    assert response.status_code == 200

    response = test_app.post("/agents", data=json.dumps({"name": name_two}))
    assert response.status_code == 200

    response = test_app.post(
        f"/agents/{name_one}/messages",
        data=json.dumps({"text": "Hello, World!", "sender_name": name_two}),
    )
    assert response.status_code == 200

    fetch_messages = test_app.get(f"/agents/{name_one}/messages")
    assert fetch_messages.json()[0]["sender"]["name"] == name_two
