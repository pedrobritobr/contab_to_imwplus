import requests
from bs4 import BeautifulSoup

from IMWPlus.codes import accounting_entry_codes, transaction_ids


class IMWLoginError(Exception):
    def __init__(self, message):
        super().__init__(message)

class IMWPlus:
    def __init__(self, username, password):
        self.session = requests.Session()
        self.__login(username, password)

    def __find_text_from_class(self, html, class_name):
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find(class_=class_name)
        return element.get_text(strip=True) if element else None

    def __login(self, username, password):
        url_login = "https://www.imwplus.com.br/app/login"
        data_login = {
            "cpf": username,
            "senha": password
        }

        response = self.session.post(url_login, data=data_login)
        msg = self.__find_text_from_class(response.text, 'alert-danger')

        if msg:
            raise IMWLoginError(msg)

    def __generate_form_data(self, insert_data):
        boundary = "--"
        data = []

        for key, value in insert_data.items():
            data.append(f"{boundary}\r\n")
            data.append(f"Content-Disposition: form-data; name=\"{key}\"\r\n\r\n{value}\r\n")

        return ''.join(data) + f"{boundary}--\r\n"

    def __build_transaction_dict(self, transaction_data):
        transaction_chart = transaction_data.get("plano_conta")
        payment_method = transaction_data.get("payment_method")

        transaction = {
            "caixa_id": transaction_ids[payment_method],
            "tipo_lancamento": "E" if transaction_chart.startswith("1") else "S",
            "valor": transaction_data.get("valor"),
            "data_lancamento": transaction_data.get("data"),
            "plano_conta_id": accounting_entry_codes[transaction_chart],
            "tipo_pagante_beneficiario": "outros",
            "pagante_favorecido_cpf_cnpj": transaction_data.get("titulo"),
        }

        return transaction

    def send_transaction(self, transaction_data):
        try:
            headers = {
                "content-type": "multipart/form-data; boundary=",
            }
            post_url = "https://www.imwplus.com.br/app/financeiro-lancamento/"

            transaction_data = self.__build_transaction_dict(transaction_data)
            transaction_data = self.__generate_form_data(transaction_data)

            response = self.session.post(post_url, headers=headers, data=transaction_data)
            alert_message = self.__find_text_from_class(response.text, 'alert-message')

            return alert_message
        except Exception as error:
            error_class = error.__class__.__name__
            error_msg = f"Erro ao enviar {transaction_data} | {error_class} | {str(error)}"
            return error_msg