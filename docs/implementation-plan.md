# Инженерский процесс

## Изменение конфигурации

1. Внести изменение в исходный модуль или канонический источник данных.
2. Пересобрать производные файлы.
3. Запустить статические проверки.
4. Выполнить dry-run установщика для затронутого профиля.
5. Проверить изменённую поверхность в Linux Wayland-сессии.
6. Подготовить отдельные коммиты по компонентам.

## Стандартная проверка

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

Для пересборки нормализованных артов требуется Pillow из
<code>tools/requirements-assets.txt</code>. Утверждённые производные файлы уже
находятся в репозитории, поэтому обычное развёртывание этой зависимости не
требует.

## Контроль перед передачей

- Состав изображений, размеры производных файлов и контрольные суммы
  соответствуют манифестам.
- Палитра генерируется из <code>theme/palette.json</code>.
- Конфигурации проходят статические валидаторы.
- Установщик не меняет локальные переопределения и имеет корректный dry-run.
- На Linux проверены stderr и поведение затронутых компонентов.
