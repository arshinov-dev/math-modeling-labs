"""Конфигурация раздела лабораторной работы №6: метод хорд."""

# Формула f(x), отрезок [A; B], EPSILON и N_MAX берутся из:
# ../../lab-05-root-finding-methods/config.py

# Визуализация
PLOT_TITLE = "Лабораторная работа номер 6: метод хорд"
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
