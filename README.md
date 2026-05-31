# 📊 Math Modeling Labs

[![Status](https://img.shields.io/badge/статус-Учебный-2a9d8f)](https://github.com/topics/arh-education)
[![License](https://img.shields.io/badge/лицензия-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white&style=flat)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white&style=flat)](https://numpy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?logo=matplotlib&logoColor=white&style=flat)](https://matplotlib.org/)

Данный репозиторий содержит учебные лабораторные работы по курсу **«Математическое компьютерное моделирование»**.

## О проекте 

Репозиторий содержит лабораторные работы по курсу **«Математическое компьютерное моделирование»**.

Теория подкрепляется практикой: все задания реализованы на **Python** с использованием **NumPy** и **Matplotlib**.

### Примечания

- **Структура**: каждая папка — отдельная лабораторная работа  
- **Гибкость**: код универсален и поддерживает любые варианты входных данных  
- **Обновления**: новые работы добавляются по мере выполнения

- Примеры результатов хранятся в examples/ внутри каждой лабы
- Виртуальное окружение .venv/ создаётся один раз в корне

---

## Список работ

| № | Тема | Статус | Ссылка |
|---|------|--------|--------|
| 1 | Численное интегрирование методом Монте-Карло | ✅ Готово | [lab-01](./lab-01-monte-carlo/) |
| 2 | Задача Бюффона | ✅ Готово | [lab-02](./lab-02-buffon-needle/) |
| 3 | Задача о разорении игрока | ✅ Готово | [lab-03](./lab-03-gambler-ruin-problem/) |
| 4 | Численные методы интегрирования | ✅ Готово | [lab-04](./lab-04-numerical-integration-methods/) |
| 5 | Методы бисекции и касательных | ✅ Готово | [lab-05](./lab-05-root-finding-methods/) |
| 6 | Методы хорд и простых итераций | ✅ Готово | [lab-06](./lab-06-chord-and-fixed-point-methods/) |

---

## Единый порядок запуска

Для всех лабораторных используется один подход:

```bash
source .venv/bin/activate
cd <папка-лабораторной>
python3 labN.py
```

Например, для лабораторной №4:

```bash
cd lab-04-numerical-integration-methods
python3 lab4.py
```

Результаты сохраняются в локальную папку `plots/`. Для лабораторной №6
команда `python3 lab6.py` последовательно запускает метод хорд и метод простых
итераций.

---

## Настройка вариантов

Алгоритмы не требуется переписывать для нового варианта: входные данные
находятся в локальных `config.py`.

| Работа | Что меняется для нового варианта |
|--------|----------------------------------|
| `lab-01` | `F1_FORMULA`, `F2_FORMULA`, сторона и центр опорного квадрата: `A`, `X0`, `Y0` |
| `lab-02` | Вариантов нет; параметры эксперимента можно менять в `config.py` |
| `lab-03` | `P`, `X`, `Y`, `N`, `N_GAMES` |
| `lab-04` | `FUNCTION_FORMULA`, границы `A`, `B`, критерии `EPSILON`, `N_MAX` |
| `lab-05` | `FUNCTION_FORMULA`, `DERIVATIVE_FORMULA`, отрезок `A`, `B`, критерии `EPSILON`, `N_MAX` |
| `lab-06` | Хорды используют функцию и критерии `lab-05`; для простых итераций меняются `PHI_FORMULA`, `PHI_DERIVATIVE_FORMULA`, `X0` |

---

## Структура проекта

```
math-modeling-labs/
├── .gitignore                    # Игнорируемые файлы Git
├── README.md                     # О проекте
├── LICENSE                       # Лицензия
├── requirements.txt              # Зависимости Python
├── lab-01-monte-carlo/           # Лабораторная работа №1
│   ├── config.py                 # Конфигурация
│   ├── lab1.py                   # Основной скрипт
│   ├── README.md                 # Инструкция по л/р
│   ├── examples/                 # Примеры графиков и варианты
│   └── plots/                    # Авто-генерация png/svg
├── lab-02-buffon-needle/         # Лабораторная работа №2
│   ├── config.py                 # Конфигурация
│   ├── lab2.py                   # Основной скрипт
│   ├── README.md                 # Инструкция по л/р
│   ├── examples/                 # Примеры графиков и условие
│   └── plots/                    # Авто-генерация png/svg
├── lab-03-gambler-ruin-problem/  # Лабораторная работа №3
│   ├── config.py                 # Конфигурация
│   ├── lab3.py                   # Основной скрипт
│   ├── README.md                 # Инструкция по л/р
│   ├── examples/                 # Примеры графиков
│   └── plots/                    # Авто-генерация png/svg
├── lab-04-numerical-integration-methods/ # Лабораторная работа №4
│   ├── config.py                 # Конфигурация
│   ├── lab4.py                   # Основной скрипт
│   ├── README.md                 # Инструкция по л/р
│   ├── examples/                 # Примеры графиков
│   └── plots/                    # Авто-генерация png/svg
├── lab-05-root-finding-methods/  # Лабораторная работа №5
│   ├── config.py                 # Формула, отрезок и критерии останова
│   ├── lab5.py                   # Бисекция и метод касательных
│   ├── README.md                 # Инструкция по л/р
│   ├── examples/                 # Примеры графиков
│   └── plots/                    # Авто-генерация png/svg
└── lab-06-chord-and-fixed-point-methods/ # Лабораторная работа №6
    ├── common.py                 # Чтение общих настроек из lab-05
    ├── lab6.py                   # Последовательный запуск двух методов
    ├── README.md                 # Общая инструкция по л/р
    ├── chord-method/             # Метод хорд
    └── fixed-point-iteration/    # Метод простых итераций
```

---

## Установка

### 1. Клонировать репозиторий

```
git clone https://github.com/arshinov-dev/math-modeling-labs.git
cd math-modeling-labs
```

### 2. Создать виртуальное окружение

```
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. Установить зависимости

```
pip install -r requirements.txt
```

> Каждая лабораторная работа содержит собственную инструкцию по запуску и настройке параметров.  
> Просто откройте папку с нужной работой и следуйте указаниям в локальном `README.md`.

---

## Лицензия

Данный проект лицензирован под [MIT License](LICENSE).

Это означает, что вы можете свободно использовать, изменять и распространять код.

> ***При условии сохранения уведомления об авторских правах.***

---

## Контакты

| Автор | Никнейм |
|:-:|:-:|
| Arshinov Maxim | [@arshinov-dev](https://github.com/arshinov-dev)|

> Другие учебные проекты: <https://github.com/topics/arh-education>

---

<p align="center">
  <img src="https://github.com/arshinov-dev/git-learning/blob/main/assets/images/avatar.png" alt="Логотип" width="85">
</p>

<p align="center">© arshinov 2026</p>

<div align="center">

[⬆️ Наверх](#-Mathematical)

«По существу, все модели неправильны, но некоторые из них полезны» — Джордж Бокс

</div>
