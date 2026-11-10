# Brief: OWUI Auto Mode — исследование и улучшения под наш контекст
Date: 2026-11-09. Тип: tech (open-source код + docs + community).
Глубина: moderate (2 раунда, без S3-гейтов).
Цель: точно разобрать, как устроен «Авто режим» (Auto tool permissions, v0.13.x) в
Open WebUI: конфигурация, механика scoring API, где применяется, fallback-поведение,
логирование; собрать известные ограничения/баги; предложить ≥5 конкретных улучшений,
разделив «настраиваемое у нас» vs «PR upstream».
Success criteria:
 SC1 anatomy с file:line из кода v0.13.3 (не из README);
 SC2 конфиг-поверхность (env vars + admin settings поля);
 SC3 известные проблемы (GitHub issues / Reddit / HN), включая «люди не понимают фичу»;
 SC4 ≥5 улучшений, каждое: проблема → предложение → к нам (config) или upstream (PR).
Источники: tarball/клон open-webui v0.13.3 (primary!), docs.openwebui.com, GitHub
issues API, Reddit (PullPush/Arctic Shift), HN Algolia. 'latest/current' = 2026.
