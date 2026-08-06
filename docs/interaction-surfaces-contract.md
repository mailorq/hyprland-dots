# Kitty, Rofi и Mako

## Ресурсы

<code>assets/art/fata-morgana/manifest.json</code> определяет доступные
изображения. Генератор <code>tools/build_art_selectors.py</code> формирует
селекторы для всех 40 мастеров.

- Kitty читает JPEG-файлы из
  <code>$HOME/.local/share/fata-morgana/art/*.jpg</code>. Режим
  <code>cscaled</code> сохраняет пропорции изображения; tint равен 0.60.
- <code>fata-rofi</code> принимает имя утверждённого файла через
  <code>FM_ROFI_ART_FILE</code>. По умолчанию используется
  <code>fata-morgana-038-moonlit-sleep.jpg</code>.
- Mako использует собственные параметры цвета, радиуса и срочности. Иконки
  приложений остаются включёнными.

Установщик размещает арты в
<code>~/.local/share/fata-morgana/art/</code>, скрипт Rofi — в
<code>~/.local/bin/fata-rofi</code>, конфигурации компонентов — в
<code>$XDG_CONFIG_HOME</code> либо <code>~/.config</code>.

## Геометрия

| Поверхность | Базовая конфигурация | QHD |
|---|---|---|
| Kitty | шрифт 12 pt, внутренний отступ 10 pt | те же point-значения |
| Rofi | ширина 42%, 7 строк, отступ 16 px | ширина 38%, 9 строк при ширине вывода от 2200 px |
| Mako | максимум 380 × 160 px, до 3 уведомлений | без изменения |

Размер Rofi составляет около 806 px на FHD и 973 px на QHD. Параметры Mako
оставляют уведомления компактными на обоих целевых разрешениях.

## Проверка на целевой системе

~~~sh
python3 tools/build_theme_colors.py
python3 tools/build_art_selectors.py
python3 tools/validate_interaction_static.py
fm_config_home=${XDG_CONFIG_HOME:-"$HOME/.config"}
rofi -rasi-validate "$fm_config_home/rofi/config.rasi"
kitty --config "$fm_config_home/kitty/kitty.conf" --debug-config
mako --config "$fm_config_home/mako/config"
~~~

Команда Mako используется как проверка запуска. Выполняйте её при отсутствии
экземпляра Mako, уже запущенного текущим сеансом.

## Ссылки

- <a href="https://sw.kovidgoyal.net/kitty/conf/">Kitty configuration</a>
- <a href="https://davatorium.github.io/rofi/current/rofi-theme.5/">Rofi Rasi</a>
- <a href="https://www.mankier.com/5/mako">Mako</a>
