# Проверка v1.0.0

Релиз проверяется в двух независимых средах: checkout и реальная Wayland-сессия. Первая среда контролирует воспроизводимые файлы и безопасность сценария; вторая — фактические возможности установленного software stack.

## Checkout gate

Подготовьте Python 3.10+ и Pillow, затем выполните:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r tools/requirements-assets.txt
python3 tools/validate_release.py --integration
```

`validate_release.py` выполняет только read-only проверки в отношении art и wallpaper. В gate входят:

| Проверка | Гарантия |
|---|---|
| `build_art_assets.py --check` | 40 masters, RGB metadata, dimensions и SHA-256 соответствуют manifest |
| `build_wallpapers.py --check` | 5 QHD 16:9 exports, provenance и SHA-256 соответствуют manifest |
| `build_release_manifest.py --check` | checksum inventory в точности покрывает разворачиваемые источники |
| static validators | Lua, generated palette/adapters, Waybar JSON/CSS, Rasi, Mako и installer contracts не дрейфуют |
| `test_install_integration.sh` | чистая установка, конфликт, forced backup и restore работают в `mktemp`-home; включается флагом `--integration` |

Также выполните syntax check на той POSIX shell, где будет запускаться установщик:

```sh
sh -n scripts/fata-install
sh -n scripts/fata-rofi
sh -n tools/test_install_integration.sh
```

## Runtime gate

После развёртывания войдите в Hyprland и проверьте:

```sh
fm_config_home=${XDG_CONFIG_HOME:-"$HOME/.config"}
hyprctl reload
hyprctl monitors all
hyprctl devices
hyprctl hyprpaper listactive
rofi -rasi-validate "$fm_config_home/rofi/config.rasi"
kitty --config "$fm_config_home/kitty/kitty.conf" --debug-config
```

При остановленных экземплярах Mako и Waybar используйте:

```sh
mako --config "$fm_config_home/mako/config"
waybar --config "$fm_config_home/waybar/config.jsonc" --style "$fm_config_home/waybar/style.css"
```

Подтвердите вручную:

- `Super + Q`, `Super + Escape`, `Super + Tab` и `Super + F`;
- переключение и перенос окна между workspaces 1–10;
- отсутствие в desktop-профиле battery, backlight, temperature, CPU, memory и power profile;
- корректный выбор каждого ноутбучного профиля на подходящем устройстве;
- отсутствие parser errors и warnings, относящихся к собственным конфигурационным файлам.

## Публикационный checklist

1. Рабочее дерево содержит только осознанные изменения релиза.
2. `assets/deployment.sha256` пересобран после любого изменения разворачиваемого файла; все разворачиваемые текстовые файлы имеют LF line endings.
3. `python3 tools/validate_release.py --integration` завершился успешно.
4. Runtime gate завершён в целевой Wayland-сессии.
5. Версия в `VERSION`, Git tag и release notes согласованы.
6. Изображения и screenshots не менялись, если релиз не был отдельно одобрен как asset revision.

Checksum manifest контролирует только целостность checkout. Перед публикацией проверяйте remote, историю изменений и подпись тега согласно принятой Git-политике проекта.
