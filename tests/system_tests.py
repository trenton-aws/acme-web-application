import os
import requests

def test_website():
    with requests.get(os.environ["WEBSITE_URL"]) as response:
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/html"
