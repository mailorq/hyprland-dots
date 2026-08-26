# Генерация и build boundary

`scripts/fata-build` — единственная shell-точка входа для генерации производных текстовых файлов и проверки checkout. Установку в пользовательский каталог выполняет только `scripts/fata-install`; builder не вызывает установщик, пакетный менеджер или `sudo`.

## Предварительные условия

Требуются POSIX `sh` с базовыми утилитами `cat`, `command`, `dirname` и `pwd`, Python 3.10+ и Pillow из `tools/requirements-assets.txt`. По умолчанию script вызывает `python3`; для другого интерпретатора задайте переменную `PYTHON` как имя команды или абсолютный путь без аргументов.

```sh
PYTHON=python3 sh scripts/fata-build --check
```

## Режимы

| Режим | Изменяет checkout | Действие |
|---|---:|---|
| `--check` | нет | запускает полный статический release gate; режим по умолчанию |
| `--refresh-generated` | только производные текстовые файлы | синхронизирует palette adapters, Kitty/Rofi selectors, Waybar profiles и deployment checksum, затем запускает release gate |
| `--integration` | нет в checkout | запускает `--check` и изолированный install/update/restore тест во временном `mktemp`-home |

`--refresh-generated` применяется только после осознанного изменения канонических текстовых источников: `theme/palette.json`, art manifest или Python generator. После запуска просмотрите diff перед коммитом.

## Замороженные изображения

Builder намеренно не вызывает `build_art_assets.py`, `build_wallpapers.py` или `--rebuild-frozen-assets`. Он не меняет `.jpg` в `assets/` и не обращается к `pictures/` как к источнику записи. Пересмотр изображений остаётся отдельной явно одобренной процедурой вне этого shell interface.

## Проверка перед коммитом

```sh
sh -n scripts/fata-build
PYTHON=python3 sh scripts/fata-build --check
git diff --check
```

Для полного проверочного цикла:

```sh
PYTHON=python3 sh scripts/fata-build --integration
```
