import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image
import json
import os

# Конфигурация API
# Можно настроить через переменную окружения STREAMLIT_API_URL
API_BASE_URL = os.getenv("STREAMLIT_API_URL", "http://127.0.0.1:8000")

# Показываем текущий URL API в боковой панели для отладки
st.sidebar.markdown("---")
st.sidebar.markdown(f"**API URL:** `{API_BASE_URL}`")

# Топ-10 признаков
TOP10_FEATURES = [
    "number_inpatient",
    "number_diagnoses",
    "number_emergency",
    "number_outpatient",
    "time_in_hospital",
    "diag_1",
    "diag_2",
    "diag_3",
    "medical_specialty",
    "diabetesMed"
]

# Настройка страницы
st.set_page_config(
    page_title="Аналитика повторных госпитализаций",
    page_icon="🏥",
    layout="wide"
)

# CSS для улучшения дизайна
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Заголовок
st.markdown('<h1 class="main-header">🏥 Аналитическая платформа повторных госпитализаций</h1>', unsafe_allow_html=True)
st.markdown("---")

# Боковая панель для навигации
st.sidebar.title("📊 Навигация")
page = st.sidebar.radio(
    "Выберите раздел:",
    ["📈 Дашборд", "🔮 Предсказание", "📤 Загрузка данных", "ℹ️ О проекте"]
)

# Функция для обработки ошибок API
def make_api_request(url, method="GET", json_data=None, files=None):
    """Универсальная функция для запросов к API с обработкой ошибок"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, timeout=30)
            else:
                response = requests.post(url, json=json_data, timeout=10, headers={"Content-Type": "application/json"})
        else:
            raise ValueError(f"Неподдерживаемый метод: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError as e:
        st.error(f"❌ Не удалось подключиться к API. Убедитесь, что сервер запущен на http://127.0.0.1:8000\nОшибка: {str(e)}")
        return None
    except requests.exceptions.Timeout:
        st.error("❌ Превышено время ожидания ответа от сервера")
        return None
    except requests.exceptions.HTTPError as e:
        try:
            error_detail = response.json().get("detail", str(e))
        except:
            error_detail = f"{e.response.status_code} {e.response.reason}: {str(e)}"
        st.error(f"❌ Ошибка API ({e.response.status_code}): {error_detail}")
        # Показываем больше информации для отладки
        if e.response.status_code == 502:
            st.warning("💡 Подсказка: 502 Bad Gateway обычно означает, что запрос не дошел до сервера. Проверьте, что API запущен и доступен.")
        return None
    except Exception as e:
        st.error(f"❌ Неожиданная ошибка: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None

# Страница дашборда
if page == "📈 Дашборд":
    st.markdown('<h2 class="sub-header">📊 Аналитические графики</h2>', unsafe_allow_html=True)
    
    # Загрузка статистики
    with st.spinner("Загрузка статистики..."):
        stats = make_api_request(f"{API_BASE_URL}/dashboard/stats")
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Всего записей", stats.get("rows", 0))
        with col2:
            st.metric("Процент повторных госпитализаций", f"{stats.get('readmission_rate', 0):.2f}%")
        with col3:
            st.metric("С повторной госпитализацией", stats.get("readmission_count", 0))
        with col4:
            st.metric("Без повторной госпитализации", stats.get("no_readmission_count", 0))
    
    st.markdown("---")
    
    # Выбор типа графика
    st.markdown("### Выберите график для отображения")
    
    chart_types = {
        "readmission_by_diagnoses": "📊 Зависимость от количества диагнозов",
        "readmission_by_inpatient_visits": "🏥 Зависимость от стационарных визитов",
        "readmission_by_diabetes_med": "💊 Зависимость от приема препаратов"
    }
    
    selected_chart = st.selectbox(
        "Тип графика:",
        options=list(chart_types.keys()),
        format_func=lambda x: chart_types[x]
    )
    
    if st.button("🔄 Построить график", type="primary"):
        with st.spinner("Построение графика..."):
            chart_data = make_api_request(f"{API_BASE_URL}/dashboard/chart?chart_type={selected_chart}")
        
        if chart_data:
            try:
                # Декодируем изображение
                img_data = base64.b64decode(chart_data["image_base64"])
                img = Image.open(BytesIO(img_data))
                
                st.markdown(f"### {chart_data.get('title', 'График')}")
                st.image(img, use_container_width=True)
                
                # Показываем данные графика
                with st.expander("📋 Данные графика"):
                    st.json(chart_data.get("data", {}))
            except Exception as e:
                st.error(f"Ошибка при отображении графика: {str(e)}")

# Страница предсказания
elif page == "🔮 Предсказание":
    st.markdown('<h2 class="sub-header">🔮 Прогноз повторной госпитализации</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>Инструкция:</strong> Заполните все поля данными пациента для получения прогноза вероятности повторной госпитализации.
    </div>
    """, unsafe_allow_html=True)
    
    # Форма ввода данных
    col1, col2 = st.columns(2)
    
    inputs = {}
    with col1:
        st.markdown("### Числовые признаки")
        inputs["number_inpatient"] = st.number_input("Количество стационарных визитов", min_value=0, value=0, step=1)
        inputs["number_diagnoses"] = st.number_input("Количество диагнозов", min_value=0, value=1, step=1)
        inputs["number_emergency"] = st.number_input("Количество экстренных визитов", min_value=0, value=0, step=1)
        inputs["number_outpatient"] = st.number_input("Количество амбулаторных визитов", min_value=0, value=0, step=1)
        inputs["time_in_hospital"] = st.number_input("Время в больнице (дни)", min_value=0, value=1, step=1, help="Количество дней пребывания в больнице")
    
    with col2:
        st.markdown("### Категориальные признаки")
        inputs["diag_1"] = st.text_input("Диагноз 1", value="250.83", help="Код основного диагноза")
        inputs["diag_2"] = st.text_input("Диагноз 2", value="Unknown", help="Код второго диагноза")
        inputs["diag_3"] = st.text_input("Диагноз 3", value="Unknown", help="Код третьего диагноза")
        inputs["medical_specialty"] = st.text_input("Медицинская специальность", value="Unknown", help="Например: Cardiology, InternalMedicine")
        inputs["diabetesMed"] = st.selectbox("Прием диабетических препаратов", options=["Yes", "No"], index=1)
    
    if st.button("🔮 Получить прогноз", type="primary", use_container_width=True):
        # Валидация
        if not all(str(v).strip() for v in inputs.values()):
            st.error("❌ Пожалуйста, заполните все поля")
        else:
            with st.spinner("Выполняется прогноз..."):
                result = make_api_request(
                    f"{API_BASE_URL}/model/predict",
                    method="POST",
                    json_data={"data": inputs}
                )
            
            if result:
                st.markdown("---")
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.markdown(f"### ✅ Результат прогноза")
                
                # Используем данные из API (уже нормализованные)
                prediction_category = result.get("prediction_category", "Неопределено")
                risk_level = result.get("risk_level", "Неопределено")
                probability = result.get("probability", 0.0)
                
                # Определяем цвет по уровню риска
                if risk_level == "Низкий риск":
                    prediction_color = "🟢"
                elif risk_level == "Высокий риск":
                    prediction_color = "🟡"
                elif risk_level == "Средний риск":
                    prediction_color = "🟠"
                else:
                    prediction_color = "⚪"
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Уровень риска", f"{prediction_color} {risk_level}")
                with col2:
                    st.metric("Прогноз", prediction_category)
                with col3:
                    st.metric("Вероятность", f"{probability:.2%}")
                
                # Дополнительная информация
                st.info(f"**Интерпретация:** {prediction_category}. Вероятность данного исхода составляет {probability:.1%}.")
                
                st.markdown('</div>', unsafe_allow_html=True)

# Страница загрузки данных
elif page == "📤 Загрузка данных":
    st.markdown('<h2 class="sub-header">📤 Загрузка данных в базу</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>Требования к файлу:</strong>
    <ul>
        <li>Формат: CSV</li>
        <li>Все столбцы должны быть заполнены (без пропусков)</li>
        <li>Обязательные столбцы: number_inpatient, number_diagnoses, number_emergency, number_outpatient, 
        time_in_hospital, diag_1, diag_2, diag_3, medical_specialty, diabetesMed, readmitted</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Выберите CSV файл", type=["csv"])
    
    if uploaded_file is not None:
        if st.button("📤 Загрузить в базу данных", type="primary"):
            with st.spinner("Загрузка и валидация данных..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                result = make_api_request(
                    f"{API_BASE_URL}/data/upload",
                    method="POST",
                    files=files
                )
            
            if result:
                st.success(f"✅ {result.get('message', 'Данные успешно загружены')}")
                st.info(f"📊 Добавлено записей: {result.get('rows_added', 0)}")
                st.info(f"📈 Всего записей в БД: {result.get('total_rows_in_db', 0)}")

# Страница о проекте
elif page == "ℹ️ О проекте":
    st.markdown('<h2 class="sub-header">ℹ️ О проекте</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    ## Аналитическая платформа повторных госпитализаций пациентов с диабетом
    
    ### Описание
    Данная платформа предназначена для анализа факторов, влияющих на повторные госпитализации 
    пациентов с диабетом, и прогнозирования вероятности повторной госпитализации.
    
    ### Функциональность
    - **📊 Дашборд**: Визуализация данных и анализ зависимостей
    - **🔮 Предсказание**: Прогнозирование повторной госпитализации на основе данных пациента
    - **📤 Загрузка данных**: Пополнение базы данных новыми записями
    
    ### Используемые признаки (топ-10)
    1. number_inpatient - количество стационарных визитов
    2. number_diagnoses - количество диагнозов
    3. number_emergency - количество экстренных визитов
    4. number_outpatient - количество амбулаторных визитов
    5. time_in_hospital - время пребывания в больнице (дни)
    6. diag_1 - основной диагноз
    7. diag_2 - второй диагноз
    8. diag_3 - третий диагноз
    9. medical_specialty - медицинская специальность
    10. diabetesMed - прием диабетических препаратов
    
    ### Технологии
    - Backend: FastAPI, SQLAlchemy, CatBoost
    - Frontend: Streamlit
    - База данных: SQLite
    - Визуализация: Matplotlib, Seaborn
    """)
    
    # Проверка подключения к API
    st.markdown("---")
    st.markdown("### 🔌 Статус подключения")
    if st.button("Проверить подключение к API"):
        with st.spinner("Проверка..."):
            response = make_api_request(f"{API_BASE_URL}/")
        if response:
            st.success("✅ API доступен и работает")
        else:
            st.error("❌ API недоступен")

