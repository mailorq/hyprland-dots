# Развёртывание и восстановление

`scripts/fata-install` разворачивает только перечисленные в нём пользовательские файлы. Он не вызывает пакетный менеджер, не использует `sudo`, не удаляет каталоги и не пытается определить тип устройства эвристически.

## Предварительные условия

Установите компоненты Wayland-сессии стандартным для вашей системы способом. Для всех профилей необходимы:

```sh
for command in Hyprland hyprpaper waybar rofi kitty btop mako sha256sum; do
    command -v "$command" || exit 1
done
```

Требуется Hyprland 0.55 или новее с Lua-конфигурацией. Waybar должен быть собран с модулями `hyprland/workspaces`, `hyprland/window`, `pulseaudio`, `network` и `tray`; `pulseaudio` работает с PulseAudio-совместимым сервером. Rofi должен работать в Wayland-сеансе.

Проверка версии в уже запущенной сессии:

```sh
hyprctl version
```

Для ноутбучных профилей подтвердите наличие соответствующих sysfs-устройств:

```sh
ls /sys/class/power_supply/BAT* 2>/dev/null
ls /sys/class/backlight/* 2>/dev/null
```

## Выбор профиля

| Профиль | Содержимое панели |
|---|---|
| `desktop` | меню, десять workspaces, заголовок окна, часы, звук, сеть, tray |
| `laptop-battery` | desktop + battery |
| `laptop-backlight` | desktop + backlight |
| `laptop-battery-backlight` | desktop + battery + backlight |

Ни один профиль не добавляет temperature, CPU, memory или power-profile module. Установщик прекращает работу до записи, если выбранный ноутбучный профиль не находит необходимое sysfs-устройство.

## Обычное развёртывание

Все команды запускаются из корня проверенного checkout:

```sh
# Верифицировать checksum-манифест и увидеть список будущих файлов.
sh scripts/fata-install --profile desktop

# Верифицировать checksum-манифест, программы и аппаратные условия профиля.
sh scripts/fata-install --profile desktop --check

# Развернуть конфигурацию, если ни один управляемый target ещё не существует.
sh scripts/fata-install --profile desktop --apply
```

По умолчанию `--apply` отказывается заменять уже существующий управляемый файл. Это включает и файлы, созданные предыдущим запуском проекта, и несвязанные пользовательские файлы с тем же путём. Символьная ссылка в любом сегменте целевого пути также отклоняется.

## Обновление

Сначала изучите изменения и повторите dry-run. Затем выполните явную замену:

```sh
git pull --ff-only
sh scripts/fata-install --profile desktop
sh scripts/fata-install --profile desktop --apply --force
```

При `--force` каждый существующий regular file до замены копируется в:

```text
~/.local/state/fata-morgana/backups/<UTC-timestamp-pid>/
```

Внутри backup-каталога воспроизводится логическая структура target-файлов, а `targets.tsv` содержит сопоставление исходного target и backup-пути. Публикация каждой новой версии происходит через временный файл и `mv`, поэтому отдельный файл не бывает виден в усечённом виде.

## Восстановление

`--restore` не принимает произвольные пути: каталог должен находиться внутри `~/.local/state/fata-morgana/backups/` текущего `HOME`, не быть символьной ссылкой и содержать `targets.tsv`.

```sh
backup_dir="$HOME/.local/state/fata-morgana/backups/<UTC-timestamp-pid>"
sh scripts/fata-install --restore "$backup_dir"
```

Восстановление использует текущие `HOME` и `XDG_CONFIG_HOME`; они должны совпадать со значениями во время обновления. Возвращаются только файлы, которые были заменены `--force` и потому существуют в backup-каталоге. Сценарий намеренно не удаляет файлы, созданные первой или прерванной установкой.

## Целевые пути

| Источник checkout | Target |
|---|---|
| `config/hypr` | `$XDG_CONFIG_HOME/hypr` |
| `config/hypr/hyprpaper.conf` | `~/.config/hypr/hyprpaper.conf` |
| `config/kitty`, `config/rofi`, `config/mako`, `config/waybar` | соответствующие каталоги `$XDG_CONFIG_HOME` |
| `scripts/fata-rofi` | `~/.local/bin/fata-rofi` |
| `assets/art/fata-morgana/*.jpg` | `~/.local/share/fata-morgana/art/` |
| `assets/wallpapers/fata-morgana/*.jpg` | `~/.local/share/fata-morgana/wallpapers/` |

Все текстовые конфигурации получают режим `0644`; `fata-rofi` — `0755`; изображения — `0644`. `fata/local.lua` не находится в списке target-файлов и не перезаписывается.

Hyprpaper по документированному контракту читает `~/.config/hypr/hyprpaper.conf`, даже если пользователь переопределил `XDG_CONFIG_HOME`. Это единственное намеренное исключение из общего XDG-маршрута.

## Локальная конфигурация оборудования

После первого развёртывания создайте локальный override:

```sh
fm_config_home=${XDG_CONFIG_HOME:-"$HOME/.config"}
cp "$fm_config_home/hypr/fata/local.lua.example" "$fm_config_home/hypr/fata/local.lua"
hyprctl monitors all
hyprctl devices
```

В `local.lua` укажите реальные имена выходов, режимы, размещение экранов, раскладку и параметры указателя. Портативная конфигурация специально не содержит фиктивных connector names и не пытается вывести DPI мыши в sensitivity.

## Проверка после запуска сессии

```sh
fm_config_home=${XDG_CONFIG_HOME:-"$HOME/.config"}
hyprctl reload
hyprctl monitors all
hyprctl hyprpaper listactive
rofi -rasi-validate "$fm_config_home/rofi/config.rasi"
kitty --config "$fm_config_home/kitty/kitty.conf" --debug-config
```

Если Mako и Waybar ещё не запущены текущей сессией, их можно запустить с явными путями для чтения stderr:

```sh
mako --config "$fm_config_home/mako/config"
waybar --config "$fm_config_home/waybar/config.jsonc" --style "$fm_config_home/waybar/style.css"
```

Не включайте одновременно unit `hyprpaper.service` и автозапуск Hyprpaper из `fata/autostart.lua`. То же правило относится к дублирующим экземплярам Mako и Waybar.

## Сценарии отказа

| Симптом | Причина | Действие |
|---|---|---|
| `deployment source integrity check failed` | checkout повреждён или изменён после генерации checksum-манифеста | восстановить проверенный checkout; не обходить проверку |
| `existing managed target` | target существует, а `--force` не указан | сравнить файл с проектом или выполнить осознанный `--force` |
| отказ из-за symbolic link | путь ведёт через symlink | использовать обычный каталог или разворачивать конфигурацию вручную после проверки маршрута |
| Waybar не показывает workspaces или не переключает их | несовместимость конкретной сборки Waybar с Hyprland Lua IPC | проверить версию/сборку Waybar и runtime-логи в целевой сессии |
| отсутствует звук в панели | нет PulseAudio-совместимого сервера или модуль не собран | запустить совместимый аудиосервис и проверить модули Waybar |
| отсутствует фон | Hyprpaper не запущен или выбран неверный путь | проверить `hyprctl hyprpaper listactive` и единственность владельца процесса |
| прерывание во время `--apply` | файловая система или питание оборвали набор независимых publish-операций | при обновлении выполнить `--restore` из backup; при первой установке удалить только явно созданные управляемые файлы или повторить `--apply --force` после проверки |

Checksum-манифест контролирует содержимое файлов, разворачиваемых установщиком. Он не заменяет проверку происхождения Git remote или подписи релизного тега.
