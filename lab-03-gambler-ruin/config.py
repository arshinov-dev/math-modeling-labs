"""Конфигурация лабораторной работы №3: задача о разорении игрока."""

# Основные параметры эксперимента
P = 0.58  # вероятность выигрыша 1 рубля первым игроком
X = 79  # начальный капитал первого игрока
Y = 121  # начальный капитал второго игрока
N = 1000  # максимальное число шагов в одной игре
N_GAMES = 1000  # количество моделируемых игр
RANDOM_SEED = 777

# Визуализация
PLOT_TITLE = "Лабораторная работа номер 3: задача о разорении игрока"
FIGURE_SIZE = (15, 6)
BACKGROUND_TRAJECTORIES = 180
HIGHLIGHT_TRAJECTORIES = 5
TRAJECTORY_COLOR = "#457b9d"
TRAJECTORY_ALPHA = 0.08
HIGHLIGHT_COLORS = ("#1d3557", "#2a9d8f", "#e76f51", "#f4a261", "#7b2cbf")
PLAYER_1_RUIN_COLOR = "#e63946"
PLAYER_2_RUIN_COLOR = "#2a9d8f"
DRAW_COLOR = "#7f8c8d"
THEORY_COLOR = "#1d3557"
START_COLOR = "#6c757d"
GRID_ALPHA = 0.3

# Сохранение графиков
PLOT_DIR = "plots"
PLOT_BASENAME = "gambler_ruin_result"
SAVE_FORMATS = ("png", "svg")
PLOT_DPI = 200
SAVE_UNIQUE_NAMES = True
FILENAME_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S_%f"

# Показывать окно графика после сохранения
SHOW_PLOT = True
