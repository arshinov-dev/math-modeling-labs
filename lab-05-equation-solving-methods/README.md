# 📉 Lab 05: Numerical Equation Solving Methods

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-2.0.2-013243?logo=numpy&logoColor=white)](https://numpy.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.9.4-11557c)](https://matplotlib.org/)
[![Variant](https://img.shields.io/badge/Lab-5-f39c12)]()

Лабораторная работа №5 по дисциплине **«Математическое компьютерное моделирование»**.

---

## Описание задачи

Исследовать численные методы решения уравнений:

1. Метод бисекции
2. Метод касательных (метод Ньютона)
3. Метод хорд
4. Метод простых итераций

Чтобы код и графики разных методов не смешивались, работа разделена на три
самостоятельных каталога. Методы бисекции и касательных находятся в одном
разделе, поскольку они сравниваются для одной функции.

---

## Разделы работы

| Раздел | Методы | Запуск | Документация |
|--------|--------|--------|--------------|
| `bisection-newton/` | Бисекция и метод касательных | `python3 bisection_newton.py` | [README](bisection-newton/) |
| `chord-method/` | Метод хорд | `python3 chord_method.py` | [README](chord-method/) |
| `fixed-point-iteration/` | Метод простых итераций | `python3 fixed_point_iteration.py` | [README](fixed-point-iteration/) |

---

## Запуск всей работы

# 1. Активировать виртуальное окружение (из корня проекта)
```
source .venv/bin/activate
```

# 2. Перейти в папку лабораторной работы
```
cd lab-05-equation-solving-methods
```

# 3. Запустить все методы последовательно
```
python3 run_all.py
```

Каждый раздел также можно запускать отдельно. Его настройки находятся в
локальном `config.py`, а сгенерированные графики сохраняются в локальную папку
`plots/`.

---

## Структура папки
```
lab-05-equation-solving-methods/
├── README.md
├── run_all.py
├── bisection-newton/
│   ├── config.py
│   ├── bisection_newton.py
│   ├── README.md
│   ├── examples/
│   └── plots/
├── chord-method/
│   ├── config.py
│   ├── chord_method.py
│   ├── README.md
│   ├── examples/
│   └── plots/
└── fixed-point-iteration/
    ├── config.py
    ├── fixed_point_iteration.py
    ├── README.md
    ├── examples/
    └── plots/
```
<div align="center">

[⬆️ Наверх](#-Lab-05-Numerical-Equation-Solving-Methods)

</div>
