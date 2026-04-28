from ollama import Client
from api.config import AI_MODEL

class LLMAnswers:
    def __init__(self):
        self.client = Client()
        self.model = AI_MODEL

    def answer(self, question: str, role_user: str, history: list[str]):
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

        system_prompt = "Ты AI-помощница под именем Техна, которая помогает сотрудникам получать мгновенные и достоверные ответы на вопросы, связанные с HR-процессами и внутренними нормативами компании. \n" + text_role + "\n Если что-то не понятно, то говори 'Вызываю оператора''. Отвечай простым текстом БЕЗ приписки TECHNA:"
        prompt = "(на следующей строке история переписки тебя с сотрудником, а потом вопрос от него) " + history + "\n ВОПРОС: \n " + question # TODO: добавить документ

        try:
            resp = self.client.chat(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                options={"temperature": 0.25, "num_predict": 512}
            )
            return resp["message"]["content"]

        except:
            return "Произошла ошибка на сервере, попробуйте ещё раз"
        
llm = LLMAnswers()
