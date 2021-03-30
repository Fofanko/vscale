# Микросервис для создания серверов в vscale

## Описание
Данный микросервис используя публичный API Vscale, может создавать и удалять группу серверов.


## Stack
- Python 3.8
- FastAPI 0.63.0
- Database: PostgreSQL  


## Установка
1. Перейти в папку проекта  
Скопировать файл .example.env в .env и установить необходимые значения для переменных окружения

2. Запустить сборку приложения с использованием docker-compose  
```console
vova@MacBook-Pro-Vladimir vscale % docker-compose build
```

4. Запустить приложение и инстанс бд
```console
vova@MacBook-Pro-Vladimir vscale % docker-compose up -d
```

3. Применить миграции   
Для того чтобы применить миграции необходимо войти в контейнер с приложением (app)
   в интерактивном режиме и выполнить следующие команды
```console
vova@MacBook-Pro-Vladimir vscale % docker exec -it vscale_app_1 bash
root@fc2abdddebd9:/code# alembic upgrade head
```


После выполнения этих действий приложение будет доступно по адресу, указанному в переменных окружения.

## Использование

По адресу http://<%host%>:<%port%>/docs находится авто генерируемый сваггер файл

### Просмотр созданных серверов
Patter: /v1/servers/  
Method: GET  
Возвращает список всех существующих на данный момент серверов

Пример запроса:
```console
curl -X 'GET' \
  'http://0.0.0.0:8000/v1/servers/' \
  -H 'accept: application/json'
```

### Создание новых серверов
Patter: /v1/servers/  
Method: POST  
Принимает список из конфигураций серверов и создает их в vscale. В случае если один из
серверов не создался, то все созданные сервера будут удалены

Пример запроса:
```console
curl -X 'POST' \
  'http://0.0.0.0:8000/v1/servers/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "make_from": "ubuntu_18.04_64_001_master",
    "rplan": "medium",
    "do_start": false,
    "name": "New-Test-1",
    "password": "secr",
    "location": "spb0"
  },
  {
    "make_from": "ubuntu_18.04_64_001_master",
    "rplan": "medium",
    "do_start": false,
    "name": "New-Test-2",
    "password": "secr",
    "location": "spb0"
  }
]'
```


### Удаление серверов
Patter: /v1/servers/  
Method: DELETE  
Удаляются все ранее созданные сервера

Пример запроса:
```console
curl -X 'DELETE' \
  'http://0.0.0.0:8000/v1/servers/' \
  -H 'accept: application/json'
```


### Массовое создание серверов единой конфигурации
Patter: /v1/servers/bulk  
Method: POST  
Создание множества серверов с одной и той же конфигурацией. Количество создаваемых 
серверов передается в query param и является обязательным

Пример запроса:
```console
curl -X 'POST' \
  'http://0.0.0.0:8000/v1/servers/bulk?count=3' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "make_from": "ubuntu_18.04_64_001_master",
    "rplan": "medium",
    "do_start": false,
    "name": "New-Test-1",
    "password": "secr",
    "location": "spb0"
}'
```
