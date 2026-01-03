"""
Модуль: src/data_processing/advanced_preprocessing.py

Назначение:
    Расширенная предобработка данных с анализом выбросов, стандартизацией, нормализацией
    и кодированием категориальных признаков. Строит графики для визуализации.

Входные данные:
    - CSV файл data/processed/diabetic_data_top10.csv с топ-10 признаками

Выходные данные:
    - Статистики в консоль (пропуски, выбросы, описательная статистика)
    - Графики в отдельных окнах (ящики с усами, распределения, корреляции)
    - Результаты обучения CatBoost (метрики, важность признаков)
    - Обработанные данные (стандартизированные, нормализованные)

Использование:
    - Запускается вручную: python -m src.data_processing.advanced_preprocessing
    - Используется для демонстрации этапов предобработки и обучения модели
    - Графики отображаются в отдельных окнах (в PyCharm - в боковой панели)
    - Модель CatBoost обучается автоматически с выводом метрик
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.preprocessing import label_binarize
import warnings
warnings.filterwarnings('ignore')

# Опциональный импорт CatBoost
try:
    from catboost import CatBoostClassifier
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
    print("⚠️ CatBoost не установлен. Обучение модели будет пропущено.")
    print("   Для установки: pip install catboost")

# Настройка для отображения графиков в PyCharm
# Пробуем разные backends для совместимости
try:
    import matplotlib
    # Для PyCharm используем Agg backend, но с отображением в отдельных окнах
    matplotlib.use('TkAgg', force=True)  # Принудительно TkAgg
    import matplotlib.pyplot as plt
    plt.switch_backend('TkAgg')  # Переключаемся на TkAgg
except Exception as e:
    print(f"⚠️ Не удалось настроить TkAgg backend: {e}")
    try:
        matplotlib.use('Qt5Agg', force=True)
        import matplotlib.pyplot as plt
        plt.switch_backend('Qt5Agg')
    except:
        try:
            matplotlib.use('Agg', force=True)  # Без GUI для сохранения
            print("⚠️ Графики будут сохранены в файлы, но не отображены")
        except:
            print("❌ Не удалось настроить matplotlib backend")

plt.ion()  # Интерактивный режим
sns.set_style("whitegrid")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TOP10_PATH = PROJECT_ROOT / "data" / "processed" / "diabetic_data_top10.csv"

# Топ-10 признаков
NUMERICAL_FEATURES = [
    "number_inpatient",
    "number_diagnoses",
    "number_emergency",
    "number_outpatient",
    "time_in_hospital"
]

CATEGORICAL_FEATURES = [
    "diag_1",
    "diag_2",
    "diag_3",
    "medical_specialty",
    "diabetesMed"
]

TARGET = "readmitted"


def load_data():
    """Загружает данные с топ-10 признаками"""
    if not TOP10_PATH.exists():
        raise FileNotFoundError(f"Файл {TOP10_PATH} не найден. Сначала запустите select_top_features.py")
    
    df = pd.read_csv(TOP10_PATH)
    print(f"✅ Загружено {len(df)} записей, {len(df.columns)} столбцов")
    return df


def analyze_missing_values(df):
    """Анализ пропусков в данных"""
    print("\n" + "="*60)
    print("АНАЛИЗ ПРОПУСКОВ В ДАННЫХ")
    print("="*60)
    
    missing = df.isna().sum()
    missing_pct = (missing / len(df)) * 100
    
    missing_df = pd.DataFrame({
        'Столбец': missing.index,
        'Количество пропусков': missing.values,
        'Процент пропусков (%)': missing_pct.values
    })
    missing_df = missing_df[missing_df['Количество пропусков'] > 0]
    
    if missing_df.empty:
        print("✅ Пропусков в данных не обнаружено")
    else:
        print(missing_df.to_string(index=False))
    
    return missing_df


def detect_outliers_iqr(df, feature):
    """Обнаружение выбросов методом IQR (межквартильный размах)"""
    Q1 = df[feature].quantile(0.25)
    Q3 = df[feature].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df[feature] < lower_bound) | (df[feature] > upper_bound)]
    
    return {
        'Q1': Q1,
        'Q3': Q3,
        'IQR': IQR,
        'lower_bound': lower_bound,
        'upper_bound': upper_bound,
        'outliers_count': len(outliers),
        'outliers_pct': (len(outliers) / len(df)) * 100
    }


def analyze_outliers(df):
    """Анализ выбросов для числовых признаков"""
    print("\n" + "="*60)
    print("АНАЛИЗ ВЫБРОСОВ (МЕТОД IQR)")
    print("="*60)
    
    outliers_info = {}
    
    for feature in NUMERICAL_FEATURES:
        if feature in df.columns:
            info = detect_outliers_iqr(df, feature)
            outliers_info[feature] = info
            
            print(f"\n📊 {feature}:")
            print(f"   Q1 (25%): {info['Q1']:.2f}")
            print(f"   Q3 (75%): {info['Q3']:.2f}")
            print(f"   IQR: {info['IQR']:.2f}")
            print(f"   Границы: [{info['lower_bound']:.2f}, {info['upper_bound']:.2f}]")
            print(f"   Выбросов: {info['outliers_count']} ({info['outliers_pct']:.2f}%)")
    
    return outliers_info


def plot_boxplots(df):
    """Построение ящиков с усами для числовых признаков"""
    print("\n" + "="*60)
    print("ПОСТРОЕНИЕ ЯЩИКОВ С УСАМИ")
    print("="*60)
    
    num_features = [f for f in NUMERICAL_FEATURES if f in df.columns]
    n_features = len(num_features)
    
    if n_features == 0:
        print("⚠️ Нет числовых признаков для построения графиков")
        return
    
    # Создаем сетку графиков
    cols = 2
    rows = (n_features + 1) // 2
    
    fig, axes = plt.subplots(rows, cols, figsize=(14, 4 * rows))
    fig.suptitle('Ящики с усами для числовых признаков (выявление выбросов)',
                 fontsize=16, fontweight='bold')
    
    if n_features == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
    
    for idx, feature in enumerate(num_features):
        ax = axes[idx]
        df.boxplot(column=feature, ax=ax, vert=True)
        ax.set_title(f'{feature}', fontweight='bold')
        ax.set_ylabel('Значение')
        ax.grid(True, alpha=0.3)
    
    # Скрываем лишние подграфики
    for idx in range(n_features, len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.4, wspace=0.3, top=0.85)  # Увеличиваем расстояние между графиками и опускаем их ниже
    plt.draw()
    plt.pause(0.1)
    print("✅ Графики ящиков с усами построены")


def plot_distributions(df):
    """Построение распределений для числовых признаков"""
    print("\n" + "="*60)
    print("РАСПРЕДЕЛЕНИЯ ЧИСЛОВЫХ ПРИЗНАКОВ")
    print("="*60)
    
    num_features = [f for f in NUMERICAL_FEATURES if f in df.columns]
    n_features = len(num_features)
    
    if n_features == 0:
        return
    
    cols = 2
    rows = (n_features + 1) // 2

    fig, axes = plt.subplots(rows, cols, figsize=(14, 5 * rows))
    fig.suptitle('Распределения числовых признаков', fontsize=16, fontweight='bold')
    
    if n_features == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
    
    for idx, feature in enumerate(num_features):
        ax = axes[idx]
        df[feature].hist(bins=30, ax=ax, edgecolor='black', alpha=0.7, color='steelblue')
        ax.set_title(f'{feature}', fontweight='bold')
        ax.set_xlabel('Значение')
        ax.set_ylabel('Частота')
        ax.grid(True, alpha=0.3)
        # Добавляем вертикальные линии для среднего и медианы
        ax.axvline(df[feature].mean(), color='red', linestyle='--', linewidth=2, label=f'Среднее: {df[feature].mean():.2f}')
        ax.axvline(df[feature].median(), color='green', linestyle='--', linewidth=2, label=f'Медиана: {df[feature].median():.2f}')
        ax.legend()
    
    for idx in range(n_features, len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.4, wspace=0.3, top=0.85)  # Увеличиваем расстояние между графиками и опускаем их ниже
    plt.draw()
    plt.pause(0.1)
    print("✅ Графики распределений построены")


def plot_correlation_heatmap(df):
    """Построение тепловой карты корреляций для числовых признаков"""
    print("\n" + "="*60)
    print("ТЕПЛОВАЯ КАРТА КОРРЕЛЯЦИЙ")
    print("="*60)
    
    num_features = [f for f in NUMERICAL_FEATURES if f in df.columns]
    
    if len(num_features) < 2:
        print("⚠️ Недостаточно числовых признаков для построения корреляций")
        return
    
    # Вычисляем корреляцию
    corr_matrix = df[num_features].corr()
    
    # Строим тепловую карту
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8})
    plt.title('Корреляционная матрица числовых признаков', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.draw()
    plt.pause(0.1)
    print("✅ Тепловая карта корреляций построена")
    
    # Выводим топ корреляций
    print("\nТоп-5 пар признаков с наибольшей корреляцией:")
    corr_pairs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_pairs.append((
                corr_matrix.columns[i],
                corr_matrix.columns[j],
                corr_matrix.iloc[i, j]
            ))
    corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    for feat1, feat2, corr in corr_pairs[:5]:
        print(f"   {feat1} ↔ {feat2}: {corr:.3f}")


def plot_target_distribution(df):
    """Построение распределения целевого признака"""
    if TARGET not in df.columns:
        return
    
    print("\n" + "="*60)
    print("РАСПРЕДЕЛЕНИЕ ЦЕЛЕВОГО ПРИЗНАКА")
    print("="*60)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Столбчатая диаграмма
    value_counts = df[TARGET].value_counts()
    colors = ['#2ecc71', '#f39c12', '#e74c3c']  # Зеленый, оранжевый, красный
    ax1.bar(value_counts.index, value_counts.values, color=colors[:len(value_counts)], 
           edgecolor='black', alpha=0.7)
    ax1.set_xlabel('Категория повторной госпитализации', fontweight='bold')
    ax1.set_ylabel('Количество', fontweight='bold')
    ax1.set_title('Распределение по категориям', fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    # Добавляем значения на столбцы
    for i, (idx, val) in enumerate(value_counts.items()):
        ax1.text(idx, val, str(val), ha='center', va='bottom', fontweight='bold')
    
    # Круговая диаграмма
    labels = []
    for idx in value_counts.index:
        if idx == 'NO':
            labels.append('Нет повторной\nгоспитализации')
        elif idx == '<30':
            labels.append('Госпитализация\n<30 дней')
        elif idx == '>30':
            labels.append('Госпитализация\n>30 дней')
        else:
            labels.append(str(idx))
    
    ax2.pie(value_counts.values, labels=labels, autopct='%1.1f%%', 
           colors=colors[:len(value_counts)], startangle=90, 
           explode=[0.05] * len(value_counts), shadow=True)
    ax2.set_title('Процентное распределение', fontweight='bold')
    
    plt.tight_layout()
    plt.draw()
    plt.pause(0.1)
    print("✅ Графики распределения целевого признака построены")


def analyze_categorical_features(df):
    """Анализ категориальных признаков"""
    print("\n" + "="*60)
    print("АНАЛИЗ КАТЕГОРИАЛЬНЫХ ПРИЗНАКОВ")
    print("="*60)
    
    for feature in CATEGORICAL_FEATURES:
        if feature in df.columns:
            unique_count = df[feature].nunique()
            value_counts = df[feature].value_counts()
            
            print(f"\n📋 {feature}:")
            print(f"   Уникальных значений: {unique_count}")
            print(f"   Топ-5 значений:")
            for val, count in value_counts.head(5).items():
                pct = (count / len(df)) * 100
                print(f"      {val}: {count} ({pct:.2f}%)")


def standardize_data(df):
    """Стандартизация числовых признаков (Z-score нормализация)"""
    print("\n" + "="*60)
    print("СТАНДАРТИЗАЦИЯ ДАННЫХ (Z-score)")
    print("="*60)
    
    df_standardized = df.copy()
    scaler = StandardScaler()
    
    num_features = [f for f in NUMERICAL_FEATURES if f in df.columns]
    
    if num_features:
        df_standardized[num_features] = scaler.fit_transform(df[num_features])
        
        print("✅ Стандартизация выполнена")
        print("\nСтатистики ДО стандартизации:")
        print(df[num_features].describe().round(2))
        
        print("\nСтатистики ПОСЛЕ стандартизации:")
        print(df_standardized[num_features].describe().round(2))
        
        print("\nПроверка: среднее должно быть ~0, std должно быть ~1")
        print(f"Средние значения: {df_standardized[num_features].mean().round(4).to_dict()}")
        print(f"Стандартные отклонения: {df_standardized[num_features].std().round(4).to_dict()}")
    else:
        print("⚠️ Нет числовых признаков для стандартизации")
    
    return df_standardized, scaler


def normalize_data(df):
    """Нормализация данных (Min-Max scaling)"""
    print("\n" + "="*60)
    print("НОРМАЛИЗАЦИЯ ДАННЫХ (Min-Max scaling)")
    print("="*60)
    
    df_normalized = df.copy()
    scaler = MinMaxScaler()
    
    num_features = [f for f in NUMERICAL_FEATURES if f in df.columns]
    
    if num_features:
        df_normalized[num_features] = scaler.fit_transform(df[num_features])
        
        print("✅ Нормализация выполнена")
        print("\nСтатистики ДО нормализации:")
        print(df[num_features].describe().round(2))
        
        print("\nСтатистики ПОСЛЕ нормализации:")
        print(df_normalized[num_features].describe().round(2))
        
        print("\nПроверка: значения должны быть в диапазоне [0, 1]")
        print(f"Минимальные значения: {df_normalized[num_features].min().round(4).to_dict()}")
        print(f"Максимальные значения: {df_normalized[num_features].max().round(4).to_dict()}")
    else:
        print("⚠️ Нет числовых признаков для нормализации")
    
    return df_normalized, scaler


def train_and_evaluate_catboost(df):
    """Обучение и оценка модели CatBoost"""
    print("Подготовка данных для обучения...")

    target = TARGET
    if target not in df.columns:
        print(f"❌ Целевой признак '{target}' не найден в данных")
        return None

    X = df.drop(columns=[target])
    y = df[target].astype(str)

    # Категориальные признаки для CatBoost
    cat_features = [col for col in X.columns if X[col].dtype == 'object']

    print(f"✅ Признаков: {X.shape[1]}, категориальных: {len(cat_features)}")
    print(f"✅ Размер целевого признака: {y.shape}")
    print(f"Распределение классов: {y.value_counts().to_dict()}")

    # Разделение на обучающую и тестовую выборки
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Обучение модели CatBoost...")

    # Создание и обучение модели
    model = CatBoostClassifier(
        iterations=300,
        depth=6,
        learning_rate=0.1,
        loss_function="MultiClass",
        verbose=50,  # Показывать прогресс каждые 50 итераций
        random_seed=42
    )

    model.fit(X_train, y_train, cat_features=cat_features)

    # Предсказания
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)

    # Бинаризация для ROC-AUC
    y_test_bin = label_binarize(y_test, classes=list(sorted(set(y_test))))

    try:
        roc_auc = roc_auc_score(y_test_bin, y_prob, average="macro", multi_class="ovr")
    except Exception as e:
        roc_auc = None
        print(f"⚠️ Не удалось рассчитать ROC-AUC: {e}")

    # Метрики
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)

    print("\n" + "="*50)
    print("РЕЗУЛЬТАТЫ ОБУЧЕНИЯ CATBOOST")
    print("="*50)
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-score:  {f1:.4f}")
    if roc_auc is not None:
        print(f"ROC-AUC:   {roc_auc:.4f}")

    print("\nConfusion Matrix:")
    print(cm)

    print("\nКлассы модели:")
    for i, class_name in enumerate(sorted(set(y_test))):
        print(f"  {class_name}: индекс {i}")

    # Важность признаков
    feature_importance = model.get_feature_importance()
    feature_names = X.columns

    print(f"\nТоп-10 важных признаков:")
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': feature_importance
    }).sort_values('importance', ascending=False)

    for idx, row in importance_df.head(10).iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")

    return {
        'model': model,
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'roc_auc': roc_auc,
        'confusion_matrix': cm,
        'feature_importance': importance_df
    }


def print_summary_statistics(df):
    """Вывод общей статистики по данным"""
    print("\n" + "="*60)
    print("ОБЩАЯ СТАТИСТИКА ПО ДАННЫМ")
    print("="*60)
    
    print(f"\nРазмер датасета: {df.shape[0]} строк × {df.shape[1]} столбцов")
    
    print("\n📊 Числовые признаки:")
    num_features = [f for f in NUMERICAL_FEATURES if f in df.columns]
    if num_features:
        print(df[num_features].describe().round(2))
    
    print("\n📋 Категориальные признаки:")
    cat_features = [f for f in CATEGORICAL_FEATURES if f in df.columns]
    for feature in cat_features:
        print(f"\n{feature}:")
        print(f"   Уникальных значений: {df[feature].nunique()}")
        print(f"   Топ-3: {df[feature].value_counts().head(3).to_dict()}")
    
    if TARGET in df.columns:
        print(f"\n🎯 Целевой признак ({TARGET}):")
        print(df[TARGET].value_counts())
        print(f"\nРаспределение (%):")
        print((df[TARGET].value_counts(normalize=True) * 100).round(2))


def main():
    """Основная функция предобработки"""
    print("="*60)
    print("РАСШИРЕННАЯ ПРЕДОБРАБОТКА ДАННЫХ")
    print("="*60)
    
    # 1. Загрузка данных
    df = load_data()
    
    # 2. Анализ пропусков
    analyze_missing_values(df)
    
    # 3. Общая статистика
    print_summary_statistics(df)
    
    # 4. Анализ выбросов
    outliers_info = analyze_outliers(df)
    
    # 5. Построение графиков выбросов
    plot_boxplots(df)
    
    # 6. Построение распределений
    plot_distributions(df)

    # 6.1. Тепловая карта корреляций
    plot_correlation_heatmap(df)

    # 6.2. Распределение целевого признака
    plot_target_distribution(df)

    # 7. Анализ категориальных признаков
    analyze_categorical_features(df)

    # Добавляем небольшую паузу между графиками
    plt.pause(1)
    
    # 8. Стандартизация
    df_standardized, scaler_std = standardize_data(df)

    # 9. Нормализация
    df_normalized, scaler_minmax = normalize_data(df)

    print("\n" + "="*60)
    print("ИТОГОВАЯ СВОДКА ПРЕДОБРАБОТКИ")
    print("="*60)
    print(f"✅ Исходных признаков: {len(df.columns)}")
    print(f"✅ Числовых признаков стандартизировано: {len(NUMERICAL_FEATURES)}")
    print(f"✅ Категориальных признаков: {len(CATEGORICAL_FEATURES)}")
    print(f"✅ Выбросов обнаружено: {sum(info['outliers_count'] for info in outliers_info.values())}")

    # 10. Обучение модели CatBoost (если доступен)
    if CATBOOST_AVAILABLE:
        print("\n" + "="*60)
        print("ОБУЧЕНИЕ МОДЕЛИ CATBOOST")
        print("="*60)

        model_results = train_and_evaluate_catboost(df)
    else:
        print("\n" + "="*60)
        print("ОБУЧЕНИЕ МОДЕЛИ ПРОПУЩЕНО")
        print("="*60)
        print("⚠️ CatBoost не установлен. Установите для обучения модели:")
        print("   pip install catboost")
        model_results = None

    print("\n" + "="*60)
    if CATBOOST_AVAILABLE:
        print("ПРЕДОБРАБОТКА И ОБУЧЕНИЕ ЗАВЕРШЕНЫ")
    else:
        print("ПРЕДОБРАБОТКА ЗАВЕРШЕНА")
    print("="*60)
    print("\n💡 Примечание: Графики отображаются в отдельных окнах.")
    print("   Закройте окна графиков для завершения работы скрипта.")

    return {
        'original': df,
        'standardized': df_standardized,
        'normalized': df_normalized,
        'outliers_info': outliers_info,
        'model_results': model_results
    }


if __name__ == "__main__":
    try:
        results = main()
        
        # Держим графики открытыми
        print("\n" + "="*60)
        print("Все графики построены. Закройте окна графиков для завершения.")
        print("\n" + "="*60)
        print("Все готово! Графики отображаются в отдельных окнах.")
        print("Закройте все окна графиков для завершения работы скрипта.")
        print("="*60)

        # Держим скрипт активным до закрытия графиков
        input("\nНажмите Enter после закрытия всех графиков...")
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
    except Exception as e:
        print(f"\n\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

