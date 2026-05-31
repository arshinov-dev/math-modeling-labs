from datetime import datetime
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

import config

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import LAB5_CONFIG as root_config
from common import compile_formula, get_lab5_reference_root


FUNCTION = compile_formula(root_config.FUNCTION_FORMULA)


def f(x):
    """Вычисляем значение функции из конфигурации лабораторной №5."""
    return FUNCTION(np.asarray(x, dtype=float))


def exact_root():
    """Возвращаем контрольный корень из конфигурации лабораторной №5."""
    return get_lab5_reference_root(f)


def validate_config():
    """Проверяем корректность входных параметров."""
    if root_config.B <= root_config.A:
        raise ValueError("Параметр B должен быть больше A.")
    if root_config.EPSILON <= 0:
        raise ValueError("Параметр EPSILON должен быть больше нуля.")
    if int(root_config.N_MAX) <= 0:
        raise ValueError("Параметр N_MAX должен быть больше нуля.")
    if int(config.CURVE_SAMPLES) < 2:
        raise ValueError("Параметр CURVE_SAMPLES должен быть не меньше 2.")
    if int(config.MAX_CHORDS_SHOW) < 0:
        raise ValueError("Параметр MAX_CHORDS_SHOW не может быть отрицательным.")

    fa = float(f(root_config.A))
    fb = float(f(root_config.B))
    if fa == 0.0 or fb == 0.0:
        return
    if fa * fb > 0:
        raise ValueError("На концах отрезка функция должна иметь разные знаки.")


def chord_method():
    """Находим корень методом хорд с остановом по N_MAX или Δx < EPSILON."""
    a = float(root_config.A)
    b = float(root_config.B)
    fa = float(f(a))
    fb = float(f(b))
    history = []

    if fa == 0.0:
        return {
            "root": a,
            "iterations": 0,
            "last_delta": 0.0,
            "status": "Левая граница отрезка является корнем",
            "history": history,
        }
    if fb == 0.0:
        return {
            "root": b,
            "iterations": 0,
            "last_delta": 0.0,
            "status": "Правая граница отрезка является корнем",
            "history": history,
        }

    previous_x = None
    x_current = None
    last_delta = np.inf

    for iteration in range(1, int(root_config.N_MAX) + 1):
        denominator = fb - fa
        if denominator == 0.0:
            raise ValueError("Невозможно построить хорду: f(a) и f(b) совпали.")

        x_current = a - fa * (b - a) / denominator
        fx = float(f(x_current))
        last_delta = np.inf if previous_x is None else abs(x_current - previous_x)

        history.append((iteration, a, b, x_current, fx, last_delta))

        if fx == 0.0:
            return {
                "root": x_current,
                "iterations": iteration,
                "last_delta": 0.0,
                "status": "Найдено точное пересечение f(x)=0",
                "history": history,
            }

        if last_delta < root_config.EPSILON:
            return {
                "root": x_current,
                "iterations": iteration,
                "last_delta": last_delta,
                "status": "Выполнено условие Δx < ε",
                "history": history,
            }

        if fa * fx < 0:
            b = x_current
            fb = fx
        else:
            a = x_current
            fa = fx

        previous_x = x_current

    return {
        "root": x_current,
        "iterations": int(root_config.N_MAX),
        "last_delta": last_delta,
        "status": "Достигнут лимит N_MAX",
        "history": history,
    }


def calculate_errors(root):
    """Считаем абсолютную погрешность относительно точного корня."""
    exact = exact_root()
    absolute_error = abs(root - exact)
    return exact, absolute_error


def build_output_basename(output_dir, base_name):
    """Формируем уникальное имя для файлов графиков."""
    base = base_name
    if config.SAVE_UNIQUE_NAMES:
        timestamp = datetime.now().strftime(config.FILENAME_TIMESTAMP_FORMAT)
        base = f"{base}_{timestamp}"

    candidate = base
    index = 1
    while any((output_dir / f"{candidate}.{ext}").exists() for ext in config.SAVE_FORMATS):
        candidate = f"{base}_{index}"
        index += 1

    return candidate


def save_figure(fig, output_dir, base_name):
    """Сохраняем фигуру в настроенных форматах."""
    output_dir.mkdir(parents=True, exist_ok=True)
    file_base = build_output_basename(output_dir, base_name)
    saved_paths = []
    for extension in config.SAVE_FORMATS:
        file_path = output_dir / f"{file_base}.{extension}"
        fig.savefig(file_path, dpi=config.PLOT_DPI, bbox_inches="tight")
        saved_paths.append(file_path)
    return saved_paths


def plot_base_function(ax, exact, root=None, show_interval=True):
    """Рисуем функцию, ось Ox, исходный отрезок и корень."""
    x_margin = (root_config.B - root_config.A) * 0.08
    x_line = np.linspace(root_config.A - x_margin, root_config.B + x_margin, int(config.CURVE_SAMPLES))
    y_line = f(x_line)

    ax.plot(
        x_line,
        y_line,
        color=config.FUNCTION_COLOR,
        linewidth=2.2,
        label=root_config.FUNCTION_LABEL or f"f(x) = {root_config.FUNCTION_FORMULA}",
        zorder=3,
    )
    ax.axhline(0, color="#000000", linewidth=1.0)
    if show_interval:
        ax.axvspan(
            root_config.A,
            root_config.B,
            color=config.INTERVAL_COLOR,
            alpha=0.08,
            label=f"Исходный отрезок [{root_config.A:g}; {root_config.B:g}]",
        )
    ax.axvline(
        exact,
        color=config.EXACT_ROOT_COLOR,
        linestyle=":",
        linewidth=1.8,
        label=f"Точный корень {exact:.6f}",
    )
    if root is not None:
        ax.scatter(
            [root],
            [float(f(root))],
            color=config.ROOT_COLOR,
            s=80,
            marker="o",
            label=f"Найденный корень {root:.6f}",
            zorder=6,
        )
    return x_line, y_line


def plot_overview(result, exact):
    """Строим общий график без лишних учебных обозначений."""
    fig, ax = plt.subplots(figsize=config.OVERVIEW_FIGURE_SIZE)
    x_margin = (root_config.B - root_config.A) * 0.08
    root = result["root"]
    _, y_line = plot_base_function(ax, exact, root=root, show_interval=True)

    y_finite = y_line[np.isfinite(y_line)]
    y_padding = (float(np.max(y_finite)) - float(np.min(y_finite))) * 0.08
    ax.set_xlim(root_config.A - x_margin, root_config.B + x_margin)
    ax.set_ylim(float(np.min(y_finite)) - y_padding, float(np.max(y_finite)) + y_padding)
    ax.set_title("Общий график функции")
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.grid(True, alpha=config.GRID_ALPHA)
    ax.legend(loc="best", fontsize=9)
    fig.suptitle(config.PLOT_TITLE, fontsize=12)
    plt.tight_layout(rect=(0, 0, 1, 0.94))
    return fig


def plot_zoom_construction(result, exact):
    """Строим увеличенный график, где видна геометрия метода хорд."""
    fig, ax = plt.subplots(figsize=config.ZOOM_FIGURE_SIZE)
    root = result["root"]
    plot_base_function(ax, exact, root=root, show_interval=False)

    visible_history = result["history"][: int(config.MAX_CHORDS_SHOW)]
    for index, (iteration, a, b, x_current, fx, _) in enumerate(visible_history):
        chord_x = np.array([a, b])
        chord_y = f(chord_x)
        label = "Хорды" if index == 0 else None
        ax.plot(
            chord_x,
            chord_y,
            color=config.CHORD_COLOR,
            alpha=0.42 + 0.1 * min(index, 3),
            linewidth=1.8,
            label=label,
            zorder=2,
        )
        projection_label = r"$\hat{x}_n \rightarrow f(\hat{x}_n)$" if index == 0 else None
        ax.annotate(
            "",
            xy=(x_current, fx),
            xytext=(x_current, 0),
            arrowprops=dict(
                arrowstyle="->",
                color=config.PROJECTION_COLOR,
                linestyle="--",
                linewidth=1.6,
                alpha=0.86,
            ),
            zorder=5,
        )
        ax.plot(
            [x_current, x_current],
            [0, fx],
            color=config.PROJECTION_COLOR,
            linestyle="--",
            linewidth=1.2,
            alpha=0.5,
            label=projection_label,
            zorder=4,
        )
        ax.scatter(
            [x_current],
            [0],
            color=config.CHORD_COLOR,
            s=54,
            alpha=0.86,
            edgecolor="white",
            linewidth=0.8,
            label=r"$\hat{x}_n$ на $Ox$" if index == 0 else None,
            zorder=4,
        )
        ax.scatter(
            [x_current],
            [fx],
            color=config.ITERATION_POINT_COLOR,
            s=62,
            edgecolor="white",
            linewidth=0.8,
            label=r"$(\hat{x}_n, f(\hat{x}_n))$" if index == 0 else None,
            zorder=6,
        )
        ax.annotate(
            rf"$\hat{{x}}_{iteration}$",
            xy=(x_current, 0),
            xytext=(8, -22 if fx >= 0 else 10),
            textcoords="offset points",
            fontsize=10,
            color=config.CHORD_COLOR,
        )

    ax.set_xlim(1.05, 1.58)
    ax.set_ylim(-0.45, 0.68)
    ax.set_title("Увеличенное построение хорд")
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.grid(True, alpha=config.GRID_ALPHA)
    ax.legend(loc="best", fontsize=9)
    fig.suptitle("Метод хорд: как строится следующее приближение", fontsize=12)
    plt.tight_layout(rect=(0, 0, 1, 0.94))
    return fig


def plot_results(result, exact):
    """Строим общий и увеличенный графики и сохраняем их в папку plots/."""
    output_dir = Path(__file__).resolve().parent / config.PLOT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    overview_fig = plot_overview(result, exact)
    zoom_fig = plot_zoom_construction(result, exact)
    saved_paths = [
        ("Общий график", save_figure(overview_fig, output_dir, f"{config.PLOT_BASENAME}_overview")),
        ("Увеличенное построение", save_figure(zoom_fig, output_dir, f"{config.PLOT_BASENAME}_zoom")),
    ]
    backend = plt.get_backend().lower()
    if config.SHOW_PLOT and "agg" not in backend:
        plt.show()
    else:
        plt.close(overview_fig)
        plt.close(zoom_fig)

    return saved_paths


def print_report(result, exact, absolute_error, saved_paths):
    """Выводим краткий итоговый отчёт в консоль."""
    root = result["root"]

    print("=" * 64)
    print("ЛАБОРАТОРНАЯ РАБОТА №6: МЕТОД ХОРД")
    print("=" * 64)
    print(f"Функция из lab-05: f(x) = {root_config.FUNCTION_FORMULA}")
    print(f"Отрезок: [{root_config.A:g}; {root_config.B:g}]")
    print(f"Условия останова: Δx < {root_config.EPSILON:.0e} или N_MAX = {int(root_config.N_MAX)}")
    print("-" * 64)
    print(f"Найденный корень x_hat: {root:.15f}")
    print(f"Точный корень x*:       {exact:.15f}")
    print(f"|x_hat - x*|:           {absolute_error:.3e}")
    print(f"f(x_hat):               {float(f(root)):.3e}")
    print(f"Итераций:               {result['iterations']}")
    print(f"Остановка:              {result['status']} (Δx = {result['last_delta']:.3e})")
    print("-" * 64)
    print("Графики:")
    for label, paths in saved_paths:
        print(label)
        for path in paths:
            print(f"- {path}")


def main():
    try:
        validate_config()
        result = chord_method()
    except ValueError as exc:
        raise SystemExit(f"Ошибка в параметрах config.py: {exc}") from exc

    exact, absolute_error = calculate_errors(result["root"])
    saved_paths = plot_results(result, exact)
    print_report(result, exact, absolute_error, saved_paths)


if __name__ == "__main__":
    main()
