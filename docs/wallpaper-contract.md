# Обои и Hyprpaper

## Набор и происхождение

В <code>assets/wallpapers/fata-morgana/</code> находятся пять утверждённых
экспортов 16:9. Их состав определяется полем <code>wallpaper.eligible</code>
в <code>assets/art/fata-morgana/manifest.json</code>. Никакой файл из
<code>pictures/</code> не используется Hyprpaper напрямую.

| ID | Разрешение | Потеря площади исходного кадра | Режим |
|---|---:|---:|---|
| <code>fm-016</code> | 2560 x 1440 | 21.0% | вручную подготовленный экспорт; стандартный фон |
| <code>fm-031</code> | 2560 x 1440 | 19.5% | вручную подготовленный экспорт |
| <code>fm-035</code> | 2560 x 1440 | 20.4% | вручную подготовленный экспорт |
| <code>fm-038</code> | 2560 x 1440 | 0.0% | вручную подготовленный экспорт |
| <code>fm-040</code> | 2560 x 1440 | 20.5% | вручную подготовленный экспорт |

Все пять QHD-файлов являются курируемыми экспортами. Сборщик требует их
наличия, проверяет RGB и разрешение 2560 x 1440, но не открывает их для
записи. Для всех файлов манифест фиксирует исходный мастер, контрольные суммы,
координаты утверждённого кадра, размер и режим экспорта.

## Конфигурация

<code>config/hypr/hyprpaper.conf</code> содержит современную конфигурацию
Hyprpaper с <code>splash = false</code>, <code>ipc = true</code> и fallback-
правилом <code>fit_mode = cover</code>. Правило без имени монитора применяется
к каждому выходу, для которого нет локального переопределения.

Установщик размещает файл в <code>~/.config/hypr/hyprpaper.conf</code>.
<code>fata/autostart.lua</code> запускает один экземпляр Hyprpaper; отдельный
пользовательский сервис для него одновременно включать не следует.

## Проверка

~~~sh
python3 tools/build_art_assets.py --check
python3 tools/build_wallpapers.py --check
python3 tools/validate_wallpapers_static.py
hyprctl hyprpaper listactive
~~~

Последняя команда выполняется в запущенной Wayland-сессии и должна показать
<code>fm-016</code> на каждом выходе без локального переопределения.

## Источник

- <a href="https://wiki.hypr.land/Hypr-Ecosystem/hyprpaper/">Документация Hyprpaper</a>
