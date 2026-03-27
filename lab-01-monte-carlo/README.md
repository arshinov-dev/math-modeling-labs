# 🔬 Lab 01: Monte Carlo Method

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-2.0.2-013243?logo=numpy&logoColor=white)](https://numpy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.9.4-11557c)](https://matplotlib.org/)
[![Variant](https://img.shields.io/badge/Lab-1-f39c12)]()

Лабораторная работа №1 по дисциплине **«Математическое компьютерное моделирование»**.

---

## Описание задачи (на примере варианта – 1) 

Оценка площади области, ограниченной функциями, методом Монте-Карло:

$$ y = x^2 - 2 $$
$$ y = 2 - x^2 $$

**Опорный квадрат:** центр (1, 1), сторона = 2

Полное задание и список вариантов: [task-variants.pdf](https://github.com/arushinofu/math-modeling-labs/tree/main/lab-01-monte-carlo/examples/task-variants.pdf)

---

## Примеры результатов

Разные варианты параметров конфигурации (см. `config.py`):

| Вариант 1 | Вариант 7 |
|:---------:|:---------:|
| ![Variant 1](https://raw.githubusercontent.com/arushinofu/math-modeling-labs/main/lab-01-monte-carlo/examples/variant-01.png) | ![Variant 7](https://raw.githubusercontent.com/arushinofu/math-modeling-labs/main/lab-01-monte-carlo/examples/variant-07.png) |

| Вариант 14 | Вариант 21 |
|:----------:|:----------:|
| ![Variant 14](https://raw.githubusercontent.com/arushinofu/math-modeling-labs/main/lab-01-monte-carlo/examples/variant-14.png) | ![Variant 21](https://raw.githubusercontent.com/arushinofu/math-modeling-labs/main/lab-01-monte-carlo/examples/variant-21.png) |

---

## Возможности

| Функция | Описание |
|---------|----------|
| Параметризация | Все настройки в `config.py` |
| Оценка площади | Расчёт через долю попаданий |
| Оценка погрешности | Статистическая погрешность ±1σ |
| Визуализация | Цвета для попаданий/промахов |
| Экспорт графиков | PNG + SVG в папку `plots/` |

---

## Технологии

| Компонент | Версия | Назначение |
|-----------|--------|------------|
| Python | 3.9+ | Основной язык |
| NumPy | 2.0.2 | Генерация случайных точек |
| Matplotlib | 3.9.4 | Построение графиков |

---

## Запуск

# 1. Активировать виртуальное окружение (из корня проекта)
```
source .venv/bin/activate
```

# 2. Перейти в папку лабы
```
cd lab-01-monte-carlo
```

# 3. Запустить скрипт
```
python3 lab1.py
```

---

## После запуска:
1. Выведет число точек, попаданий, оценку площади
2. Создаст папку plots/ (если нет)
3. Сохранит графики с уникальным именем

---

## Конфигурация
Все параметры в config.py:
|Параметр|Описание|
|---|---|
|`N_POINTS`|Количество случайных точек|
|`X0`, `Y0`, `A`|Центр и сторона опорного квадрата|
|`LOWER_FORMULA`|Нижняя граница области|
|`UPPER_FORMULA`|Верхняя граница области|
|`RANDOM_SEED`|Зерно генератора (None = случайно)|
|`SAVE_UNIQUE_NAMES`|Защита от перезаписи файлов (False -> если нужно отключить)|

**Поддерживаемый синтаксис формул:** `x`, `+`, `-`, `*`, `/`, `^`, скобки, `sin`, `cos`, `tan`, `exp`, `log`, `sqrt`, `abs`, `pi`, `e`

---

## Структура папки
```
lab-01-monte-carlo/
├── config.py                 # Конфигурация задачи
├── lab1.py                   # Основной скрипт
├── README.md                 # Этот файл
├── examples/                 # Примеры для README
│   ├── variant-01.png
│   ├── variant-07.png
│   ├── variant-14.png
│   └── task-variants.pdf
└── plots/                    # Графики
```
<div align="center">

[⬆️ Наверх](#-Lab)

</div>
