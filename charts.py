"""PNG charts for the digest (matplotlib, installed on first use)."""
import io
import subprocess
import sys
from datetime import datetime

_plt = None


def _matplotlib():
    global _plt
    if _plt is not None:
        return _plt
    try:
        import matplotlib
    except ImportError:
        print("Installing matplotlib for charts (once per run)…", file=sys.stderr)
        r = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
                            "matplotlib"], capture_output=True, text=True, timeout=240)
        if r.returncode != 0:
            print(f"Couldn't install matplotlib, skipping charts: {r.stderr[-300:]}", file=sys.stderr)
            _plt = False
            return _plt
        import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    _plt = plt
    return plt


BG, FG, GRID = "#2b2d31", "#dbdee1", "#3f4147"
PALETTE = ["#5865F2", "#3BA55D", "#FAA61A", "#ED4245", "#EB459E", "#1ABC9C", "#9B59B6", "#F1C40F"]


def _style(ax, fig):
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    for s in ax.spines.values():
        s.set_color(GRID)
    ax.tick_params(colors=FG, labelsize=9)
    ax.yaxis.label.set_color(FG)
    ax.title.set_color(FG)
    ax.grid(True, color=GRID, linewidth=0.6)


def _kfmt(v, _=None):
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if v >= 1000:
        return f"{v/1000:.0f}K"
    return f"{v:.0f}"


def line_chart(series, title, log=True):
    """series: list of (label, {day: value}). Returns PNG bytes or None."""
    plt = _matplotlib()
    if not plt or not series:
        return None
    from matplotlib.ticker import FuncFormatter
    fig, ax = plt.subplots(figsize=(9, 4.6), dpi=110)
    _style(ax, fig)
    drawn = 0
    for i, (label, days) in enumerate(series):
        pts = sorted((datetime.strptime(d, "%Y-%m-%d"), v) for d, v in days.items() if v)[-14:]
        if len(pts) < 2:
            continue
        drawn += 1
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=PALETTE[i % len(PALETTE)], linewidth=2.2, marker="o", markersize=3.5,
                label=label[:28])
    if not drawn:
        plt.close(fig)
        return None
    if log:
        ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(_kfmt))
    ax.yaxis.set_minor_formatter(FuncFormatter(lambda v, _: ""))
    fig.autofmt_xdate(rotation=0, ha="center")
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.set_title(title, fontsize=12, loc="left", pad=10, color=FG)
    ax.set_ylabel("daily peak players" + (" (log scale)" if log else ""))
    leg = ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False, fontsize=9)
    for t in leg.get_texts():
        t.set_color(FG)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=BG)
    plt.close(fig)
    return buf.getvalue()


def bar_chart(labels, values, title, unit="%"):
    plt = _matplotlib()
    if not plt or not labels:
        return None
    fig, ax = plt.subplots(figsize=(9, max(3, 0.38 * len(labels) + 1)), dpi=110)
    _style(ax, fig)
    colors = ["#3BA55D" if v >= 0 else "#ED4245" for v in values]
    ax.barh(range(len(labels)), values, color=colors)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.axvline(0, color=FG, linewidth=0.8)
    for i, v in enumerate(values):
        ax.text(v + (1 if v >= 0 else -1), i, f"{v:+.0f}{unit}", va="center",
                ha="left" if v >= 0 else "right", color=FG, fontsize=8)
    lo, hi = min(values + [0]), max(values + [0])
    pad = (hi - lo) * 0.18 + 5
    ax.set_xlim(lo - pad, hi + pad)
    ax.set_title(title, fontsize=12, loc="left", pad=10, color=FG)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=BG)
    plt.close(fig)
    return buf.getvalue()
