# Aircraft tracker

#
## Ключевые архитектурные решения (SOLID)

- **S (Single Responsibility)**:  
  `NominatimAPI` — получение координат; `OpenSkyAPI` — получение данных о самолётах; `DBManager` — выполнение SQL-запросов; `DBInitializer` — создание таблиц; `DataService` — координация бизнес-логики.
- **O (Open/Closed)**:  
  Абстрактный `BaseAPIClient` позволяет подключать новые источники данных без модификации существующего кода.
- **L (Liskov Substitution)**:  
  `NominatimAPI` и `OpenSkyAPI` взаимозаменяемы как наследники `BaseAPIClient`.
- **I (Interface Segregation)**:  
  `DBManager` содержит только минимально необходимые методы без избыточной функциональности.
- **D (Dependency Inversion)**:  
  `DataService` получает зависимости через конструктор, избегая жёсткой привязки к реализациям.

## Схема базы данных

### Таблица `countries`
- `id` — первичный ключ;
- `name` — название страны (UNIQUE);
- `center_lat`, `center_lon` — координаты центра;
- `bbox_min_lat`, `bbox_max_lat`, `bbox_min_lon`, `bbox_max_lon` — границы bounding box.

### Таблица `aircraft`
- `id` — первичный ключ;
- `icao24` — идентификатор самолёта;
- `callsign` — позывной;
- `origin_country` — страна происхождения;
- `latitude`, `longitude` — текущие координаты;
- `altitude` — высота;
- `on_ground` — статус (на земле/в полёте);
- `velocity` — скорость;
- `heading` — курс;
- `vertical_rate` — вертикальная скорость;
- `country_id` — внешний ключ к `countries`.

## Основные методы `DBManager`

- `get_countries_and_aeroplanes_count()` — JOIN `countries` и `aircraft` с агрегацией `COUNT` и группировкой `GROUP BY`.
- `get_all_aeroplanes()` — выборка всех самолётов с присоединением данных о странах.
- `get_avg_speed()` — расчёт средней скорости (`AVG(velocity)`) с фильтрацией `IS NOT NULL`.
- `get_aeroplanes_with_higher_speed()` — выборка самолётов со скоростью выше средней (через подзапрос).
- `get_aeroplanes_with_keyword(keyword)` — поиск по подстроке в поле `callsign` (оператор `ILIKE %keyword%`).

## Тестирование и покрытие кода

- Покрытие тестами превышает 80%.
- Используются моки для HTTP-запросов и подключения к PostgreSQL.
- Тестируются все ключевые модули: модели, API-клиенты, менеджер БД, сервис.

Для генерации отчёта о покрытии:
```powershell
pytest --cov=src --cov-report=html

## Запуск проекта
### 1 Установка зависимостей: poetry install
### 2 Настройка config.ini под параметры вашей БД
### 3 Запуск: python main.py



## Структура проекта
```bash

aviation_tracker/
├── /src
│   ├── api/
│   │   ├── nominatim_api.py     — клиент Nominatim (координаты стран)
│   │   └── opensky_api.py       — клиент OpenSky (данные о самолётах)
│   ├── database/

│   │   ├── db_init.py           — создание таблиц (DDL)
│   │   └── db_manager.py        — класс DBManager (запросы к БД)
│   ├── models/
│   │   ├── country.py           — модель Country
│   │   └── aircraft.py          — модель Aircraft
│   ├── services/
│   │   └── data_service.py      — оркестрация: API → БД
│   └── utils/
│       └── config.py            — загрузка конфигурации из config.ini
├── tests/
│   ├── conftest.py              — общие фикстуры
│   ├── test_models.py           — тесты Country и Aircraft
│   ├── test_nominatim_api.py    — тесты NominatimAPI
│   ├── test_opensky_api.py      — тесты OpenSkyAPI
│   ├── test_db_manager.py       — тесты DBManager
│   ├── test_db_init.py          — тесты DBInitializer
│   ├── test_db_config.py        — тесты DatabaseConnection и load_config
│   └── test_data_service.py     — тесты DataService
├── main.py                      — точка входа
├── config.ini                   — управление подключением к PostgreSQL
├── config.ini.example           — пример конфигурации БД
├── requirements.txt             — зависимости
├── pytest.ini                   — конфигурация pytest с покрытием
├── .coveragerc                  — конфигурация coverage
├── .gitignore                   — исключения git
├── fix_constraints.py           — 
└── README.md                    — документация
aviation_tracker/ 
├── src/ 
│    ├── api/ 
│    │ ├── nominatim_api.py — клиент Nominatim (координаты стран) 
│    │ └── opensky_api.py — клиент OpenSky (данные о самолётах) 
│    ├── database/ 
│    │    ├── db_init.py — создание таблиц (DDL) 
│         └── db_manager.py — класс DBManager (запросы к БД) 
│    ├── models/ 
│    │    ├── country.py — модель Country 
│    │    └── aircraft.py — модель Aircraft 
│    ├── services/ 
│    │    └── data_service.py — оркестрация: API → БД 
│    └── utils/ 
│         └── config.py — загрузка конфигурации из config.ini 
├── tests/ 
│ ├── conftest.py — общие фикстуры 
│ ├── test_models.py — тесты Country и Aircraft 
│ ├── test_nominatim_api.py — тесты NominatimAPI 
│ ├── test_opensky_api.py — тесты OpenSkyAPI 
│ ├── test_db_manager.py — тесты DBManager 
│ ├── test_db_init.py — тесты DBInitializer 
│ ├── test_db_config.py — тесты DatabaseConnection и load_config 
│ └── test_data_service.py — тесты DataService 
├── main.py — точка входа 
├── config.ini — управление подключением к PostgreSQL 
├── config.ini.example — пример конфигурации БД 
├── requirements.txt — зависимости 
├── pytest.ini — конфигурация pytest с покрытием 
├── .coveragerc — конфигурация coverage 
├── .gitignore — исключения git 
├── fix_constraints.py — скрипт исправления ограничений БД 
└── git_commits.md