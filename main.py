"""
main.py — Центральный серверный узел системы КИБЕРЩИТ (FastAPI Core).

ВЕРСИЯ: 3.3.5 (VseGPT DeepSeek V4 Flash Edition)
ТЕХНОЛОГИИ: FastAPI, Uvicorn, Pydantic v2, CORS Middleware.

ОПИСАНИЕ:
Этот файл запускает высокопроизводительный сервер, который:
1. Принимает запросы от веб-интерфейса Next.js (порт 3000).
2. Проверяет наличие и валидность API-ключей в окружении.
3. Перенаправляет данные в модули интеллектуального анализа (analyzer.py).
4. Поддерживает диалоговую сессию с чат-ботом (chatbot.py).
5. Возвращает структурированные JSON-ответы.
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from dotenv import load_dotenv
from pathlib import Path

# --- ГЛУБОКАЯ ДИАГНОСТИКА ОКРУЖЕНИЯ ---
# Мы определяем абсолютный путь к папке проекта, чтобы Python точно нашел файл .env
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

print("\n" + "="*70)
print("🔍 СИСТЕМА ДИАГНОСТИКИ СЕРВЕРА КИБЕРЩИТ:")
print(f"📂 Корневая папка проекта: {BASE_DIR}")
print(f"📄 Поиск конфигурации .env: {ENV_PATH}")

if ENV_PATH.exists():
    # Принудительно загружаем переменные из .env
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    print("✅ Конфигурационный файл .env успешно загружен.")
else:
    print("❌ КРИТИЧЕСКАЯ ОШИБКА: Файл .env не обнаружен в папке проекта!")

# Проверка ключа VseGPT
api_key = os.getenv("OPENROUTER_API_KEY")
if api_key:
    # Очищаем ключ от возможных кавычек
    api_key = api_key.strip().replace('"', '').replace("'", "")
    print(f"🔑 API Ключ: ОБНАРУЖЕН (Начинается на {api_key[:11]}...)")
    if not api_key.startswith("sk-or-vv-"):
        print("⚠️ ПРЕДУПРЕЖДЕНИЕ: Формат ключа отличается от стандарта VseGPT (sk-or-vv-).")
else:
    print("❌ ОШИБКА: Переменная OPENROUTER_API_KEY отсутствует в .env!")
print("="*70 + "\n")

# Теперь, когда ключи в памяти, импортируем наши функциональные модули
import analyzer
import chatbot

# ============================================================
# ИНИЦИАЛИЗАЦИЯ FASTAPI
# ============================================================

app = FastAPI(
    title="КИБЕРЩИТ API 2026",
    description="Центральный узел обработки киберугроз на базе DeepSeek V4 Flash.",
    version="3.3.5"
)

# НАСТРОЙКА CORS
# Позволяет вашему сайту (фронтенду) безопасно общаться с этим сервером
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # В режиме разработки разрешаем запросы отовсюду
    allow_credentials=True,
    allow_methods=["*"], # Разрешаем все типы запросов (POST, GET и т.д.)
    allow_headers=["*"], # Разрешаем все заголовки
)

# ============================================================
# МОДЕЛИ ДАННЫХ (Pydantic)
# ============================================================

class AnalyzeRequest(BaseModel):
    """Схема данных для запроса на анализ текста."""
    text: str = Field(..., min_length=1, description="Текст сообщения для проверки")

class ChatMessage(BaseModel):
    """Схема одного сообщения в истории диалога."""
    role: str = Field(..., description="Роль отправителя (user или assistant)")
    content: str = Field(..., description="Текст сообщения")

class ChatRequest(BaseModel):
    """Схема данных для запроса к чат-боту."""
    messages: List[ChatMessage] = Field(..., description="Массив истории переписки")

# ============================================================
# ЭНДПОИНТЫ (МАРШРУТЫ API)
# ============================================================

@app.get("/")
async def status_check():
    """Проверка доступности сервера."""
    return {
        "status": "ONLINE",
        "engine": "DeepSeek V4 Flash (VseGPT)",
        "protocol": "2026.3.3",
        "message": "Система КиберЩит готова к защите пользователей 🛡️"
    }

@app.post("/api/analyze")
async def api_analyze(req: AnalyzeRequest):
    """
    Принимает текст с сайта и запускает процесс интеллектуального сканирования.
    """
    print(f"📡 [SCAN] Получен текст на анализ ({len(req.text)} симв.)")
    
    try:
        # Вызываем логику анализа из analyzer.py
        result = analyzer.analyze_text(req.text)
        
        # Если модуль вернул ошибку внутри словаря
        if "error" in result:
            print(f"⚠️ Ошибка в analyzer.py: {result['error']}")
            
            # Определяем тип ошибки для корректного HTTP статуса
            if "Ошибка сети" in result["error"] or "VseGPT" in result["error"]:
                raise HTTPException(status_code=502, detail=result["error"])
            raise HTTPException(status_code=400, detail=result["error"])
            
        print(f"✅ [SCAN] Анализ завершен. Результат: {result.get('threat_level')}")
        return result

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ [SCAN] Критическая ошибка API: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Внутренний сбой сервера при анализе: {str(e)}"
        )

@app.post("/api/chat")
async def api_chat(req: ChatRequest):
    """
    Принимает историю диалога и возвращает ответ КиберДруга.
    """
    print(f"💬 [CHAT] Запрос от пользователя. История: {len(req.messages)} сообщ.")
    
    try:
        # Конвертируем список Pydantic-объектов в обычные словари (dict)
        # Используем современный метод model_dump() (Pydantic v2)
        formatted_history = []
        for msg in req.messages:
            formatted_history.append(msg.model_dump())
        
        # Вызываем функцию из chatbot.py
        response = chatbot.get_chatbot_response(formatted_history)
        
        if "error" in response:
            print(f"⚠️ Ошибка в chatbot.py: {response['error']}")
            if "Ошибка связи" in response["error"]:
                raise HTTPException(status_code=502, detail=response["error"])
            raise HTTPException(status_code=400, detail=response["error"])
            
        print(f"✅ [CHAT] Ответ КиберДруга успешно отправлен")
        return response

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ [CHAT] Критическая ошибка API: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Внутренний сбой сервера чат-модуля: {str(e)}"
        )

# ============================================================
# ЗАПУСК ИСПОЛНЯЕМОГО ФАЙЛА
# ============================================================

if __name__ == "__main__":
    # Стилизованный лог запуска в консоли
    print("\n" + "*"*60)
    print("🚀 КИБЕРЩИТ: ЦЕНТРАЛЬНОЕ ЯДРО ЗАПУСКАЕТСЯ...")
    print("📍 API доступно по адресу: http://localhost:8000")
    print("📑 Документация (Swagger): http://localhost:8000/docs")
    print("*"*60 + "\n")
    
    # Запускаем сервер через uvicorn
    # host="0.0.0.0" позволяет подключаться по локальной сети
    # port=8000 — наш стандартный порт для бекенда
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )