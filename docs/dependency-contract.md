# Зависимости и профили

## Обязательная среда

| Компонент | Требование | Область |
|---|---|---|
| Композитор | Hyprland 0.55+ | все профили |
| Обои | hyprpaper | все профили |
| Терминал | kitty | все профили |
| Лаунчер | rofi с поддержкой Wayland | все профили |
| Уведомления | mako | все профили |
| Панель | waybar с модулями Hyprland, PulseAudio, network и tray | все профили |
| Развёртывание | POSIX sh, cat, chmod, cp, dirname, mkdir | локальный checkout |

Установщик выполняет предварительную проверку бинарных файлов перед
развёртыванием. Выбор пакетов и системных сервисов остаётся задачей
дистрибутива; соответствующие команды приведены в корневом README.

## Профили Waybar

| Профиль | Дополнительные модули |
|---|---|
| <code>desktop</code> | отсутствуют |
| <code>laptop-battery</code> | батарея |
| <code>laptop-backlight</code> | подсветка |
| <code>laptop-battery-backlight</code> | батарея и подсветка |

Профиль выбирается параметром <code>--profile</code>. Для батареи проверяется
<code>/sys/class/power_supply/BAT*</code>, для подсветки —
<code>/sys/class/backlight/*</code>. Температура, CPU, память и
power-profile не поставляются в существующих профилях.

## Внешние команды

<code>fata-rofi</code> зависит только от POSIX <code>sh</code> и
Wayland-версии Rofi. Hyprland и Waybar запускают установленный файл по полному
пути <code>$HOME/.local/bin/fata-rofi</code>; пользовательский PATH не является
частью контракта запуска.

## Проверка

| Поверхность | Проверка на Linux |
|---|---|
| Hyprland | <code>hyprctl reload</code>, <code>hyprctl monitors all</code>, <code>hyprctl devices</code> |
| Hyprpaper | <code>hyprctl hyprpaper listactive</code> и stderr процесса |
| Rofi | <code>rofi -rasi-validate</code> |
| Kitty | <code>kitty --debug-config</code> |
| Mako | запуск с целевой конфигурацией и stderr |
| Waybar | запуск с явными путями config/style и stderr |
| Скрипты | <code>sh -n</code>; ShellCheck при наличии в рабочей среде |

## Первичные источники

- <a href="https://wiki.hypr.land/Configuring/Start/">Hyprland Lua configuration</a>
- <a href="https://wiki.hypr.land/Hypr-Ecosystem/hyprpaper/">Hyprpaper</a>
- <a href="https://davatorium.github.io/rofi/current/rofi-theme.5/">Rofi Rasi</a>
- <a href="https://sw.kovidgoyal.net/kitty/conf/">Kitty</a>
- <a href="https://www.mankier.com/5/mako">Mako</a>
- <a href="https://github.com/Alexays/Waybar">Waybar</a>
