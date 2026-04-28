from services.ollama import ask_ollama


SPLIT_PROMPT = """Ты - эксперт по разбору документов. Твоя задача - разделить документ на логические блоки.

Для каждого блока определи:
1. Заголовок (краткое осмысленное название, характеризующее содержимое, например: "Порядок увольнения", "Права работника", "Оплата труда" и т.д.)
2. Текст (полное содержание раздела)

Верни ответ СТРОГО в формате JSON массива:
[
  {"title": "#Осмысленный заголовок1", "text": "#Полный текст блока 1"},
  {"title": "#Осмысленный заголовок2", "text": "#Полный текст блока 2"}
]

Правила:
1. Заголовок должен КРАТКО характеризовать содержимое (2-7 слов)
2. Текст должен содержать полное содержание раздела
3. НЕ используй номера в заголовках (не "1.1", а смысл например "Увольнение по собственному желанию")
4. НЕ добавляй никакой дополнительный текст, только JSON массив
5. Если документ невозможно разделить, верни один блок с заголовком из смысла документа

Пример ответа:
[
  {"title": "Порядок увольнения", "text": "Работник имеет право расторгнуть трудовой договор..."},
  {"title": "Выплаты при увольнении", "text": "При увольнении работодатель обязан выплатить..."}
]"""


INVALID_SPLIT_RESPONSE = """Ответ не является валидным JSON массивом. Пожалуйста, верни JSON массив блоков в формате:

[
  {"title": "Осмысленный заголовок", "text": "Текст блока"},
  {"title": "Заголовок2", "text": "Текст блока2"}
]

Верни только JSON массив, без дополнительного текста."""


async def split_document_with_llm(text: str, filename: str = "document") -> list[dict]:
    import json
    import re
    
    text = text[:8000]
    
    prompt = f"""Раздели следующий документ на логические блоки с осмысленными заголовками:

{text}

{SPLIT_PROMPT}"""
    
    for attempt in range(3):
        try:
            response = await ask_ollama(SPLIT_PROMPT, text)
            
            response = response.strip()
            
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                response = json_match.group()
            
            blocks = json.loads(response.strip())
            
            if isinstance(blocks, list) and len(blocks) > 0:
                result = []
                for b in blocks:
                    title = b.get("title", "").strip()
                    text_content = b.get("text", "").strip()
                    if title and text_content:
                        key_from_title = generate_key_from_title(title)
                        result.append({
                            "title": title,
                            "text": text_content,
                            "key": key_from_title
                        })
                return result
            
        except (json.JSONDecodeError, ValueError) as e:
            if attempt < 2:
                prompt = f"{text}\n\n{INVALID_SPLIT_RESPONSE}"
            continue
    
    key = filename.replace("_", " ").title()
    return [{"title": key, "text": text[:4000], "key": key}]


def generate_key_from_title(title: str) -> str:
    import re
    
    title_lower = title.lower()
    
    keywords = {
        ("увольнен", "уволен", "увольнение"): "3.6",
        ("оплат", "зарплат", "заработн", "преми", "деньг"): "4.5",
        ("отпуск", "отдыха", "отгул"): "2.5",
        ("охрана", "безопасн", "трудоохран"): "5.3",
        ("трудов", "распорядок", "внутренн"): "2.1",
        ("пользовател", "соглашени", "договор"): "1.2",
        ("устав", "организац", "предприят"): "1.1",
        ("приём", "принят", "найм"): "3.1",
        ("перевод", "перемещен"): "3.2",
        ("режим", "рабочее время"): "2.1",
        ("дисциплин", "взыскан", "нарушен"): "3.4",
    }
    
    for (keywords_list, key) in keywords.items():
        for kw in keywords_list:
            if kw in title_lower:
                return key
    
    words = re.findall(r'\w+', title_lower)
    hash_val = hash(tuple(words)) % 1000
    return f"doc_{hash_val}"