"""Конфигурация лабораторной работы №4: численное интегрирование."""

# Подынтегральная функция.
# Разрешено: x, +, -, *, /, ^, скобки, sin, cos, tan, exp, log, sqrt, abs, pi, e.
FUNCTION_FORMULA = "(x + 1) * sqrt(1 - x)"

# Отрезок интегрирования
A = 0.0
B = 1.0

# Эталонное значение интеграла для расчёта погрешностей.
# None -> вычислить автоматически уточнением метода Симпсона.
REFERENCE_AREA = None
REFERENCE_EPSILON = 1e-10
REFERENCE_MAX_REFINEMENTS = 24

# Критерии останова для автоматического уточнения каждого численного метода
EPSILON = 1e-4
N_MAX = 100_000
INITIAL_N = 10

# Количество фигур/разбиений/случайных точек для таблицы
N_VALUES = (10, 100, 1000)

# Количество фигур на графиках методов
PLOT_N = 10

# Начальное зерно генератора для метода Монте-Карло (None -> случайно)
RANDOM_SEED = 777

# Визуализация
PLOT_TITLE = "Лабораторная работа номер 4: вычисление площади функции"
FUNCTION_LABEL = None
FIGURE_SIZE = (15, 10)
CURVE_SAMPLES = 800
FUNCTION_COLOR = "#1d3557"
FIGURE_COLOR = "#2a9d8f"
FIGURE_EDGE_COLOR = "#264653"
SIMPSON_COLOR = "#e76f51"
MC_COLOR = "#7b2cbf"
GRID_ALPHA = 0.3

# Сохранение графиков
PLOT_DIR = "plots"
PLOT_BASENAME = "integration_methods_result"
SAVE_FORMATS = ("png", "svg")
PLOT_DPI = 200
SAVE_UNIQUE_NAMES = True
FILENAME_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S_%f"

# Показывать окно графика после сохранения
SHOW_PLOT = True
