# Web parser для Avito
Получает информацию о товарах с авито
* Заголовок
* Цена
* Время размещения
* Район
* Номер телефона
## Установка:
- Скачать ZIP проекта
- Распаковать
```
cd /путь до распакованной папки
```

### Если на локальной машине установлен mysql:
#### В консоли:
```
pip install virtualenv (Если не получилось: sudo pip install virtualenv)
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python database_creator.py
```
#### Для запуска веб приложения:
```
python parser-flask.py
```
##### Готово, переходим по ссылке http://127.0.0.1:5000/
#### Для авторизации внутри приложения использовать логин "admin" пароль "root"