from datetime import datetime
from html import escape
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

import config

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import LAB5_CONFIG as root_config
from common import bisect_root, compile_formula, formula_to_javascript


PHI = compile_formula(config.PHI_FORMULA)
PHI_PRIME = compile_formula(config.PHI_DERIVATIVE_FORMULA)


def phi(x):
    """Вычисляем значение phi(x) из config.py."""
    return PHI(np.asarray(x, dtype=float))


def phi_prime(x):
    """Вычисляем производную phi'(x) из config.py."""
    return PHI_PRIME(np.asarray(x, dtype=float))


def control_root():
    """Находим контрольный корень уравнения x = phi(x)."""
    return bisect_root(
        lambda x: float(phi(x)) - x,
        config.CONTROL_A,
        config.CONTROL_B,
        root_config.REFERENCE_EPSILON,
        root_config.REFERENCE_N_MAX,
    )


def validate_config():
    """Проверяем корректность входных параметров."""
    if root_config.EPSILON <= 0:
        raise ValueError("Параметр EPSILON должен быть больше нуля.")
    if int(root_config.N_MAX) <= 0:
        raise ValueError("Параметр N_MAX должен быть больше нуля.")
    if config.CONTROL_B <= config.CONTROL_A:
        raise ValueError("CONTROL_B должен быть больше CONTROL_A.")
    if int(config.CURVE_SAMPLES) < 2:
        raise ValueError("Параметр CURVE_SAMPLES должен быть не меньше 2.")
    if config.DOMAIN_X_MAX <= config.DOMAIN_X_MIN:
        raise ValueError("DOMAIN_X_MAX должен быть больше DOMAIN_X_MIN.")
    if config.CHECK_X_MAX <= config.CHECK_X_MIN:
        raise ValueError("CHECK_X_MAX должен быть больше CHECK_X_MIN.")
    if config.COBWEB_X_MAX <= config.COBWEB_X_MIN:
        raise ValueError("COBWEB_X_MAX должен быть больше COBWEB_X_MIN.")
    if config.COBWEB_Y_MAX <= config.COBWEB_Y_MIN:
        raise ValueError("COBWEB_Y_MAX должен быть больше COBWEB_Y_MIN.")
    if int(config.COBWEB_STEPS_SHOW) <= 0:
        raise ValueError("COBWEB_STEPS_SHOW должен быть больше нуля.")
    if int(config.INTERACTIVE_STEPS_SHOW) <= 0:
        raise ValueError("INTERACTIVE_STEPS_SHOW должен быть больше нуля.")
    if not np.isfinite(float(config.X0)):
        raise ValueError("Параметр X0 должен быть конечным числом.")

    check_x = np.linspace(config.CHECK_X_MIN, config.CHECK_X_MAX, int(config.CURVE_SAMPLES))
    if not np.all(np.isfinite(phi(check_x))):
        raise ValueError("PHI_FORMULA должна быть конечной на интервале проверки.")
    if not np.all(np.isfinite(phi_prime(check_x))):
        raise ValueError("PHI_DERIVATIVE_FORMULA должна быть конечной на интервале проверки.")


def fixed_point_iteration():
    """Находим неподвижную точку методом простой итерации."""
    x_previous = float(config.X0)
    history = []

    for iteration in range(1, int(root_config.N_MAX) + 1):
        x_next = float(phi(x_previous))
        if not np.isfinite(x_next):
            raise ValueError("Итерации вышли за область конечных чисел.")

        delta = abs(x_next - x_previous)
        history.append((iteration, x_previous, x_next, delta))

        if delta < root_config.EPSILON:
            return {
                "root": x_next,
                "iterations": iteration,
                "last_delta": delta,
                "status": "Выполнено условие Δx < ε",
                "history": history,
            }

        x_previous = x_next

    return {
        "root": x_previous,
        "iterations": int(root_config.N_MAX),
        "last_delta": history[-1][3] if history else np.inf,
        "status": "Достигнут лимит N_MAX",
        "history": history,
    }


def calculate_report_values(root):
    """Считаем контрольные величины для отчёта."""
    exact = control_root()
    absolute_error = abs(root - exact)
    residual = abs(root - float(phi(root)))
    check_x = np.linspace(config.CHECK_X_MIN, config.CHECK_X_MAX, int(config.CURVE_SAMPLES))
    phi_values = phi(check_x)
    derivative_values = phi_prime(check_x)
    return {
        "exact": exact,
        "absolute_error": absolute_error,
        "residual": residual,
        "derivative_at_root": float(phi_prime(root)),
        "max_abs_derivative": float(np.max(np.abs(derivative_values))),
        "phi_min": float(np.min(phi_values)),
        "phi_max": float(np.max(phi_values)),
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


def plot_base_curves(ax, x_min, x_max, root=None):
    """Рисуем phi(x), диагональ y=x и найденную неподвижную точку."""
    x_line = np.linspace(x_min, x_max, int(config.CURVE_SAMPLES))
    y_phi = phi(x_line)

    ax.plot(
        x_line,
        y_phi,
        color=config.PHI_COLOR,
        linewidth=2.2,
        label=config.PHI_LABEL or f"φ(x) = {config.PHI_FORMULA}",
        zorder=3,
    )
    ax.plot(
        x_line,
        x_line,
        color=config.DIAGONAL_COLOR,
        linestyle="--",
        linewidth=1.8,
        label=config.DIAGONAL_LABEL,
        zorder=2,
    )
    if root is not None:
        ax.scatter(
            [root],
            [root],
            color=config.ROOT_COLOR,
            s=80,
            marker="o",
            label=f"Найденная точка {root:.6f}",
            zorder=6,
        )
    return x_line, y_phi


def plot_overview(result):
    """Строим общий график phi(x) и y=x."""
    fig, ax = plt.subplots(figsize=config.OVERVIEW_FIGURE_SIZE)
    plot_base_curves(ax, config.DOMAIN_X_MIN, config.DOMAIN_X_MAX, root=result["root"])
    ax.scatter(
        [config.X0],
        [config.X0],
        color=config.START_COLOR,
        s=60,
        marker="s",
        label=f"Старт x0={config.X0:g}",
        zorder=5,
    )

    ax.set_title("Общий график уравнения x = φ(x)")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_xlim(config.DOMAIN_X_MIN, config.DOMAIN_X_MAX)
    ax.set_ylim(config.DOMAIN_X_MIN, config.DOMAIN_X_MAX)
    ax.grid(True, alpha=config.GRID_ALPHA)
    ax.legend(loc="best", fontsize=9)
    fig.suptitle(config.PLOT_TITLE, fontsize=12)
    plt.tight_layout(rect=(0, 0, 1, 0.94))
    return fig


def plot_derivative(report_values):
    """Строим график производной и проверку условия |phi'(x)| < 1."""
    fig, ax = plt.subplots(figsize=config.DERIVATIVE_FIGURE_SIZE)
    x_line = np.linspace(config.CHECK_X_MIN, config.CHECK_X_MAX, int(config.CURVE_SAMPLES))
    derivative_line = phi_prime(x_line)
    root = report_values["exact"]
    comparison = "< 1" if report_values["max_abs_derivative"] < 1.0 else ">= 1"

    ax.plot(
        x_line,
        derivative_line,
        color=config.DERIVATIVE_COLOR,
        linewidth=2.2,
        label=config.PHI_DERIVATIVE_LABEL or f"φ'(x) = {config.PHI_DERIVATIVE_FORMULA}",
    )
    ax.axhline(
        1.0,
        color=config.CONTRACTION_COLOR,
        linestyle="--",
        linewidth=1.4,
        label=r"$|\varphi'(x)|=1$",
    )
    ax.axhline(
        -1.0,
        color=config.CONTRACTION_COLOR,
        linestyle="--",
        linewidth=1.4,
    )
    ax.axhline(0.0, color="#000000", linewidth=1.0)
    ax.scatter(
        [root],
        [report_values["derivative_at_root"]],
        color=config.ROOT_COLOR,
        s=80,
        zorder=5,
        label=rf"$\varphi'(x^*)\approx {report_values['derivative_at_root']:.6f}$",
    )
    ax.text(
        0.03,
        0.06,
        f"На [{config.CHECK_X_MIN:g}; {config.CHECK_X_MAX:g}]:\n"
        f"max |φ'(x)| ≈ {report_values['max_abs_derivative']:.6f} {comparison}\n"
        f"φ([{config.CHECK_X_MIN:g}; {config.CHECK_X_MAX:g}]) "
        f"⊂ [{report_values['phi_min']:.6f}; {report_values['phi_max']:.6f}]",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=9.5,
        bbox=dict(facecolor="white", alpha=0.86, edgecolor="#d0d0d0"),
    )
    ax.set_title("Проверка сходимости через производную")
    ax.set_xlabel("x")
    ax.set_ylabel(r"$\varphi'(x)$")
    ax.set_xlim(config.CHECK_X_MIN, config.CHECK_X_MAX)
    ax.set_ylim(-1.12, 1.12)
    ax.grid(True, alpha=config.GRID_ALPHA)
    ax.legend(loc="best", fontsize=9)
    fig.suptitle("Условие сходимости: |φ'(x)| < 1", fontsize=12)
    plt.tight_layout(rect=(0, 0, 1, 0.94))
    return fig


def draw_arrow_segment(ax, start, end, color, label=None, alpha=0.9):
    """Рисуем один направленный участок улитки."""
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops=dict(
            arrowstyle="->",
            color=color,
            linewidth=1.7,
            alpha=alpha,
            shrinkA=0,
            shrinkB=0,
        ),
        zorder=4,
    )
    ax.plot(
        [start[0], end[0]],
        [start[1], end[1]],
        color=color,
        linewidth=1.5,
        alpha=alpha * 0.65,
        label=label,
        zorder=3,
    )


def plot_cobweb(result):
    """Строим увеличенный график-улитку метода простой итерации."""
    fig, ax = plt.subplots(figsize=config.COBWEB_FIGURE_SIZE)
    root = result["root"]
    plot_base_curves(ax, config.COBWEB_X_MIN, config.COBWEB_X_MAX, root=root)

    visible_history = result["history"][: int(config.COBWEB_STEPS_SHOW)]
    for index, (iteration, x_previous, x_next, _) in enumerate(visible_history):
        y_start = 0.0 if index == 0 else x_previous
        vertical_start = (x_previous, y_start)
        vertical_end = (x_previous, x_next)
        horizontal_end = (x_next, x_next)
        alpha = max(0.28, 0.95 - index * 0.045)

        draw_arrow_segment(
            ax,
            vertical_start,
            vertical_end,
            config.VERTICAL_STEP_COLOR,
            label=r"Подъём к $\varphi(x_n)$" if index == 0 else None,
            alpha=alpha,
        )
        draw_arrow_segment(
            ax,
            vertical_end,
            horizontal_end,
            config.HORIZONTAL_STEP_COLOR,
            label=r"Переход к $y=x$" if index == 0 else None,
            alpha=alpha,
        )
        ax.scatter(
            [x_previous],
            [x_next],
            color=config.ITERATION_POINT_COLOR,
            s=48,
            edgecolor="white",
            linewidth=0.7,
            zorder=6,
            label=r"Точки $(x_n,\varphi(x_n))$" if index == 0 else None,
        )

        if index < 5:
            ax.annotate(
                rf"$x_{iteration - 1}$",
                xy=(x_previous, y_start),
                xytext=(5, -17),
                textcoords="offset points",
                fontsize=9,
                color=config.HORIZONTAL_STEP_COLOR,
            )
            ax.annotate(
                rf"$x_{iteration}$",
                xy=horizontal_end,
                xytext=(6, 8),
                textcoords="offset points",
                fontsize=9,
                color=config.HORIZONTAL_STEP_COLOR,
            )

    ax.set_title("Улитка простой итерации")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_xlim(config.COBWEB_X_MIN, config.COBWEB_X_MAX)
    ax.set_ylim(config.COBWEB_Y_MIN, config.COBWEB_Y_MAX)
    ax.grid(True, alpha=config.GRID_ALPHA)
    ax.legend(loc="best", fontsize=9)
    fig.suptitle("Метод простой итерации: x_{n+1}=φ(x_n)", fontsize=12)
    plt.tight_layout(rect=(0, 0, 1, 0.94))
    return fig


def build_interactive_html(result):
    """Создаём HTML с улиткой, которую можно приближать колесом мыши."""
    steps = [
        {
            "iteration": int(iteration),
            "xPrevious": float(x_previous),
            "xNext": float(x_next),
        }
        for iteration, x_previous, x_next, _ in result["history"][: int(config.INTERACTIVE_STEPS_SHOW)]
    ]
    payload = {
        "x0": float(config.X0),
        "root": float(result["root"]),
        "steps": steps,
        "view": {
            "xMin": float(config.COBWEB_X_MIN),
            "xMax": float(config.COBWEB_X_MAX),
            "yMin": float(config.COBWEB_Y_MIN),
            "yMax": float(config.COBWEB_Y_MAX),
        },
    }
    data_json = json.dumps(payload, ensure_ascii=False)
    phi_javascript = formula_to_javascript(config.PHI_FORMULA)
    phi_formula_html = escape(config.PHI_FORMULA)

    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Lab 06: интерактивная улитка</title>
  <style>
    body {{
      margin: 0;
      font-family: Arial, sans-serif;
      background: #f7f8fa;
      color: #1f2933;
    }}
    header {{
      padding: 14px 18px;
      background: #ffffff;
      border-bottom: 1px solid #d9dee5;
    }}
    h1 {{
      margin: 0 0 4px;
      font-size: 20px;
      font-weight: 600;
    }}
    .hint {{
      font-size: 13px;
      color: #52606d;
    }}
    #toolbar {{
      display: flex;
      gap: 10px;
      align-items: center;
      padding: 10px 18px;
      background: #ffffff;
      border-bottom: 1px solid #d9dee5;
    }}
    button {{
      border: 1px solid #b8c2cc;
      background: #ffffff;
      border-radius: 6px;
      padding: 7px 11px;
      cursor: pointer;
      font-size: 13px;
    }}
    #canvas {{
      display: block;
      width: 100vw;
      height: calc(100vh - 111px);
      background: #ffffff;
      cursor: grab;
    }}
    #canvas:active {{
      cursor: grabbing;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Метод простой итерации: улитка</h1>
    <div class="hint">Колесо мыши — приближение, зажатая левая кнопка — перемещение, двойной клик — сброс.</div>
  </header>
  <div id="toolbar">
    <button id="reset">Сбросить вид</button>
    <span class="hint">φ(x)={phi_formula_html}, x₀={float(config.X0):g}, корень≈{float(result["root"]):.15f}</span>
  </div>
  <canvas id="canvas"></canvas>
  <script>
    const data = {data_json};
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    const initialView = {{ ...data.view }};
    let view = {{ ...initialView }};
    let dragging = false;
    let lastMouse = null;

    function phi(x) {{
      return {phi_javascript};
    }}

    function resize() {{
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = Math.max(1, Math.floor(rect.width * dpr));
      canvas.height = Math.max(1, Math.floor(rect.height * dpr));
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      draw();
    }}

    function screenToWorld(px, py) {{
      const rect = canvas.getBoundingClientRect();
      const x = view.xMin + (px - rect.left) / rect.width * (view.xMax - view.xMin);
      const y = view.yMax - (py - rect.top) / rect.height * (view.yMax - view.yMin);
      return {{ x, y }};
    }}

    function worldToScreen(x, y) {{
      const rect = canvas.getBoundingClientRect();
      return {{
        x: (x - view.xMin) / (view.xMax - view.xMin) * rect.width,
        y: (view.yMax - y) / (view.yMax - view.yMin) * rect.height,
      }};
    }}

    function drawLine(x1, y1, x2, y2, color, width = 1.5, dash = []) {{
      const a = worldToScreen(x1, y1);
      const b = worldToScreen(x2, y2);
      ctx.save();
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      ctx.setLineDash(dash);
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.stroke();
      ctx.restore();
    }}

    function drawArrow(x1, y1, x2, y2, color, width = 1.6) {{
      const a = worldToScreen(x1, y1);
      const b = worldToScreen(x2, y2);
      const angle = Math.atan2(b.y - a.y, b.x - a.x);
      const size = 8;
      ctx.save();
      ctx.strokeStyle = color;
      ctx.fillStyle = color;
      ctx.lineWidth = width;
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(b.x, b.y);
      ctx.lineTo(b.x - size * Math.cos(angle - Math.PI / 6), b.y - size * Math.sin(angle - Math.PI / 6));
      ctx.lineTo(b.x - size * Math.cos(angle + Math.PI / 6), b.y - size * Math.sin(angle + Math.PI / 6));
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }}

    function drawPoint(x, y, color, radius = 4.5) {{
      const p = worldToScreen(x, y);
      ctx.save();
      ctx.fillStyle = color;
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.arc(p.x, p.y, radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
      ctx.restore();
    }}

    function drawText(text, x, y, color = "#1f2933") {{
      const p = worldToScreen(x, y);
      ctx.save();
      ctx.fillStyle = color;
      ctx.font = "13px Arial";
      ctx.fillText(text, p.x + 6, p.y - 6);
      ctx.restore();
    }}

    function drawGrid() {{
      const xStep = niceStep((view.xMax - view.xMin) / 8);
      const yStep = niceStep((view.yMax - view.yMin) / 8);
      ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);
      for (let x = Math.ceil(view.xMin / xStep) * xStep; x <= view.xMax; x += xStep) {{
        drawLine(x, view.yMin, x, view.yMax, "#d9dee5", 1);
        drawText(Number(x.toFixed(3)).toString(), x, view.yMin, "#657786");
      }}
      for (let y = Math.ceil(view.yMin / yStep) * yStep; y <= view.yMax; y += yStep) {{
        drawLine(view.xMin, y, view.xMax, y, "#d9dee5", 1);
        drawText(Number(y.toFixed(3)).toString(), view.xMin, y, "#657786");
      }}
      drawLine(view.xMin, 0, view.xMax, 0, "#111111", 1.4);
      drawLine(0, view.yMin, 0, view.yMax, "#111111", 1.0);
    }}

    function niceStep(raw) {{
      const power = Math.pow(10, Math.floor(Math.log10(raw)));
      const scaled = raw / power;
      if (scaled < 2) return power;
      if (scaled < 5) return 2 * power;
      return 5 * power;
    }}

    function drawCurves() {{
      const samples = 600;
      ctx.save();
      ctx.strokeStyle = "#1d3557";
      ctx.lineWidth = 2.4;
      ctx.beginPath();
      for (let i = 0; i <= samples; i++) {{
        const x = view.xMin + i / samples * (view.xMax - view.xMin);
        const p = worldToScreen(x, phi(x));
        if (i === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
      }}
      ctx.stroke();
      ctx.restore();
      drawLine(view.xMin, view.xMin, view.xMax, view.xMax, "#2f2f2f", 1.8, [7, 5]);
    }}

    function drawCobweb() {{
      data.steps.forEach((step, index) => {{
        const yStart = index === 0 ? 0 : step.xPrevious;
        const alpha = Math.max(0.32, 1 - index * 0.035);
        ctx.globalAlpha = alpha;
        drawArrow(step.xPrevious, yStart, step.xPrevious, step.xNext, "#457b9d", 1.8);
        drawArrow(step.xPrevious, step.xNext, step.xNext, step.xNext, "#e76f51", 1.8);
        drawPoint(step.xPrevious, step.xNext, "#f4a261", 4.8);
        if (index < 6) {{
          drawText("x" + (step.iteration - 1), step.xPrevious, yStart, "#e76f51");
          drawText("x" + step.iteration, step.xNext, step.xNext, "#e76f51");
        }}
        ctx.globalAlpha = 1;
      }});
      drawPoint(data.root, data.root, "#7b2cbf", 6);
      drawText("root", data.root, data.root, "#7b2cbf");
    }}

    function drawLegend() {{
      const x = 18;
      let y = 22;
      ctx.save();
      ctx.fillStyle = "rgba(255,255,255,0.88)";
      ctx.strokeStyle = "#cbd2d9";
      ctx.fillRect(12, 10, 260, 112);
      ctx.strokeRect(12, 10, 260, 112);
      ctx.font = "14px Arial";
      ctx.fillStyle = "#1f2933";
      ctx.fillText("Синяя кривая: y = φ(x)", x, y); y += 22;
      ctx.fillText("Пунктир: y = x", x, y); y += 22;
      ctx.fillText("Синие шаги: xₙ → φ(xₙ)", x, y); y += 22;
      ctx.fillText("Оранжевые шаги: переход к y=x", x, y); y += 22;
      ctx.fillText("Колесо мыши приближает улитку", x, y);
      ctx.restore();
    }}

    function draw() {{
      drawGrid();
      drawCurves();
      drawCobweb();
      drawLegend();
    }}

    canvas.addEventListener("wheel", (event) => {{
      event.preventDefault();
      const mouse = screenToWorld(event.clientX, event.clientY);
      const factor = event.deltaY < 0 ? 0.86 : 1.16;
      view = {{
        xMin: mouse.x + (view.xMin - mouse.x) * factor,
        xMax: mouse.x + (view.xMax - mouse.x) * factor,
        yMin: mouse.y + (view.yMin - mouse.y) * factor,
        yMax: mouse.y + (view.yMax - mouse.y) * factor,
      }};
      draw();
    }}, {{ passive: false }});

    canvas.addEventListener("mousedown", (event) => {{
      dragging = true;
      lastMouse = screenToWorld(event.clientX, event.clientY);
    }});
    window.addEventListener("mouseup", () => dragging = false);
    window.addEventListener("mousemove", (event) => {{
      if (!dragging) return;
      const current = screenToWorld(event.clientX, event.clientY);
      const dx = lastMouse.x - current.x;
      const dy = lastMouse.y - current.y;
      view.xMin += dx;
      view.xMax += dx;
      view.yMin += dy;
      view.yMax += dy;
      lastMouse = screenToWorld(event.clientX, event.clientY);
      draw();
    }});
    canvas.addEventListener("dblclick", () => {{
      view = {{ ...initialView }};
      draw();
    }});
    document.getElementById("reset").addEventListener("click", () => {{
      view = {{ ...initialView }};
      draw();
    }});
    window.addEventListener("resize", resize);
    resize();
  </script>
</body>
</html>
"""


def save_interactive_html(result, output_dir):
    """Сохраняем интерактивную HTML-улитку."""
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / config.INTERACTIVE_HTML_NAME
    file_path.write_text(build_interactive_html(result), encoding="utf-8")
    return file_path


def plot_results(result, report_values):
    """Строим общий график, улитку и интерактивный HTML."""
    output_dir = Path(__file__).resolve().parent / config.PLOT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    overview_fig = plot_overview(result)
    derivative_fig = plot_derivative(report_values)
    cobweb_fig = plot_cobweb(result)
    saved_paths = [
        ("Общий график", save_figure(overview_fig, output_dir, f"{config.PLOT_BASENAME}_overview")),
        ("Производная", save_figure(derivative_fig, output_dir, f"{config.PLOT_BASENAME}_derivative")),
        ("Улитка", save_figure(cobweb_fig, output_dir, f"{config.PLOT_BASENAME}_cobweb")),
        ("Интерактивная улитка", [save_interactive_html(result, output_dir)]),
    ]

    backend = plt.get_backend().lower()
    if config.SHOW_PLOT and "agg" not in backend:
        plt.show()
    else:
        plt.close(overview_fig)
        plt.close(derivative_fig)
        plt.close(cobweb_fig)

    return saved_paths


def print_report(result, report_values, saved_paths):
    """Выводим краткий итоговый отчёт в консоль."""
    root = result["root"]
    comparison = "< 1" if report_values["max_abs_derivative"] < 1.0 else ">= 1"

    print("=" * 70)
    print("ЛАБОРАТОРНАЯ РАБОТА №6: МЕТОД ПРОСТОЙ ИТЕРАЦИИ")
    print("=" * 70)
    print("Уравнение: x = phi(x)")
    print(f"phi(x) = {config.PHI_FORMULA}")
    print(f"phi'(x) = {config.PHI_DERIVATIVE_FORMULA}")
    print(f"Начальное приближение: x0 = {config.X0:g}")
    print(f"Условия останова: Δx < {root_config.EPSILON:.0e} или N_MAX = {int(root_config.N_MAX)}")
    print(f"Интервал проверки сходимости: [{config.CHECK_X_MIN:g}; {config.CHECK_X_MAX:g}]")
    print("-" * 70)
    print(f"Найденная неподвижная точка x_hat: {root:.15f}")
    print(f"Контрольный корень x*:             {report_values['exact']:.15f}")
    print(f"|x_hat - x*|:                      {report_values['absolute_error']:.3e}")
    print(f"|x_hat - phi(x_hat)|:              {report_values['residual']:.3e}")
    print(f"phi'(x_hat):                       {report_values['derivative_at_root']:.6f}")
    print(f"max |phi'(x)| на интервале:        {report_values['max_abs_derivative']:.6f} {comparison}")
    print(f"Итераций:                          {result['iterations']}")
    print(f"Остановка:                         {result['status']} (Δx = {result['last_delta']:.3e})")
    print("-" * 70)
    print("Графики:")
    for label, paths in saved_paths:
        print(label)
        for path in paths:
            print(f"- {path}")


def main():
    try:
        validate_config()
        result = fixed_point_iteration()
        report_values = calculate_report_values(result["root"])
    except ValueError as exc:
        raise SystemExit(f"Ошибка в параметрах config.py: {exc}") from exc

    saved_paths = plot_results(result, report_values)
    print_report(result, report_values, saved_paths)


if __name__ == "__main__":
    main()
