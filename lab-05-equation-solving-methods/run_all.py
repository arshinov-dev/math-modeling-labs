from pathlib import Path
import subprocess
import sys


METHODS = (
    ("Бисекция и метод касательных", "bisection-newton", "bisection_newton.py"),
    ("Метод хорд", "chord-method", "chord_method.py"),
    ("Метод простых итераций", "fixed-point-iteration", "fixed_point_iteration.py"),
)


def run_method(lab_dir, label, relative_dir, script_name):
    """Запускаем один раздел лабораторной работы в его рабочем каталоге."""
    method_dir = lab_dir / relative_dir
    script_path = method_dir / script_name
    print("\n" + "=" * 80, flush=True)
    print(label.upper(), flush=True)
    print("=" * 80, flush=True)
    subprocess.run([sys.executable, script_path.name], cwd=method_dir, check=True)


def main():
    """Последовательно запускаем все численные методы решения уравнений."""
    lab_dir = Path(__file__).resolve().parent
    for label, relative_dir, script_name in METHODS:
        run_method(lab_dir, label, relative_dir, script_name)


if __name__ == "__main__":
    main()
