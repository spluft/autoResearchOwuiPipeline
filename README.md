# autoResearchOwuiPipeline

Две независимые возможности Open WebUI в одном репозитории:

1. **Авто Режим (Auto Tool Permissions)** — исследование + `decisions-shim`
   (микросервис-переводчик диалектов скореров решений) для auto-approval
   tool-вызовов. v0.13.x.
2. **Deep Research Skill** — production-скилл Open WebUI для дисциплинированного
   многоходового исследования (evidence ledger, fact-checking, contradiction
   analysis, цитирование только реально прочитанных страниц).

Они решают разные задачи и архитектурно независимы
([docs/04-skill-separation.md](docs/04-skill-separation.md)).

## Не путать эти четыре вещи

| | Что это | Где живёт | Включение |
|---|---|---|---|
| **Auto Tool Permissions** | решает, исполнять ли tool-вызов без человека (full/ask/auto, engines `''`/`decisions`) | этот репозиторий: `shim/` + env OWUI | `ENABLE_TOOL_PERMISSIONS` + `_AUTO` (+ shim как `/decisions`-сервер) |
| **Deep Research Skill** | markdown-инструкции: КАК модель исследует доступными инструментами | `skills/deep-research/` | Workspace → Skills → Import; `$deep-research` или attachment к модели |
| **Web Search OWUI (native)** | builtin-инструменты `search_web`/`fetch_url` — ЧЕМ модель ищет и читает | сам Open WebUI | `ENABLE_WEB_SEARCH`, `WEB_SEARCH_ENGINE`, `WEB_LOADER_ENGINE`, capabilities модели |
| **Sub-agents** | опциональная параллельная работа через `delegate_task` | сам Open WebUI | `ENABLE_SUBAGENTS` (+ лимиты); skill работает и без них (секвентильно) |

## skills/deep-research — состав

```
skills/deep-research/
  SKILL.md                      # компактный (< read limit 20k), стандартные секции OWUI
  references/
    research-methodology.md     # полная спецификация 10 фаз + query perspectives
    source-evaluation.md        # иерархия источников, критерии, правила confidence
    fact-checking.md            # Phase-9 чеклист (universal / software / scientific)
    citation-policy.md          # механика цитирования OWUI v0.13.3 + анти-паттерны
    openwebui-integration.md    # верифицированные тулзы/env/провайдеры (v0.13.3)
    research-completion-criteria.md  # гейты A–F, бюджет-политика
  templates/                    # research-plan / evidence-ledger / final-report
  examples/                     # technical / comparative / current-information (учебные)
```

Принципы: режимы quick/standard/deep с жёсткими бюджетами; snippet ≠ evidence
(цитировать можно только `fetch_url`-страницы — так устроены citations в Native
mode); ledger-строка на каждое утверждение; dedicated fact-check pass; гейты A–F
без имитации прохождения; отсутствующие инструменты — честная деградация, без
«я поискал» когда поиска не было.

**Проверено против:** Open WebUI **v0.13.3** (latest stable, 2026-11-08),
официальные доки docs.openwebui.com (Skills, Sub-agents, Agentic Search, Tools,
Env Configuration), верификация 2026-11-10.

### Импорт и активация

1. Архив: `cd skills && zip -r deep-research.skill deep-research/` (или Zip папки).
2. OWUI → Workspace → Skills → **Import** (`.skill`/`.zip`), либо «Import from URL»
   на папку репозитория (админ).
3. Активация: `$deep-research` в чате, либо +-меню → Skills, либо attach к модели
   (Workspace → Models → Skills). Нужны Native function calling + Builtin Tools +
   категория Skills у модели; без skill-тулов скилл инжектится целиком в каждый
   запрос (до 100k символов) — включите `ENABLE_SKILL_LAZY_LOADING` или включите
   builtin tools.
4. Capability-чеклист минимальной конфигурации —
   `skills/deep-research/references/openwebui-integration.md` (§ Minimum
   configuration): рабочий `WEB_SEARCH_ENGINE`, browser-подобный `USER_AGENT`,
   model capability Web Search, Default Features → Web Search, опционально
   `ENABLE_SUBAGENTS` + лимиты.

### Валидация и оценка

```bash
python3 tools/validate_skill.py            # структура/frontmatter/размеры — OK
```

`evaluation/scenarios.md` — 10 сценариев (trivia → deep multi-area, KB+web,
отключённый поиск, конфликты источников) с рубрикой 12×2 балла и журналом
EXECUTED/SIMULATED/REQUIRES-OWUI. Структурные проверки выполнены; живые прогоны
требуют настроенного OWUI и документируются честно — выдуманные «passed» запрещены.

## shim/ — decisions-shim (Auto Tool Permissions)

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
  - `04-skill-separation.md` — решение о независимости skill и shim;
  - `plan.md` — план боевой конфигурации (Этапы 0–4, откат, чего не делаем);
  - `report.md` — итоговый отчёт исследования.

### Ключевые решения шима (детали — docs/plan.md)

- Default-движок (самоаппрув той же модели) не используется — injection-вектор.
  Бой = `engine=decisions` + локальный доверенный скорер через шим.
- Только 9router (политика сети); Plan-B — `api.neuraldeep.ru/v1/decisions` напрямую
  (`SHIM_UPSTREAM_URL` без правки кода).
- Порог `0.35` (строже дефолта 0.5 — семейный инстанс).
- Откат: `ENABLE_TOOL_PERMISSIONS_AUTO=false` → auto-чаты деградируют в `ask`, никогда в `full`.

### Запуск shim

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

Статус: исследование завершено (2026-11-09), шим написан и протестирован (12/12,
2026-11-10), в кластере ещё не развёрнут — развёртывание после регресс-чеклиста
Этапа 0. Deep Research Skill: реализован и структурно валидирован (2026-11-10),
живые прогоны сценариев — после импорта в боевой OWUI (см. evaluation/scenarios.md).
