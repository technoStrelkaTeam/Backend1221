from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

class Parser:
    def __init__(self):
        self.driver = webdriver.Chrome()
    
    def auth_user(self, user, password):
        self.driver.get("https://portal-test.1221systems.ru/account/?logout")
        email_input = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div/main/div/div/form/label[1]/input")
        password_input = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div/main/div/div/form/label[2]/div/input")
        email_input.send_keys(user)
        password_input.send_keys(password)
        button = self.driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div/main/div/div/form/div/button")
        button.click()

    def get_my_data(self, user, password):
        #try:
            self.auth_user(user, password)
            self.driver.get("https://portal-test.1221systems.ru/account/")
            sleep(1)
            otpusk_ostatok = self.driver.find_element(By.XPATH, '//*[@id="tab-my-profile"]/div[2]/div/a[1]/div/span[2]').text.split()[1]
            days_off = self.driver.find_element(By.XPATH, '//*[@id="tab-my-profile"]/div[2]/div/a[2]/div/span[2]').text.split()[1]
            try:
                blagodarochki = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/div[1]/div[2]/main/div[1]/div/div[2]/div[1]/span[2]').text
            except:
                blagodarochki = 0
            coins1221 = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/div[1]/div[2]/main/div[1]/a/div[2]/div[1]/span[2]').text
            fio = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/div[1]/div[1]/div/div/div[2]/h1').text
            profession = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/div[1]/div[1]/div/div/div[2]/div[1]/div[1]').text
            departament = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/div[1]/div[1]/div/div/div[2]/div[1]/div[2]').text
            stazh = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/div[1]/div[1]/div/div/div[2]/div[1]/div[3]/span[1]').text
            number_telephone = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/div[1]/div[1]/div/div/div[2]/div[2]/div[1]/span').text
            email = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/div[1]/div[1]/div/div/div[2]/div[2]/div[2]/span').text
            cadr_reserve = self.driver.find_element(By.XPATH, '//*[@id="tab-my-profile"]/div[1]/div[2]/div/div/span[2]').text

            try:
                self.driver.get("https://portal-test.1221systems.ru/account/vacation/")
                sleep(1)
                self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/main/div[2]/div[1]/form/div[2]/div/div[1]').click()
                self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/main/div[2]/div[1]/form/div[2]/div/div[2]/div[2]').find_element(By.XPATH, f"//div[text()='{fio}']").click()
                self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/main/div[2]/div[1]/form/div[2]/div/div[2]/div[3]/button').click()
                okolo_otpusk = self.driver.find_element(By.CLASS_NAME, 'month_line__vacation--plan').find_element(By.CLASS_NAME, 'month_line__info-date')
                okolo_otpusk = self.driver.execute_script('return arguments[0].textContent;', okolo_otpusk)
            except:
                okolo_otpusk = "в этом году отпуска нет"

            

            return {
            'Остаток отпуска': otpusk_ostatok,
            'Остаток отгулов': days_off,
            'Благодарочки': blagodarochki,
            '1221 Коинсы для покупок мерча': coins1221,
            'ФИО': fio,
            'Профессия': profession,
            'Департамент': departament,
            'Стаж работы': stazh,
            'Номер телефона': number_telephone,
            'Почта': email,
            'Кадровый резерв': cadr_reserve,
            'Ближайший отпуск': okolo_otpusk
            }
        #except Exception as e:
         #   print(e)
    
parser_site = Parser()

if __name__ == "__main__":
    print(parser_site.get_my_data(input("Почта: "), input("Пароль: ")))
