from ollama import Client
from api.config import AI_MODEL
import selenium
import json

class LLMAnswers:
    def __init__(self):
        self.client = Client()
        self.model = AI_MODEL

    #def get_site(username, password):
     #   driver = webdriver.Chrome()
#
 #       driver.get('https://selenium.dev/documentation')
#
 #       driver.quit()

    def answer(self, question: str, role_user: str, history: list[str], password: str):
        text_role = ""
        if role_user == "new_user":
            text_role = "С тобой общается новый сотрудник, который ещё только-только адаптируется, и ему нужна базовая информация о компании, реквизитах, графику работы"
        elif role_user == "common_user":
            text_role = "С тобой общается обычный сотрудник (линейный персонал), которого интересуют вопросы о зарплате, отпускам, премиям и ДМС"
        else:
            text_role = "С тобой общается один из руководителей компании, которого интересуют вопросы по оформлению сотрудников, стажировкам и материальной ответственности"
        history = "\n ИСТОРИЯ ПЕРЕПИСКИ С ПОЛЬЗОВАТЕЛЕМ (если пуста, значит вы только начали общаться): "
        for i, message in enumerate(history, start=0):
            add_msm = ""
            if i % 2:
                add_msm = "TECHNA: "
            else:
                add_msm = "USER: "
            add_msm += message
            history += "\n" + add_msm

        with open("api/base_company/ПВТР.txt", "r", encoding="utf-8") as doc_file:
            system_prompt = f'''Ты AI-помощница под именем Техна, которая помогает сотрудникам получать мгновенные и достоверные ответы на вопросы, связанные с HR-процессами и внутренними нормативами компании. \n {text_role}\n Если что-то не понятно, то говори 'Вызываю оператора' в формате обычного текста. Во всех остальных случаях отвечай ТОЛЬКО в формате JSON следующего вида
             
              {{
                  "answer": "тут ты пишешь свой ответ, не говоря на основании какого документа он",
                  "base": "тут пишешь источник откуда ты получила эти данные, например *Основание: п. 4.2 Правил внутреннего трудового распорядка*"
              }}
                .  \n Вот документ компании для ответов на вопросы: \n {str(doc_file)}'''
        prompt = "(на следующей строке история переписки тебя с сотрудником, а потом вопрос от него) " + history + "\n ВОПРОС: \n " + question # TODO: добавить документ

        try:
            resp = self.client.chat(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                options={"temperature": 0.25, "num_predict": 512}
            )
            ans = resp["message"]["content"]
            if 'вызываю оператора' in ans.lower():
                return {
                    "answer": "Извините, я не могу найти ответ на вопрос в базе данных, прошу, свяжитесь с HR-человеком \n Номер телефона: +71111111111 \n Почта: hr@portal-test.1221systems.ru \n Телеграм: @tghr",
                    "base": "В базе данных не найдена нужная информация",
                }
            else:
                start = ans.find("{")
                end = ans.rfind("}") + 1
                return json.loads(ans[start:end].replace("\n", ""))
        except:
            return "Произошла ошибка на сервере, попробуйте ещё раз"
        
llm = LLMAnswers()
