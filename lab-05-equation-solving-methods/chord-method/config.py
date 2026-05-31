"""Конфигурация раздела лабораторной работы №5: метод хорд."""

# Отрезок поиска корня
A = 0.0
B = 2.0

# Условия останова
EPSILON = 1e-14
N_MAX = 10**6

# Визуализация
PLOT_TITLE = "Лабораторная работа номер 5: метод хорд"
FUNCTION_LABEL = r"$f(x)=\frac{2}{(x^2-x+1)^2}-1$"
OVERVIEW_FIGURE_SIZE = (10, 6)
ZOOM_FIGURE_SIZE = (11, 7)
CURVE_SAMPLES = 1000
MAX_CHORDS_SHOW = 4
FUNCTION_COLOR = "#1d3557"
CHORD_COLOR = "#e76f51"
PROJECTION_COLOR = "#457b9d"
ITERATION_POINT_COLOR = "#f4a261"
INTERVAL_COLOR = "#2a9d8f"
ROOT_COLOR = "#7b2cbf"
EXACT_ROOT_COLOR = "#2f2f2f"
GRID_ALPHA = 0.3

# Сохранение графиков
PLOT_DIR = "plots"
PLOT_BASENAME = "chord_method_result"
SAVE_FORMATS = ("png", "svg")
PLOT_DPI = 200
SAVE_UNIQUE_NAMES = True
FILENAME_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S_%f"

# Показывать окно графика после сохранения
SHOW_PLOT = True
