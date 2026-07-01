sample_posting = {
    "company": "Acme Inc",
    "role": "Junior Frontend Developer",
    "description": "We are looking for a junior frontend dev with React and TypeScript experience...",
    "role_category": "frontend",
    "status": "saved",
    "location": "Montreal, QC",
    "work_mode": "hybrid",
    "source": "Adzuna",
    "link": "https://acme.com/careers/junior-frontend",
    "notes": "Looks like a good React fit",
    "years_experience": 1,
    "match_score": 0,
}

def test_create_posting(client):    
    response = client.post("/postings", json=sample_posting)

    assert response.status_code == 200
    data = response.json()
    assert data["company"] == "Acme Inc"
    assert "id" in data
    assert "created_at" in data


def test_list_postings(client):
    client.post("/postings", json=sample_posting)
    response = client.get("/postings")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_by_id(client):
    post_resp = client.post("/postings", json=sample_posting).json()
    post_id = post_resp["id"]
    resp = client.get(f"/postings/{post_id}")

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == post_id

def test_get_posting_not_found(client):
    resp = client.get("/postings/9999999")
    assert resp.status_code == 404

def test_patch_posting(client):
    post_data = client.post("/postings", json=sample_posting).json()


    update_data = {
        "company": "New Company"
    }
    resp = client.patch(f"/postings/{post_data["id"]}", json=update_data)

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == post_data["id"]
    assert data["company"] == "New Company"
    assert data["role"] == "Junior Frontend Developer"

def test_delete_posting(client):
    post_data = client.post("/postings", json=sample_posting).json()
    resp = client.delete(f"/postings/{post_data["id"]}")

    assert resp.status_code == 200
    get_resp = client.get(f"/postings/{post_data["id"]}")
    assert get_resp.status_code == 404



