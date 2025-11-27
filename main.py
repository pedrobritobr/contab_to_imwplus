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
def send_imwplus():
    config = Config()
    app.config.from_object(config)

    payload = request.get_json()
    imwplus_login = payload.get("imwplus_login")

    if not imwplus_login:
        return jsonify({"error": "Dados de login não informados"}), 400

    user_login = imwplus_login.get("user_login")
    user_password = imwplus_login.get("user_password")

    if not user_login or not user_password:
        return jsonify({"error": "Dados de login não informados"}), 400

    transactions = payload.get("transactions")

    try:
        imwPlus = IMWPlus(user_login, user_password)

        if isinstance(transactions, dict):
            app.config["GCP_CREDS"] = config.get_gcp_credentials()
            transactions = BigQueryService().get_transactions(transactions)

        transactions_error = []
        sucessfull_msg = "Atenção: Cadastro realizado com Sucesso!"
        for i, t in enumerate(transactions):
            response = imwPlus.send_transaction(t)
            print(f"[{i+1}/{len(transactions)}] {list(t.values())} {response}")

            if response != sucessfull_msg:
                transactions_error.append({**t, "error": response})

        len_transactions_error = len(transactions_error)

        if len_transactions_error != 0:
            return jsonify({
                "count_errors": f"{len_transactions_error}/{len(transactions)}",
                "errors": transactions_error
            }), 200

        return jsonify({"success": "Todas as transações foram enviadas com sucesso"}), 200

    except IMWLoginError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        print(e)
        return jsonify({"error": "Erro inesperado"}), 500

if __name__ == '__main__':
    import os
    import glob
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    # GCP_CREDS = os.getenv("GCP_CREDS")
    # print("Valor da chave GCP_CREDS:", GCP_CREDS)

    for file in glob.glob("*.png"):
        os.remove(file)

    payload = {
        "imwplus_login": {
            "user_login": os.environ.get('IMW_PLUS_LOGIN'),
            "user_password": os.environ.get('IMW_PLUS_PASSWORD')
        },
        "transactions" : {
            "type": "all",
            "month": "2025-10"
        },
        # "transactions": [
        #     {"data": "01/06/2025", "plano_conta":"2.17.10 - MINISTÉRIOS - Santa Ceia", "titulo":"Elementos da Ceia", "valor":"31,28" }
        # ]
    }

    response = app.test_client().post(
        '/send_imwplus',
        data=json.dumps(payload),
        content_type='application/json'
    )

    print("Status Code:", response.status_code)
    print("Response Data:", response.get_data(as_text=True))
