"""
Утилиты для построения графиков для дашборда
"""
import pandas as pd
import base64
import io
import matplotlib
matplotlib.use('Agg')  # Используем backend без GUI
import matplotlib.pyplot as plt
import seaborn as sns

# Настройка стиля
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        plt.style.use('ggplot')
sns.set_palette("husl")


def create_readmission_by_diagnoses_chart(df: pd.DataFrame) -> dict:
    """
    График 1: Зависимость повторных госпитализаций от количества диагнозов
    """
    try:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Группируем по количеству диагнозов
        chart_data = df.groupby('number_diagnoses')['readmitted'].apply(
            lambda x: (x.isin(['<30', '>30']).sum() / len(x)) * 100
        ).reset_index()
        chart_data.columns = ['number_diagnoses', 'readmission_rate']
        
        # Строим график
        ax.bar(chart_data['number_diagnoses'], chart_data['readmission_rate'], 
               color='steelblue', alpha=0.7, edgecolor='black')
        ax.set_xlabel('Количество диагнозов', fontsize=12, fontweight='bold')
        ax.set_ylabel('Процент повторных госпитализаций (%)', fontsize=12, fontweight='bold')
        ax.set_title('Зависимость повторных госпитализаций от количества диагнозов', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # Сохраняем в base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode()
        plt.close()
        
        return {
            "chart_type": "readmission_by_diagnoses",
            "title": "Зависимость повторных госпитализаций от количества диагнозов",
            "image_base64": img_base64,
            "data": chart_data.to_dict('records')
        }
    except Exception as e:
        raise Exception(f"Ошибка при создании графика: {str(e)}")


def create_readmission_by_inpatient_visits_chart(df: pd.DataFrame) -> dict:
    """
    График 2: Зависимость повторных госпитализаций от количества стационарных визитов
    """
    try:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Группируем по количеству стационарных визитов
        chart_data = df.groupby('number_inpatient')['readmitted'].apply(
            lambda x: (x.isin(['<30', '>30']).sum() / len(x) * 100) if len(x) > 0 else 0
        ).reset_index()
        chart_data.columns = ['number_inpatient', 'readmission_rate']
        
        # Фильтруем только те значения, где есть достаточно данных
        chart_data = chart_data[chart_data['number_inpatient'] <= 10]  # Ограничиваем для читаемости
        
        # Строим график
        ax.plot(chart_data['number_inpatient'], chart_data['readmission_rate'], 
               marker='o', linewidth=2, markersize=8, color='crimson')
        ax.fill_between(chart_data['number_inpatient'], chart_data['readmission_rate'], 
                       alpha=0.3, color='crimson')
        ax.set_xlabel('Количество стационарных визитов', fontsize=12, fontweight='bold')
        ax.set_ylabel('Процент повторных госпитализаций (%)', fontsize=12, fontweight='bold')
        ax.set_title('Зависимость повторных госпитализаций от количества стационарных визитов', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        # Сохраняем в base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode()
        plt.close()
        
        return {
            "chart_type": "readmission_by_inpatient_visits",
            "title": "Зависимость повторных госпитализаций от количества стационарных визитов",
            "image_base64": img_base64,
            "data": chart_data.to_dict('records')
        }
    except Exception as e:
        raise Exception(f"Ошибка при создании графика: {str(e)}")


def create_readmission_by_diabetes_med_chart(df: pd.DataFrame) -> dict:
    """
    График 3: Зависимость повторных госпитализаций от приема диабетических препаратов
    """
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Подготовка данных
        chart_data = df.groupby('diabetesMed')['readmitted'].apply(
            lambda x: pd.Series({
                'NO': (x == 'NO').sum(),
                '<30': (x == '<30').sum(),
                '>30': (x == '>30').sum(),
                'total': len(x)
            })
        ).unstack()
        
        # График 1: Столбчатая диаграмма
        chart_data_pct = chart_data[['NO', '<30', '>30']].div(chart_data['total'], axis=0) * 100
        chart_data_pct.plot(kind='bar', ax=ax1, color=['#2ecc71', '#f39c12', '#e74c3c'], 
                           edgecolor='black', alpha=0.8)
        ax1.set_xlabel('Прием диабетических препаратов', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Процент (%)', fontsize=11, fontweight='bold')
        ax1.set_title('Распределение повторных госпитализаций\nпо приему препаратов', 
                     fontsize=12, fontweight='bold')
        ax1.legend(['Нет повторной госпитализации', '<30 дней', '>30 дней'], 
                  loc='upper right', fontsize=9)
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=0)
        ax1.grid(axis='y', alpha=0.3)
        
        # График 2: Круговая диаграмма для "Yes"
        if 'Yes' in chart_data_pct.index:
            yes_data = chart_data_pct.loc['Yes', ['NO', '<30', '>30']]
            ax2.pie(yes_data.values, labels=['Нет', '<30 дней', '>30 дней'], 
                   autopct='%1.1f%%', startangle=90, 
                   colors=['#2ecc71', '#f39c12', '#e74c3c'], 
                   explode=(0.05, 0.1, 0.1), shadow=True)
            ax2.set_title('Распределение для пациентов\nс приемом препаратов', 
                         fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        # Сохраняем в base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode()
        plt.close()
        
        return {
            "chart_type": "readmission_by_diabetes_med",
            "title": "Зависимость повторных госпитализаций от приема диабетических препаратов",
            "image_base64": img_base64,
            "data": chart_data_pct.to_dict('index')
        }
    except Exception as e:
        raise Exception(f"Ошибка при создании графика: {str(e)}")


def create_custom_chart(df: pd.DataFrame, feature: str, chart_type: str = "bar") -> dict:
    """
    Создает произвольный график зависимости повторных госпитализаций от выбранного признака
    
    Входные данные:
    - df: DataFrame с данными (должен содержать столбцы feature и 'readmitted')
    - feature: название признака для анализа
    - chart_type: тип графика ('bar', 'line', 'pie')
    
    Возвращает:
    - dict с полями: chart_type, title, image_base64, data
    
    Используется в: src/api/routes/dashboard.py для построения произвольных графиков
    """
    # Словарь русских названий признаков
    feature_names_ru = {
        "number_inpatient": "Количество стационарных визитов",
        "number_diagnoses": "Количество диагнозов",
        "number_emergency": "Количество экстренных визитов",
        "number_outpatient": "Количество амбулаторных визитов",
        "time_in_hospital": "Время в больнице (дни)",
        "diag_1": "Основной диагноз",
        "diag_2": "Второй диагноз",
        "diag_3": "Третий диагноз",
        "medical_specialty": "Медицинская специальность",
        "diabetesMed": "Прием диабетических препаратов"
    }
    
    # Получаем русское название признака
    feature_ru = feature_names_ru.get(feature, feature)
    
    try:
        if feature not in df.columns:
            raise ValueError(f"Признак '{feature}' не найден в данных")
        
        if feature == 'readmitted':
            raise ValueError("Нельзя строить график по целевому признаку")
        
        # Определяем тип признака
        is_numeric = pd.api.types.is_numeric_dtype(df[feature])
        
        if chart_type == "bar":
            fig, ax = plt.subplots(figsize=(12, 6))
            
            if is_numeric:
                # Для числовых признаков группируем
                chart_data = df.groupby(feature)['readmitted'].apply(
                    lambda x: (x.isin(['<30', '>30']).sum() / len(x) * 100) if len(x) > 0 else 0
                ).reset_index()
                chart_data.columns = [feature, 'readmission_rate']
                # Ограничиваем для читаемости
                if len(chart_data) > 20:
                    chart_data = chart_data.head(20)
                
                ax.bar(chart_data[feature], chart_data['readmission_rate'], 
                      color='steelblue', alpha=0.7, edgecolor='black')
            else:
                # Для категориальных признаков
                chart_data = df.groupby(feature)['readmitted'].apply(
                    lambda x: (x.isin(['<30', '>30']).sum() / len(x) * 100) if len(x) > 0 else 0
                ).reset_index()
                chart_data.columns = [feature, 'readmission_rate']
                chart_data = chart_data.sort_values('readmission_rate', ascending=False).head(15)
                
                ax.bar(range(len(chart_data)), chart_data['readmission_rate'], 
                      color='steelblue', alpha=0.7, edgecolor='black')
                ax.set_xticks(range(len(chart_data)))
                ax.set_xticklabels(chart_data[feature], rotation=45, ha='right')
            
            ax.set_xlabel(feature_ru, fontsize=12, fontweight='bold')
            ax.set_ylabel('Процент повторных госпитализаций (%)', fontsize=12, fontweight='bold')
            ax.set_title(f'Зависимость повторных госпитализаций от {feature_ru}', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.grid(axis='y', alpha=0.3)
            
        elif chart_type == "line":
            if not is_numeric:
                raise ValueError("Линейный график можно строить только для числовых признаков")
            
            fig, ax = plt.subplots(figsize=(12, 6))
            chart_data = df.groupby(feature)['readmitted'].apply(
                lambda x: (x.isin(['<30', '>30']).sum() / len(x) * 100) if len(x) > 0 else 0
            ).reset_index()
            chart_data.columns = [feature, 'readmission_rate']
            chart_data = chart_data.sort_values(feature)
            
            if len(chart_data) > 50:
                chart_data = chart_data.head(50)
            
            ax.plot(chart_data[feature], chart_data['readmission_rate'], 
                   marker='o', linewidth=2, markersize=6, color='crimson')
            ax.fill_between(chart_data[feature], chart_data['readmission_rate'], 
                          alpha=0.3, color='crimson')
            ax.set_xlabel(feature_ru, fontsize=12, fontweight='bold')
            ax.set_ylabel('Процент повторных госпитализаций (%)', fontsize=12, fontweight='bold')
            ax.set_title(f'Зависимость повторных госпитализаций от {feature_ru}', 
                        fontsize=14, fontweight='bold', pad=20)
            ax.grid(axis='y', alpha=0.3)
            
        elif chart_type == "pie":
            if is_numeric:
                raise ValueError("Круговую диаграмму можно строить только для категориальных признаков")
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Группируем по признаку и считаем распределение readmitted
            chart_data = df.groupby(feature)['readmitted'].apply(
                lambda x: pd.Series({
                    'NO': (x == 'NO').sum(),
                    '<30': (x == '<30').sum(),
                    '>30': (x == '>30').sum(),
                })
            ).unstack()
            
            # Берем топ-10 категорий
            top_categories = chart_data.sum(axis=1).nlargest(10).index
            chart_data = chart_data.loc[top_categories]
            
            # Строим круговую диаграмму для каждой категории (берем первую)
            if len(chart_data) > 0:
                first_category = chart_data.index[0]
                values = chart_data.loc[first_category, ['NO', '<30', '>30']].values
                labels = ['Нет повторной госпитализации', '<30 дней', '>30 дней']
                colors = ['#2ecc71', '#f39c12', '#e74c3c']
                
                ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90,
                      colors=colors, explode=(0.05, 0.1, 0.1), shadow=True)
                ax.set_title(f'Распределение для {feature_ru}: {first_category}', 
                           fontsize=14, fontweight='bold')
        else:
            raise ValueError(f"Неизвестный тип графика: {chart_type}")
        
        plt.tight_layout()
        
        # Сохраняем в base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode()
        plt.close()
        
        return {
            "chart_type": f"custom_{chart_type}",
            "title": f"Зависимость повторных госпитализаций от {feature_ru}",
            "image_base64": img_base64,
            "data": chart_data.to_dict('records') if hasattr(chart_data, 'to_dict') else {}
        }
    except Exception as e:
        raise Exception(f"Ошибка при создании графика: {str(e)}")


# Словарь доступных графиков
AVAILABLE_CHARTS = {
    "readmission_by_diagnoses": create_readmission_by_diagnoses_chart,
    "readmission_by_inpatient_visits": create_readmission_by_inpatient_visits_chart,
    "readmission_by_diabetes_med": create_readmission_by_diabetes_med_chart,
    "custom": create_custom_chart
}

