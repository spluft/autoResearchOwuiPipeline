---
title: Разделение Auto Tool Permissions и Deep Research Skill
date: 2026-11-10
status: принято
related: [[deep-owui-automode-2026-11/report]]
---

# 04 — Почему Skill и decisions-shim архитектурно независимы

## Решение

В одном репозитории живут две несвязанные возможности Open WebUI:

1. **Auto Tool Permissions** (`shim/` + `docs/00–03, plan, report`) — решение
   «разрешить ли этот tool-вызов автоматически или спросить человека». Это
   безопасность/разрешения: точки применения — `requires_tool_approval` внутри
   `execute_tool_call`, движок `decisions`, fail-closed к человеку.
2. **Deep Research Skill** (`skills/deep-research/`) — методология «как модели
   вести исследование доступными инструментами». Это качество рассуждения: план,
   ledger, цитирования, гейты.

## Обоснование

- Решают разные проблемы на разных уровнях: разрешения фильтруют ЧТО инструмент
  может сделать; skill задаёт КАК модель использует инструменты. Никакой общей
  поверхности: skill — markdown-инструкции, shim — FastAPI-сервис.
- Независимая эволюция: skill работает и при выключенных Tool Permissions
  (`ENABLE_TOOL_PERMISSIONS=false`), и при engine `''`/`decisions`; shim нужен и
  без всякого research-skill (для terminal/файловых инструментов).
- Совместимость только через Open WebUI: обе функции общаются с OWUI каждая по
  своему контракту (`/decisions` у шима; builtin-инструменты `search_web`,
  `fetch_url`, `delegate_task`, KB-тулы у skill). Прямых связей нет и не будет.

## Ограничение на изменения

`shim/app.py`, `shim/test_app.py`, `shim/Dockerfile`, `shim/deployment.yaml` —
не трогать, пока техническая зависимость не продемонстрирована. Работа над skill
не потребовала ни одного изменения (подтверждено git-diff при добавлении skill,
2026-11-10: baseline 12/12 pytest зелёные до и после).

## Границы скоупа skill

Skill не изобретает инструменты: использует только верифицированные builtin-имена
v0.13.3; отсутствующие возможности — честная деградация (см.
`skills/deep-research/references/openwebui-integration.md`). Skill не меняет
конфигурацию OWUI (sub-agents и пр. — админская зона, только документирование).
