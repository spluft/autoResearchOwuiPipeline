---
title: План изменений Авто Режима OWUI (v0.13.3 → боевой Auto с локальным ревьюером)
date: 2026-11-09
status: план (реализация не начата)
related: [[deep-owui-automode-2026-11/report]] [[open-webui]] [[homelab-infra]]
---

# План: что меняем в Авто Режиме OWUI

Принцип-основа: Default-движок (самоаппрув той же модели) не используем никогда —
инjection-вектор задокументирован. Боевая конфигурация = `engine=decisions` +
LiteLLM-сайдкар + локальный/доверенный decision-скорер. Дефолт `gpt-6-luna`
@api.openai.com — не трогаем (утечка аргументов наружу).

## Этап 0 — регресс-чеклист approval-слоя (до включения)
- [ ] Тест-чат: approval в side-chat (чинился #33873 08.11, ровно наш билд).
- [ ] Temp-chat: инструмент не стартует без спроса (регресс #29249).
- [ ] После approve: вложения/system prompt на месте (#32028/#31501).
- [ ] Кнопки Allow/Deny работают (у нас TG/десктоп не проблема, но прогнать).
Критерий: все 4 зелёные, иначе включение откладываем (сырая state-машина = ложное чувство защиты).

## Этап 1 — скорер: 9router /v1/systemone (маршрут ЖИВОЙ, проверка 2026-11-09)
Проверено живьём:
- `POST :30613/v1/systemone` с моделью `oc/jev-1.13-free` → 200, `noul: 0.98` на
  «rm -rf» (бесплатный ярус OpenCode Zen отвечает; 429 был только на chat-пути).
- `nd/clef-flash` / `nd/frida-decisions` через systemone → 500: у кастомного
  ND-провайдера нет `systemoneConfig`, билдер URL из сохранённого baseUrl ломается
  (systemoneCore.js: PROVIDER_MEDIA[provider]?.systemoneConfig; без cfg.path
  base юзается как полный URL). Правка = строчка в реестре `{path:"/v1/decisions"}`
  или поле systemone-override для кастом-провайдеров → это честный PR upstream
  (в трекере уже висит #4738 в том же направлении).
- **ND-диалект == SystemOne-диалект** (`state` + questions-dict + `noul`,
  passthrough без трансляции — вербатим доков ND и нашего прогона). Значит тело
  запроса для ND и для 9router-systemone ОДНО И ТО ЖЕ, различается только путь.
План:
- [ ] Шим (~100 строк FastAPI): OWUI-диалект (`input`, questions-LIST, `predicate`,
      ответ `answers[{probability}]`) ↔ systemone (`state`, questions-DICT, `noul`).
      Targets: сегодня `model: oc/jev-1.13-free`; после PR upstream —
      `nd/clef-flash` (8192 ctx со схемой) — просто смена model string в конфиге
      OWUI. Ни один ключ наружу из OWUI не уходит вообще (ND-креды живут в 9router).
- [ ] Порог на 0.35; тест-сьют калибрует (rm -rf/force-push/echo).
- [ ] Таймаут шима <5 с; 429/5xx/битый JSON → HTTP-error → OWUI к человеку.
      429-риск jev-яруса = главный аргумент пилить PR быстрее: free-лимит = стена
      вопросов. План-B переходный: шим → api.neuraldeep.ru/v1/decisions напрямую
      с ND-ключом в секрете шима (пока PR не мёржнут).
- [ ] PR upstream: decolua/9router — systemoneConfig/override для ND + тесты
      (привязка к #4738). Метрика приёмки: `nd/clef-flash` через /v1/systemone.

## Этап 2 — включение Auto
- [ ] ENV/Admin: `ENABLE_TOOL_PERMISSIONS=true`, `ENABLE_TOOL_PERMISSIONS_AUTO=true`,
      `TOOL_PERMISSIONS_AUTO_ENGINE=decisions`,
      `TOOL_PERMISSIONS_AUTO_DECISIONS_API_BASE_URL=http://decisions-shim.llm-gateway.svc:8080`,
      `TOOL_PERMISSIONS_AUTO_DECISIONS_MODEL=clef-flash`,
      `TOOL_PERMISSIONS_AUTO_DECISIONS_THRESHOLD=0.35` (строже дефолтного 0.5 —
      инстанс семейный, Марина основной пользователь).
- [ ] `TOOL_PERMISSIONS_AUTO_PROMPT` — своя политика (EN, кратко): destructive FS/git
      force ops, внешняя публикация, деньги, креды/ключи, изменения доступа → required;
      чтение/поиск/запись в workspace-директории → free.
- [ ] `models.default_params.tool_approval_mode=auto` для боевых моделей;
      для «семейной» группы моделей — тот же auto (не ask: смысл фичи именно в Auto
      со строгим порогом). Помнить: это мягкий дефолт, пользователь может перебить.
- [ ] Ревизия: ни один канал (channels) не имеет прикрученных инструментов/terminal —
      там всегда full.
- [ ] Метрики приёмки: тест-сьют (rm -rf → спросил; echo/cat → не спросил;
      git push -f → спросил) + p95 добавленной латентности ≤ ~1 с (локальный) /
      ≤ 2.5 с (OR-jev) + fail-closed проверка (scale litellm=0 → всё спрашивает).

## Этап 3 — аудит до апстрима (костыль, неделя-две)
- [ ] Cron-скрипт: раз в сутки вытаскивать `permission_review` из JSON сообщений
      (webui.db/Postgres), сводка вероятностей/причин в TG-чат.
- [ ] Фиксация ложных approvals (целевое 0) — аргументация для PR B1.

## Этап 4 — PR upstream (отдельный трек, порядок по ценности)
1. B1 audit-log вердиктов + рендер `permission_review` в UI (ссылки #33238/#33735).
2. B3 параллельный ревью батча tool-вызовов (сейчас sequential, до 5с×N; снимает
   «over-blocking» — главную боль, на неё жалуется core dev).
3. B2 кэш вердиктов по fingerprint (TTL, инвалидация по смене policy).
4. B4 per-group floor-режим в `resolve_tool_approval_mode` (наша семейная асимметрия).
5. B5 per-group/per-model threshold.
6. B6 доделать #28279 по-настоящему (stream-hook для фильтров).
Перед каждым PR: проверить открытые PR по той же теме + contributor guide OWUI.

## Откат
Любой этап: `ENABLE_TOOL_PERMISSIONS_AUTO=false` → все сохранённые auto-чаты
деградируют в `ask`, никогда в `full` (подтверждено кодом resolve_tool_approval_mode).
Полный выключатель: `ENABLE_TOOL_PERMISSIONS=false` → прежнее поведение.

## Чего НЕ делаем
- Не трогаем gothrottler (шим — отдельный мелкий сервис, не ещё один маршрут монолита).
- Не включаем Default-движок.
- Не верим Portkey-диалекту (list-формат OWUI его не примет).
- Не ходим ни в OpenRouter, ни в иные внешние скореры — только 9router (политика сети).
