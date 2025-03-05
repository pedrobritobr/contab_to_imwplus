from selenium import webdriver
import os
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json


load_dotenv()

app = Flask(__name__)
CORS(app)
app.json.ensure_ascii=False

@app.route('/', methods=['POST'])
def main():
    data = request.get_json()
    user_login = data.get("user_login")
    user_password = data.get("user_password")

    browserless_token = os.getenv("BROWSERLESS_TOKEN")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.set_capability('browserless:token', browserless_token)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")

    driver = webdriver.Remote(
        command_executor='https://chrome.browserless.io/webdriver',
        options=chrome_options
    )
    wait = WebDriverWait(driver, 10)

    imwplus_login_url = "https://www.imwplus.com.br/app/login"
    driver.get(imwplus_login_url)

    cpf = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#cpf')))
    senha = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#senha')))

    cpf.send_keys(user_login)
    senha.send_keys(user_password)

    submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
    submit_button.click()

    wait.until(EC.url_changes(imwplus_login_url))

    sucessful_url = "https://www.imwplus.com.br/app/"

    if driver.current_url != sucessful_url:
        driver.quit()
        return "Login failed"

    title = driver.title
    driver.quit()
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
