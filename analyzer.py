"""
analyzer.py — Модуль глубокого интеллектуального анализа киберугроз системы КИБЕРЩИТ.

ВЕРСИЯ: 3.3.5 (VseGPT DeepSeek V4 Flash Edition)
ТЕХНОЛОГИИ: VseGPT API, DeepSeek V4 Flash, VirusTotal API v3, Regex.

ОСНОВНОЙ ФУНКЦИОНАЛ:
1. Автоматическое извлечение доменов и ссылок из текста сообщения.
2. Техническая проверка репутации ссылок через глобальные антивирусы (VirusTotal).
3. Лингвистический и логический анализ текста платной нейросетью DeepSeek V4 Flash.
4. Оценка психологического давления и техник социальной инженерии.
5. Формирование структурированного JSON-отчета для веб-интерфейса.
"""

import os
import json
import re
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Принудительная инициализация переменных окружения из файла .env
load_dotenv()

def get_ai_client(api_key: str = None) -> OpenAI:
    """
    Создаёт и настраивает клиент OpenAI для взаимодействия с сервером VseGPT.
    
    Аргументы:
        api_key: Ключ API (если не задан, берется из переменной OPENROUTER_API_KEY).
    """
    # Получаем ключ: приоритет у аргумента функции, затем значение из .env
    raw_key = api_key or os.getenv("OPENROUTER_API_KEY")
    
    if not raw_key:
        raise ValueError(
            "❌ КРИТИЧЕСКАЯ ОШИБКА: API ключ не найден в файле .env!\n"
            "Добавьте строку: OPENROUTER_API_KEY=sk-or-vv-..."
        )
    
    # Очищаем ключ от кавычек и пробелов, которые могут возникнуть при копировании
    clean_key = raw_key.strip().replace('"', '').replace("'", "")
    
    # Инициализируем клиент OpenAI с базовым адресом VseGPT
    # Для ключей sk-or-vv- используется именно https://api.vsegpt.ru/v1
    return OpenAI(
        api_key=clean_key,
        base_url="https://api.vsegpt.ru/v1",
        timeout=60.0,  # Увеличенное время ожидания для стабильности связи из СНГ
        max_retries=3   # Автоматический перезапрос при временных сбоях сети
    )

def check_domain_virustotal(domain: str, vt_api_key: str = None) -> dict:
    """
    Выполняет технический запрос к API VirusTotal v3 для проверки репутации домена.
    
    Аргументы:
        domain: Строка с доменом (например, 'scam-site.ru').
        vt_api_key: Ключ доступа VirusTotal.
    """
    # Получаем ключ доступа к VirusTotal из окружения
    vt_key = vt_api_key or os.getenv("VIRUSTOTAL_API_KEY")
    
    # Если ключ не настроен, пропускаем технический этап, не прерывая работу всей системы
    if not vt_key:
        return None

    # Формируем URL согласно спецификации VirusTotal API v3
    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    headers = {
        "x-apikey": vt_key.strip().replace('"', '').replace("'", "")
    }
    
    try:
        # Отправляем запрос с таймаутом 10 секунд
        response = requests.get(url, headers=headers, timeout=10.0)
        
        # Если данные найдены (статус 200)
        if response.status_code == 200:
            data = response.json()
            # Извлекаем финальную статистику (malicious, suspicious, harmless, etc.)
            stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
            return stats
            
        # Статус 404 означает, что домена еще нет в базе (считаем его потенциально нейтральным)
        return None
            
    except Exception as e:
        print(f"⚠️ Ошибка связи с VirusTotal для {domain}: {e}")
        return None

# ============================================================
# ГЛАВНЫЙ СИСТЕМНЫЙ ПРОМПТ (ЛОГИЧЕСКОЕ ЯДРО СИСТЕМЫ)
# ============================================================
ANALYSIS_SYSTEM_PROMPT = """
Ты — КИБЕРЩИТ, элитный автономный эксперт по кибербезопасности версии 2026.
Твоя цель: защищать подростков (10-17 лет) от киберпреступников и социальной инженерии.

ТВОЯ ЗАДАЧА:
Проведи глубокий анализ текста сообщения. Ищи признаки:
- Фишинга (кража аккаунтов, паролей, данных карт).
- Социальной инженерии (давление на жалость, страх, жадность).
- Поддельных выигрышей и фейковых раздач игровых скинов/валюты.
- Шантажа, угроз и попыток вовлечения в незаконную деятельность.

ПРАВИЛА ОТВЕТА:
1. Используй простой, современный и серьезный язык, понятный подростку.
2. Не используй сложную терминологию без объяснения.
3. ОТВЕЧАЙ СТРОГО В ФОРМАТЕ JSON. Никакого текста до или после структуры JSON.

СТРУКТУРА ОБЪЕКТА JSON:
{
  "threat_level": "LOW" | "MEDIUM" | "HIGH",
  "threat_level_ru": "Низкий" | "Средний" | "Высокий",
  "threat_emoji": "🟢" | "🟡" | "🔴",
  "scam_type": "Название типа мошенничества",
  "confidence": число от 0 до 100,
  "is_scam": true | false,
  "red_flags": [
    "Признак №1: что именно кажется подозрительным",
    "Признак №2"
  ],
  "explanation": "Подробный разбор ситуации простыми словами (3-4 предложения).",
  "recommendations": [
    "Совет №1: конкретное действие",
    "Совет №2",
    "Совет №3"
  ]
}
"""

def analyze_text(user_text: str, ai_api_key: str = None, vt_api_key: str = None) -> dict:
    """
    Главная функция обработки сообщения. Объединяет технический и нейросетевой анализ.
    """
    print(f"--- АКТИВАЦИЯ НЕЙРОСЕТЕВОГО УЗЛА (DEEPSEEK V4 FLASH) ---")
    
    # 1. Валидация входного текста
    if not user_text or len(user_text.strip()) < 2:
        return {"error": "Текст сообщения слишком короткий для проведения анализа."}
    
    # Ограничение длины (максимум 5000 символов для глубокого разбора)
    if len(user_text) > 5000:
        user_text = user_text[:5000]

    # 2. Поиск доменов в тексте через регулярное выражение
    domain_pattern = r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'
    found_domains = re.findall(domain_pattern, user_text)
    
    vt_warnings = []
    
    # 3. Проверка каждого уникального домена через VirusTotal
    for domain in set(found_domains):
        # Пропускаем известные безопасные ресурсы
        if domain.lower() in ['google.com', 'yandex.ru', 'vk.com', 't.me', 'youtube.com', 'localhost', 'github.com']:
            continue
            
        stats = check_domain_virustotal(domain, vt_api_key)
        if stats:
            malicious_hits = stats.get('malicious', 0)
            suspicious_hits = stats.get('suspicious', 0)
            
            # Если хотя бы один сканер пометил домен как опасный
            if malicious_hits > 0 or suspicious_hits > 0:
                vt_warnings.append(
                    f"⚠️ ТЕХНИЧЕСКИЙ АНАЛИЗ: Ссылка {domain} обнаружена в базе вредоносных ресурсов (Подтверждено: {malicious_hits} вендоров)."
                )

    # 4. Анализ содержания текста нейросетью DeepSeek V4 Flash (через VseGPT)
    try:
        client = get_ai_client(ai_api_key)
        
        # Выполняем запрос к платной модели
        response = client.chat.completions.create(
            model="deepseek/deepseek-v4-flash", 
            messages=[
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": f"Проанализируй данное сообщение и выдай JSON-вердикт:\n\n{user_text}"}
            ],
            temperature=0.1,  # Минимальная случайность для стабильного JSON-формата
            max_tokens=2000,
            response_format={"type": "json_object"}, # Параметр для строгого возврата JSON
            extra_headers={
                "X-Title": "KiberShield AI 2026", # Мета-данные для VseGPT
            }
        )
        
        # Получаем текстовый контент ответа
        raw_content = response.choices[0].message.content
        
        # ОЧИСТКА JSON (на случай, если модель все же добавила Markdown-теги)
        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if json_match:
            clean_json_str = json_match.group(0)
        else:
            clean_json_str = raw_content.strip()

        # Декодируем строку в словарь Python
        result = json.loads(clean_json_str)
        
        # 5. СИНТЕЗ: Объединение результатов ИИ и Технического сканирования
        # Если VirusTotal нашел прямую угрозу, мы переопределяем вердикт на HIGH RISK
        if vt_warnings:
            result['threat_level'] = "HIGH"
            result['threat_level_ru'] = "Высокий"
            result['threat_emoji'] = "🔴"
            result['is_scam'] = True
            result['confidence'] = 100 
            
            # Вставляем технические предупреждения в начало списка красных флагов
            result['red_flags'] = vt_warnings + result.get('red_flags', [])
            
            # Корректируем итоговое объяснение
            result['explanation'] = "КРИТИЧЕСКАЯ УГРОЗА: Технический сканер подтвердил опасность ссылки в тексте! " + result.get('explanation', '')

        print(f"✅ Анализ успешно завершен. Вердикт: {result.get('threat_level')}")
        return result
        
    except json.JSONDecodeError as jde:
        print(f"❌ Ошибка парсинга JSON: {jde}")
        return {"error": "Интеллектуальное ядро прислало ответ в неверном формате. Попробуйте еще раз."}
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ СИСТЕМНАЯ ОШИБКА МОДУЛЯ: {error_msg}")
        
        # Обработка ошибки баланса (HTTP 402)
        if "402" in error_msg or "credits" in error_msg.lower():
            return {"error": "💳 Баланс VseGPT пуст. Пополните счет для использования платной модели DeepSeek V4 Flash."}
            
        return {"error": f"Произошел сбой нейросетевого протокола: {error_msg}"}

# ============================================================
# БЛОК ТЕСТИРОВАНИЯ (Запуск через: python analyzer.py)
# ============================================================
if __name__ == "__main__":
    print("🧪 Запуск локального диагностического теста системы...")
    
    # Пример сообщения с элементами фишинга и опасной ссылкой
    test_message = "ВНИМАНИЕ! Ваш аккаунт заблокирован. Срочно подтвердите данные: telegram-secure-verify.net"
    
    # Запуск анализа (убедитесь, что в .env прописан OPENROUTER_API_KEY)
    final_result = analyze_text(test_message)
    
    # Красивый вывод результата в консоль
    print("\n" + "="*70)
    print(json.dumps(final_result, indent=2, ensure_ascii=False))
    print("="*70 + "\n")