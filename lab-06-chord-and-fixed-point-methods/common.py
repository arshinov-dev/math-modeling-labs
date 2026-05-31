from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import re

import numpy as np


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


def load_lab5_config():
    """Загружаем общие настройки уравнения и останова из лабораторной №5."""
    config_path = Path(__file__).resolve().parents[1] / "lab-05-root-finding-methods" / "config.py"
    spec = spec_from_file_location("lab5_root_finding_config", config_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Не удалось загрузить конфигурацию лабораторной №5: {config_path}")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def bisect_root(function, a, b, epsilon, n_max):
    """Находим контрольный корень функции бисекцией."""
    a = float(a)
    b = float(b)
    fa = float(function(a))
    fb = float(function(b))
    if fa == 0.0:
        return a
    if fb == 0.0:
        return b
    if fa * fb > 0:
        raise ValueError("Для контрольной бисекции нужна смена знака на заданном отрезке.")

    for _ in range(int(n_max)):
        midpoint = (a + b) / 2.0
        f_midpoint = float(function(midpoint))
        if abs(f_midpoint) < epsilon or abs(b - a) < epsilon:
            return midpoint
        if fa * f_midpoint < 0:
            b = midpoint
            fb = f_midpoint
        else:
            a = midpoint
            fa = f_midpoint

    return (a + b) / 2.0


def get_lab5_reference_root(function):
    """Возвращаем настроенный или автоматически найденный корень из варианта lab-05."""
    if LAB5_CONFIG.REFERENCE_ROOT is not None:
        return float(LAB5_CONFIG.REFERENCE_ROOT)
    return bisect_root(
        function,
        LAB5_CONFIG.A,
        LAB5_CONFIG.B,
        LAB5_CONFIG.REFERENCE_EPSILON,
        LAB5_CONFIG.REFERENCE_N_MAX,
    )


def formula_to_javascript(formula):
    """Преобразуем поддерживаемую формулу Python в выражение JavaScript."""
    javascript = formula.replace("^", "**")
    replacements = {
        "sin": "Math.sin",
        "cos": "Math.cos",
        "tan": "Math.tan",
        "exp": "Math.exp",
        "log": "Math.log",
        "sqrt": "Math.sqrt",
        "abs": "Math.abs",
        "pi": "Math.PI",
        "e": "Math.E",
    }
    for name, replacement in replacements.items():
        javascript = re.sub(rf"\b{name}\b", replacement, javascript)
    return javascript


LAB5_CONFIG = load_lab5_config()
