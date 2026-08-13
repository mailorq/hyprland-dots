# Контракт зависимостей

Этот документ разделяет зависимости runtime, развёртывания и разработки. Установщик проверяет только то, что способен проверить до запуска графической сессии; он не устанавливает пакеты и не меняет системные сервисы.

## Runtime

| Компонент | Минимальное условие | Использование |
|---|---|---|
| Hyprland | 0.55+, Lua entry point `hyprland.lua` | compositor, bindings, workspaces, session autostart |
| Hyprpaper | доступная команда `hyprpaper` | fallback-обои и IPC проверки |
| Waybar | сборка с `hyprland`, `pulseaudio`, `network`, `tray` | панель |
| Rofi | Wayland-совместимый build | launcher через `fata-rofi` |
| Kitty | доступная команда `kitty` | терминал и фоновые иллюстрации |
| Mako | доступная команда `mako` | уведомления |
| PulseAudio-compatible audio service | активен в пользовательской сессии | модуль `pulseaudio` Waybar |

Hyprland запускает Hyprpaper, Mako и Waybar на событии `hyprland.start`. Для каждого из них должен существовать ровно один владелец запуска в пользовательской сессии. Дополнительные user services для тех же процессов отключаются или не запускаются параллельно.

`xdg-desktop-portal-hyprland` и обычный XDG portal рекомендованы для полноценной интеграции приложений, screen sharing и file chooser, но этот набор конфигураций их не вызывает и не считает установленными зависимостями.

## Профили оборудования

| Профиль | Проверка до установки | Добавляемые Waybar modules |
|---|---|---|
| `desktop` | нет sysfs-проверки | нет аппаратных модулей |
| `laptop-battery` | `/sys/class/power_supply/BAT*` | `battery` |
| `laptop-backlight` | `/sys/class/backlight/*` | `backlight` |
| `laptop-battery-backlight` | обе проверки | `battery`, `backlight` |

Temperature, CPU, memory и power-profiles не входят в любой профиль. Профиль не выбирается автоматически: пользователь передаёт его в `scripts/fata-install --profile`.

## Зависимости установщика

`scripts/fata-install` написан для POSIX `sh` и использует только следующие системные утилиты:

| Утилита | Роль |
|---|---|
| `cat`, `chmod`, `cp`, `date`, `dirname`, `mkdir`, `mktemp`, `mv`, `pwd`, `rm` | контролируемое развёртывание, backup и cleanup собственного временного файла |
| `sha256sum` | проверка `assets/deployment.sha256` до dry-run, preflight и apply |

`rm` вызывается только для временного файла, созданного `mktemp`, или внутри интеграционного теста для временного каталога, созданного этим тестом. Установщик не вызывает рекурсивное удаление и не удаляет пользовательские target-каталоги.

`assets/deployment.sha256` имеет LF-окончания строк и закреплён в `.gitattributes`. Это важно для byte-oriented парсинга `sha256sum -c` независимо от платформы, с которой был подготовлен checkout.

## Зависимости разработки

| Компонент | Назначение |
|---|---|
| Python 3.10+ | generators и static validators |
| Pillow 12.x | проверка формата, размеров и SHA-256 images |
| POSIX `sh` | shell syntax и `tools/test_install_integration.sh` |

Установка среды разработки:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r tools/requirements-assets.txt
python3 tools/validate_release.py --integration
```

`validate_release.py --integration` не изменяет assets и запускает shell-тест в `mktemp`-каталоге. Для `build_art_assets.py` и `build_wallpapers.py` режим по умолчанию также не пишет файлы: потребуется явный `--rebuild-frozen-assets`, предназначенный только для отдельно одобренного пересмотра изображений.

## Известные непроверяемые условия

- Наличие исполняемого файла Waybar не доказывает, что его build содержит нужные модули или совместим с текущим Lua IPC Hyprland. Это проверяется запуском панели в сессии.
- Наличие `pulseaudio` module не доказывает, что audio service запущен и имеет default sink.
- Наличие `rofi` не доказывает корректность его Wayland backend; проверяется `rofi -rasi-validate` и запуском `fata-rofi` в Wayland-сессии.
- Установщик не управляет monitor connector names, раскладкой, acceleration profile и display scale. Эти параметры принадлежат `fata/local.lua`.
