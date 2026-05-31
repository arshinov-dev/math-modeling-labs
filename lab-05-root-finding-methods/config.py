"""Конфигурация лабораторной работы №5: бисекция и метод касательных."""

# Уравнение f(x) = 0 и его производная.
# Разрешено: x, +, -, *, /, ^, скобки, sin, cos, tan, exp, log, sqrt, abs, pi, e.
FUNCTION_FORMULA = "2 / (x^2 - x + 1)^2 - 1"
DERIVATIVE_FORMULA = "-4 * (2 * x - 1) / (x^2 - x + 1)^3"

# Отрезок поиска корня для метода бисекции
A = 0.0
B = 2.0

# Начальное приближение для метода Ньютона
X0 = 1.5

# Условия останова
EPSILON = 1e-14
N_MAX = 10**6
DERIVATIVE_MIN_ABS = 1e-15

# Контрольный корень для расчёта погрешности.
# None -> найти автоматически более точной бисекцией на [A; B].
REFERENCE_ROOT = None
REFERENCE_EPSILON = 1e-15
REFERENCE_N_MAX = 200

# Визуализация
PLOT_TITLE = "Лабораторная работа номер 5: поиск корня функции"
FUNCTION_LABEL = None
OVERVIEW_FIGURE_SIZE = (12, 6)
ITERATIONS_FIGURE_SIZE = (12, 10)
CONVERGENCE_FIGURE_SIZE = (14, 5)
CURVE_SAMPLES = 1000
MAX_ITERATIONS_SHOW = 4
X_MARGIN = 0.5
Y_MIN = -2.0
Y_MAX = 3.0
FUNCTION_COLOR = "#1d3557"
BISECTION_COLOR = "#457b9d"
NEWTON_COLOR = "#f4a261"
TANGENT_COLOR = "#e76f51"
INTERVAL_COLOR = "#e9c46a"
ROOT_COLOR = "#2a9d8f"
EXACT_ROOT_COLOR = "#2f2f2f"
GRID_ALPHA = 0.3

# Сохранение графиков
PLOT_DIR = "plots"
PLOT_BASENAME = "root_finding_methods_result"
SAVE_FORMATS = ("png", "svg")
PLOT_DPI = 200
SAVE_UNIQUE_NAMES = True
FILENAME_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S_%f"

# Показывать окна графиков после сохранения
SHOW_PLOT = True
