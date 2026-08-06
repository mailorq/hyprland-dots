# Waybar

## Профили

<code>tools/build_waybar_profiles.py</code> генерирует JSON-конфигурации
профилей. При установке активируется ровно один файл
<code>config.&lt;profile&gt;.jsonc</code>.

| Профиль | Дополнительные ячейки | Исключённые показатели |
|---|---|---|
| <code>desktop</code> | — | батарея, подсветка, температура, CPU, память, power-profile |
| <code>laptop-battery</code> | батарея | подсветка, температура, CPU, память, power-profile |
| <code>laptop-backlight</code> | подсветка | батарея, температура, CPU, память, power-profile |
| <code>laptop-battery-backlight</code> | батарея, подсветка | температура, CPU, память, power-profile |

Общие модули: статичная ячейка MENU, 10 рабочих пространств Hyprland,
заголовок активного окна, часы, звук, сеть и трей. MENU запускает
<code>$HOME/.local/bin/fata-rofi</code> без фонового polling-процесса.

## Геометрия

| Параметр | Значение |
|---|---:|
| Высота панели | 40 px |
| Верхний / боковой отступ | 8 / 12 px |
| Высота ячейки | 32 px |
| Интервал ячеек | 6 px |
| Граница / скругление | 2 / 8 px |
| Внутренний отступ ячейки | 10 px |
| Кнопка рабочего пространства | минимум 22 px, горизонтальный padding 7 px |
| Минимум заголовка окна | 240 px |

Конфигурация укладывается в ширину 1920 px: блок пространств занимает около
250 px, заголовок ограничен 46 символами, а <code>fixed-center</code> сохраняет
позицию часов.

## Рабочие пространства

Hyprland объявляет пространства 1–10 постоянными, а Waybar отражает это через
<code>persistent-workspaces: { "*": 10 }</code>. Клик назначает пространство
текущему монитору; прокрутка модуля отключена.

## Проверка

~~~sh
python3 tools/build_theme_colors.py
python3 tools/build_waybar_profiles.py
python3 tools/validate_waybar_static.py
fm_config_home=${XDG_CONFIG_HOME:-"$HOME/.config"}
waybar --config "$fm_config_home/waybar/config.jsonc" --style "$fm_config_home/waybar/style.css"
~~~

Проверьте кнопки 1–10 на каждом дисплее и stderr Waybar. Для профиля desktop
подтвердите отсутствие аппаратных модулей.

## Ссылки

- <a href="https://github.com/Alexays/Waybar/blob/master/man/waybar-hyprland-workspaces.5.scd">Hyprland workspaces module</a>
- <a href="https://github.com/Alexays/Waybar/blob/master/man/waybar-custom.5.scd">Custom module</a>
- <a href="https://github.com/Alexays/Waybar/blob/master/man/waybar-pulseaudio.5.scd">PulseAudio module</a>
