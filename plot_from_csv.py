import argparse
import base64
from io import BytesIO

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from cycler import cycler

DEFAULT_PREFIXES = ["backend", "frontend", "worker"]


def group_containers(df: pd.DataFrame, prefixes: list[str]) -> dict[str, pd.DataFrame]:
    groups: dict[str, pd.DataFrame] = {}
    matched = pd.Series([False] * len(df), index=df.index)

    for prefix in prefixes:
        mask = df["Container Name"].str.startswith(prefix)
        groups[prefix] = df[mask]
        matched |= mask

    groups["other"] = df[~matched]
    return groups


def create_plot(group: pd.DataFrame, group_name: str) -> str:
    if group.empty:
        return ""

    fig, axs = plt.subplots(3, 1, figsize=(14, 14), sharex=True)

    unique_containers = group["Container Name"].unique()
    colors = plt.get_cmap("tab20", len(unique_containers))
    color_cycle = cycler("color", [colors(i) for i in range(len(unique_containers))])
    for ax in axs:
        ax.set_prop_cycle(color_cycle)

    for container in unique_containers:
        data = group[group["Container Name"] == container]

        axs[0].plot(data["Timestamp"], data["CPU (%)"], label=f"{container} CPU (%)")
        axs[1].plot(data["Timestamp"], data["Memory Usage (MB)"], label=f"{container} Memory (MB)")
        axs[2].plot(data["Timestamp"], data["Network RX (MB)"], label=f"{container} RX (MB)", linestyle="--")
        axs[2].plot(data["Timestamp"], data["Network TX (MB)"], label=f"{container} TX (MB)", linestyle="--")

    axs[0].set_ylabel("CPU (%)")
    axs[0].set_title(f"{group_name} — CPU Usage")
    axs[0].set_ylim(0, 100)
    axs[0].grid(True)

    axs[1].set_ylabel("Memory (MB)")
    axs[1].set_title(f"{group_name} — Memory Usage")
    axs[1].grid(True)

    axs[2].set_ylabel("Network (MB)")
    axs[2].set_title(f"{group_name} — Network I/O")
    axs[2].grid(True)

    axs[2].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()

    for ax in axs:
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.3), ncol=4, fontsize="x-small", frameon=False)

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.3)

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    plt.close(fig)

    return image_base64


def generate_html(groups: dict[str, str], output_file: str) -> None:
    sections = ""
    for group_name, img_base64 in groups.items():
        if img_base64:
            sections += f"""
    <h2>{group_name.capitalize()} Group</h2>
    <img src="data:image/png;base64,{img_base64}" alt="{group_name} group chart">
"""

    html = f"""<html>
<head><title>Container Monitoring Report</title></head>
<body>
<h1>Monitoring Results</h1>
{sections}
</body>
</html>"""

    with open(output_file, "w") as f:
        f.write(html)

    print(f"Report saved: {output_file}")


def plot_from_csv(
    csv_file: str = "container_stats.csv",
    prefixes: list[str] | None = None,
    output_file: str = "monitoring_graphs.html",
) -> None:
    if prefixes is None:
        prefixes = DEFAULT_PREFIXES

    df = pd.read_csv(csv_file, parse_dates=["Timestamp"])
    groups = group_containers(df, prefixes)

    charts = {name: create_plot(df_group, name) for name, df_group in groups.items()}
    generate_html(charts, output_file)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate HTML report from container stats CSV")
    parser.add_argument("--csv", default="container_stats.csv", help="Path to CSV file")
    parser.add_argument("--prefixes", nargs="+", default=DEFAULT_PREFIXES, help="Container name prefixes to group by")
    parser.add_argument("--output", default="monitoring_graphs.html", help="Output HTML file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    plot_from_csv(csv_file=args.csv, prefixes=args.prefixes, output_file=args.output)