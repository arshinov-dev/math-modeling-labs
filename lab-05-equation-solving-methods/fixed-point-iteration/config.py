"""Конфигурация раздела лабораторной работы №5: метод простой итерации."""

# Начальное приближение для x_{n+1} = phi(x_n)
X0 = 0.0

# Условия останова
EPSILON = 1e-14
N_MAX = 10**6

# Визуализация
PLOT_TITLE = "Лабораторная работа номер 5: метод простой итерации"
PHI_LABEL = r"$\varphi(x)=\frac{5}{x^2+2x+5}$"
DIAGONAL_LABEL = r"$y=x$"
OVERVIEW_FIGURE_SIZE = (10, 6)
COBWEB_FIGURE_SIZE = (11, 7)
DERIVATIVE_FIGURE_SIZE = (10, 6)
CURVE_SAMPLES = 1000
DOMAIN_X_MIN = -0.15
DOMAIN_X_MAX = 1.25
CHECK_X_MIN = 0.0
CHECK_X_MAX = 1.0
COBWEB_X_MIN = -0.05
COBWEB_X_MAX = 1.05
COBWEB_Y_MIN = -0.05
COBWEB_Y_MAX = 1.05
COBWEB_STEPS_SHOW = 12
INTERACTIVE_STEPS_SHOW = 24

PHI_COLOR = "#1d3557"
DIAGONAL_COLOR = "#2f2f2f"
DERIVATIVE_COLOR = "#7b2cbf"
CONTRACTION_COLOR = "#e63946"
VERTICAL_STEP_COLOR = "#457b9d"
HORIZONTAL_STEP_COLOR = "#e76f51"
ITERATION_POINT_COLOR = "#f4a261"
ROOT_COLOR = "#7b2cbf"
START_COLOR = "#2a9d8f"
GRID_ALPHA = 0.3

# Сохранение графиков
PLOT_DIR = "plots"
PLOT_BASENAME = "fixed_point_iteration_result"
INTERACTIVE_HTML_NAME = "fixed_point_cobweb_interactive.html"
SAVE_FORMATS = ("png", "svg")
PLOT_DPI = 200
SAVE_UNIQUE_NAMES = True
FILENAME_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S_%f"

# Показывать окно графика после сохранения
SHOW_PLOT = True
