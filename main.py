from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
import json

from IMWPlus_WebPage import IMWPlus

load_dotenv()

app = Flask(__name__)
CORS(app)
app.json.ensure_ascii=False

@app.route('/', methods=['POST'])
def main():
    data = request.get_json()
    user_login = data.get("user_login")
    user_password = data.get("user_password")
    
    imwPlus = IMWPlus(user_login, user_password)
    title = imwPlus.login
    return title

if __name__ == '__main__':
    payload = {
    }

    response = app.test_client().post(
        '/',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    print("Status Code:", response.status_code)
    print("Response Data:", response.get_data(as_text=True))
