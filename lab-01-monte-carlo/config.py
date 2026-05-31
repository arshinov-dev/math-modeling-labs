"""Конфигурация лабораторной работы по методу Монте-Карло."""

# Количество случайных точек
N_POINTS = 1000

# Опорный квадрат: центр (X0, Y0) и длина стороны A
X0 = 1.0
Y0 = 1.0
A = 2.0

# Начальное зерно генератора (None -> новый результат на каждом запуске)
RANDOM_SEED = 777

# Границы области f1(x) и f2(x).
# Разрешено: x, +, -, *, /, ^, скобки, sin, cos, tan, exp, log, sqrt, abs, pi, e.
F1_FORMULA = "x^2 - 2"
F2_FORMULA = "2 - x^2"

# True -> включать точки на границе, False -> строго между кривыми
INCLUDE_BORDER = True

# Подписи (None -> генерируются автоматически из формул)
F1_LABEL = None
F2_LABEL = None

# Цвета кривых
F1_COLOR = "#1d3557"
F2_COLOR = "#e63946"

# Настройки графика
PLOT_TITLE = "Лабораторная работа номер 1: метод Монте-Карло – вариант 1"
FIGURE_SIZE = (9, 7)
CURVE_SAMPLES = 600
INSIDE_COLOR = "#2a9d8f"
OUTSIDE_COLOR = "#b0b0b0"
INSIDE_POINT_SIZE = 20
OUTSIDE_POINT_SIZE = 16
INSIDE_ALPHA = 0.75
OUTSIDE_ALPHA = 0.5
BOUNDS_COLOR = "#2f2f2f"

# Сохранение графика
PLOT_DIR = "plots"
PLOT_BASENAME = "monte_carlo_result"
SAVE_FORMATS = ("png", "svg")
PLOT_DPI = 200
SAVE_UNIQUE_NAMES = True
FILENAME_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S_%f"

# Показывать окно графика после сохранения
SHOW_PLOT = True
