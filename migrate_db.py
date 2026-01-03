"""
Скрипт для миграции БД: пересоздание таблицы с новой схемой
"""
from pathlib import Path
from src.data_processing.database import engine, Base, DB_PATH
from src.data_processing.models import PatientTop10
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
TOP10_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "diabetic_data_top10.csv"

def migrate_database():
    """
    Пересоздает БД с новой схемой (time_in_hospital вместо patient_nbr)
    """
    print("=== Миграция базы данных ===")
    
    # Проверяем наличие CSV файла
    if not TOP10_CSV_PATH.exists():
        print(f"❌ Ошибка: Файл {TOP10_CSV_PATH} не найден!")
        print("Убедитесь, что файл diabetic_data_top10.csv существует и содержит столбец time_in_hospital")
        return False
    
    # Проверяем структуру CSV
    print(f"\nПроверка структуры CSV файла...")
    df_check = pd.read_csv(TOP10_CSV_PATH, nrows=1)
    required_cols = [
        "number_inpatient", "number_diagnoses", "number_emergency",
        "number_outpatient", "time_in_hospital",
        "diag_1", "diag_2", "diag_3", "medical_specialty", "diabetesMed", "readmitted"
    ]
    
    missing_cols = set(required_cols) - set(df_check.columns)
    if missing_cols:
        print(f"❌ Ошибка: В CSV файле отсутствуют столбцы: {missing_cols}")
        return False
    
    if "patient_nbr" in df_check.columns:
        print("⚠️  Внимание: В CSV файле все еще есть столбец patient_nbr!")
        print("Убедитесь, что вы обновили файл diabetic_data_top10.csv")
        response = input("Продолжить миграцию? (y/n): ")
        if response.lower() != 'y':
            return False
    
    print("✅ Структура CSV файла корректна")
    
    # Удаляем старую таблицу
    print("\nУдаление старой таблицы...")
    try:
        Base.metadata.drop_all(bind=engine, tables=[PatientTop10.__table__])
        print("✅ Старая таблица удалена")
    except Exception as e:
        print(f"⚠️  Предупреждение при удалении таблицы: {e}")
    
    # Создаем новую таблицу
    print("\nСоздание новой таблицы...")
    Base.metadata.create_all(bind=engine, tables=[PatientTop10.__table__])
    print("✅ Новая таблица создана")
    
    # Загружаем данные из CSV
    print(f"\nЗагрузка данных из {TOP10_CSV_PATH}...")
    df = pd.read_csv(TOP10_CSV_PATH)
    print(f"Загружено {len(df)} записей из CSV")
    
    # Проверяем, что time_in_hospital есть в данных
    if "time_in_hospital" not in df.columns:
        print("❌ Ошибка: В CSV файле отсутствует столбец time_in_hospital!")
        print("Убедитесь, что вы обновили файл diabetic_data_top10.csv")
        return False
    
    # Импортируем SessionLocal
    from src.data_processing.database import SessionLocal
    
    # Загружаем данные в БД
    db = SessionLocal()
    try:
        records = []
        for idx, row in df.iterrows():
            try:
                record = PatientTop10(
                    number_inpatient=int(row['number_inpatient']) if pd.notna(row['number_inpatient']) else 0,
                    number_diagnoses=int(row['number_diagnoses']) if pd.notna(row['number_diagnoses']) else 0,
                    number_emergency=int(row['number_emergency']) if pd.notna(row['number_emergency']) else 0,
                    number_outpatient=int(row['number_outpatient']) if pd.notna(row['number_outpatient']) else 0,
                    time_in_hospital=int(row['time_in_hospital']) if pd.notna(row['time_in_hospital']) else 0,
                    diag_1=str(row['diag_1']) if pd.notna(row['diag_1']) else 'Unknown',
                    diag_2=str(row['diag_2']) if pd.notna(row['diag_2']) else 'Unknown',
                    diag_3=str(row['diag_3']) if pd.notna(row['diag_3']) else 'Unknown',
                    medical_specialty=str(row['medical_specialty']) if pd.notna(row['medical_specialty']) else 'Unknown',
                    diabetesMed=str(row['diabetesMed']) if pd.notna(row['diabetesMed']) else 'Unknown',
                    readmitted=str(row['readmitted']) if pd.notna(row['readmitted']) else 'NO'
                )
                records.append(record)
            except Exception as e:
                print(f"⚠️  Ошибка при обработке строки {idx}: {e}")
                continue
        
        print(f"\nДобавление {len(records)} записей в БД...")
        db.bulk_save_objects(records)
        db.commit()
        print(f"✅ Успешно добавлено {len(records)} записей")
        
        # Проверяем результат
        count = db.query(PatientTop10).count()
        print(f"\n✅ Миграция завершена успешно!")
        print(f"Всего записей в БД: {count}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при загрузке данных: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("\n🎉 База данных успешно мигрирована!")
        print("Теперь можно запускать API сервер.")
    else:
        print("\n❌ Миграция не удалась. Проверьте ошибки выше.")
        exit(1)

