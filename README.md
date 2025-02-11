# Docflow Tasks Analyzer

Анализатор задач документооборота для системы XDE. Скрипт отслеживает и анализирует логи задач документооборота, собирая статистику по различным типам событий (WARN, ERROR, INFO и т.д.) и сохраняя результаты в SQL Server.

## Функциональность

- Мониторинг логов документооборота из нескольких директорий
- Подсчет различных типов событий (WARN, ERROR, INFO, DEBUG, TRACE)
- Автоматическое определение временного интервала для анализа
- Запись результатов в SQL Server Database
- Конфигурируемое логирование процесса

## Требования

- Python 3.8+
- SQL Server
- Доступ к сетевым директориям с логами XDE

## Зависимости

Основные зависимости:
- pyodbc==4.0.39
- python-dotenv==1.0.0

## Настройка

#Создайте файл `.env` на основе примера:
```ini
Database connection
DB_DRIVER={SQL Server}
DB_SERVER=your_server_name
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
Logging configuration
LOG_LEVEL=INFO
TASK_CHECK_INTERVAL=600
OUTPUT_DIR=./output
Logs directories
LOGS_DIR_2IJ=\\server-path\LogsXDE\IM\2IJ\your_path\DocflowTasks
...
COLUMN_2IJ=DocflowTasks_ERROR_2IJ
...
```

## Использование

```bash
python DocflowTasks.py
```

## Логика работы

1. Скрипт определяет временной интервал для анализа на основе текущего времени
2. Читает логи из указанных директорий
3. Подсчитывает количество различных типов событий
4. Записывает результаты в базу данных

## Структура SQL таблицы

Таблица `dbo.DocflowTasks`:
- datetime - время анализа
- DocflowTasks_ERROR_2IJ - количество ошибок для организации 2IJ
- DocflowTasks_ERROR_2BM - количество ошибок для организации 2BM
- и т.д.

## Обработка ошибок

- Логирование всех ошибок в консоль
- Пропуск отсутствующих файлов логов
- Обработка ошибок подключения к базе данных

## Поддержка

При возникновении проблем:
1. Проверьте доступность сетевых путей
2. Проверьте права доступа к базе данных
3. Убедитесь в корректности настроек в файле .env
4. Проверьте лог-файлы на наличие ошибок

## Лицензия

Внутренний проект компании. Все права защищены.
