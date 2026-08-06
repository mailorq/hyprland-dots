# Графические материалы и палитра

## Набор изображений

Проект включает 40 утверждённых материалов The House in Fata Morgana. Состав
задаётся SHA-256 allowlist в <code>tools/build_art_assets.py</code>, а итоговые
контрольные суммы и размеры публикуются в
<code>assets/art/fata-morgana/manifest.json</code>. Неотслеживаемый каталог
<code>pictures/</code> служит только входом для сборщика и не включается в
установку.

При подготовке мастер-арта сборщик корректирует EXIF-ориентацию, приводит
изображение к sRGB/RGB, удаляет служебные метаданные и ограничивает максимальную
сторону 2048 px. Кадрирование и увеличение запрещены. Любая замена исходника
должна быть явно добавлена в allowlist, иначе сборка завершается ошибкой.

## Обои

Из утверждённых мастеров выделены пять 16:9-кандидатов. <code>fm-016</code>
создаётся из нормализованного мастера. <code>fm-031</code>, <code>fm-035</code>,
<code>fm-038</code> и <code>fm-040</code> — сохранённые вручную QHD-экспорты,
которые проверяются без повторного кодирования. Полный контракт приведён в
<a href="wallpaper-contract.md">документации обоев</a>.

## Палитра

<code>theme/palette.json</code> — единственный источник цветовых токенов.
Генераторы создают <code>colors.css</code> для Waybar, <code>colors.rasi</code>
для Rofi, <code>colors.conf</code> для Kitty и <code>colors.lua</code> для
Hyprland.

| Токен | HEX | Назначение |
|---|---|---|
| <code>bg</code> | <code>#2C2D2E</code> | базовая поверхность |
| <code>surface</code> | <code>#3C3B3B</code> | панели и карточки |
| <code>surface_warm</code> | <code>#493B36</code> | тёплая глубина |
| <code>fg</code> | <code>#E9E1D7</code> | основной текст |
| <code>fg_dim</code> | <code>#92949A</code> | вторичный текст |
| <code>burgundy</code> | <code>#5F2F28</code> | активное состояние |
| <code>brass</code> | <code>#B39A6A</code> | фокус и акцент |
| <code>storm</code> | <code>#8E9BA8</code> | холодный акцент |

Контраст на <code>bg</code>: <code>fg</code> — 10.66:1, <code>fg_dim</code> —
4.55:1, <code>brass</code> — 5.09:1.
