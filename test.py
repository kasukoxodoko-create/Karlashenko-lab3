import json
import urllib.parse
import urllib.request
from googletrans import Translator, LANGUAGES
from googletrans.models import Detected, Translated

translator = Translator()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}


def _fetch_google_translate(text: str, dest: str, src: str = "auto"):
    """Надсилає запит до API Google Translate через стандартний urllib."""
    query = urllib.parse.urlencode({
        "client": "gtx",
        "sl": src,
        "tl": dest,
        "dt": "t",
        "q": text,
    })
    url = f"https://translate.googleapis.com/translate_a/single?{query}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as response:
        raw_data = response.read().decode("utf-8")
        return json.loads(raw_data)


def _working_detect(self, text: str, **kwargs):
    """Визначення мови тексту для googletrans 3.1.0a0."""
    data = _fetch_google_translate(text, dest="en", src="auto")
    lang = data[2] if len(data) > 2 and data[2] else "en"

    confidence = 1
    try:
        raw_conf = data[8][2][0]
        confidence = int(raw_conf) if raw_conf == 1 else round(float(raw_conf), 2)
    except Exception:
        confidence = 1

    return Detected(lang=lang, confidence=confidence)


def _working_translate_method(self, text: str, dest: str = "en", src: str = "auto", **kwargs):
    """Переклад тексту для googletrans 3.1.0a0."""
    data = _fetch_google_translate(text, dest=dest, src=src)
    translated_text = "".join(part[0] for part in data[0] if part and part[0])
    detected_src = data[2] if len(data) > 2 and data[2] else src

    return Translated(
        src=detected_src,
        dest=dest,
        origin=text,
        text=translated_text,
        pronunciation=None,
    )


Translator.detect = _working_detect
Translator.translate = _working_translate_method


def CodeLang(lang: str) -> str:
    """Повертає код мови за її назвою або назву мови за її кодом."""
    if not isinstance(lang, str) or not lang.strip():
        return "Помилка: параметр мови повинен бути непорожнім рядком."

    lang_clean = lang.strip().lower()

    if lang_clean in LANGUAGES:
        return LANGUAGES[lang_clean].capitalize()

    for code, name in LANGUAGES.items():
        if name.lower() == lang_clean:
            return code

    return f"Помилка: мову або код '{lang}' не знайдено у таблиці мов."


def LangDetect(txt: str):
    """Визначає мову тексту та рівень впевненості (confidence)."""
    if not isinstance(txt, str) or not txt.strip():
        return "Помилка: текст для визначення мови не може бути порожнім."

    try:
        detected = translator.detect(txt.strip())
        if detected is None or not hasattr(detected, "lang"):
            return "Помилка: не вдалося розпізнати мову тексту."
        return detected
    except Exception as e:
        return f"Помилка визначення мови: {e}"


def Translate(text: str, lang: str) -> str:
    """Перекладає текст на вказану мову (за назвою або ISO-639 кодом)."""
    if not isinstance(text, str) or not text.strip():
        return "Помилка: текст для перекладу не може бути порожнім."

    if not isinstance(lang, str) or not lang.strip():
        return "Помилка: не вказано мову перекладу."

    lang_clean = lang.strip().lower()
    target_code = None

    if lang_clean in LANGUAGES:
        target_code = lang_clean
    else:
        for code, name in LANGUAGES.items():
            if name.lower() == lang_clean:
                target_code = code
                break

    if not target_code:
        return f"Помилка: мову '{lang}' не знайдено."

    try:
        result = translator.translate(text.strip(), dest=target_code)
        if result is None or not getattr(result, "text", None):
            return "Помилка: сервіс перекладу повернув порожній результат."
        return result.text
    except Exception as e:
        return f"Помилка перекладу: {e}"
if __name__ == "__main__":
    # 1. Перевірка на стандартному прикладі з умови завдання
    txt = "Доброго дня. Як справи?"
    lang = "en"
    print(txt)
    print(LangDetect(txt))
    print(Translate(txt, lang))
    print(CodeLang("En"))
    print(CodeLang("English"))

    print("-" * 40)

    # 2. Додаткові перевірки граничних випадків та помилок
    print("Тест з різним регістром та пробілами:")
    print("CodeLang('  uK  '):", CodeLang("  uK  "))
    print("CodeLang('german'):", CodeLang("german"))
    print("Translate на мову за назвою:", Translate("Привіт, світе!", "French"))

    print("\nТест обробки некоректних даних:")
    print("Порожній текст у LangDetect:", LangDetect("   "))
    print("Порожній текст у Translate:", Translate("", "en"))
    print("Неіснуюча мова у Translate:", Translate("Привіт", "Elvish"))
    print("Неіснуючий код у CodeLang:", CodeLang("xyz"))
    print("Неправильний тип даних у CodeLang:", CodeLang(123))

    print("-" * 40)

    # 3. Інтерактивний переклад тексту, заданого користувачем
    user_text = input("Введіть текст для перекладу: ")
    if not user_text.strip():
        print("Помилка: ви не ввели текст для перекладу.")
    else:
        user_lang = input("Введіть мову перекладу (назву або код, напр. 'en' або 'German'): ")
        if not user_lang.strip():
            print("Помилка: ви не ввели мову перекладу.")
        else:
            print("Визначена мова:", LangDetect(user_text))
            print("Переклад:", Translate(user_text, user_lang))