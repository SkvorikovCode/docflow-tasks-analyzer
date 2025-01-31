import os
import datetime
import logging
import pyodbc
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
logger = logging.getLogger(__name__)

# Загрузка директорий логов из .env
logs_dirs = [
    os.getenv('LOGS_DIR_2IJ'),
    os.getenv('LOGS_DIR_2BM'),
    os.getenv('LOGS_DIR_2LD'),
    os.getenv('LOGS_DIR_2BE'),
    os.getenv('LOGS_DIR_2BK')
]

# Загрузка имен колонок из .env
column_names = {
    "2IJ": [os.getenv('COLUMN_2IJ')],
    "2BM": [os.getenv('COLUMN_2BM')],
    "2LD": [os.getenv('COLUMN_2LD')],
    "2BE": [os.getenv('COLUMN_2BE')],
    "2BK": [os.getenv('COLUMN_2BK')]
}

def connect_to_sql():
    """
    Подключается к SQL Server Database.
    """
    logger.info("Подключаемся к SQL Server Database...")
    conn_str = (
        f'DRIVER={os.getenv("DB_DRIVER")};'
        f'SERVER={os.getenv("DB_SERVER")};'
        f'DATABASE={os.getenv("DB_NAME")};'
        f'UID={os.getenv("DB_USER")};'
        f'PWD={os.getenv("DB_PASSWORD")}'
    )
    try:
        conn = pyodbc.connect(conn_str)
        logger.info("Соединение с SQL Server Database установлено.")
        return conn
    except pyodbc.Error as ex:
        logger.error("Ошибка при подключении к SQL Server Database.", exc_info=True)
        return None

def write_to_sql(conn, value_counts_by_dir, date_time):
    """
    Записывает данные в SQL Server Database.
    """
    current_date = date_time.strftime('%Y-%m-%d %H:%M:%S')
    logger.info("Записываем данные в SQL Server Database.")
    try:
        cursor = conn.cursor()

        # Формируем список значений для INSERT-запроса
        values = [current_date]  
        for dir_name in value_counts_by_dir:
            for count_type in ['WARN']:
                values.append(str(value_counts_by_dir[dir_name][count_type]))

        # Формируем SQL-запрос с помощью f-строки и экранированием названий столбцов
        sql_query = f"INSERT INTO dbo.DocflowTasks (datetime, {', '.join([f'{name}' for col_names in column_names.values() for name in col_names])}) VALUES ({', '.join(['?'] * len(values))})"
        print("SQL-запрос:", sql_query)
        print("Значения:", values)

        cursor.execute(sql_query, values)
        conn.commit()

        logger.info("Данные успешно записаны в SQL Server Database.")

    except pyodbc.Error as ex:
        logger.error("Ошибка при записи данных в SQL Server Database.", exc_info=True)

def close_sql_connection(conn):
    """
    Закрывает соединение с SQL Server Database.
    """
    if conn:
        conn.close()
        logger.info("Соединение с SQL Server Database закрыто.")

# Подключение к SQL Server Database
conn = connect_to_sql()
if conn is None:
    exit(1)

# Получаем текущую дату и время
current_datetime = datetime.datetime.now()
date_str = current_datetime.strftime("%d.%m.%Y")
current_hour = current_datetime.hour
current_minute = current_datetime.minute

# Определяем файл для чтения
if current_minute >= 30:
    hour_to_read = current_hour - 1
else:
    hour_to_read = current_hour - 2

# Парсинг файлов из каждой директории
value_counts_by_dir = {}
for logs_dir in logs_dirs:
    log_file_name = f"DocflowTasks-{date_str} {hour_to_read:02d}-00.log"
    print(f'Обрабатываю файл: {log_file_name}\nВ директории: {logs_dir}')
    log_file_path = os.path.join(logs_dir, log_file_name)

    value_counts = {'TRACE': 0, 'ERROR': 0, 'INFO': 0, 'DEBUG': 0, '|Error|': 0, 'WARN': 0}

    if os.path.exists(log_file_path):
        with open(log_file_path, "r", encoding="utf-8") as f:
            for line in f:
                if "TRACE" in line:
                    value_counts['TRACE'] += 1
                elif "ERROR" in line:
                    value_counts['ERROR'] += 1
                elif "INFO" in line:
                    value_counts['INFO'] += 1
                elif "DEBUG" in line:
                    value_counts['DEBUG'] += 1
                elif "WARN" in line:
                    value_counts['WARN'] += 1
    else:
        logger.error(f"Файл '{log_file_path}' не найден.")
        # exit(1)  # Выход из программы только если ни одного файла не найдено, иначе продолжить парсинг

    # Извлечение имени директории
    dir_name = logs_dir.split("\\")[-2]  # Используем split("\")[-2] для извлечения имени директории

    # Добавление данных в словарь
    value_counts_by_dir[dir_name] = value_counts

# Запись данных в SQL Server Database
write_to_sql(conn, value_counts_by_dir, current_datetime)

# Закрытие соединения с SQL Server Database
close_sql_connection(conn)
