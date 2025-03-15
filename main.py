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
    imwplus_login = data.get("imwplus_login")

    if not imwplus_login:
        return jsonify({"error": "Dados de login não informados"}), 400

    user_login = imwplus_login.get("user_login")
    user_password = imwplus_login.get("user_password")

    if not user_login or not user_password:
        return jsonify({"error": "Dados de login não informados"}), 400

    transactions = data.get("transactions")

    try:
        imwPlus = IMWPlus(user_login, user_password)

        if isinstance(transactions, dict):
            app.config["GCP_CREDS"] = config.get_gcp_credentials()
            transactions = BigQueryService().get_transactions(transactions)

        transactions_error = []
        sucessfull_msg = "Atenção: Cadastro realizado com Sucesso!"
        for t in transactions:
            response = imwPlus.send_transaction(t)

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

    for file in glob.glob("*.png"):
        os.remove(file)

    payload = {
        "imwplus_login": {
        },
        "transactions" : {
            "type": "all",
            "month": "2025-03"
        },
        # "transactions": [
        #     {'data': '01/02/2025', 'plano_conta': '1.01.01 - Dizimo dos Membros', 'titulo': 'teste', 'valor': '1'},
        #     {'data': '04/02/2025', 'plano_conta': '1.02.01 - Oferta de Culto', 'titulo': 'teste', 'valor': '1'},
        # ]
    }

    response = app.test_client().post(
        '/send_imwplus',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    print("Status Code:", response.status_code)
    print("Response Data:", response.get_data(as_text=True))
