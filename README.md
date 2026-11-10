# autoResearchOwuiPipeline

Авто Режим Open WebUI (tool-permissions auto-approval, v0.13.x) — исследование,
план боевой конфигурации и `decisions-shim`: микросервис-переводчик диалектов
скореров решений.

## Что здесь

- `shim/` — **decisions-shim**: FastAPI-сервис (~100 строк). OWUI POST `/decisions`
  (OpenAI predicate-диалект: `input`, questions-LIST, `predicate`, ответ
  `answers[{probability}]`) → 9router `/v1/systemone` (SystemOne/ND-диалект:
  `state`, questions-DICT, `noul`). Fail-closed: любой сбой апстрима = HTTP 502,
  OWUI уходит к человеку; шим никогда не фабрикует низкую вероятность.
  - `app.py` — переводчик + аудит-лог каждого вердикта (JSON per line).
  - `test_app.py` — 12 тестов (калибровка rm -rf/force-push/echo, fail-closed, битый JSON).
  - `runserver.py` — локальный запуск для разработки.
  - `Dockerfile`, `deployment.yaml` — образ python:3.12-slim и деплой в ns `llm-gateway`
    (секрет `SHIM_UPSTREAM_KEY` создаётся out-of-band, в репозиторий не коммитится).
- `docs/` — исследование и план (`deep-owui-automode-2026-11`):
  - `00-brief.md` — постановка; `01-code-anatomy.md` — механика Auto Mode по коду v0.13.3 (file:line);
  - `02-community-issues.md` — известные баги/боли из GitHub/Reddit/HN;
  - `03-round2-decisions-endpoint.md` — разбор decisions-endpoint, ND vs SystemOne диалекты;
  - `plan.md` — план боевой конфигурации (Этапы 0–4, откат, чего не делаем);
  - `report.md` — итоговый отчёт исследования.

## Ключевые решения (детали — docs/plan.md)

- Default-движок (самоаппрув той же модели) не используется — injection-вектор.
  Бой = `engine=decisions` + локальный доверенный скорер через шим.
- Только 9router (политика сети); Plan-B — `api.neuraldeep.ru/v1/decisions` напрямую
  (`SHIM_UPSTREAM_URL` без правки кода).
- Порог `0.35` (строже дефолта 0.5 — семейный инстанс).
- Откат: `ENABLE_TOOL_PERMISSIONS_AUTO=false` → auto-чаты деградируют в `ask`, никогда в `full`.

## Запуск

```bash
# тесты
cd shim && python -m venv .venv && .venv/bin/pip install -r requirements.txt pytest
.venv/bin/pytest test_app.py -q

# локально
.venv/bin/python runserver.py            # :8080, env SHIM_UPSTREAM_URL/SHIM_MODEL

# в кластере (образ собирается локально x86_64, импорт через k3s ctr)
docker build -t decisions-shim:amd64-0.1.0 shim/
docker save decisions-shim:amd64-0.1.0 | ssh spluft@192.168.1.200 sudo k3s ctr -n k8s.io images import -
kubectl apply -f shim/deployment.yaml
```

ENV OWUI для включения Auto (см. docs/plan.md, Этап 2):
`ENABLE_TOOL_PERMISSIONS=true`, `ENABLE_TOOL_PERMISSIONS_AUTO=true`,
`TOOL_PERMISSIONS_AUTO_ENGINE=decisions`,
`TOOL_PERMISSIONS_AUTO_DECISIONS_API_BASE_URL=http://decisions-shim.llm-gateway.svc:8080`.

Статус: исследование завершено (2026-11-09), шим написан и протестирован,
в кластере ещё не развёрнут — развёртывание после регресс-чеклиста Этапа 0.
