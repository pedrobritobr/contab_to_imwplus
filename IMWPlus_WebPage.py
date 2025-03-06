import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class IMWPlus:
    url_lancamentos_entrada = "https://pae.wesleyana.com.br/financeiro/lancamento/incluir/entrada/"
    url_lancamentos_saida = "https://pae.wesleyana.com.br/financeiro/lancamento/incluir/saida/"

    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password
        browserless_token = os.getenv("BROWSERLESS_TOKEN")

        chrome_options = webdriver.ChromeOptions()
        chrome_options.set_capability('browserless:token', browserless_token)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")

        self.driver = webdriver.Remote(
            command_executor='https://chrome.browserless.io/webdriver',
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, 5)
        self.login = self.__login()

    def __login(self):
        imwplus_login_url = "https://www.imwplus.com.br/app/login"
        self.driver.get(imwplus_login_url)

        username_input = self.wait_by_css_selector('#cpf')
        password_input = self.wait_by_css_selector('#senha')

        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        password_input.submit()

        self.wait.until(EC.url_changes(imwplus_login_url))

        sucessful_url = "https://www.imwplus.com.br/app/"
        if self.driver.current_url != sucessful_url:
            self.driver.quit()
            return "Login failed"
        return "Login successful"

    def wait_by_css_selector(self, selector):
        return self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
