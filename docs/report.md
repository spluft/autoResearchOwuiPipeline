---
title: Авто режим OWUI (Auto tool permissions) — анатомия v0.13.3 и план улучшений
date: 2026-11-09
depth: moderate (S2, 2 волны)
status: validated
method: анатомия исходников tarball v0.13.3 (file:line) + офиц. доки + GitHub issues + Reddit (Arctic Shift) + вендор-доки; round-2 закрыл /decisions-экосистему, #28279, per-user; ключевой факт верифицирован родителем напрямую (LiteLLM /v1/decisions)
---

# Авто Режим в Open WebUI: как устроен на самом деле и что с этим делать у нас

## Резюме

- «Авто режим» = третий режим разрешений инструментов (`full` / `ask` / `auto`), v0.13.1+ (2026-11-03), экспериментальный, по умолчанию выключен. Включается одной парой глобальных env-флагов; режим выбирается **пользователем per-chat** и запоминается в его server-side настройках.
- **Два движка ревью**: Default — **модель сама оценивает свои вызовы** (безколейно, но доки прямо предупреждают: контент в tool-результатах может направить решение = injection-вектор); Decisions — внешний scorer `POST {base}/decisions` (OpenAI Decisions API контракт), probability ≥ threshold (0.5) → человек. Всё падает закрытым: таймаут 5 с, ошибка, >64 KB → всегда спросить человека.
- Дефолт скоринга — `gpt-6-luna` на `api.openai.com`: включить «как есть» у нас = слать аргументы tool-вызовов наружу. Нельзя.
- Дыры, подтверждённые в коде: нет audit-лога вердиктов (только в JSON сообщений, UI не рендерит), нет кэша вердиктов (одинаковые вызовы ревьюятся каждый заново), в auto-режиме вызовы исполняются **последовательно** (до +5 с на каждый канал при decisions), нет per-user RBAC — семейная асимметрия «Коля auto / Марине построже» не выражается (только мягкий default, клиент всегда может переопределить).
- Экосистема `/decisions` в 2026 реальная: OpenAI нативно, OpenRouter хостит TypeSafe **Jev** (`~typesafe/jev-*`), гейтвеи LiteLLM / Bifrost / Portkey / TrueFoundry. **Верифицировано нами**: LiteLLM отдаёт `/v1/decisions` в OpenAI-диалекте со списком провайдеров вплоть до **vLLM** — то есть локальный ревьюер ставится LiteLLM-прокси без единой строчки кода.
- Community-боль: ревью-слой переблокирует («core dev сам ходит с approvals off — блокирует слишком много команд»), state-машина approval'ов была хрупкой (молчаливый обход #29249, вечные ожидания #33873/#29293, потеря контекста после approve #31501/#31986 — всё чинилось в 0.12–0.13.x), видимость ожидания (#33735) и audit (#33238) — открытые раны.
- Для нас Auto с decisions-движком = ровно тот средний слой, которого не хватало (между «спрашивай всегда» и «full»); план: LiteLLM + локальная decision-модель (другая семья, по нашему же принципу), регресс-чеклист перед включением, 5 PR upstream.

## 1. Анатомия по коду v0.13.3

**Конфиг** (`backend/open_webui/config.py:2262-2272` → ключи `chat.tool_permissions.*`): `ENABLE_TOOL_PERMISSIONS` (пара-включатель), `ENABLE_TOOL_PERMISSIONS_AUTO`, `TOOL_PERMISSIONS_AUTO_ENGINE` (`''`|`'decisions'`), `TOOL_PERMISSIONS_AUTO_PROMPT`, `TOOL_PERMISSIONS_AUTO_DECISIONS_{API_BASE_URL,API_KEY,MODEL,THRESHOLD}`. Дефолт модели — `gpt-6-luna` @ api.openai.com. Порог — поле 0..1, один на весь инстанс.

**Режимы** (`utils/tool_permissions.py:72-87`): channel-чаты принудительно `full` (auto там даже выбрать нельзя — HTTP 400); выключенный админом auto деградирует в `ask`, никогда в `full`.

**Default-движок** (`tool_permissions.py:53-61` + `utils/tool_calling.py:59-70`): в системный промпт инжектится `<tool_approval_policy>` + в каждую схему инструмента обязательный аргумент `__approval__.required`; исполнение без спроса только при строго `{"required": false}`, всё остальное (включая отсутствие) → approval. Нулевая стоимость, но судья = исполнитель; доки прямо: «content that steers the model, such as instructions in a tool result, can also steer its decision».

**Decisions-движок** (`tool_permissions.py:160-199`): `POST {base}/decisions`, `{model, input: evidence, questions:[{type:'predicate', name:'requires_confirmation', instructions: policy+prompt}]}` → `{answers:[{probability}]}`; `probability >= threshold` → человек. Evidence = текущее + последние 4 **user-role** сообщения + спека инструмента + аргументы + `{tool_type, terminal_id}` («Only user messages express authorization» — грамотная защита от injection через tool-результаты). Таймаут 5 с (`asyncio.timeout`), >64 KB evidence, битый порог, неизвестный движок, refusal — всё `return True` (к человеку).

**Гейт и скоуп**: единственная точка — `requires_tool_approval` внутри `execute_tool_call` (`utils/middleware.py:3206`) — накрывает function/MCP/builtin/**terminal** инструменты. Освобождены: `ask_user`, builtin `search_tools`, channel-чаты, pipes/valves (не tool-вызовы). Temp-чаты: молчание 120 с / закрытая вкладка = **авто-отказ**.

**Латентность/кэш**: вердиктов кэш нет; дедуп — только approved+fingerprint (sha256 по name/args/terminal_id) на конкретный объект вызова; в auto-ветке вызовы исполняются строго последовательно (`middleware.py:6000-6007`) → до 5 с ревью на каждый вызов в раунде.

**Audit**: вердикт (`engine/probability/threshold/reason`) живёт только в JSON сообщения; `log.*` в `tool_permissions.py` — ноль; `permission_review` фронтендом не рендерится вообще.

**RBAC** (`utils/payload.py:118`, `main.py:1201-1216`): режим — клиентский параметр без permission-gate; админ может **мягко** засеять дефолт через `models.default_params` (per-model/per-group по доступу к моделям), но параметры запроса мержатся последними — клиент перебивает всегда. Жёстких per-user ручек нет.

## 2. Экосистема /decisions и наш путь

Контракт — официальный OpenAI Decisions API (predicate→probability), поэтому дефолт `gpt-6-luna`. OWUI — только клиент, сервера: OpenAI нативно; OpenRouter — модели TypeSafe Jev (`~typesafe/jev-*`, «jev» из вопроса пользователя на Reddit; «JEVA» не существует — garbling); гейтвеи **LiteLLM**, Bifrost (8 провайдеров), Portkey, TrueFoundry. **Проверено родителем вживую (2026-11-09, docs.litellm.ai/docs/decisions)**: LiteLLM поднимает `/v1/decisions` в OpenAI-диалекте для ЛЮБОЙ decision-модели из `model_list`, провайдеры: OpenAI (`gpt-6-luna`), TypeSafe Jev, OpenRouter jev, **vLLM** (с v1.104.3) — т.е. локальная decision-модель на наших GPU отдаётся в OWUI-совместимом диалекте из коробки. Диалект-ловушка: Portkey документирует dict-форму `questions/answers` — парсер OWUI (`parse_decision_scores`, list-формат) её не примет → fail-closed (неопасно, но бесполезно). У «Decider 2B» Perplexity точный размер не подтверждён.

## 3. Что болит у людей (SC3)

- Непонимание фичи даже у профи: «The auto mode sounds great. But I did not understand it fully. Can the decision be made by a decision model like jev or Decider 2B?» → сам же нашёл ответ в доках: «Was not aware of that!» (r/OpenWebUI 1xqw605, 2026-11-08) — discoverability-провал.
- Переблок: core dev (u/ClassicMain) ходит с approvals off: «it blocks a few too many commands. Needs some improvement».
- Хрупкость approval-машинерии: #29249 (молчаливый обход: `search_chats` прочитал чаты без спроса), #33873 (side-chat висит навечно, closed 2026-11-08), #29293, #33403 (кнопки не клавиатурятся), #31501/#31986/#32028 (после approve терялись system prompt/вложения/источники).
- Открытые: #33735 (карточка ask_user невидимая — «easy to scroll past»), #33238 (audit log пропускает большинство model calls).
- #28279 (filter-hook «core ships the hook, deployments ship the policy») закрыт completed 2026-08-11, **но хука в v0.13.3 нет** — фильтры по-прежнему не видят tool-calls до исполнения; единственный программный policy-хук — сам /decisions-эндпоинт.
- HN: ноль релевантного (проверено). Широта Reddit-сэмпла ограничена rate-лимитам — «нет жалоб на false-approve» ≠ «их нет».

## 4. Улучшения (SC4): наша конфигурация vs PR upstream

### У нас, сегодня (без кода)
| # | Улучшение | Зачем/доказательство |
|---|---|---|
| A1 | Включать Auto **только** с `TOOL_PERMISSIONS_AUTO_ENGINE=decisions`; Default-движок не использовать | Default = самоаппрув модели, injection-вектор задокументирован (02-F2); дефолт скоринга вообще наружу, на OpenAI (01-F1) |
| A2 | Ревьюер: **LiteLLM-прокси** в k3s ns `owui` → `/v1/decisions`, backend: локальная decision-модель (Jev/Clef-class через vLLM) или OpenRouter `~typesafe/jev-*`; в ревью — другая семья моделей, чем исполнитель (наш принцип) | LiteLLM верифицирован живьём; dialect-нормализация бесплатна; gothrottler `/decisions` не имеет (проверено в main.go) — не extending gothrottler, а sidecar |
| A3 | Порог: глобальный 0.5 → поставить **ниже** (строже, ~0.3–0.4) — у нас инстанс семейный, Marina в нём основной пользователь terminal/subagents | порог один на инстанс (01-F1); per-group порога нет — см. B5 |
| A4 | Никаких инструментов/terminal в **channel-чатах** — там всегда `full`, Auto не выбрать | 01-F2 / 02-F4, verbatim docs |
| A5 | Перед включением — регресс-чеклист на нашем v0.13.3: approval в side-chat (#33873 чинился 08.11!), temp-chat обход (#29249), потеря вложений после approve (#32028) | баг-кластер F8 — слой молодой |
| A6 | Марина: выставить режим один раз (он persist в её user settings) + мягкий default `ask` на её модели через `models.default_params`; понимать, что переопределить она может — это комфорт, не защита | 03-F6/F7 verbatim кода |

### PR upstream (по убыванию пользы/наш вес)
| # | PR | Боль→решение |
|---|---|---|
| B1 | **Audit log вердиктов + UI-рендер `permission_review`** (engine/probability/threshold/reason) | вердикты сейчас невидимы и не логируются; резонирует с #33238/#33735; для семьи «почему меня спросили» критично |
| B2 | **Кэш вердиктов по fingerprint** (name+args+tool_id, TTL, инвалидация по смене policy) | одинаковые вызовы ревьюятся каждый заново, последовательно; на локальном GPU — токены и латентность, на платном API — деньги |
| B3 | **Параллельный ревью батча** (gather всех `requires_tool_approval` перед исполнением, как уже делает не-auto ветка с delegate_task) | до 5 с × N последовательно в раунде — прямой источник «over-blocking», на который жалуется core dev |
| B4 | **RBAC: per-group floor-режим** (`resolve_tool_approval_mode` + access_control: «user may not pick full/auto», админский минимум) | семейная асимметрия сегодня не выражается вовсе (01-F8, 03-F7) |
| B5 | **Per-model/per-group threshold** поверх global | продолжение A3 |
| B6 | **Доделать #28279 по-настоящему**: stream-event с собранными tool-calls в filter-цепочку (deny до исполнения) | закрыт completed, хука нет (03-F4/F5) — мы как раз носители запроса «deployments ship the policy» |

Метрика успеха после включения: доля автоспустившихся вызовов, число ложных approvals (=0 цель), p50/p95 добавленной латентности (бюджет ≤1 с при локальном ревьюере), «молчаливых» сессий без единого вопроса при реальных destructive-операциях (тест-сьют: rm -rf, git push -f, отправка писем-пайпом).

## Ограничения

- Широта Reddit-сигнала ограничена rate-лимитами архивов (PullPush 526, Arctic Shift 422) — клалились только anchor-треды; отсутствие массовых жалоб на false-approve — не доказательство их отсутствия.
- Вендор-доки (OpenAI guide, TrueFoundry, Bifrost частично) частично из search-сниппетов; полностью вычитаны и верифицированы родителем: LiteLLM decisions page, docs OWUI, tarball v0.13.3, GitHub API.
- Диалект-риск Portkey — инференс из доков, не прогонялся.
- Наличие локально-раскатываемых decision-моделей (Jev/Clef веса под vLLM) — направление, не факт: перед A2 нужен smoke-тест (взять Clef/Jev веса, поднять в vLLM, прогнать /v1/decisions через LiteLLM против curl-реплики OWUI-payload).
- `[LACK_OF_DATA]`: поддержка `/decisions` в new-api; внутренний rationale закрытия #28279 (комментарии не читаны); покрывают ли inlet-filter tools гейт (негативная grep-доказательная база).

## Источники

- https://docs.openwebui.com/features/extensibility/plugin/tools/ (Auto/Ask/full, config-таблица, exemption-правила; fetched 2026-11-09)
- https://github.com/open-webui/open-webui/releases/tag/v0.13.1 (Auto tool permissions shipped)
- https://github.com/open-webui/open-webui/blob/main/CHANGELOG.md («Administrators can now turn on Auto...», «Filters before approved tool calls»)
- https://github.com/open-webui/open-webui/issues/29249, /33873, /29293, /33403, /31315, /31501, /31502, /31986, /32028, /33735, /33238, /28279 (GitHub API, 2026-11-09)
- https://reddit.com/r/OpenWebUI/comments/1xqw605/ (2026-11-08, Arctic Shift)
- https://reddit.com/r/OpenWebUI/comments/1wo05i7/ (u/ClassicMain, ~2026-09-23, Arctic Shift)
- https://docs.litellm.ai/docs/decisions (fetched wholly, родитель 2026-11-09)
- https://developers.openai.com/api/docs/guides/decisions (сниппет)
- https://docs.getbifrost.ai/quickstart/gateway/decisions (fetched leaf)
- https://docs.portkey.ai/docs/product/ai-gateway/decisions-api (сниппет)
- https://www.kimi.com/code/docs/en/kimi-code-cli/changelog.html, https://docs.databricks.com/gcp/en/release-notes/product/ (косвенные: auto-mode как индустриальный паттерн)
- Локально: tarball v0.13.3 (file:line выше), /mnt/git/spluft/gothrottler/main.go (маршруты: /decisions нет)
- HN Algolia: 0 на-тему записей (проверено полным просмотром)

---
_Метод: S2 moderate, 2 волны (3 листa), верификация URL ниже; ключевой факт (LiteLLM /v1/decisions) поднят родителем независимо от листа._
_URL-верификация: 14 URL проверено, 0 dead (4 RESTRICTED 403 — оставлены как есть)._
