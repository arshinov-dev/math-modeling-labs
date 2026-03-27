"""Конфигурация лабораторной работы №2: метод Бюффона."""

# Основные параметры эксперимента (обозначения как в условии)
L = 0.5  # длина иглы
A = 2.0  # расстояние между линиями
N = 10000  # количество бросков
RANDOM_SEED = 777

# Геометрия области для визуализации
BOARD_WIDTH = 10.0
Y_MIN = 0.0
NUM_STRIPS = 10  # количество промежутков между линиями

# Учитывать попадание на линию как пересечение
INCLUDE_BORDER = True

# Визуализация
PLOT_TITLE = "Лабораторная работа номер 2: метод Бюффона."
FIGURE_SIZE = (14, 6)
MAX_NEEDLES_SHOW = 200
LINE_COLOR = "#7f8c8d"
LINE_ALPHA = 0.55
HIT_COLOR = "#e63946"
MISS_COLOR = "#1d3557"
HIT_WIDTH = 2.2
MISS_WIDTH = 1.2
NEEDLE_ALPHA = 0.75
CONVERGENCE_COLOR = "#457b9d"
CONVERGENCE_ALPHA = 0.5
CONVERGENCE_WIDTH = 0.7
TRUE_PI_COLOR = "#e76f51"
TRUE_PI_WIDTH = 2.0
CONVERGENCE_EVERY = 1

# Сохранение графиков
PLOT_DIR = "plots"
PLOT_BASENAME = "buffon_needle_result"
SAVE_FORMATS = ("png", "svg")
PLOT_DPI = 200
SAVE_UNIQUE_NAMES = True
FILENAME_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S_%f"

# Показывать окно графика после сохранения
SHOW_PLOT = True
