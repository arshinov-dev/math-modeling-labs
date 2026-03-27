from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import config


def validate_config():
    """Проверяем корректность входных параметров."""
    if config.N <= 0:
        raise ValueError("Параметр N должен быть больше нуля.")
    if config.L <= 0:
        raise ValueError("Параметр L должен быть больше нуля.")
    if config.A <= 0:
        raise ValueError("Параметр A должен быть больше нуля.")
    if config.L > config.A:
        raise ValueError(
            "Формула оценки π корректна только при L <= A."
        )
    if config.BOARD_WIDTH <= 0:
        raise ValueError("Параметр BOARD_WIDTH должен быть больше нуля.")
    if config.NUM_STRIPS <= 0:
        raise ValueError("Параметр NUM_STRIPS должен быть больше нуля.")
    if config.MAX_NEEDLES_SHOW < 0:
        raise ValueError("Параметр MAX_NEEDLES_SHOW не может быть отрицательным.")


def get_board_bounds():
    """Вычисляем границы области по вертикали."""
    y_min = float(config.Y_MIN)
    y_max = y_min + float(config.A) * int(config.NUM_STRIPS)
    if y_max <= y_min:
        raise ValueError("Неверные границы области: y_max должен быть больше y_min.")
    return y_min, y_max


def simulate_throws(y_min, y_max):
    """Генерируем броски иглы и определяем пересечения с линиями."""
    rng = np.random.default_rng(config.RANDOM_SEED)
    n = int(config.N)

    phi = rng.uniform(0.0, np.pi, size=n)
    y_center = rng.uniform(y_min, y_max, size=n)

    offset = np.mod(y_center - y_min, config.A)
    distance_to_line = np.minimum(offset, config.A - offset)
    projection = 0.5 * config.L * np.sin(phi)

    if config.INCLUDE_BORDER:
        crosses = distance_to_line <= projection
    else:
        crosses = distance_to_line < projection

    n_show = min(n, int(config.MAX_NEEDLES_SHOW))
    if n_show > 0:
        x_center = rng.uniform(0.0, config.BOARD_WIDTH, size=n_show)
        phi_show = phi[:n_show]
        y_show = y_center[:n_show]

        dx = 0.5 * config.L * np.cos(phi_show)
        dy = 0.5 * config.L * np.sin(phi_show)

        x0 = x_center - dx
        x1 = x_center + dx
        y0 = y_show - dy
        y1 = y_show + dy
        show_crosses = crosses[:n_show]
    else:
        x0 = np.array([])
        x1 = np.array([])
        y0 = np.array([])
        y1 = np.array([])
        show_crosses = np.array([], dtype=bool)

    return crosses, (x0, x1, y0, y1, show_crosses)


def compute_statistics(crosses):
    """Вычисляем приближение π и ошибки."""
    n = int(crosses.size)
    m = int(np.count_nonzero(crosses))

    if m > 0:
        pi_estimate = (2.0 * config.L * n) / (config.A * m)
    else:
        pi_estimate = np.nan

    pi_true = float(np.pi)
    abs_error = float(abs(pi_true - pi_estimate)) if np.isfinite(pi_estimate) else np.nan
    rel_error = (
        float(abs_error / pi_true * 100.0) if np.isfinite(abs_error) else np.nan
    )

    hit_probability = m / n
    theoretical_probability = (2.0 * config.L) / (
        np.pi * config.A
    )

    return {
        "n": n,
        "m": m,
        "pi_estimate": pi_estimate,
        "pi_true": pi_true,
        "abs_error": abs_error,
        "rel_error": rel_error,
        "hit_probability": hit_probability,
        "theoretical_probability": theoretical_probability,
    }


def build_convergence_series(crosses):
    """Строим ряд сходимости значения π."""
    n = int(crosses.size)
    if n == 0:
        return np.array([]), np.array([])

    m_cumulative = np.cumsum(crosses.astype(int))
    throws = np.arange(1, n + 1, dtype=float)
    pi_cumulative = np.full_like(throws, np.nan, dtype=float)
    np.divide(
        2.0 * config.L * throws,
        config.A * m_cumulative,
        out=pi_cumulative,
        where=m_cumulative > 0,
    )

    step = max(1, int(config.CONVERGENCE_EVERY))
    return throws[step - 1 :: step], pi_cumulative[step - 1 :: step]


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


def plot_results(needles, crosses, stats, bounds):
    """Строим графики и сохраняем их в папку plots/."""
    x0, x1, y0, y1, show_crosses = needles
    y_min, y_max = bounds

    output_dir = Path(__file__).resolve().parent / config.PLOT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=config.FIGURE_SIZE)

    pi_text = (
        f"{stats['pi_estimate']:.6f}" if np.isfinite(stats["pi_estimate"]) else "—"
    )
    pi_true_text = f"{stats['pi_true']:.6f}"
    abs_error_text = (
        f"{stats['abs_error']:.6f}" if np.isfinite(stats["abs_error"]) else "—"
    )
    rel_error_text = (
        f"{stats['rel_error']:.4f}%" if np.isfinite(stats["rel_error"]) else "—"
    )
    fig.suptitle(
        f"{config.PLOT_TITLE}\nN={stats['n']}, M={stats['m']}, π≈{pi_text}",
        fontsize=12,
    )

    ax1.set_title(f"Броски иглы (первые {len(show_crosses)} из {stats['n']})")
    ax1.set_xlabel("X координата")
    ax1.set_ylabel("Y координата")
    ax1.set_xlim(0, config.BOARD_WIDTH)
    ax1.set_ylim(y_min, y_max)
    ax1.set_aspect("equal")

    for y in np.arange(y_min, y_max + config.A * 0.5, config.A):
        ax1.axhline(
            y=y,
            color=config.LINE_COLOR,
            linestyle="-",
            linewidth=1.0,
            alpha=config.LINE_ALPHA,
        )

    hit_label_added = False
    miss_label_added = False
    for i in range(len(show_crosses)):
        is_hit = bool(show_crosses[i])
        if is_hit:
            color = config.HIT_COLOR
            width = config.HIT_WIDTH
            label = "Пересечение" if not hit_label_added else None
            hit_label_added = True
        else:
            color = config.MISS_COLOR
            width = config.MISS_WIDTH
            label = "Нет пересечения" if not miss_label_added else None
            miss_label_added = True

        ax1.plot(
            [x0[i], x1[i]],
            [y0[i], y1[i]],
            color=color,
            linewidth=width,
            alpha=config.NEEDLE_ALPHA,
            label=label,
        )

    ax1.grid(True, alpha=0.3)
    if hit_label_added or miss_label_added:
        ax1.legend(loc="upper right")

    ax2.set_title("Сходимость метода Бюффона к значению π")
    ax2.set_xlabel("Количество бросков")
    ax2.set_ylabel("Приближённое значение π")

    throws, pi_series = build_convergence_series(crosses)
    if pi_series.size:
        ax2.plot(
            throws,
            pi_series,
            color=config.CONVERGENCE_COLOR,
            linewidth=config.CONVERGENCE_WIDTH,
            alpha=config.CONVERGENCE_ALPHA,
            label="Приближение π",
        )

    ax2.axhline(
        y=stats["pi_true"],
        color=config.TRUE_PI_COLOR,
        linestyle="--",
        linewidth=config.TRUE_PI_WIDTH,
        label="Истинное π",
    )
    ax2.text(
        0.02,
        0.98,
        "Сравнение π:\n"
        f"π≈{pi_text}\n"
        f"π={pi_true_text}\n"
        f"|Δ|={abs_error_text}\n"
        f"δ={rel_error_text}",
        transform=ax2.transAxes,
        va="top",
        ha="left",
        fontsize=9.5,
        bbox=dict(facecolor="white", alpha=0.85, edgecolor="#d0d0d0"),
    )
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc="best")
    ax2.set_xlim(0, stats["n"])

    if pi_series.size and np.isfinite(pi_series).any():
        min_val = np.nanmin(pi_series)
        max_val = np.nanmax(pi_series)
        padding = (max_val - min_val) * 0.08 if max_val > min_val else 0.2
        ax2.set_ylim(min_val - padding, max_val + padding)

    plt.tight_layout(rect=(0, 0, 1, 0.93))

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


def print_report(stats, saved_paths, bounds):
    """Выводим результаты эксперимента в консоль."""
    y_min, y_max = bounds
    print("=" * 60)
    print("РЕЗУЛЬТАТЫ МЕТОДА БЮФФОНА")
    print("=" * 60)
    print(f"Длина иглы (l):               {config.L}")
    print(f"Расстояние между линиями (a): {config.A}")
    print(f"Количество бросков (N):       {stats['n']}")
    print(f"Число пересечений (M):        {stats['m']}")
    print("-" * 60)
    print("СРАВНЕНИЕ С π")
    if np.isfinite(stats["pi_estimate"]):
        print(f"Приближённое значение π:      {stats['pi_estimate']:.10f}")
    else:
        print("Приближённое значение π:      —")
    print(f"Истинное значение π:          {stats['pi_true']:.10f}")
    if np.isfinite(stats["abs_error"]):
        print(f"Абсолютная погрешность:       {stats['abs_error']:.10f}")
        print(f"Относительная погрешность:    {stats['rel_error']:.4f}%")
    else:
        print("Абсолютная погрешность:       —")
        print("Относительная погрешность:    —")
    print("=" * 60)
    print(f"Диапазон по Y: [{y_min}, {y_max}]")
    print("Дополнительная статистика")
    print(f"P(пересечение) = M/N:         {stats['hit_probability']:.6f}")
    print(
        f"Теоретическая вероятность:    {stats['theoretical_probability']:.6f}"
    )
    print(f"Коэффициент l/a:              {config.L / config.A:.6f}")
    print("Файлы графика:")
    for path in saved_paths:
        print(f"- {path}")


def main():
    try:
        validate_config()
        bounds = get_board_bounds()
    except ValueError as exc:
        raise SystemExit(f"Ошибка в параметрах config.py: {exc}") from exc

    crosses, needles = simulate_throws(*bounds)
    stats = compute_statistics(crosses)
    saved_paths = plot_results(needles, crosses, stats, bounds)
    print_report(stats, saved_paths, bounds)


if __name__ == "__main__":
    main()
