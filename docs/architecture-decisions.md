# Архитектурные решения

## Конфигурационная модель

Hyprland 0.55+ использует Lua entry point `config/hypr/hyprland.lua`. Конфигурация разделена по областям ответственности:

| Модуль | Владелец |
|---|---|
| `fata/appearance.lua` | gaps, borders, rounding, decoration и анимации |
| `fata/input.lua` | нейтральная pointer sensitivity и cursor size |
| `fata/monitors.lua` | переносимый fallback `preferred/auto` |
| `fata/workspaces.lua` | десять persistent numeric workspaces |
| `fata/bindings.lua` | базовые Super-привязки |
| `fata/autostart.lua` | Hyprpaper, Mako и Waybar на `hyprland.start` |
| `fata/colors.lua` | сгенерированная палитра |
| `fata/local.lua` | неотслеживаемые параметры конкретного оборудования |

Каждый обязательный Lua-модуль подключается через `require()`. Отсутствие `fata/local.lua` — единственное штатно подавляемое исключение. Любая другая ошибка local-модуля остаётся видимой, чтобы не скрывать неисправную конфигурацию оборудования.

## Границы переносимости

Базовая конфигурация не содержит названий видеовыходов, частоты, масштаба, раскладки или модели мыши. Эти данные нельзя достоверно вывести из размера монитора или аппаратного DPI. После первого запуска пользователь копирует `local.lua.example` в `local.lua` и вносит фактические значения из `hyprctl monitors all` и `hyprctl devices`.

Характеристики 27″ QHD и 23″ FHD влияют только на выбранную плотность интерфейса: компактные 8/12 px gaps, 2 px border, 8 px rounding, 40 px Waybar и 12 pt Kitty. Они не кодируются как аппаратные правила.

## UI-слои

Waybar использует строгий JSON в файлах с расширением `.jsonc`: это упрощает машинную проверку без comment stripper. CSS использует только селекторы и свойства, ожидаемые GTK CSS для Waybar; не применяются `-gtk-` хаки, CSS variables, `box-shadow`, transitions или keyframes.

Rofi использует Rasi, а не GTK CSS. Фон передаётся через переменную `FM_ROFI_ART`, которую формирует `fata-rofi` после allowlist-проверки имени файла. Kitty использует документированную обработку JPEG glob для одобренного каталога и не включает remote control. Mako получает самодостаточный конфиг без non-portable include path и без `exec` hooks.

## Контент и генераторы

`theme/palette.json` — единственный источник палитры. `tools/build_theme_colors.py` синхронизирует адаптеры Hyprland, Waybar, Rofi, Kitty и Mako.

`assets/art/fata-morgana/manifest.json` задаёт утверждённые masters, их хеши и роли. `tools/build_art_selectors.py` генерирует Kitty/Rofi adapters и shell allowlist. Имена файлов, ID и роли валидируются до генерации, поэтому JSON не может внедрить shell syntax в `fata-rofi`.

`assets/wallpapers/fata-morgana/manifest.json` задаёт пять утверждённых QHD-экспортов. Art и wallpaper builders по умолчанию выполняют только проверку; для записи требуется явный `--rebuild-frozen-assets`. Это предотвращает случайную перекодировку, изменение размера или замену зафиксированных изображений.

## Целостность и поставка

`tools/build_release_manifest.py` формирует `assets/deployment.sha256` для каждого файла, который `fata-install` реально разворачивает. Перед dry-run, `--check` и `--apply` установщик запускает `sha256sum -c`. Манифест предотвращает использование неполного или случайно изменённого checkout.

Манифест не является подписью: он хранится в том же checkout, что и код. Доверие к происхождению обеспечивается проверенным Git remote, code review и, для опубликованного релиза, подписанным тегом.

При `--apply` installer выполняет conflict pass до первой записи. При `--force` исходные target-файлы сохраняются под `~/.local/state/fata-morgana/backups/`. Каждая новая версия создаётся `mktemp`, получает ожидаемый режим и публикуется `mv`. Главный `hyprland.lua` публикуется последним: все требуемые модули к этому времени уже находятся на месте.

Набор файлов не является атомарной транзакцией: остановка процесса после нескольких успешных publish-операций способна оставить смешанную версию конфигурации. Backup нужен именно для восстановления существующих файлов после `--force`; первая чистая установка не удаляет ничего и не нуждается в автоматическом rollback.

## Проверка

`tools/validate_release.py` объединяет неизменяющие проверки manifests, asset hash/dimensions, Lua structure, generated adapters, JSON/CSS/Rasi contracts и installer safety. `tools/test_install_integration.sh` проверяет first install, конфликт, forced update и restore в изолированном `mktemp`-home с подставными бинарниками. Нативные парсеры Hyprland, Waybar, Rofi, Kitty и Mako дополнительно проверяются внутри реальной Wayland-сессии.
