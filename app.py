import streamlit as st
from datetime import datetime
import os
from dotenv import load_dotenv

# Импортируем наши новые модули
import analyzer
import chatbot

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="🛡️ КиберЩит | #КиберПраво",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Raycast-inspired dark theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Exo+2:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary-gradient: linear-gradient(135deg, #00d4ff 0%, #8b5cf6 100%);
        --secondary-gradient: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        --card-bg: rgba(17, 24, 39, 0.6);
        --card-hover: rgba(31, 41, 55, 0.8);
        --glass-blur: blur(12px);
        --border-radius: 18px;
        --transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    * {
        box-sizing: border-box;
        margin: 0;
        padding: 0;
    }
    
    body {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0d1117 100%);
        color: #e5e7eb;
        min-height: 100vh;
    }
    
    .main {
        padding: 0;
    }
    
    [data-testid="stSidebar"] {
        background: rgba(10, 14, 26, 0.95);
        backdrop-filter: var(--glass-blur);
        border-right: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    .sidebar-header {
        padding: 2rem 1.5rem;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(139, 92, 246, 0.1));
        border-radius: 18px;
        margin-left: 1.5rem;
        margin-right: 1.5rem;
    }
    
    .sidebar-title {
        font-family: 'Exo 2', sans-serif;
        font-weight: 700;
        font-size: 1.35rem;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 0.5px;
    }
    
    .nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 1.5rem;
        margin: 0.5rem 1.5rem;
        border-radius: var(--border-radius);
        transition: var(--transition);
        cursor: pointer;
        color: #9ca3af;
        text-decoration: none;
        font-weight: 500;
    }
    
    .nav-item:hover {
        background: rgba(255, 255, 255, 0.05);
        color: #fff;
        transform: translateX(4px);
    }
    
    .nav-item.active {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(139, 92, 246, 0.15));
        color: #fff;
        border-left: 3px solid var(--primary-gradient);
    }
    
    .api-key-section {
        padding: 1.5rem;
        margin-top: auto;
        border-top: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    .api-key-label {
        font-size: 0.85rem;
        color: #9ca3af;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    
    .api-key-input {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        color: #e5e7eb;
        font-size: 0.9rem;
        transition: var(--transition);
    }
    
    .api-key-input:focus {
        outline: none;
        border-color: rgba(0, 212, 255, 0.5);
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
    }
    
    .card {
        background: var(--card-bg);
        backdrop-filter: var(--glass-blur);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        border: 1px solid rgba(148, 163, 184, 0.1);
        transition: var(--transition);
    }
    
    .card:hover {
        background: var(--card-hover);
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    h1 {
        font-family: 'Exo 2', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        background: linear-gradient(to right, #00d4ff, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    
    h2 {
        font-family: 'Exo 2', sans-serif;
        font-weight: 600;
        font-size: 1.8rem;
        margin-bottom: 1.5rem;
        color: #e5e7eb;
    }
    
    h3 {
        font-weight: 600;
        font-size: 1.25rem;
        margin-bottom: 0.75rem;
        color: #caf0f8;
    }
    
    p {
        color: #cbd5e1;
        line-height: 1.7;
        margin-bottom: 1rem;
    }
    
    .btn-gradient {
        background: var(--primary-gradient);
        border: none;
        border-radius: 12px;
        padding: 0.85rem 1.5rem;
        color: white;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: var(--transition);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.2);
    }
    
    .btn-gradient:hover {
        transform: scale(1.03);
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3);
    }
    
    .btn-gradient:active {
        transform: scale(0.98);
    }
    
    .btn-secondary {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        color: #e5e7eb;
        font-weight: 500;
        font-size: 0.95rem;
        cursor: pointer;
        transition: var(--transition);
    }
    
    .btn-secondary:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(139, 92, 246, 0.5);
    }
    
    .input-element {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 14px;
        padding: 1rem;
        color: #e5e7eb;
        font-size: 1rem;
        transition: var(--transition);
    }
    
    .input-element:focus {
        outline: none;
        border-color: rgba(0, 212, 255, 0.5);
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
    }
    
    .highlight {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(139, 92, 246, 0.15));
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
        font-weight: 600;
    }
    
    .safe { color: #34d399; }
    .warning { color: #facc15; }
    .danger { color: #f87171; }
    
    .risk-indicator {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        margin-top: 1rem;
        font-size: 1.1rem;
    }
    
    .risk-safe { background: rgba(52, 211, 153, 0.1); color: #34d399; }
    .risk-warning { background: rgba(250, 204, 21, 0.1); color: #facc15; }
    .risk-danger { background: rgba(248, 113, 113, 0.1); color: #f87171; }
    
    .chat-message {
        background: rgba(255, 255, 255, 0.03);
        padding: 1rem;
        border-radius: 14px;
        margin-bottom: 1rem;
        border-left: 3px solid rgba(0, 212, 255, 0.3);
    }
    
    .chat-message.user {
        background: rgba(0, 212, 255, 0.05);
        border-left: 3px solid #00d4ff;
    }
    
    .chat-message.bot {
        background: rgba(139, 92, 246, 0.05);
        border-left: 3px solid #8b5cf6;
    }
    
    .section {
        margin-bottom: 2.5rem;
    }
    
    .demo-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        cursor: pointer;
        transition: var(--transition);
        border: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    .demo-card:hover {
        background: rgba(255, 255, 255, 0.06);
        transform: translateY(-2px);
    }
    
    .tab-container {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    .tab {
        padding: 1rem 1.5rem;
        cursor: pointer;
        transition: var(--transition);
        color: #9ca3af;
    }
    
    .tab.active {
        background: rgba(0, 212, 255, 0.1);
        color: #00d4ff;
        border-right: 3px solid rgba(0, 212, 255, 0.3);
    }
    
    .tab-content {
        padding: 1.5rem;
    }
    
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 3rem;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 1.5rem;
        transition: var(--transition);
        border: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    .feature-card:hover {
        background: rgba(255, 255, 255, 0.06);
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 212, 255, 0.1);
    }
    
    .resource-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 3px solid rgba(0, 212, 255, 0.3);
        transition: var(--transition);
    }
    
    .resource-card:hover {
        background: rgba(255, 255, 255, 0.06);
    }
    
    .quote {
        font-style: italic;
        color: #cbd5e1;
        border-left: 3px solid rgba(0, 212, 255, 0.5);
        padding-left: 1rem;
        margin: 1rem 0;
    }
    
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem;
        }
        
        .section {
            margin-bottom: 1.5rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if "page" not in st.session_state:
    st.session_state.page = "threat_analyzer"
    
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
if "ds_api_key" not in st.session_state:
    st.session_state.ds_api_key = os.getenv("DEEPSEEK_API_KEY", "")

if "vt_api_key" not in st.session_state:
    st.session_state.vt_api_key = os.getenv("VIRUSTOTAL_API_KEY", "")

if "analysis_count" not in st.session_state:
    st.session_state.analysis_count = 0

# Header section with raycast-inspired design
st.markdown("""
    <div style="margin-bottom: 2rem; text-align: center;">
        <h1 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem;">
            <span style="background: linear-gradient(to right, #00d4ff, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🛡️ КиберЩит</span>
        </h1>
        <p style="color: #cbd5e1; font-size: 1.1rem; max-width: 600px; margin: 0 auto;">
            Ваш компаньон в кибербезопасности для подростков 📱💻🔒
        </p>
    </div>
""", unsafe_allow_html=True)

# Main content container
main_container = st.container()

with main_container:
    # Sidebar navigation
    with st.sidebar:
        st.markdown('<div class="sidebar-header">🛡️ CODE <span class="sidebar-title">КиберЩит</span></div>', unsafe_allow_html=True)
        
        # Navigation items
        nav_items = [
            ("🔍 Анализатор угроз", "threat_analyzer"),
            ("🤖 КиберДруг", "cyber_friend"),
            ("📚 Обучение", "learning"),
        ]
        
        for item in nav_items:
            if st.session_state.page == item[1]:
                st.markdown(f'<div class="nav-item active" onclick="st.session_state.page=\'{item[1]}\'">\
                    <span>{item[0]}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="nav-item" onclick="st.session_state.page=\'{item[1]}\'">\
                    <span>{item[0]}</span></div>', unsafe_allow_html=True)
        
        # API Key Section
        st.markdown('<div class="api-key-section">', unsafe_allow_html=True)
        st.markdown('<div class="api-key-label">🔑 DeepSeek API Key</div>', unsafe_allow_html=True)
        st.session_state.ds_api_key = st.text_input(
            "", 
            value=st.session_state.ds_api_key, 
            type="password", 
            key="ds_api_key_input",
            label_visibility="collapsed",
            help="Введите ваш DeepSeek API ключ для использования AI-функций"
        )
        
        st.markdown('<div class="api-key-label" style="margin-top:10px;">🔑 VirusTotal API (опционально)</div>', unsafe_allow_html=True)
        st.session_state.vt_api_key = st.text_input(
            "", 
            value=st.session_state.vt_api_key, 
            type="password", 
            key="vt_api_key_input",
            label_visibility="collapsed",
            help="Введите ваш VirusTotal API ключ для проверки ссылок"
        )
        
        # Stats
        st.markdown("<div style='margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(148,163,184,0.1)'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 0.85rem; color: #9ca3af;'>✅ Проверок: {st.session_state.analysis_count}</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top: 0.5rem; font-size: 0.85rem; color: #9ca3af;'> 10-17 years old</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ==========================================
    # СТРАНИЦА: АНАЛИЗАТОР УГРОЗ
    # ==========================================
    if st.session_state.page == "threat_analyzer":
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.markdown('<h2>🔍 Анализатор Угроз</h2>', unsafe_allow_html=True)
            
            # Quick demo examples
            st.markdown('<div class="card" style="margin-bottom: 1.5rem;">', unsafe_allow_html=True)
            st.markdown('<h3 style="margin-bottom: 1rem;">💡 Быстрые примеры:</h3>', unsafe_allow_html=True)
            
            col1_profit, col2_profit, col3_profit = st.columns(3)
            
            with col1_profit:
                if st.button("📧 Фишинговое письмо", key="demo1"):
                    st.session_state.example_text = "Здравствуйте! Вы победили в конкурсе 1 000 000 руб. Нажмите сюда: bit.ly/prize-12345"
            
            with col2_profit:
                if st.button("🔗 Подозрительная ссылка", key="demo2"):
                    st.session_state.example_text = "Проверь этот сайт: tinyurl.com/suspicious-8f2d4"
            
            with col3_profit:
                if st.button("👥 Сообщение от друга", key="demo3"):
                    st.session_state.example_text = "Привет! Прости что украл твой аккаунт в игре, я вернусь с новым паролем..."
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Input area
            st.markdown('<div class="card" style="margin-bottom: 1.5rem;">', unsafe_allow_html=True)
            text_input = st.text_area(
                "📝 Введите текст для анализа:",
                value=st.session_state.get("example_text", ""),
                placeholder="Например: Здравствуйте! Вы выиграли iPhone 15. Чтобы получить подарок, перейдите по ссылке...",
                height=150,
                key="text_analysis"
            )
            
            if st.button("🚀 Проанализировать", use_container_width=True, key="analyze_button"):
                if text_input.strip():
                    if not st.session_state.ds_api_key:
                        st.warning("⚠️ Пожалуйста, введите DeepSeek API ключ в боковой панели!")
                    else:
                        with st.spinner("🔍 Щит сканирует данные..."):
                            # Используем наш новый модуль analyzer (DeepSeek + VirusTotal)
                            result = analyzer.analyze_text(
                                text_input, 
                                st.session_state.ds_api_key, 
                                st.session_state.vt_api_key
                            )
                            
                            if "error" in result:
                                st.error(f"⚠️ Ошибка: {result['error']}")
                            else:
                                st.session_state.analysis_count += 1
                                
                                # Определяем стили в зависимости от угрозы
                                threat_level = result.get("threat_level", "LOW")
                                if threat_level == "HIGH":
                                    risk_class = "risk-danger"
                                    risk_text = "⚠️ Высокая опасность"
                                elif threat_level == "MEDIUM":
                                    risk_class = "risk-warning"
                                    risk_text = "🟡 Внимание: Риск"
                                else:
                                    risk_class = "risk-safe"
                                    risk_text = "✅ Относительно безопасно"
                                
                                # Отображение результатов
                                st.markdown('<div class="card" style="margin-bottom: 1.5rem;">', unsafe_allow_html=True)
                                st.markdown(f'<h3 style="margin-bottom: 1rem;">📊 Результат анализа</h3>', unsafe_allow_html=True)
                                
                                col_result1, col_result2 = st.columns(2)
                                
                                with col_result1:
                                    st.markdown(f'<div class="risk-indicator {risk_class}" style="font-size: 1.25rem;">{risk_text}</div>', unsafe_allow_html=True)
                                    st.markdown(f"""
                                        <div class="card" style="margin-top: 1rem; background: rgba(15, 23, 42, 0.5);">
                                            <div style="font-size: 0.9rem; color: #9ca3af;">Уверенность ИИ</div>
                                            <div style="font-size: 2.5rem; font-weight: 700; color: #e5e7eb;">
                                                {result.get('confidence', 0)}%
                                            </div>
                                        </div>
                                    """, unsafe_allow_html=True)
                                
                                with col_result2:
                                    st.markdown(f"""
                                        <div class="card" style="background: rgba(15, 23, 42, 0.5);">
                                            <div style="font-size: 0.9rem; color: #9ca3af;">Идентифицированные угрозы ({result.get('scam_type', 'Неизвестно')})</div>
                                            <div style="margin-top: 0.5rem;">
                                    """, unsafe_allow_html=True)
                                    for flag in result.get("red_flags", [])[:3]:
                                        st.markdown(f"- {flag}")
                                    st.markdown("</div></div>", unsafe_allow_html=True)
                                
                                st.info(f"💬 **Почему это опасно:** {result.get('explanation', '')}")

                                # AI recommendations
                                st.markdown('<div class="card" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
                                st.markdown('<h3 style="margin-bottom: 1rem;">💡 Рекомендации</h3>', unsafe_allow_html=True)
                                for i, advice in enumerate(result.get("recommendations", [])[:3], 1):
                                    st.markdown(f"""
                                        <div class="card" style="background: rgba(0, 212, 255, 0.08); margin-bottom: 1rem;">
                                            <div style="color: #00d4ff; font-weight: 600; margin-bottom: 0.5rem;">🛡️ Шаг {i}</div>
                                            {advice}
                                        </div>
                                    """, unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.warning("Введите текст для анализа!")
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.markdown('<h2>📦 Проверьте это:</h2>', unsafe_allow_html=True)
            
            # Features section
            st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
            
            feature_cards = [
                ("🔗 Ссылка на сайт", "Анализ URL и проверка по базе VirusTotal"),
                ("📧 Электронное письмо", "Проверка фишинговых индикаторов через DeepSeek"),
                ("💬 Чат диалог", "Оценка угроз в переписке (социальная инженерия)"),
                ("📱 SMS уведомление", "Анализ коротких сообщений и подозрительных номеров")
            ]
            
            for title, desc in feature_cards:
                st.markdown(f"""
                    <div class="feature-card">
                        <h3 style="color: #00d4ff;">{title}</h3>
                        <p style="margin-bottom: 0;">{desc}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Safety tips
            st.markdown('<div class="card" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            st.markdown('<h3>🛡️ Быстрые советы по безопасности:</h3>', unsafe_allow_html=True)
            
            safety_tips = [
                ("Никогда не отдавай личные данные", "Ваши данные только вы можете защитить"),
                ("Проверь, что источник достоверен", "Trust but verify"),
                ("Пришло подозрительное сообщение?", "Спроси взрослого или проверь через другой канал"),
                ("Используй сильные пароли", "Сочетание букв, цифр и символов"),
                ("Проверяй настройки безопасности", "Регулярно смотри активные сессии")
            ]
            
            for tip, subtext in safety_tips:
                st.markdown(f"""
                    <div class="resource-card">
                        <div style="color: #a5f3fc; font-weight: 600;">{tip}</div>
                        <div style="color: #cbd5e1;">{subtext}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # ==========================================
    # СТРАНИЦА: КИБЕРДРУГ (ЧАТ-БОТ)
    # ==========================================
    elif st.session_state.page == "cyber_friend":
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown('<h2>🤖 КиберДруг</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Chat container
            chat_container = st.container()
            
            with chat_container:
                for message in st.session_state.chat_history:
                    if message["role"] == "user":
                        st.markdown(f"""
                            <div class="chat-message user">
                                <div style="color: #9ca3af; font-size: 0.8rem; margin-bottom: 0.5rem;">Вы • {message["timestamp"]}</div>
                                <div>{message["content"]}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="chat-message bot">
                                <div style="color: #9ca3af; font-size: 0.8rem; margin-bottom: 0.5rem;">🛡️ КиберДруг • {message["timestamp"]}</div>
                                <div>{message["content"]}</div>
                            </div>
                        """, unsafe_allow_html=True)
            
            # Input area
            user_input = st.text_input(
                "Введи свой вопрос про кибербезопасность...",
                key="cyber_friend_input",
                placeholder="Например: Как понять, что это фишинг? Или: Что такое двухфакторная аутентификация?"
            )
            
            if st.button("Отправить вопрос", key="chat_send"):
                if user_input.strip():
                    if not st.session_state.ds_api_key:
                        st.warning("⚠️ Пожалуйста, введите DeepSeek API ключ в боковой панели!")
                    else:
                        # Add user message to chat history
                        timestamp = datetime.now().strftime("%H:%M")
                        st.session_state.chat_history.append({
                            "role": "user",
                            "content": user_input,
                            "timestamp": timestamp
                        })
                        
                        with st.spinner("КиберДруг печатает..."):
                            # Используем наш модуль chatbot
                            bot_response = chatbot.get_chatbot_response(
                                st.session_state.chat_history, 
                                st.session_state.ds_api_key
                            )
                            
                            if "error" in bot_response:
                                st.error(f"⚠️ Ошибка: {bot_response['error']}")
                            else:
                                st.session_state.chat_history.append({
                                    "role": "assistant",
                                    "content": bot_response["content"],
                                    "timestamp": datetime.now().strftime("%H:%M")
                                })
                                st.experimental_rerun()
        
        with col2:
            st.markdown('<div class="card" style="margin-top: 0;">', unsafe_allow_html=True)
            st.markdown('<h3 style="margin-bottom: 1rem;">💡 Частые темы:</h3>', unsafe_allow_html=True)
            
            topic_cards = [
                ("🛡️ Защита аккаунта", "Как надежно защитить свою учетную запись"),
                ("🕵️ Фишинг", "Как распознать фишинговые письма и ссылки"),
                ("🔒 Пароли", "Как создать надежный пароль"),
                ("📱 Social Engineering", "Как не стать жертвой социальной инженерии"),
                ("🌐 Анонимность", "Как сохранить анонимность в сети")
            ]
            
            for topic, desc in topic_cards:
                st.markdown(f"""
                    <div class="resource-card">
                        <div style="color: #8b5cf6; font-weight: 600;">{topic}</div>
                        <div style="color: #9ca3af; font-size: 0.9em; margin-top: 0.3rem;">{desc}</div>
                    </div>
                """, unsafe_allow_html=True)
        
            st.markdown("</div>", unsafe_allow_html=True)
    
    # ==========================================
    # СТРАНИЦА: ОБУЧЕНИЕ (ПОЛНОСТЬЮ ВОССТАНОВЛЕННАЯ)
    # ==========================================
    elif st.session_state.page == "learning":
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.markdown('<h2>📚 Учитель</h2>', unsafe_allow_html=True)
        
        # Tabs for learning content
        tabs = ["Фишинг", "Пароли и безопасность", "Безопасность в социальных сетях", "Законы Беларуси"]
        
        # Используем Streamlit радио-кнопки стилизованные под табы для логики переключения
        selected_tab = st.radio("Выберите тему:", tabs, horizontal=True)
        
        # Content based on selected tab
        if selected_tab == "Фишинг":
            st.markdown('<div class="card" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            st.markdown('<h3>🤔 Что такое фишинг?</h3>', unsafe_allow_html=True)
            st.markdown("""
                <div style="background: rgba(0, 212, 255, 0.1); border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">
                    <p style="font-size: 1.1rem; line-height: 1.6;">
                        <strong>Фишинг</strong> — это попытка выманить у вас конфиденциальную информацию 
                        (пароли, номера карт, персональные данные), представившись trustworthy source.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<h4>Как распознать фишинг:</h4>', unsafe_allow_html=True)
            
            phishing_hall = [
                ("📧 Подозрительный отправитель", "Проверь email адрес - часто содержит опечатки"),
                ("⚠️ Срочность", "«Срочно!» / «Ваш аккаунт заблокирован!» / «Потеряете бонусы!»"),
                ("🔗 Подозрительная ссылка", "Проверь URL перед переходом, наведи мышку"),
                ("💸 Платежные запросы", "Запросы перевода денег, особенно криптовалюты"),
                ("🎁 Награды и выигрыши", "Сообщения «Вы выиграли!» без объяснимой причины")
            ]
            
            col_phishing1, col_phishing2 = st.columns(2)
            
            for i, (title, desc) in enumerate(phishing_hall[:5]):
                if i % 2 == 0:
                    col_phishing1.markdown(f"""
                        <div class="resource-card">
                            <div style="color: #00d4ff; font-weight: 600;">{title}</div>
                            <div style="color: #cbd5e1;">{desc}</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    col_phishing2.markdown(f"""
                        <div class="resource-card">
                            <div style="color: #00d4ff; font-weight: 600;">{title}</div>
                            <div style="color: #cbd5e1;">{desc}</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Interactive example
            st.markdown('<h4>Попробуй определить:</h4>', unsafe_allow_html=True)
            
            phishing_examples = [
                ("Письмо от банка", "Срочно подтвердите данные своей карты по ссылке bank-support-verify.com"),
                ("Письмо от друга", "Привет! Вижу, что у тебя отличный дизайн, мы бы хотели с тобой поработать - пришли портфолио на drive.google.com/my-fake-folder"),
                ("Сообщение в игре", "Привет! Твой аккаунт заблокирован за нарушение. Нажми здесь для разблокировки game-support-verify.ru"),
                ("Сообщение в мессенджере", "Привет, это мама! Срочно transferring money для экстренного случая, pin-код: 1234")
            ]
            
            col_phishing1, col_phishing2 = st.columns(2)
            
            for i, (scenario, example) in enumerate(phishing_examples):
                with (col_phishing1 if i % 2 == 0 else col_phishing2):
                    with st.expander(f"Сценарий {i+1}: {scenario}"):
                        st.markdown(f"""
                            <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 8px; margin: 1rem 0;">
                                {example}
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown("<div style='padding: 0.5rem; color: #a5f3fc; font-weight: 600;'>💡 Смущает ли вас это сообщение? Всегда проверяйте адресанта!</div>", unsafe_allow_html=True)
            
            st.markdown('<div class="card" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            st.markdown('<h3>🛡️ Как защититься:</h3>', unsafe_allow_html=True)
            
            safe_practices = [
                ("Всегда проверяй URL-адреса", "Даже мелкие отличия от нормального домена — красный флаг"),
                ("Не следуй по ссылкам из подозрительных сообщений", "Переходи на сайт напрямую через поисковик"),
                ("Включай двухфакторную аутентификацию", "Даже если не просили - это ваша дополнительная защита"),
                ("Регулярно проверяй безопасность аккаунта", "Настройки > Безопасность > Активные сессии"),
                ("Сообщай подозрительным сообщениям", "В социальных сетях есть кнопка «Сообщить о фишинге»")
            ]
            
            for practice in safe_practices:
                st.markdown(f"""
                    <div class="resource-card">
                        <div style="color: #34d399; font-weight: 600;">{practice[0]}</div>
                        <div style="color: #cbd5e1;">{practice[1]}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        elif selected_tab == "Пароли и безопасность":
            st.markdown('<div class="card" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            st.markdown('<h3>🔑 Что такое надежный пароль?</h3>', unsafe_allow_html=True)
            st.markdown("""
                <div style="background: rgba(0, 212, 255, 0.1); border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">
                    <p style="font-size: 1.1rem; line-height: 1.6;">
                        <strong>Надежный пароль</strong> — это комбинация символов, которая:
                    </p>
                    <ul style="margin-left: 1.5rem; margin-top: 1rem;">
                        <li style="color: #a5f3fc; margin-bottom: 0.5rem;">• Длина: минимум 12 символов (лучше 16+)</li>
                        <li style="color: #a5f3fc; margin-bottom: 0.5rem;">• Смешивает заглавные, строчные буквы, цифры, символы</li>
                        <li style="color: #a5f3fc; margin-bottom: 0.5rem;">• Не содержит личную информацию</li>
                        <li style="color: #a5f3fc;">• Уникален для каждого сервиса</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            
            # Password strength examples
            st.markdown('<h4>Примеры паролей:</h4>', unsafe_allow_html=True)
            
            pwd_examples = [
                ("❌ Слабый пароль", "qwerty123", "Очень легко взламывается"),
                ("⚠️ Ненадежный пароль", "yourname2005", "Содержит личные данные"),
                ("✅ Хороший пароль", "C0DE#Blue$Sky2025%", "Комбинация без смысла, но сложная"),
                ("🔐 Ультрасильный", "T7#kL9$vM!zQ4@pR", "Максимальная сложность, но трудно запомнить")
            ]
            
            col_pwd1, col_pwd2 = st.columns(2)
            
            for i, (title, pwd, desc) in enumerate(pwd_examples):
                with (col_pwd1 if i % 2 == 0 else col_pwd2):
                    st.markdown(f"""
                        <div class="resource-card" style="background: {'rgba(248, 113, 113, 0.1)' if 'Слабый' in title else 'rgba(52, 211, 153, 0.1)' if 'Хороший' in title else 'rgba(250, 204, 21, 0.1)' if 'Ненадежный' in title else 'rgba(139, 92, 246, 0.1)'}">
                            <div style="color: {'#f87171' if 'Слабый' in title else '#34d399' if 'Хороший' in title else '#facc15' if 'Ненадежный' in title else '#8b5cf6'}; font-weight: 700;">{title}</div>
                            <div style="font-weight: 600; font-family: monospace; margin: 0.5rem 0; padding: 0.5rem; background: rgba(15, 23, 42, 0.5); border-radius: 6px;">{pwd}</div>
                            <div style="color: #cbd5e1;">{desc}</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Password management
            st.markdown('<div class="card" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            st.markdown('<h3>🛡️ Как управлять паролями:</h3>', unsafe_allow_html=True)
            
            pwd_tools = [
                ("Менеджеры паролей", "Безопасное хранилище всех паролей (например, Bitwarden, 1Password)"),
                ("Двухфакторная аутентификация (2FA)", "Даже если пароль украдут, доступ закроется без кода из SMS/Приложения"),
                ("Регулярная смена", "Особенно для важных аккаунтов"),
                ("Уникальность", "Разные пароли для разных сервисов"),
                ("Мнемонические правила", "Фразы для запоминания сложных паролей (Например: 'Я люблю пить кофе по утрам!' -> 'Ялпкпу!')")
            ]
            
            for title, desc in pwd_tools:
                st.markdown(f"""
                    <div class="resource-card">
                        <div style="color: #00d4ff; font-weight: 600;">{title}</div>
                        <div style="color: #cbd5e1;">{desc}</div>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        elif selected_tab == "Безопасность в социальных сетях":
            st.markdown('<div class="card" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            st.markdown('<h3>📱 Социальные сети: твой цифровой дом</h3>', unsafe_allow_html=True)
            st.markdown("""
                <div style="background: rgba(0, 212, 255, 0.1); border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">
                    <p style="font-size: 1.1rem; line-height: 1.6;">
                        <strong>Социальные сети</strong> — это площадка для общения, но они должны быть защищены:
                    </p>
                    <ul style="margin-left: 1.5rem; margin-top: 1rem;">
                        <li style="color: #a5f3fc; margin-bottom: 0.5rem;">• Настройте приватность профиля</li>
                        <li style="color: #a5f3fc; margin-bottom: 0.5rem;">• Ограничьте доступ к личным данным</li>
                        <li style="color: #a5f3fc; margin-bottom: 0.5rem;">• Будьте осторожны с постами и метаданными (геолокация)</li>
                        <li style="color: #a5f3fc;">• Проверяйте источники сообщений</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            
            # Privacy check
            st.markdown('<h4>Проверка приватности:</h4>', unsafe_allow_html=True)
            
            privacy_checks = [
                ("Кто видит мою аватарку и номер?", "Зайди в 'Настройки' > 'Конфиденциальность' > 'Номер телефона' -> Никто/Только контакты"),
                ("Кто видит мои посты?", "Сделай профиль закрытым, если не хочешь посторонних глаз"),
                ("Кто может найти меня по email?", "Настройки > Конфиденциальность > Кто может найти меня"),
                ("Кто видит мои подписки?", "Скрой список подписок и подписчиков в настройках профиля"),
                ("Самые важные настройки", "Безопасность > Активные сессии (устройства) > Заверши все незнакомые")
            ]
            
            col_privacy1, col_privacy2 = st.columns(2)
            
            for i, (question, action) in enumerate(privacy_checks):
                with col_privacy1 if i % 2 == 0 else col_privacy2:
                    st.markdown(f"""
                        <div class="resource-card">
                            <div style="color: #8b5cf6; font-weight: 600;">{question}</div>
                            <div style="color: #cbd5e1; font-size: 0.9em; margin-top: 0.5rem;">{action}</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Cyberbullying
            st.markdown('<div class="card" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            st.markdown('<h3>🛡️ Как защититься от кибербуллинга:</h3>', unsafe_allow_html=True)
            
            cyberbully_steps = [
                ("Не отвечайте агрессорам", "Ответная агрессия или эмоции — это то, чего добивается тролль. Игнор работает лучше всего."),
                ("Сохраняйте доказательства", "Делайте скриншоты сообщений, сохраняйте email и ссылки на профиль агрессора."),
                ("Блокируйте и жалуйтесь", "Во всех соцсетях есть функция «В черный список» и кнопка «Пожаловаться» (Report)."),
                ("Обратитесь за помощью", "Обязательно расскажите доверенным взрослым: родителям, учителям, старшим братьям/сестрам.")
            ]
            
            for step in cyberbully_steps:
                st.markdown(f"""
                    <div class="resource-card">
                        <div style="color: #34d399; font-weight: 600;">{step[0]}</div>
                        <div style="color: #cbd5e1;">{step[1]}</div>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        elif selected_tab == "Законы Беларуси":
            st.markdown('<div class="card" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            st.markdown('<h3>⚖️ Цифровая реальность Республики Беларусь</h3>', unsafe_allow_html=True)
            st.markdown("""
                <div style="background: rgba(0, 212, 255, 0.1); border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">
                    <p style="font-size: 1.1rem; line-height: 1.6;">
                        <strong>Знать законы — значит уметь защищать свои права и не нарушать чужие.</strong><br>
                        Действия в интернете имеют реальные юридические последствия!
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Key legal areas
            legal_topics = [
                ("🛡️ Защита персональных данных", "Закон РБ «О защите персональных данных» (от 7 мая 2021 г. № 99-З). Никто не имеет права собирать и публиковать твои данные без твоего согласия."),
                ("💻 Преступления против информационной безопасности", "Уголовный кодекс РБ (Глава 31, ст. 349-355). Наказания за взлом аккаунтов (несанкционированный доступ), создание вирусов и модификацию компьютерной информации."),
                ("💳 Хищение имущества путем модификации информации", "Ст. 212 УК РБ. Кража денег с чужой банковской карты (даже если ты её просто нашел на улице и оплатил покупку) — это уголовное преступление!"),
                ("📱 Кибербуллинг и оскорбления", "Оскорбление в интернете (ст. 10.2 КоАП РБ), клевета (ст. 10.1 КоАП РБ, ст. 188 УК РБ). За травлю в сети предусмотрена реальная ответственность.")
            ]
            
            for topic, description in legal_topics:
                st.markdown(f"""
                    <div class="resource-card">
                        <div style="color: #3b82f6; font-weight: 700;">{topic}</div>
                        <div style="color: #cbd5e1; margin-top: 0.5rem;">{description}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Safe practices by law
            st.markdown('<div class="card" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
            st.markdown('<h3>🚔 Что делать, если ты стал жертвой:</h3>', unsafe_allow_html=True)
            
            legal_safety = [
                ("Куда обращаться", "Если украли деньги или взломали аккаунт — необходимо обратиться в милицию (по телефону 102 или в ближайший РУВД)."),
                ("Управление 'К'", "В МВД Беларуси работает специализированное Управление по противодействию киберпреступлениям («Управление К»)."),
                ("Как подготовиться", "Ничего не удаляй! Сохрани переписку, сделай скриншоты экранов с угрозами или фактом мошенничества, запиши номера телефонов или адреса сайтов злоумышленников.")
            ]
            
            for safety in legal_safety:
                st.markdown(f"""
                    <div class="resource-card">
                        <div style="color: #34d399; font-weight: 600;">{safety[0]}</div>
                        <div style="color: #cbd5e1; margin-top: 0.3rem;">{safety[1]}</div>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Footer section
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("💡 КиберЩит | #КиберПраво • Помогаем подросткам безопасно в цифровом мире")
    st.markdown("Сделано с ❤️ для поколения Z • 2025")
    st.markdown("</div>", unsafe_allow_html=True)