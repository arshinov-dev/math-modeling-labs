from datetime import datetime
from functools import lru_cache
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import config


SAFE_NAMES = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "exp": np.exp,
    "log": np.log,
    "sqrt": np.sqrt,
    "abs": np.abs,
    "pi": np.pi,
    "e": np.e,
}

METHODS = (
    ("ЛПР", "Метод левых прямоугольников", "left_rectangles"),
    ("ППР", "Метод правых прямоугольников", "right_rectangles"),
    ("СПР", "Метод средних прямоугольников", "midpoint_rectangles"),
    ("ТР", "Метод трапеций", "trapezoids"),
    ("ММК", "Метод Монте-Карло для интеграла", "monte_carlo"),
    ("СИМП", "Метод Симпсона", "simpson"),
)


def compile_formula(formula):
    """Компилируем формулу от x из config.py в вызываемую функцию."""
    normalized = formula.replace("^", "**")
    try:
        code = compile(normalized, "<formula>", "eval")
    except SyntaxError as exc:
        raise ValueError(f"Некорректная формула '{formula}': {exc.msg}") from exc

    unknown_names = sorted(set(code.co_names) - (set(SAFE_NAMES) | {"x"}))
    if unknown_names:
        names = ", ".join(unknown_names)
        raise ValueError(f"Недопустимые имена в формуле '{formula}': {names}")

    def formula_function(value):
        scope = dict(SAFE_NAMES)
        scope["x"] = value
        result = eval(code, {"__builtins__": {}}, scope)
        value_array = np.asarray(value)
        if value_array.ndim > 0 and np.asarray(result).ndim == 0:
            return np.full(value_array.shape, result, dtype=float)
        return result

    return formula_function


FUNCTION = compile_formula(config.FUNCTION_FORMULA)


def f(x):
    """Вычисляем значение подынтегральной функции из config.py."""
    return FUNCTION(np.asarray(x, dtype=float))


def simpson_reference(subintervals):
    """Вычисляем эталонное приближение методом Симпсона."""
    x_points = np.linspace(config.A, config.B, subintervals + 1)
    y_points = f(x_points)
    dx = (config.B - config.A) / subintervals
    return float(
        dx
        / 3.0
        * (
            y_points[0]
            + y_points[-1]
            + 4.0 * np.sum(y_points[1:-1:2])
            + 2.0 * np.sum(y_points[2:-1:2])
        )
    )


@lru_cache(maxsize=1)
def true_area():
    """Возвращаем настроенное или автоматически уточнённое значение интеграла."""
    if config.REFERENCE_AREA is not None:
        return float(config.REFERENCE_AREA)

    subintervals = 2
    previous = simpson_reference(subintervals)
    for _ in range(int(config.REFERENCE_MAX_REFINEMENTS)):
        subintervals *= 2
        current = simpson_reference(subintervals)
        if abs(current - previous) < config.REFERENCE_EPSILON:
            return current
        previous = current
    return previous


def reference_area_description():
    """Описываем источник эталонного значения интеграла."""
    if config.REFERENCE_AREA is not None:
        return "задано в config.py"
    return f"уточнение Симпсона до Δ < {config.REFERENCE_EPSILON:.0e}"


def validate_config():
    """Проверяем корректность входных параметров."""
    if config.B <= config.A:
        raise ValueError("Параметр B должен быть больше A.")
    if config.REFERENCE_EPSILON <= 0:
        raise ValueError("Параметр REFERENCE_EPSILON должен быть больше нуля.")
    if int(config.REFERENCE_MAX_REFINEMENTS) <= 0:
        raise ValueError("Параметр REFERENCE_MAX_REFINEMENTS должен быть больше нуля.")
    if config.EPSILON <= 0:
        raise ValueError("Параметр EPSILON должен быть больше нуля.")
    if int(config.INITIAL_N) <= 0:
        raise ValueError("Параметр INITIAL_N должен быть больше нуля.")
    if int(config.N_MAX) < int(config.INITIAL_N):
        raise ValueError("Параметр N_MAX должен быть не меньше INITIAL_N.")
    if not config.N_VALUES:
        raise ValueError("Параметр N_VALUES не должен быть пустым.")
    for n in config.N_VALUES:
        if int(n) <= 0:
            raise ValueError("Все значения N_VALUES должны быть больше нуля.")
    if int(config.PLOT_N) <= 0:
        raise ValueError("Параметр PLOT_N должен быть больше нуля.")

    values = np.asarray(f(np.linspace(config.A, config.B, 64)), dtype=float)
    if not np.all(np.isfinite(values)):
        raise ValueError("FUNCTION_FORMULA должна быть конечной на всём отрезке [A; B].")


def make_rng(n):
    """Создаём генератор для метода Монте-Карло с устойчивым seed."""
    if config.RANDOM_SEED is None:
        return np.random.default_rng()
    return np.random.default_rng(int(config.RANDOM_SEED) + int(n))


def left_rectangles(n):
    """Вычисляем площадь методом левых прямоугольников."""
    dx = (config.B - config.A) / n
    x_left = config.A + np.arange(n) * dx
    return float(dx * np.sum(f(x_left)))


def right_rectangles(n):
    """Вычисляем площадь методом правых прямоугольников."""
    dx = (config.B - config.A) / n
    x_right = config.A + np.arange(1, n + 1) * dx
    return float(dx * np.sum(f(x_right)))


def midpoint_rectangles(n):
    """Вычисляем площадь методом средних прямоугольников."""
    dx = (config.B - config.A) / n
    x_mid = config.A + (np.arange(n) + 0.5) * dx
    return float(dx * np.sum(f(x_mid)))


def trapezoids(n):
    """Вычисляем площадь методом трапеций."""
    dx = (config.B - config.A) / n
    x_points = np.linspace(config.A, config.B, n + 1)
    y_points = f(x_points)
    return float(dx * (0.5 * y_points[0] + np.sum(y_points[1:-1]) + 0.5 * y_points[-1]))


def monte_carlo(n):
    """Вычисляем площадь методом Монте-Карло для интеграла."""
    rng = make_rng(n)
    x_random = rng.uniform(config.A, config.B, n)
    return float((config.B - config.A) * np.mean(f(x_random)))


def simpson(n):
    """Вычисляем площадь методом Симпсона для n параболических фигур."""
    subintervals = 2 * n
    dx = (config.B - config.A) / subintervals
    x_points = np.linspace(config.A, config.B, subintervals + 1)
    y_points = f(x_points)
    return float(
        dx
        / 3.0
        * (
            y_points[0]
            + y_points[-1]
            + 4.0 * np.sum(y_points[1:-1:2])
            + 2.0 * np.sum(y_points[2:-1:2])
        )
    )


METHOD_FUNCTIONS = {
    "left_rectangles": left_rectangles,
    "right_rectangles": right_rectangles,
    "midpoint_rectangles": midpoint_rectangles,
    "trapezoids": trapezoids,
    "monte_carlo": monte_carlo,
    "simpson": simpson,
}


def refine_method(method):
    """Уточняем результат метода до Δ < EPSILON или достижения N_MAX."""
    n = int(config.INITIAL_N)
    previous = method(n)
    delta = np.inf

    while n < int(config.N_MAX):
        n_next = min(n * 2, int(config.N_MAX))
        current = method(n_next)
        delta = abs(current - previous)
        if delta < config.EPSILON:
            return {
                "estimate": current,
                "n": n_next,
                "delta": delta,
                "status": "Выполнено условие Δ < EPSILON",
            }
        n = n_next
        previous = current

    return {
        "estimate": previous,
        "n": n,
        "delta": delta,
        "status": "Достигнут лимит N_MAX",
    }


def build_refinement_results():
    """Уточняем результат каждого метода по критериям останова из config.py."""
    return [
        {
            "short_name": short_name,
            "full_name": full_name,
            **refine_method(METHOD_FUNCTIONS[function_name]),
        }
        for short_name, full_name, function_name in METHODS
    ]


def calculate_errors(estimate, exact_area):
    """Считаем абсолютную и относительную погрешности."""
    absolute_error = abs(estimate - exact_area)
    relative_error = absolute_error / abs(exact_area) * 100.0 if exact_area != 0 else np.nan
    return absolute_error, relative_error


def build_results():
    """Строим таблицу результатов для всех методов и n."""
    exact_area = true_area()
    results = []
    for short_name, full_name, function_name in METHODS:
        row = {
            "short_name": short_name,
            "full_name": full_name,
            "values": {},
        }
        method = METHOD_FUNCTIONS[function_name]
        for n in config.N_VALUES:
            estimate = method(int(n))
            absolute_error, relative_error = calculate_errors(estimate, exact_area)
            row["values"][int(n)] = {
                "estimate": estimate,
                "absolute_error": absolute_error,
                "relative_error": relative_error,
            }
        results.append(row)
    return results


def format_result_cell(value):
    """Форматируем одну ячейку таблицы как в примере primer.xlsx."""
    return (
        f"Ŝ={value['estimate']:.8f}; "
        f"Δ={value['absolute_error']:.8f}; "
        f"δ={value['relative_error']:.4f}%"
    )


def format_results_table(results):
    """Формируем консольную таблицу результатов."""
    headers = ["Методы"] + [f"n={int(n)}" for n in config.N_VALUES]
    rows = []
    for row in results:
        rows.append(
            [row["short_name"]]
            + [format_result_cell(row["values"][int(n)]) for n in config.N_VALUES]
        )

    widths = [
        max(len(headers[col]), *(len(row[col]) for row in rows))
        for col in range(len(headers))
    ]
    border = "+-" + "-+-".join("-" * width for width in widths) + "-+"

    lines = [border]
    lines.append(
        "| "
        + " | ".join(headers[col].ljust(widths[col]) for col in range(len(headers)))
        + " |"
    )
    lines.append(border)
    for row in rows:
        lines.append(
            "| "
            + " | ".join(row[col].ljust(widths[col]) for col in range(len(row)))
            + " |"
        )
    lines.append(border)
    return "\n".join(lines)


def find_best_results(results):
    """Ищем методы с минимальной абсолютной погрешностью."""
    best_by_n = {}
    overall_best = None

    for n in config.N_VALUES:
        n = int(n)
        best_row = min(
            results,
            key=lambda row: row["values"][n]["absolute_error"],
        )
        best_by_n[n] = {
            "short_name": best_row["short_name"],
            "full_name": best_row["full_name"],
            **best_row["values"][n],
        }

    for row in results:
        for n, value in row["values"].items():
            candidate = {
                "n": n,
                "short_name": row["short_name"],
                "full_name": row["full_name"],
                **value,
            }
            if (
                overall_best is None
                or candidate["absolute_error"] < overall_best["absolute_error"]
            ):
                overall_best = candidate

    return best_by_n, overall_best


def format_best_result(value):
    """Форматируем строку с лучшим методом."""
    return (
        f"{value['short_name']} ({value['full_name']}): "
        f"Ŝ={value['estimate']:.10f}; "
        f"Δ={value['absolute_error']:.10f}; "
        f"δ={value['relative_error']:.6f}%"
    )


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


def plot_function(ax):
    """Строим график функции."""
    x_line = np.linspace(config.A, config.B, config.CURVE_SAMPLES)
    y_line = f(x_line)
    ax.plot(
        x_line,
        y_line,
        color=config.FUNCTION_COLOR,
        linewidth=2.2,
        label=config.FUNCTION_LABEL or f"f(x) = {config.FUNCTION_FORMULA}",
        zorder=3,
    )


def setup_method_axis(ax, title):
    """Настраиваем общие параметры осей графиков."""
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_xlim(config.A, config.B)
    y_values = np.asarray(f(np.linspace(config.A, config.B, 200)), dtype=float)
    y_min = min(0.0, float(np.min(y_values)))
    y_max = max(0.0, float(np.max(y_values)))
    padding = max((y_max - y_min) * 0.12, 1e-9)
    ax.set_ylim(y_min - padding, y_max + padding)
    ax.grid(True, alpha=config.GRID_ALPHA)


def plot_left_rectangles(ax, n):
    """Показываем метод левых прямоугольников."""
    dx = (config.B - config.A) / n
    x_left = config.A + np.arange(n) * dx
    ax.bar(
        x_left,
        f(x_left),
        width=dx,
        align="edge",
        color=config.FIGURE_COLOR,
        edgecolor=config.FIGURE_EDGE_COLOR,
        alpha=0.35,
        linewidth=1.0,
        label="Левые прямоугольники",
    )


def plot_right_rectangles(ax, n):
    """Показываем метод правых прямоугольников."""
    dx = (config.B - config.A) / n
    x_right = config.A + np.arange(1, n + 1) * dx
    ax.bar(
        x_right - dx,
        f(x_right),
        width=dx,
        align="edge",
        color=config.FIGURE_COLOR,
        edgecolor=config.FIGURE_EDGE_COLOR,
        alpha=0.35,
        linewidth=1.0,
        label="Правые прямоугольники",
    )


def plot_midpoint_rectangles(ax, n):
    """Показываем метод средних прямоугольников."""
    dx = (config.B - config.A) / n
    x_left = config.A + np.arange(n) * dx
    x_mid = x_left + 0.5 * dx
    ax.bar(
        x_left,
        f(x_mid),
        width=dx,
        align="edge",
        color=config.FIGURE_COLOR,
        edgecolor=config.FIGURE_EDGE_COLOR,
        alpha=0.35,
        linewidth=1.0,
        label="Средние прямоугольники",
    )
    ax.scatter(x_mid, f(x_mid), s=18, color=config.FIGURE_EDGE_COLOR, zorder=4)


def plot_trapezoids(ax, n):
    """Показываем метод трапеций."""
    x_points = np.linspace(config.A, config.B, n + 1)
    y_points = f(x_points)
    for i in range(n):
        polygon_x = [x_points[i], x_points[i], x_points[i + 1], x_points[i + 1]]
        polygon_y = [0, y_points[i], y_points[i + 1], 0]
        ax.fill(
            polygon_x,
            polygon_y,
            color=config.FIGURE_COLOR,
            edgecolor=config.FIGURE_EDGE_COLOR,
            alpha=0.32,
            linewidth=1.0,
        )
    ax.plot(x_points, y_points, color=config.FIGURE_EDGE_COLOR, linewidth=1.2, label="Трапеции")


def plot_monte_carlo(ax, n):
    """Показываем метод Монте-Карло для интеграла."""
    rng = make_rng(n)
    x_random = np.sort(rng.uniform(config.A, config.B, n))
    y_random = f(x_random)
    width = (config.B - config.A) / n
    ax.bar(
        x_random,
        y_random,
        width=width * 0.85,
        align="center",
        color=config.MC_COLOR,
        edgecolor=config.FIGURE_EDGE_COLOR,
        alpha=0.32,
        linewidth=0.9,
        label="Случайные прямоугольники",
    )
    ax.scatter(x_random, y_random, s=20, color=config.MC_COLOR, zorder=4)


def plot_simpson(ax, n):
    """Показываем n параболических фигур метода Симпсона."""
    subintervals = 2 * n
    x_points = np.linspace(config.A, config.B, subintervals + 1)
    y_points = f(x_points)
    for figure_index in range(n):
        i = 2 * figure_index
        local_x = x_points[i : i + 3]
        local_y = y_points[i : i + 3]
        coefficients = np.polyfit(local_x, local_y, deg=2)
        x_dense = np.linspace(local_x[0], local_x[-1], 80)
        y_dense = np.polyval(coefficients, x_dense)
        ax.fill_between(
            x_dense,
            0,
            y_dense,
            color=config.SIMPSON_COLOR,
            alpha=0.28,
            edgecolor=config.FIGURE_EDGE_COLOR,
            linewidth=0.8,
        )
        ax.plot(x_dense, y_dense, color=config.SIMPSON_COLOR, linewidth=1.2)
        ax.vlines(
            [local_x[0], local_x[-1]],
            0,
            [local_y[0], local_y[-1]],
            color=config.FIGURE_EDGE_COLOR,
            alpha=0.55,
            linewidth=0.8,
        )
    ax.scatter(x_points, y_points, s=16, color=config.FIGURE_EDGE_COLOR, zorder=4, label="Узлы")


PLOTTERS = {
    "left_rectangles": plot_left_rectangles,
    "right_rectangles": plot_right_rectangles,
    "midpoint_rectangles": plot_midpoint_rectangles,
    "trapezoids": plot_trapezoids,
    "monte_carlo": plot_monte_carlo,
    "simpson": plot_simpson,
}


def plot_results():
    """Строим график функции и наложение фигур для каждого метода."""
    output_dir = Path(__file__).resolve().parent / config.PLOT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    n = int(config.PLOT_N)
    fig, axes = plt.subplots(3, 2, figsize=config.FIGURE_SIZE)
    axes_flat = axes.ravel()
    exact_area = true_area()

    fig.suptitle(
        f"{config.PLOT_TITLE}\n"
        f"f(x)={config.FUNCTION_FORMULA}, Sэт≈{exact_area:.8f}, n={n}",
        fontsize=13,
    )

    for ax, (short_name, full_name, function_name) in zip(axes_flat, METHODS):
        PLOTTERS[function_name](ax, n)
        plot_function(ax)
        estimate = METHOD_FUNCTIONS[function_name](n)
        absolute_error, relative_error = calculate_errors(estimate, exact_area)
        setup_method_axis(
            ax,
            f"{short_name}: {full_name}\n"
            f"Ŝ={estimate:.6f}; Δ={absolute_error:.6f}; δ={relative_error:.3f}%",
        )
        ax.legend(loc="best", fontsize=8)

    plt.tight_layout(rect=(0, 0, 1, 0.94))

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


def print_report(results, refinement_results, saved_paths):
    """Выводим эталонное значение и таблицу результатов."""
    exact_value = true_area()

    print("=" * 76)
    print("ЛАБОРАТОРНАЯ РАБОТА №4")
    print("Вычисление площади функции различными методами")
    print("=" * 76)
    print(f"f(x) = {config.FUNCTION_FORMULA}")
    print(f"Отрезок интегрирования: [{config.A}, {config.B}]")
    print(f"Sэт = {exact_value:.10f} ({reference_area_description()})")
    print(f"Критерии останова уточнения: Δ < {config.EPSILON:.0e} или N_MAX = {int(config.N_MAX)}")
    print("-" * 76)
    print(format_results_table(results))
    print("-" * 76)
    best_by_n, overall_best = find_best_results(results)
    print("ЛУЧШИЙ МЕТОД ПО МИНИМАЛЬНОЙ АБСОЛЮТНОЙ ПОГРЕШНОСТИ")
    for n in config.N_VALUES:
        n = int(n)
        print(f"n={n}: {format_best_result(best_by_n[n])}")
    print("Лучший результат по всей таблице:")
    print(f"n={overall_best['n']}: {format_best_result(overall_best)}")
    print("-" * 76)
    print("АВТОМАТИЧЕСКОЕ УТОЧНЕНИЕ ПО КРИТЕРИЯМ ОСТАНОВА")
    for value in refinement_results:
        print(
            f"{value['short_name']}: Ŝ={value['estimate']:.10f}; "
            f"n={value['n']}; Δ={value['delta']:.3e}; {value['status']}"
        )
    print("=" * 76)
    print("Файлы графика:")
    for path in saved_paths:
        print(f"- {path}")


def main():
    try:
        validate_config()
    except ValueError as exc:
        raise SystemExit(f"Ошибка в параметрах config.py: {exc}") from exc

    results = build_results()
    refinement_results = build_refinement_results()
    saved_paths = plot_results()
    print_report(results, refinement_results, saved_paths)


if __name__ == "__main__":
    main()
