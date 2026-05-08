from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import config


def validate_config():
    """Проверяем корректность входных параметров."""
    if not 0.0 <= config.P <= 1.0:
        raise ValueError("Параметр P должен быть в диапазоне [0, 1].")
    if config.X <= 0:
        raise ValueError("Параметр X должен быть больше нуля.")
    if config.Y <= 0:
        raise ValueError("Параметр Y должен быть больше нуля.")
    if config.N <= 0:
        raise ValueError("Параметр N должен быть больше нуля.")
    if config.N_GAMES <= 0:
        raise ValueError("Параметр N_GAMES должен быть больше нуля.")
    if config.BACKGROUND_TRAJECTORIES < 0:
        raise ValueError("Параметр BACKGROUND_TRAJECTORIES не может быть отрицательным.")
    if config.HIGHLIGHT_TRAJECTORIES < 0:
        raise ValueError("Параметр HIGHLIGHT_TRAJECTORIES не может быть отрицательным.")


def simulate_games():
    """Моделируем серию игр до разорения одного игрока или лимита шагов."""
    rng = np.random.default_rng(config.RANDOM_SEED)
    n_games = int(config.N_GAMES)
    max_steps = int(config.N)
    total_capital = int(config.X + config.Y)

    capital = np.full(n_games, int(config.X), dtype=int)
    finished = np.zeros(n_games, dtype=bool)
    outcomes = np.zeros(n_games, dtype=int)
    lengths = np.full(n_games, max_steps, dtype=int)
    trajectories = np.full((n_games, max_steps + 1), int(config.X), dtype=int)

    for step in range(1, max_steps + 1):
        active_idx = np.flatnonzero(~finished)
        if active_idx.size == 0:
            trajectories[:, step:] = capital[:, None]
            break

        wins = rng.random(active_idx.size) < config.P
        capital[active_idx] += np.where(wins, 1, -1)

        player_1_ruined = capital[active_idx] <= 0
        player_2_ruined = capital[active_idx] >= total_capital
        newly_finished = player_1_ruined | player_2_ruined

        finished_idx = active_idx[newly_finished]
        lengths[finished_idx] = step
        outcomes[active_idx[player_1_ruined]] = -1
        outcomes[active_idx[player_2_ruined]] = 1
        finished[finished_idx] = True

        trajectories[:, step] = capital

    return {
        "capital": capital,
        "finished": finished,
        "outcomes": outcomes,
        "lengths": lengths,
        "trajectories": trajectories,
        "total_capital": total_capital,
    }


def calculate_theoretical_probabilities(total_capital):
    """Считаем теоретические вероятности поглощения для неограниченной игры."""
    p = float(config.P)
    q = 1.0 - p
    start = float(config.X)
    total = float(total_capital)

    if p == 0.0:
        return 1.0, 0.0
    if p == 1.0:
        return 0.0, 1.0
    if np.isclose(p, q):
        player_2_ruin = start / total
    else:
        ratio = q / p
        player_2_ruin = (1.0 - ratio**start) / (1.0 - ratio**total)

    player_2_ruin = float(np.clip(player_2_ruin, 0.0, 1.0))
    player_1_ruin = 1.0 - player_2_ruin
    return player_1_ruin, player_2_ruin


def calculate_theoretical_duration(total_capital):
    """Считаем матожидание длительности игры без ограничения по шагам."""
    p = float(config.P)
    q = 1.0 - p
    start = float(config.X)
    total = float(total_capital)

    if p == 0.0:
        return start
    if p == 1.0:
        return total - start
    if np.isclose(p, q):
        return start * (total - start)

    ratio = q / p
    player_2_ruin = (1.0 - ratio**start) / (1.0 - ratio**total)
    return (start - total * player_2_ruin) / (q - p)


def compute_statistics(simulation):
    """Вычисляем статистику по результатам моделирования."""
    outcomes = simulation["outcomes"]
    lengths = simulation["lengths"]
    n_games = int(outcomes.size)
    total_capital = simulation["total_capital"]

    player_1_ruins = int(np.count_nonzero(outcomes == -1))
    player_2_ruins = int(np.count_nonzero(outcomes == 1))
    draws = int(np.count_nonzero(outcomes == 0))

    theory_player_1, theory_player_2 = calculate_theoretical_probabilities(total_capital)
    theory_duration = calculate_theoretical_duration(total_capital)

    return {
        "n_games": n_games,
        "max_steps": int(config.N),
        "total_capital": total_capital,
        "player_1_ruins": player_1_ruins,
        "player_2_ruins": player_2_ruins,
        "draws": draws,
        "p_player_1_ruin": player_1_ruins / n_games,
        "p_player_2_ruin": player_2_ruins / n_games,
        "p_draw": draws / n_games,
        "theory_player_1_ruin": theory_player_1,
        "theory_player_2_ruin": theory_player_2,
        "avg_length": float(np.mean(lengths)),
        "median_length": float(np.median(lengths)),
        "theory_avg_length": float(theory_duration),
    }


def build_output_basename(output_dir):
    """Формируем уникальное имя для файлов графиков."""
    base = config.PLOT_BASENAME
    if config.SAVE_UNIQUE_NAMES:
        timestamp = datetime.now().strftime(config.FILENAME_TIMESTAMP_FORMAT)
        base = f"{base}_{timestamp}"

    candidate = base
    index = 1
    while any((output_dir / f"{candidate}.{ext}").exists() for ext in config.SAVE_FORMATS):
        candidate = f"{base}_{index}"
        index += 1

    return candidate


def select_background_indices(n_games):
    """Выбираем траектории для фонового отображения."""
    n_show = min(int(config.BACKGROUND_TRAJECTORIES), n_games)
    if n_show == 0:
        return np.array([], dtype=int)
    return np.linspace(0, n_games - 1, n_show, dtype=int)


def select_highlight_indices(n_games):
    """Выбираем последние траектории для акцентного отображения."""
    n_show = min(int(config.HIGHLIGHT_TRAJECTORIES), n_games)
    if n_show == 0:
        return np.array([], dtype=int)
    return np.arange(n_games - n_show, n_games, dtype=int)


def plot_trajectory(ax, trajectory, length, **kwargs):
    """Строим одну траекторию до момента остановки игры."""
    steps = np.arange(length + 1)
    ax.plot(steps, trajectory[: length + 1], **kwargs)


def plot_results(simulation, stats):
    """Строим графики и сохраняем их в папку plots/."""
    output_dir = Path(__file__).resolve().parent / config.PLOT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    trajectories = simulation["trajectories"]
    lengths = simulation["lengths"]
    n_games = stats["n_games"]
    total_capital = stats["total_capital"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=config.FIGURE_SIZE)
    fig.suptitle(
        f"{config.PLOT_TITLE}\n"
        f"P={config.P}, X={config.X}, Y={config.Y}, N={config.N}, игр={config.N_GAMES}",
        fontsize=12,
    )

    for game_idx in select_background_indices(n_games):
        plot_trajectory(
            ax1,
            trajectories[game_idx],
            lengths[game_idx],
            color=config.TRAJECTORY_COLOR,
            alpha=config.TRAJECTORY_ALPHA,
            linewidth=0.8,
        )

    highlight_indices = select_highlight_indices(n_games)
    for color_index, game_idx in enumerate(highlight_indices):
        color = config.HIGHLIGHT_COLORS[color_index % len(config.HIGHLIGHT_COLORS)]
        plot_trajectory(
            ax1,
            trajectories[game_idx],
            lengths[game_idx],
            color=color,
            alpha=0.95,
            linewidth=2.0,
            label=f"Игра #{game_idx + 1}",
        )

    ax1.axhline(
        0,
        color=config.PLAYER_1_RUIN_COLOR,
        linestyle="--",
        linewidth=1.8,
        label="Разорение игрока 1",
    )
    ax1.axhline(
        total_capital,
        color=config.PLAYER_2_RUIN_COLOR,
        linestyle="--",
        linewidth=1.8,
        label="Разорение игрока 2",
    )
    ax1.axhline(
        config.X,
        color=config.START_COLOR,
        linestyle=":",
        linewidth=1.6,
        label=f"Старт игрока 1: {config.X}",
    )
    ax1.set_title("Траектории капитала первого игрока")
    ax1.set_xlabel("Номер шага")
    ax1.set_ylabel("Капитал первого игрока")
    ax1.set_xlim(0, config.N)
    ax1.set_ylim(-0.05 * total_capital, total_capital * 1.05)
    ax1.grid(True, alpha=config.GRID_ALPHA)
    ax1.legend(loc="best", fontsize=8)

    categories = ("Игрок 1\nразорён", "Игрок 2\nразорён", "Лимит\nшагов")
    empirical = np.array(
        [stats["p_player_1_ruin"], stats["p_player_2_ruin"], stats["p_draw"]]
    )
    theoretical = np.array(
        [stats["theory_player_1_ruin"], stats["theory_player_2_ruin"], 0.0]
    )
    x_axis = np.arange(len(categories))
    bar_width = 0.36

    bars_empirical = ax2.bar(
        x_axis - bar_width / 2,
        empirical,
        width=bar_width,
        color=[
            config.PLAYER_1_RUIN_COLOR,
            config.PLAYER_2_RUIN_COLOR,
            config.DRAW_COLOR,
        ],
        alpha=0.82,
        label="Моделирование",
    )
    bars_theoretical = ax2.bar(
        x_axis + bar_width / 2,
        theoretical,
        width=bar_width,
        color=config.THEORY_COLOR,
        alpha=0.42,
        label="Теория",
    )

    for bars in (bars_empirical, bars_theoretical):
        for bar in bars:
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.015,
                f"{height:.1%}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax2.set_title("Вероятности исходов")
    ax2.set_ylabel("Вероятность")
    ax2.set_xticks(x_axis)
    ax2.set_xticklabels(categories)
    ax2.set_ylim(0, min(1.15, max(1.0, float(np.max(empirical)) + 0.12)))
    ax2.grid(True, axis="y", alpha=config.GRID_ALPHA)
    ax2.legend(loc="upper right", fontsize=9)

    summary = (
        f"Средняя длина: {stats['avg_length']:.2f}\n"
        f"Медиана: {stats['median_length']:.2f}\n"
        f"E[T] теория: {stats['theory_avg_length']:.2f}"
    )
    ax2.text(
        0.02,
        0.98,
        summary,
        transform=ax2.transAxes,
        va="top",
        ha="left",
        fontsize=9,
        bbox=dict(facecolor="white", alpha=0.88, edgecolor="#d0d0d0"),
    )

    plt.tight_layout(rect=(0, 0, 1, 0.91))

    base_name = build_output_basename(output_dir)
    saved_paths = []
    for extension in config.SAVE_FORMATS:
        file_path = output_dir / f"{base_name}.{extension}"
        fig.savefig(file_path, dpi=config.PLOT_DPI, bbox_inches="tight")
        saved_paths.append(file_path)

    backend = plt.get_backend().lower()
    if config.SHOW_PLOT and "agg" not in backend:
        plt.show()
    else:
        plt.close(fig)

    return saved_paths


def print_report(stats, saved_paths):
    """Выводим результаты эксперимента в консоль."""
    print("=" * 64)
    print("РЕЗУЛЬТАТЫ ЗАДАЧИ О РАЗОРЕНИИ ИГРОКА")
    print("=" * 64)
    print(f"Вероятность выигрыша 1-го игрока (P): {config.P}")
    print(f"Начальный капитал 1-го игрока (X):    {config.X}")
    print(f"Начальный капитал 2-го игрока (Y):    {config.Y}")
    print(f"Суммарный капитал:                    {stats['total_capital']}")
    print(f"Максимум шагов в игре (N):            {stats['max_steps']}")
    print(f"Количество игр:                       {stats['n_games']}")
    print("-" * 64)
    print("МОДЕЛИРОВАНИЕ")
    print(
        "Разорение игрока 1:                  "
        f"{stats['player_1_ruins']} ({stats['p_player_1_ruin']:.4f})"
    )
    print(
        "Разорение игрока 2:                  "
        f"{stats['player_2_ruins']} ({stats['p_player_2_ruin']:.4f})"
    )
    print(f"Лимит шагов без разорения:            {stats['draws']} ({stats['p_draw']:.4f})")
    print(f"Средняя длина игры:                   {stats['avg_length']:.2f}")
    print(f"Медианная длина игры:                 {stats['median_length']:.2f}")
    print("-" * 64)
    print("ТЕОРИЯ ДЛЯ НЕОГРАНИЧЕННОЙ ИГРЫ")
    print(f"P(разорение игрока 1):                {stats['theory_player_1_ruin']:.8f}")
    print(f"P(разорение игрока 2):                {stats['theory_player_2_ruin']:.8f}")
    print(f"Матожидание длительности:             {stats['theory_avg_length']:.2f}")
    print("=" * 64)
    print("Файлы графика:")
    for path in saved_paths:
        print(f"- {path}")


def main():
    try:
        validate_config()
    except ValueError as exc:
        raise SystemExit(f"Ошибка в параметрах config.py: {exc}") from exc

    simulation = simulate_games()
    stats = compute_statistics(simulation)
    saved_paths = plot_results(simulation, stats)
    print_report(stats, saved_paths)


if __name__ == "__main__":
    main()
