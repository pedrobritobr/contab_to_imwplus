from flask import Flask, request, jsonify
from flask_cors import CORS
import json

from config import Config
from IMWPlus import IMWPlus, IMWLoginError
from BigQueryService import BigQueryService


app = Flask(__name__)
CORS(app)
app.json.ensure_ascii=False

@app.route('/', methods=['GET'])
def home():
    return "@pedrobritobr"

@app.route('/send_imwplus', methods=['POST'])
def main():
    config = Config()
    app.config.from_object(config)

    data = request.get_json()
    user_login = data.get("user_login")
    user_password = data.get("user_password")

    try:
        imwPlus = IMWPlus(user_login, user_password)

        app.config["GCP_CREDS"] = config.get_gcp_credentials()
        bigQueryService = BigQueryService()
        inflow = bigQueryService.read_inflow()

        return jsonify({"data": inflow})
    except IMWLoginError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        print(e)
        return jsonify({"error": "Erro inesperado"}), 500

if __name__ == '__main__':
    import os
    import glob

    for file in glob.glob("*.png"):
        os.remove(file)

    payload = {
    }

    response = app.test_client().post(
        '/send_imwplus',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    print("Status Code:", response.status_code)
    print("Response Data:", response.get_data(as_text=True))
