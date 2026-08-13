# Fata Morgana Hyprland Dots

Конфигурационный набор для Hyprland 0.55+ в эстетике The House in Fata
Morgana. В состав входят Hyprland, Hyprpaper, Waybar, Rofi, Kitty и Mako.
Конфигурация использует Lua API Hyprland и поддерживает настольный профиль, а
также явные профили для ноутбуков.

## Совместимость

| Область | Требование |
|---|---|
| Композитор | Hyprland 0.55 или новее |
| Сервисы сеанса | Hyprpaper, Mako, Waybar |
| Клиентские приложения | Kitty и Rofi с поддержкой Wayland |
| Аудио | PipeWire-Pulse или совместимый PulseAudio-сервис для Waybar |
| Развёртывание | POSIX shell и стандартные утилиты <code>cat</code>, <code>chmod</code>, <code>cp</code>, <code>dirname</code>, <code>mkdir</code>, <code>pwd</code> |

Пакеты и способ запуска Hyprland выбираются по документации используемой
системы. Перед развёртыванием проверьте версию в работающей Wayland-сессии:

~~~sh
hyprctl version
~~~

Минимальный набор пользовательских программ должен быть доступен в текущем
окружении до запуска установщика:

~~~sh
command -v Hyprland
command -v hyprpaper
command -v waybar
command -v rofi
command -v kitty
command -v mako
~~~

Для корректной работы панели также нужен PulseAudio-совместимый аудиосервис.
На ноутбуках аппаратные модули Waybar включаются только выбранным профилем и
требуют соответствующих устройств в <code>/sys/class/power_supply</code> или
<code>/sys/class/backlight</code>.

## Состав проекта

| Путь | Назначение |
|---|---|
| <code>config/hypr</code> | Lua-модули Hyprland и конфигурация Hyprpaper |
| <code>config/waybar</code> | профили панели, CSS и палитра |
| <code>config/rofi</code> | Rasi-конфигурация лаунчера |
| <code>config/kitty</code> | конфигурация терминала |
| <code>config/mako</code> | конфигурация уведомлений |
| <code>assets/art</code> | утверждённые изображения и манифест |
| <code>assets/wallpapers</code> | производные 16:9-обои |
| <code>scripts</code> | развёртывание и запуск Rofi |
| <code>tools</code> | генераторы и статические валидаторы |

## Развёртывание

### 1. Получить исходники

~~~sh
git clone https://github.com/mailorq/hyprland-dots.git
cd hyprland-dots
~~~

### 2. Выбрать профиль

| Профиль | Назначение |
|---|---|
| <code>desktop</code> | настольный ПК; без батареи, подсветки, температуры, CPU, памяти и power-profile |
| <code>laptop-battery</code> | добавить нативный индикатор батареи |
| <code>laptop-backlight</code> | добавить нативный индикатор подсветки |
| <code>laptop-battery-backlight</code> | добавить оба ноутбучных индикатора |

### 3. Проверить план и зависимости

~~~sh
sh scripts/fata-install --profile desktop
sh scripts/fata-install --profile desktop --check
~~~

Dry-run печатает список управляемых файлов. Preflight проверяет обязательные
бинарные зависимости и наличие sysfs-устройств для выбранного ноутбучного
профиля.

### 4. Применить конфигурацию

~~~sh
sh scripts/fata-install --profile desktop --apply
~~~

При существующем управляемом файле установщик останавливается. После проверки
различий допустима замена перечисленных в плане файлов:

~~~sh
sh scripts/fata-install --profile desktop --apply --force
~~~

Режим <code>--force</code> не удаляет каталоги, не следует символьным ссылкам
в целевых путях и не меняет <code>fata/local.lua</code>.

### 5. Запустить сеанс

Выберите сессию Hyprland способом, принятым в вашей системе. При старте
<code>fata/autostart.lua</code> запускает Hyprpaper, Mako и Waybar.
<code>hyprpaper.service</code> не следует включать параллельно.

## Локальная настройка оборудования

Сначала получите фактические данные:

~~~sh
hyprctl monitors all
hyprctl devices
~~~

Создайте локальный файл:

~~~sh
fm_config_home=${XDG_CONFIG_HOME:-"$HOME/.config"}
cp "$fm_config_home/hypr/fata/local.lua.example" "$fm_config_home/hypr/fata/local.lua"
~~~

В <code>fata/local.lua</code> укажите имена выходов, режимы, частоту, положение
дисплеев, раскладку и параметры мыши. Базовая чувствительность равна 0.0;
профиль ускорения <code>flat</code> или <code>adaptive</code> задаётся после
проверки устройства.

~~~sh
hyprctl reload
~~~

## Управление

| Сочетание | Действие |
|---|---|
| <code>Super + Q</code> | открыть Kitty |
| <code>Super + Tab</code> | перевести фокус на последнее активное окно |
| <code>Super + F</code> | открыть Rofi |
| <code>Super + Shift + C</code> | закрыть активное окно |
| <code>Super + Space</code> | переключить floating-режим |
| <code>Super + M</code> | переключить полноэкранный режим |
| <code>Super + 1…0</code> | перейти на пространство 1…10 текущего монитора |
| <code>Super + Shift + 1…0</code> | переместить окно на пространство 1…10 |

## Геометрия

| Параметр | Значение |
|---|---:|
| Внутренний / внешний отступ окон | 8 / 12 px |
| Граница / скругление окон | 2 / 8 px |
| Высота Waybar | 40 px |
| Верхний / боковой отступ Waybar | 8 / 12 px |
| Высота ячейки Waybar | 32 px |
| Интервал между ячейками | 6 px |
| Рабочие пространства | 1–10, постоянные |

Палитра определяется в <code>theme/palette.json</code>. Палитра и
компонентные адаптеры генерируются из одного источника.

## Изображения и обои

Мастера изображений нормализуются в sRGB/RGB, получают корректную EXIF-ориентацию
и ограничиваются максимальной стороной 2048 px. Сборка не кадрирует и не
увеличивает изображение.

Hyprpaper использует <code>fm-016</code> как fallback. Все пять 16:9-экспортов
в <code>assets/wallpapers/fata-morgana/</code> — вручную подготовленные файлы
2560 x 1440; генератор проверяет и учитывает их, но не перекодирует.

## Проверка

Внутри Wayland-сессии:

~~~sh
fm_config_home=${XDG_CONFIG_HOME:-"$HOME/.config"}
hyprctl reload
hyprctl hyprpaper listactive
rofi -rasi-validate "$fm_config_home/rofi/config.rasi"
kitty --config "$fm_config_home/kitty/kitty.conf" --debug-config
~~~

Для проверки Mako и Waybar с явными путями к конфигурации остановите либо не
запускайте их экземпляры, уже принадлежащие текущему сеансу:

~~~sh
mako --config "$fm_config_home/mako/config"
waybar --config "$fm_config_home/waybar/config.jsonc" --style "$fm_config_home/waybar/style.css"
~~~

## Разработка

~~~sh
python3 tools/build_theme_colors.py
python3 tools/build_art_assets.py --check
python3 tools/build_wallpapers.py --check
python3 tools/build_art_selectors.py
python3 tools/build_waybar_profiles.py
python3 tools/validate_hyprland_static.py
python3 tools/validate_interaction_static.py
python3 tools/validate_waybar_static.py
python3 tools/validate_wallpapers_static.py
python3 tools/validate_install_static.py
sh -n scripts/fata-install
sh scripts/fata-install --profile desktop
~~~

## Документация

- <a href="docs/architecture-decisions.md">архитектура</a>
- <a href="docs/installing.md">развёртывание</a>
- <a href="docs/hyprland-contract.md">Hyprland</a>
- <a href="docs/waybar-contract.md">Waybar</a>
- <a href="docs/interaction-surfaces-contract.md">Kitty, Rofi и Mako</a>
- <a href="docs/wallpaper-contract.md">обои и Hyprpaper</a>
- <a href="docs/art-palette-contract.md">графические материалы и палитра</a>
- <a href="docs/dependency-contract.md">зависимости и профили</a>
- <a href="docs/implementation-plan.md">инженерский процесс</a>
