# Telegram Channel Autopilot Bot

Готовый Python-проект под твой канал **@tgbots_miniapps** и чат обсуждений **@tgtoolschat**.

Что уже настроено:
- автопостинг **2 раза в день**;
- разные темы: Telegram, AI, игры, мемы, гаджеты, визуальные посты, интерактив;
- модерация комментариев в привязанном чате;
- предупреждение за мат и оскорбления;
- сбор статистики по постам;
- приоритет тем, которые заходят лучше;
- готовность к загрузке на GitHub и запуску на Render/Railway/Docker.

## Что осталось сделать вручную
Полностью за тебя я не могу только две вещи:
1. перевыпустить токен у **@BotFather**;
2. выдать боту права админа в канале и в чате обсуждений.

Без этого ни один бот не сможет начать постить и модерировать сообщения.

## Быстрый старт
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заполни в `.env`:
```env
BOT_TOKEN=НОВЫЙ_ТОКЕН
OWNER_IDS=ТВОЙ_TELEGRAM_ID
```

Все остальное уже подставлено:
```env
CHANNEL_ID=@tgbots_miniapps
DISCUSSION_CHAT=@tgtoolschat
TIMEZONE=Europe/Moscow
POST_TIMES=10:00,19:00
```

Запуск:
```bash
python -m app.main
```

## Права бота
### В канале `@tgbots_miniapps`
Нужны права:
- публиковать сообщения;
- закреплять сообщения.

### В чате `@tgtoolschat`
Нужны права:
- удалять сообщения;
- блокировать пользователей по желанию;
- читать сообщения.

## Команды владельца
- `/post_now` — сразу выложить пост
- `/top_posts` — показать лучшие посты
- `/sync_stats` — обновить статистику вручную

## Деплой
### GitHub + Render
1. создай пустой репозиторий;
2. загрузи туда файлы;
3. на Render создай **Worker**;
4. добавь переменные из `.env`;
5. стартовая команда уже есть в `render.yaml`.

### Docker
```bash
docker build -t tg-autopilot .
docker run --env-file .env tg-autopilot
```

## Файлы
- `app/main.py` — запуск
- `app/data/sources.yaml` — темы и источники
- `app/handlers/moderation.py` — удаление токсичных комментариев
- `app/handlers/admin.py` — команды владельца
- `app/services/analytics.py` — аналитика
- `app/services/content_sources.py` — подбор контента
- `render.yaml`, `Dockerfile`, `Procfile` — деплой

## Важно
Токен, который был прислан в чате, нужно считать засвеченным. Не используй его дальше — перевыпусти новый.
