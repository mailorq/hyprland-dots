# Развёртывание

## Назначение установщика

<code>scripts/fata-install</code> переносит в домашний каталог только
управляемые файлы проекта. Он не устанавливает системные пакеты, не запускает
демоны и не определяет профиль оборудования автоматически.

### Целевые пути

| Источник | Назначение |
|---|---|
| <code>config/hypr</code> | <code>$XDG_CONFIG_HOME/hypr</code> |
| <code>config/hypr/hyprpaper.conf</code> | <code>~/.config/hypr/hyprpaper.conf</code> |
| <code>config/kitty</code>, <code>config/rofi</code>, <code>config/mako</code>, <code>config/waybar</code> | соответствующие каталоги <code>$XDG_CONFIG_HOME</code> |
| <code>scripts/fata-rofi</code> | <code>~/.local/bin/fata-rofi</code> |
| арты | <code>~/.local/share/fata-morgana/art</code> |
| обои | <code>~/.local/share/fata-morgana/wallpapers</code> |

Hyprpaper использует документированный путь
<code>~/.config/hypr/hyprpaper.conf</code> независимо от
<code>XDG_CONFIG_HOME</code>.

## Порядок работы

Из корня репозитория:

~~~sh
# Показать план без записи файлов
sh scripts/fata-install --profile desktop

# Проверить зависимости
sh scripts/fata-install --profile desktop --check

# Развернуть профиль
sh scripts/fata-install --profile desktop --apply
~~~

Если управляемый файл уже существует, развёртывание останавливается. Для
сознательной замены конкретных управляемых файлов:

~~~sh
sh scripts/fata-install --profile desktop --apply --force
~~~

Режим <code>--force</code> не удаляет каталогов и отклоняет целевой путь,
содержащий символьную ссылку на любом уровне. Локальный файл
<code>fata/local.lua</code> не изменяется.

## Профили

| Профиль | Назначение |
|---|---|
| <code>desktop</code> | ПК без аппаратных ячеек панели |
| <code>laptop-battery</code> | ноутбук с индикатором батареи |
| <code>laptop-backlight</code> | ноутбук с индикатором яркости |
| <code>laptop-battery-backlight</code> | оба индикатора |

## Сеанс после установки

<code>fata/autostart.lua</code> запускает Hyprpaper, Mako и Waybar при старте
Hyprland. Не включайте одновременно <code>hyprpaper.service</code> через UWSM
или пользовательский systemd.

~~~sh
fm_config_home=${XDG_CONFIG_HOME:-"$HOME/.config"}
hyprctl reload
hyprctl hyprpaper listactive
rofi -rasi-validate "$fm_config_home/rofi/config.rasi"
kitty --config "$fm_config_home/kitty/kitty.conf" --debug-config
mako --config "$fm_config_home/mako/config"
waybar --config "$fm_config_home/waybar/config.jsonc" --style "$fm_config_home/waybar/style.css"
~~~

Эти проверки выполняются в работающей Wayland-сессии. Mako и Waybar запускайте
как диагностические процессы только при отсутствии экземпляров, которыми уже
владеет текущая сессия.
