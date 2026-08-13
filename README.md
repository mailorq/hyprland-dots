# Fata Morgana Hyprland Dots

Версия: 1.0.0

Набор конфигураций Hyprland для рабочего стола в эстетике *The House in Fata Morgana*. Проект поставляет только пользовательские конфигурации, утверждённые иллюстрации, сценарий развёртывания и проверочные инструменты. Он не устанавливает системные пакеты, не меняет загрузчик, display manager, драйверы или настройки сети.

## Состав

| Компонент | Назначение |
|---|---|
| Hyprland 0.55+ | Lua-конфигурация, десять persistent workspaces, базовые привязки и автозапуск сессии |
| Hyprpaper | Статичный fallback-обой из пяти утверждённых QHD-экспортов |
| Waybar | Сегментированная панель для desktop и трёх явных laptop-профилей |
| Rofi | Wayland launcher с одним выбранным фоном из каталога утверждённых иллюстраций |
| Kitty | Терминал с доступом ко всем утверждённым иллюстрациям как к фонам |
| Mako | Уведомления без дополнительных shell-скриптов |

Desktop-профиль не содержит battery, backlight, temperature, CPU, memory, power-profiles или аналогичных виджетов. Ноутбучные модули включаются только явным выбором профиля.

## Визуальная геометрия

Значения заданы в логических пикселях. Они рассчитаны для основного QHD-дисплея 27″ и остаются компактными на FHD-дисплее 23″.

| Поверхность | Значение |
|---|---:|
| Внутренний / внешний gap Hyprland | 8 / 12 px |
| Граница / скругление окна | 2 / 8 px |
| Waybar: высота / верхний отступ / боковой отступ | 40 / 8 / 12 px |
| Ячейка Waybar | 32 px полезной высоты, 6 px межъячеечный интервал |
| Rofi | 42% ширины на FHD, 38% на ширине от 2200 px; 7 / 9 строк |
| Kitty | 12 pt, внутренний отступ 10 px |
| Mako | 380 × 160 px, отступ 12 px, до 3 уведомлений |

Палитра определяется в [theme/palette.json](C:/Users/mailor/PycharmProjects/hyprland-dots/theme/palette.json) и генерируется в нативные форматы компонентов. Мастера `assets/art/` используются Kitty и Rofi; пять файлов `assets/wallpapers/` используются Hyprpaper. Исходные материалы в `pictures/` не входят в развёртывание и не изменяются инструментами по умолчанию.

## Установка

Перед началом установите компоненты рабочей среды способом, принятым в вашей системе. Требуются `Hyprland` версии 0.55 или новее, `hyprpaper`, `waybar`, `rofi` с поддержкой Wayland, `kitty` и `mako`.

Проверьте окружение:

```sh
for command in Hyprland hyprpaper waybar rofi kitty mako sha256sum; do
    command -v "$command" || exit 1
done
```

Получите исходники и выполните три этапа установки:

```sh
git clone https://github.com/mailorq/hyprland-dots.git
cd hyprland-dots

# Проверяет хеши источников и печатает только план копирования.
sh scripts/fata-install --profile desktop

# Проверяет runtime-зависимости и выбранный профиль оборудования.
sh scripts/fata-install --profile desktop --check

# Копирует только файлы, которыми управляет проект.
sh scripts/fata-install --profile desktop --apply
```

Для повторного развёртывания изменённых управляемых файлов требуется явное подтверждение:

```sh
sh scripts/fata-install --profile desktop --apply --force
```

Перед заменой `--force` сохраняет прежнюю версию каждого существующего управляемого файла в `~/.local/state/fata-morgana/backups/<timestamp-pid>/`. Вернуть сохранённые файлы можно тем же `HOME` и `XDG_CONFIG_HOME`:

```sh
sh scripts/fata-install --restore "$HOME/.local/state/fata-morgana/backups/<timestamp-pid>"
```

Подробный порядок, модель резервного копирования и диагностика приведены в [docs/installing.md](C:/Users/mailor/PycharmProjects/hyprland-dots/docs/installing.md).

### Профили Waybar

| Профиль | Дополнительные модули |
|---|---|
| `desktop` | отсутствуют |
| `laptop-battery` | battery |
| `laptop-backlight` | backlight |
| `laptop-battery-backlight` | battery и backlight |

Для ноутбучных профилей установщик проверяет `/sys/class/power_supply/BAT*` и `/sys/class/backlight/*`. Temperature, CPU, memory и power profile не добавляются ни в один профиль.

## После установки

Сначала выберите сессию Hyprland обычным для вашей системы способом. При запуске Hyprland стартуют Hyprpaper, Mako и Waybar. Не запускайте параллельно отдельные user services для этих же трёх компонентов.

Уточните конфигурацию двух мониторов и устройств ввода в локальном файле, который Git не отслеживает:

```sh
fm_config_home=${XDG_CONFIG_HOME:-"$HOME/.config"}
cp "$fm_config_home/hypr/fata/local.lua.example" "$fm_config_home/hypr/fata/local.lua"
hyprctl monitors all
hyprctl devices
```

После редактирования выполните `hyprctl reload`. Основная чувствительность оставлена на `0.0`: DPI 1200 — аппаратственный параметр мыши; `flat` или `adaptive` выбирается локально после проверки устройства.

Базовые привязки расположены в [config/hypr/fata/bindings.lua](C:/Users/mailor/PycharmProjects/hyprland-dots/config/hypr/fata/bindings.lua):

| Привязка | Действие |
|---|---|
| `Super + Q` | Kitty |
| `Super + Tab` | последнее активное окно |
| `Super + F` | Rofi |
| `Super + Shift + C` | закрыть активное окно |
| `Super + Space` | floating для активного окна |
| `Super + M` | fullscreen |
| `Super + 1…0` | workspace 1…10 на текущем мониторе |
| `Super + Shift + 1…0` | переместить окно в workspace 1…10 |

## Проверка релиза

Для разработки требуется Python 3.10+ и Pillow из [tools/requirements-assets.txt](C:/Users/mailor/PycharmProjects/hyprland-dots/tools/requirements-assets.txt). Проверка не изменяет изображения:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r tools/requirements-assets.txt
python3 tools/validate_release.py --integration
```

`validate_release.py --integration` проверяет хеши art и wallpaper, palette adapters, Lua/Rasi/CSS/JSONC-контракты, installer, deployment manifest и изолированный shell-сценарий установки. Интеграционный тест работает только с временным `mktemp`-каталогом и подставными бинарниками зависимостей.

Непосредственно в работающей Wayland-сессии дополнительно проверьте парсеры и IPC:

```sh
fm_config_home=${XDG_CONFIG_HOME:-"$HOME/.config"}
hyprctl reload
hyprctl hyprpaper listactive
rofi -rasi-validate "$fm_config_home/rofi/config.rasi"
kitty --config "$fm_config_home/kitty/kitty.conf" --debug-config
```

Waybar и Mako запускайте диагностически только если текущая сессия ещё не владеет их экземплярами:

```sh
mako --config "$fm_config_home/mako/config"
waybar --config "$fm_config_home/waybar/config.jsonc" --style "$fm_config_home/waybar/style.css"
```

## Ограничения и отказы

- `assets/deployment.sha256` обнаруживает повреждённый или локально изменённый checkout до записи в home. Это контроль целостности, а не криптографическая подпись релиза; доверяйте проверенному Git remote и подписанным тегам, когда они опубликованы.
- Установка публикует каждый файл атомарно, но набор файлов не является файловой транзакцией. При сбое питания первая установка может остаться частично развёрнутой; при `--force` прежние существующие файлы уже находятся в backup-каталоге.
- `--restore` восстанавливает только файлы, которые были заменены и сохранены `--force`; он намеренно не удаляет новые файлы после прерванной первой установки.
- Проверка не может заранее доказать, что конкретная сборка Waybar содержит совместимый с Lua-версией Hyprland IPC backend или что PulseAudio-совместимый сервер звука запущен. Это проверяется запуском панели в целевой Wayland-сессии.
- Hyprpaper по официальному контракту читает `~/.config/hypr/hyprpaper.conf`; этот путь не следует значению `XDG_CONFIG_HOME`.

## Документация

- [Развёртывание и восстановление](C:/Users/mailor/PycharmProjects/hyprland-dots/docs/installing.md)
- [Зависимости и профили](C:/Users/mailor/PycharmProjects/hyprland-dots/docs/dependency-contract.md)
- [Архитектурные решения](C:/Users/mailor/PycharmProjects/hyprland-dots/docs/architecture-decisions.md)
- [Проверка релиза](C:/Users/mailor/PycharmProjects/hyprland-dots/docs/release-verification.md)
- [Контракт Hyprland](C:/Users/mailor/PycharmProjects/hyprland-dots/docs/hyprland-contract.md)
- [Контракт Waybar](C:/Users/mailor/PycharmProjects/hyprland-dots/docs/waybar-contract.md)
- [Контракт Kitty, Rofi и Mako](C:/Users/mailor/PycharmProjects/hyprland-dots/docs/interaction-surfaces-contract.md)
- [Контракт обоев и Hyprpaper](C:/Users/mailor/PycharmProjects/hyprland-dots/docs/wallpaper-contract.md)
- [Контракт палитры и иллюстраций](C:/Users/mailor/PycharmProjects/hyprland-dots/docs/art-palette-contract.md)

## Первичные источники

- [Hyprland Lua configuration](https://wiki.hypr.land/Configuring/Start/)
- [Hyprland binds](https://wiki.hypr.land/Configuring/Basics/Binds/)
- [Hyprland workspace rules](https://wiki.hypr.land/Configuring/Basics/Workspace-Rules/)
- [Hyprpaper](https://wiki.hypr.land/Hypr-Ecosystem/hyprpaper/)
- [Waybar Hyprland workspaces](https://github.com/Alexays/Waybar/blob/master/man/waybar-hyprland-workspaces.5.scd)
- [Rofi Rasi](https://davatorium.github.io/rofi/current/rofi-theme.5/)
- [Kitty configuration](https://sw.kovidgoyal.net/kitty/conf/)
- [Mako manual](https://www.mankier.com/5/mako)
