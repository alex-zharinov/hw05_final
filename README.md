# Yatube

[![Django-app workflow](https://github.com/alex-zharinov/hw05_final/actions/workflows/main.yml/badge.svg)](https://github.com/alex-zharinov/hw05_final/actions/workflows/main.yml)

## Cоциальная сеть «Блогикум» с авторизацией и комментариями

> Cоциальная сеть даёт пользователям возможность создать учетную запись, публиковать записи, подписываться на любимых авторов и отмечать понравившиеся записи.

## Технологии проекта

- Python — высокоуровневый язык программирования
- HTML — язык гипертекстовой разметки документов для просмотра веб-страниц
- CSS — язык декорирования и описания внешнего вида документа
- Django — фреймворк, который позволяет быстро создавать веб-сайты
- Bootstrap — CSS-фреймворк, предназначенный для вёрстки интерфейсов сайтов
- Unittest — фреймворк модульного тестирования
- Pythonanywhere — облачная платформа, предназначенная для запуска приложений Python

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/alex-zharinov/hw05_final.git
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Создать .env. Пример:

```
#  ./.env

SECRET_KEY=#c+qu7%(2$5&p6%mv1b)z@x0cwh3x%0k_4&)kj$=s_9%8gm^!6
```

Создать БД:

```
python3 yatube/manage.py migrate
```

Запустить проект:

```
python3 yatube/manage.py runserver --insecure
```

### Ваш проект будет доступен по ссылке:

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Автор
[Жаринов Алексей](https://github.com/alex-zharinov)