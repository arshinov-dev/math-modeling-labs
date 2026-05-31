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


def normalize_formula(formula):
    """Поддерживаем запись степени через ^."""
    return formula.replace("^", "**")


def compile_formula(formula, variable_name="x"):
    """Компилируем формулу y(x) в вызываемую функцию."""
    normalized = normalize_formula(formula)

    try:
        code = compile(normalized, "<formula>", "eval")
    except SyntaxError as exc:
        raise ValueError(f"Некорректная формула '{formula}': {exc.msg}") from exc

    allowed_names = set(SAFE_NAMES) | {variable_name}
    unknown_names = sorted(set(code.co_names) - allowed_names)
    if unknown_names:
        names = ", ".join(unknown_names)
        raise ValueError(f"Недопустимые имена в формуле '{formula}': {names}")

    def formula_function(value):
        scope = dict(SAFE_NAMES)
        scope[variable_name] = value
        result = eval(code, {"__builtins__": {}}, scope)
        value_array = np.asarray(value)
        if value_array.ndim > 0 and np.asarray(result).ndim == 0:
            return np.full(value_array.shape, result, dtype=float)
        return result

    return formula_function


def build_region_model():
    """Строим модель области по двум формулам из config.py."""
    f1 = compile_formula(config.F1_FORMULA)
    f2 = compile_formula(config.F2_FORMULA)

    def lower_func(x):
        return np.minimum(f1(x), f2(x))

    def upper_func(x):
        return np.maximum(f1(x), f2(x))

    if config.INCLUDE_BORDER:
        contains = lambda x, y: (y >= lower_func(x)) & (y <= upper_func(x))
    else:
        contains = lambda x, y: (y > lower_func(x)) & (y < upper_func(x))

    f1_label = config.F1_LABEL or f"y = {config.F1_FORMULA}"
    f2_label = config.F2_LABEL or f"y = {config.F2_FORMULA}"
    boundaries = [
        {"func": f1, "label": f1_label, "color": config.F1_COLOR},
        {"func": f2, "label": f2_label, "color": config.F2_COLOR},
    ]
    return contains, boundaries


def validate_config():
    """Проверяем числовые параметры эксперимента."""
    if int(config.N_POINTS) <= 0:
        raise ValueError("Параметр N_POINTS должен быть больше нуля.")
    if int(config.CURVE_SAMPLES) < 2:
        raise ValueError("Параметр CURVE_SAMPLES должен быть не меньше 2.")
    if not np.isfinite(float(config.X0)) or not np.isfinite(float(config.Y0)):
        raise ValueError("Координаты X0 и Y0 должны быть конечными числами.")


def get_square_bounds():
    """Вычисляем границы опорного квадрата по X0, Y0 и A."""
    if config.A <= 0:
        raise ValueError("Параметр A должен быть больше нуля.")

    half_side = config.A / 2.0
    x_min = config.X0 - half_side
    x_max = config.X0 + half_side
    y_min = config.Y0 - half_side
    y_max = config.Y0 + half_side
    return x_min, x_max, y_min, y_max


def generate_points(x_min, x_max, y_min, y_max):
    """Генерируем N случайных точек в опорном квадрате."""
    rng = np.random.default_rng(config.RANDOM_SEED)
    x_rand = rng.uniform(x_min, x_max, config.N_POINTS)
    y_rand = rng.uniform(y_min, y_max, config.N_POINTS)
    return x_rand, y_rand


def check_condition(x_rand, y_rand, contains):
    """Проверяем попадание точки в целевую область."""
    return contains(x_rand, y_rand)


def calculate_area(inside_mask, support_area):
    """Считаем оценку площади и статистическую погрешность."""
    n_points = inside_mask.size
    hit_probability = float(np.mean(inside_mask))
    estimated_area = support_area * hit_probability
    error = support_area * np.sqrt(hit_probability * (1.0 - hit_probability) / n_points)
    count_inside = int(np.sum(inside_mask))
    return estimated_area, error, count_inside


def build_output_basename(output_dir):
    """Формируем уникальное имя файла для набора графиков."""
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


def plot_results(x_rand, y_rand, inside_mask, estimated_area, boundaries, bounds):
    """Строим график и сохраняем его в plots/."""
    x_min, x_max, y_min, y_max = bounds
    output_dir = Path(__file__).resolve().parent / config.PLOT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=config.FIGURE_SIZE)

    rect_x = [x_min, x_max, x_max, x_min, x_min]
    rect_y = [y_min, y_min, y_max, y_max, y_min]
    plt.plot(
        rect_x,
        rect_y,
        linestyle="--",
        color=config.BOUNDS_COLOR,
        linewidth=1.6,
        label="Опорный квадрат",
    )

    x_line = np.linspace(x_min, x_max, config.CURVE_SAMPLES)
    for boundary in boundaries:
        y_line = np.asarray(boundary["func"](x_line), dtype=float)
        y_line[~np.isfinite(y_line)] = np.nan
        plt.plot(x_line, y_line, color=boundary["color"], linewidth=2.0, label=boundary["label"])

    plt.scatter(
        x_rand[~inside_mask],
        y_rand[~inside_mask],
        s=config.OUTSIDE_POINT_SIZE,
        c=config.OUTSIDE_COLOR,
        alpha=config.OUTSIDE_ALPHA,
        label="Промахи",
        zorder=2,
    )
    plt.scatter(
        x_rand[inside_mask],
        y_rand[inside_mask],
        s=config.INSIDE_POINT_SIZE,
        c=config.INSIDE_COLOR,
        alpha=config.INSIDE_ALPHA,
        label="Попадания",
        zorder=3,
    )

    plt.title(
        f"{config.PLOT_TITLE}\nN={config.N_POINTS}, S≈{estimated_area:.6f}",
        fontsize=12,
    )
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True, alpha=0.35)
    plt.legend(loc="best")
    plt.axis("equal")
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)

    base_name = build_output_basename(output_dir)
    saved_paths = []
    for extension in config.SAVE_FORMATS:
        file_path = output_dir / f"{base_name}.{extension}"
        plt.savefig(file_path, dpi=config.PLOT_DPI, bbox_inches="tight")
        saved_paths.append(file_path)

    backend = plt.get_backend().lower()
    if config.SHOW_PLOT and "agg" not in backend:
        plt.show()
    else:
        plt.close()

    return saved_paths


def main():
    try:
        validate_config()
        contains, boundaries = build_region_model()
        bounds = get_square_bounds()
    except ValueError as exc:
        raise SystemExit(f"Ошибка в параметрах config.py: {exc}") from exc

    x_min, x_max, y_min, y_max = bounds
    support_area = (x_max - x_min) * (y_max - y_min)

    x_rand, y_rand = generate_points(x_min, x_max, y_min, y_max)
    inside_mask = check_condition(x_rand, y_rand, contains)
    estimated_area, error, count_inside = calculate_area(inside_mask, support_area)
    saved_paths = plot_results(x_rand, y_rand, inside_mask, estimated_area, boundaries, bounds)

    print(f"Всего точек: {config.N_POINTS}")
    print(f"Точек внутри области: {count_inside}")
    print(f"Оценочная площадь: {estimated_area:.6f}")
    print(f"Оценка погрешности (±1σ): {error:.6f}")
    print(f"Опорный квадрат: центр=({config.X0}, {config.Y0}), a={config.A}")
    print(f"Первая граница: y = {config.F1_FORMULA}")
    print(f"Вторая граница: y = {config.F2_FORMULA}")
    print("Файлы графика:")
    for path in saved_paths:
        print(f"- {path}")


if __name__ == "__main__":
    main()
