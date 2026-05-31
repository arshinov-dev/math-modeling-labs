from datetime import datetime
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
DERIVATIVE = compile_formula(config.DERIVATIVE_FORMULA)


def f(x):
    """Вычисляем значение функции варианта из config.py."""
    return FUNCTION(np.asarray(x, dtype=float))


def f_prime(x):
    """Вычисляем производную функции варианта из config.py."""
    return DERIVATIVE(np.asarray(x, dtype=float))


def exact_root():
    """Возвращаем настроенный или автоматически найденный контрольный корень."""
    if config.REFERENCE_ROOT is not None:
        return float(config.REFERENCE_ROOT)

    a = float(config.A)
    b = float(config.B)
    fa = float(f(a))
    fb = float(f(b))
    if fa == 0.0:
        return a
    if fb == 0.0:
        return b
    if fa * fb > 0:
        raise ValueError("Для контрольной бисекции нужна смена знака на [A; B].")

    for _ in range(int(config.REFERENCE_N_MAX)):
        midpoint = (a + b) / 2.0
        f_midpoint = float(f(midpoint))
        if abs(f_midpoint) < config.REFERENCE_EPSILON or abs(b - a) < config.REFERENCE_EPSILON:
            return midpoint
        if fa * f_midpoint < 0:
            b = midpoint
            fb = f_midpoint
        else:
            a = midpoint
            fa = f_midpoint

    return (a + b) / 2.0


def validate_config():
    """Проверяем корректность входных параметров."""
    if config.B <= config.A:
        raise ValueError("Параметр B должен быть больше A.")
    if config.EPSILON <= 0:
        raise ValueError("Параметр EPSILON должен быть больше нуля.")
    if int(config.N_MAX) <= 0:
        raise ValueError("Параметр N_MAX должен быть больше нуля.")
    if config.DERIVATIVE_MIN_ABS <= 0:
        raise ValueError("Параметр DERIVATIVE_MIN_ABS должен быть больше нуля.")
    if config.REFERENCE_EPSILON <= 0:
        raise ValueError("Параметр REFERENCE_EPSILON должен быть больше нуля.")
    if int(config.REFERENCE_N_MAX) <= 0:
        raise ValueError("Параметр REFERENCE_N_MAX должен быть больше нуля.")
    if int(config.CURVE_SAMPLES) < 2:
        raise ValueError("Параметр CURVE_SAMPLES должен быть не меньше 2.")
    if int(config.MAX_ITERATIONS_SHOW) < 0:
        raise ValueError("Параметр MAX_ITERATIONS_SHOW не может быть отрицательным.")
    if not np.isfinite(float(config.X0)):
        raise ValueError("Параметр X0 должен быть конечным числом.")

    fa = float(f(config.A))
    fb = float(f(config.B))
    if fa != 0.0 and fb != 0.0 and fa * fb > 0:
        raise ValueError("На концах отрезка функция должна иметь разные знаки.")


def bisection_method():
    """Находим корень методом бисекции."""
    a = float(config.A)
    b = float(config.B)
    fa = float(f(a))
    fb = float(f(b))
    history = []

    if fa == 0.0:
        return build_result(a, 0, 0.0, "Левая граница отрезка является корнем", history)
    if fb == 0.0:
        return build_result(b, 0, 0.0, "Правая граница отрезка является корнем", history)

    for iteration in range(1, int(config.N_MAX) + 1):
        midpoint = (a + b) / 2.0
        f_midpoint = float(f(midpoint))
        interval_length = abs(b - a)
        history.append((iteration, a, b, midpoint, f_midpoint, interval_length))

        if abs(f_midpoint) < config.EPSILON:
            return build_result(midpoint, iteration, interval_length, "|f(x)| < ε", history)
        if interval_length < config.EPSILON:
            return build_result(midpoint, iteration, interval_length, "Длина отрезка < ε", history)

        if fa * f_midpoint < 0:
            b = midpoint
            fb = f_midpoint
        else:
            a = midpoint
            fa = f_midpoint

    midpoint = (a + b) / 2.0
    return build_result(midpoint, int(config.N_MAX), abs(b - a), "Достигнут лимит N_MAX", history)


def newton_method():
    """Находим корень методом Ньютона."""
    x_current = float(config.X0)
    history = []

    for iteration in range(1, int(config.N_MAX) + 1):
        fx = float(f(x_current))
        derivative = float(f_prime(x_current))
        if abs(derivative) < config.DERIVATIVE_MIN_ABS:
            raise ValueError("Метод Ньютона остановлен: производная слишком мала.")

        x_next = x_current - fx / derivative
        if not np.isfinite(x_next):
            raise ValueError("Метод Ньютона вышел за область конечных чисел.")

        delta = abs(x_next - x_current)
        f_next = float(f(x_next))
        history.append((iteration, x_current, fx, derivative, x_next, delta))

        if abs(f_next) < config.EPSILON:
            return build_result(x_next, iteration, delta, "|f(x)| < ε", history)
        if delta < config.EPSILON:
            return build_result(x_next, iteration, delta, "Δx < ε", history)

        x_current = x_next

    return build_result(x_current, int(config.N_MAX), history[-1][5], "Достигнут лимит N_MAX", history)


def build_result(root, iterations, last_delta, status, history):
    """Формируем единый результат численного метода."""
    return {
        "root": float(root),
        "iterations": int(iterations),
        "last_delta": float(last_delta),
        "status": status,
        "history": history,
    }


def calculate_metrics(result):
    """Считаем погрешности и невязку для найденного корня."""
    exact = exact_root()
    absolute_error = abs(result["root"] - exact)
    relative_error = absolute_error / abs(exact) * 100.0
    residual = abs(float(f(result["root"])))
    return {
        "exact": exact,
        "absolute_error": absolute_error,
        "relative_error": relative_error,
        "residual": residual,
    }


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


def plot_base_function(ax, exact):
    """Рисуем функцию, ось Ox, границы исходного отрезка и точный корень."""
    x_line = np.linspace(
        config.A - config.X_MARGIN,
        config.B + config.X_MARGIN,
        int(config.CURVE_SAMPLES),
    )
    function_label = config.FUNCTION_LABEL or f"f(x) = {config.FUNCTION_FORMULA}"
    ax.plot(x_line, f(x_line), color=config.FUNCTION_COLOR, linewidth=2.2, label=function_label)
    ax.axhline(0.0, color="#000000", linewidth=1.0)
    ax.axvline(config.A, color="#e63946", linestyle="--", linewidth=1.4, label=f"a={config.A:g}")
    ax.axvline(config.B, color="#e63946", linestyle="--", linewidth=1.4, label=f"b={config.B:g}")
    ax.axvline(
        exact,
        color=config.EXACT_ROOT_COLOR,
        linestyle=":",
        linewidth=1.8,
        label=f"Точный корень {exact:.6f}",
    )


def plot_overview(results, exact):
    """Строим общий график функции и найденных корней."""
    fig, ax = plt.subplots(figsize=config.OVERVIEW_FIGURE_SIZE)
    plot_base_function(ax, exact)
    ax.axvspan(
        config.A,
        config.B,
        color=config.INTERVAL_COLOR,
        alpha=0.12,
        label=f"Отрезок [{config.A:g}; {config.B:g}]",
    )
    ax.scatter(
        [results["bisection"]["root"]],
        [float(f(results["bisection"]["root"]))],
        color=config.BISECTION_COLOR,
        s=90,
        marker="o",
        label=f"Бисекция {results['bisection']['root']:.6f}",
        zorder=5,
    )
    ax.scatter(
        [results["newton"]["root"]],
        [float(f(results["newton"]["root"]))],
        color=config.NEWTON_COLOR,
        s=100,
        marker="^",
        label=f"Ньютон {results['newton']['root']:.6f}",
        zorder=5,
    )
    ax.set_xlim(config.A - config.X_MARGIN, config.B + config.X_MARGIN)
    ax.set_ylim(config.Y_MIN, config.Y_MAX)
    ax.set_title("Общий график функции")
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.grid(True, alpha=config.GRID_ALPHA)
    ax.legend(loc="best", fontsize=9)
    fig.suptitle(config.PLOT_TITLE, fontsize=12)
    plt.tight_layout(rect=(0, 0, 1, 0.94))
    return fig


def prepare_iteration_axes(title):
    """Создаём сетку графиков для первых итераций метода."""
    columns = 2
    count = max(1, int(config.MAX_ITERATIONS_SHOW))
    rows = int(np.ceil(count / columns))
    fig, axes = plt.subplots(rows, columns, figsize=config.ITERATIONS_FIGURE_SIZE, squeeze=False)
    fig.suptitle(title, fontsize=12)
    return fig, axes.flatten()


def plot_bisection_iterations(result, exact):
    """Показываем первые деления отрезка в методе бисекции."""
    fig, axes = prepare_iteration_axes("Метод бисекции: деление отрезка пополам")
    x_line = np.linspace(config.A, config.B, int(config.CURVE_SAMPLES))

    visible_history = result["history"][: int(config.MAX_ITERATIONS_SHOW)]
    for ax, (iteration, a, b, midpoint, f_midpoint, _) in zip(axes, visible_history):
        ax.plot(x_line, f(x_line), color=config.FUNCTION_COLOR, linewidth=2.0)
        ax.axhline(0.0, color="#000000", linewidth=0.8)
        ax.axvline(exact, color=config.EXACT_ROOT_COLOR, linestyle=":", linewidth=1.4)
        ax.axvspan(a, b, color=config.INTERVAL_COLOR, alpha=0.3)
        ax.scatter([a, b], [float(f(a)), float(f(b))], color="#e63946", s=70, marker="|")
        ax.scatter([midpoint], [f_midpoint], color=config.BISECTION_COLOR, s=70, marker="o")
        ax.set_xlim(config.A - 0.1, config.B + 0.1)
        ax.set_ylim(config.Y_MIN, config.Y_MAX)
        ax.set_title(f"Итерация {iteration}: [{a:.4f}; {b:.4f}], c={midpoint:.4f}", fontsize=10)
        ax.grid(True, alpha=config.GRID_ALPHA)

    for ax in list(axes)[len(visible_history):]:
        ax.set_visible(False)

    plt.tight_layout(rect=(0, 0, 1, 0.96))
    return fig


def plot_newton_iterations(result, exact):
    """Показываем первые касательные в методе Ньютона."""
    fig, axes = prepare_iteration_axes("Метод Ньютона: последовательность касательных")
    x_line = np.linspace(config.A, config.B, int(config.CURVE_SAMPLES))

    visible_history = result["history"][: int(config.MAX_ITERATIONS_SHOW)]
    for ax, (iteration, x_current, fx, derivative, x_next, _) in zip(axes, visible_history):
        ax.plot(x_line, f(x_line), color=config.FUNCTION_COLOR, linewidth=2.0, label="f(x)")
        ax.axhline(0.0, color="#000000", linewidth=0.8)
        ax.axvline(exact, color=config.EXACT_ROOT_COLOR, linestyle=":", linewidth=1.4)
        tangent_x = np.linspace(
            max(config.A - config.X_MARGIN, x_current - 0.8),
            min(config.B + config.X_MARGIN, x_current + 0.8),
            200,
        )
        tangent_y = fx + derivative * (tangent_x - x_current)
        ax.plot(tangent_x, tangent_y, color=config.TANGENT_COLOR, linewidth=2.0, label="Касательная")
        ax.scatter([x_current], [fx], color=config.BISECTION_COLOR, s=70, marker="o", zorder=5)
        ax.scatter([x_next], [0.0], color=config.NEWTON_COLOR, s=90, marker="*", zorder=5)
        ax.set_xlim(config.A - 0.2, config.B + 0.2)
        ax.set_ylim(config.Y_MIN, config.Y_MAX)
        ax.set_title(f"Итерация {iteration}: x={x_current:.6f}, f(x)={fx:.2e}", fontsize=10)
        ax.grid(True, alpha=config.GRID_ALPHA)
        ax.legend(loc="best", fontsize=8)

    for ax in list(axes)[len(visible_history):]:
        ax.set_visible(False)

    plt.tight_layout(rect=(0, 0, 1, 0.96))
    return fig


def plot_convergence(results, exact):
    """Сравниваем абсолютную и относительную погрешности методов."""
    fig, (absolute_ax, relative_ax) = plt.subplots(1, 2, figsize=config.CONVERGENCE_FIGURE_SIZE)
    histories = {
        "Бисекция": (
            [item[3] for item in results["bisection"]["history"]],
            config.BISECTION_COLOR,
            "o",
        ),
        "Ньютон": (
            [item[1] for item in results["newton"]["history"]] + [results["newton"]["root"]],
            config.NEWTON_COLOR,
            "s",
        ),
    }

    for label, (approximations, color, marker) in histories.items():
        absolute_errors = [abs(value - exact) for value in approximations]
        relative_errors = [error / abs(exact) * 100.0 for error in absolute_errors]
        absolute_ax.semilogy(absolute_errors, marker=marker, color=color, linewidth=2.0, label=label)
        relative_ax.semilogy(relative_errors, marker=marker, color=color, linewidth=2.0, label=label)

    absolute_ax.axhline(config.EPSILON, color="#e63946", linestyle="--", linewidth=1.4, label="ε")
    absolute_ax.set_title("Абсолютная погрешность")
    absolute_ax.set_xlabel("Итерация")
    absolute_ax.set_ylabel("|x_n - x*|")
    absolute_ax.legend()
    absolute_ax.grid(True, alpha=config.GRID_ALPHA, which="both")

    relative_ax.set_title("Относительная погрешность")
    relative_ax.set_xlabel("Итерация")
    relative_ax.set_ylabel("|x_n - x*| / |x*|, %")
    relative_ax.legend()
    relative_ax.grid(True, alpha=config.GRID_ALPHA, which="both")

    fig.suptitle("Сходимость методов", fontsize=12)
    plt.tight_layout(rect=(0, 0, 1, 0.94))
    return fig


def plot_results(results, exact):
    """Строим графики и сохраняем их в папку plots/."""
    output_dir = Path(__file__).resolve().parent / config.PLOT_DIR
    figures = [
        ("Общий график", "overview", plot_overview(results, exact)),
        ("Бисекция", "bisection", plot_bisection_iterations(results["bisection"], exact)),
        ("Метод Ньютона", "newton", plot_newton_iterations(results["newton"], exact)),
        ("Сходимость", "convergence", plot_convergence(results, exact)),
    ]
    saved_paths = []
    for label, suffix, fig in figures:
        paths = save_figure(fig, output_dir, f"{config.PLOT_BASENAME}_{suffix}")
        saved_paths.append((label, paths))

    backend = plt.get_backend().lower()
    if config.SHOW_PLOT and "agg" not in backend:
        plt.show()
    else:
        for _, _, fig in figures:
            plt.close(fig)

    return saved_paths


def print_method_report(label, result, metrics):
    """Выводим показатели одного метода."""
    print(label)
    print(f"  Найденный корень:       {result['root']:.15f}")
    print(f"  Абсолютная погрешность: {metrics['absolute_error']:.3e}")
    print(f"  Относительная ошибка:   {metrics['relative_error']:.3e}%")
    print(f"  |f(x)|:                 {metrics['residual']:.3e}")
    print(f"  Итераций:               {result['iterations']}")
    print(f"  Остановка:              {result['status']} (Δ = {result['last_delta']:.3e})")


def print_report(results, metrics, saved_paths):
    """Выводим итоговое сравнение методов."""
    print("=" * 72)
    print("ЛАБОРАТОРНАЯ РАБОТА №5: БИСЕКЦИЯ И МЕТОД КАСАТЕЛЬНЫХ")
    print("=" * 72)
    print(f"Функция: f(x) = {config.FUNCTION_FORMULA}")
    print(f"Отрезок бисекции: [{config.A:g}; {config.B:g}]")
    print(f"Начальное приближение Ньютона: x0 = {config.X0:g}")
    print(f"Точный корень x*: {metrics['bisection']['exact']:.15f}")
    print(f"Условия останова: ε = {config.EPSILON:.0e}, N_MAX = {int(config.N_MAX)}")
    print("-" * 72)
    print_method_report("МЕТОД БИСЕКЦИИ", results["bisection"], metrics["bisection"])
    print("-" * 72)
    print_method_report("МЕТОД НЬЮТОНА", results["newton"], metrics["newton"])
    print("-" * 72)
    print("Графики:")
    for label, paths in saved_paths:
        print(label)
        for path in paths:
            print(f"- {path}")


def main():
    try:
        validate_config()
        results = {
            "bisection": bisection_method(),
            "newton": newton_method(),
        }
    except ValueError as exc:
        raise SystemExit(f"Ошибка в параметрах config.py: {exc}") from exc

    metrics = {
        name: calculate_metrics(result)
        for name, result in results.items()
    }
    saved_paths = plot_results(results, metrics["bisection"]["exact"])
    print_report(results, metrics, saved_paths)


if __name__ == "__main__":
    main()
