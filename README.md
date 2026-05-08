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
| 1 | Метод Монте-Карло (Вычисление площади) | ✅ Готово | [lab-01](./lab-01-monte-carlo/) |
| 2 | Метод Бюффона ( Вычисления числа $$ \pi $$ ) | ✅ Готово | [lab-02](./lab-02-buffon-needle/) |
| 3 | Задача о разорении игрока | ✅ Готово | [lab-03](./lab-03/) |

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
└── lab-03/                       # Лабораторная работа №3
    ├── config.py                 # Конфигурация
    ├── lab3.py                   # Основной скрипт
    ├── README.md                 # Инструкция по л/р
    ├── examples/                 # Примеры графиков
    └── plots/                    # Авто-генерация png/svg
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
