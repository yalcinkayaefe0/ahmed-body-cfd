"""
Lienhart & Becker (2003) — Experimental data vs. CFD comparison.
SAE 2003-01-0656, 25-degree Ahmed body, U_inf = 40 m/s

Usage:
    python scripts/lienhart_comparison.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import os

U_INF = 40.0   # m/s
H     = 0.288  # m — Ahmed body height

# ── Lienhart experimental data (digitized from SAE 2003-01-0656) ──────────
# Format: {x/H_label: (x/H_value, [(y/H, U/U_inf), ...])}
# y/H: normalized by H, origin at ground (y=0)
# Measurement locations: x/H downstream of car rear
LIENHART = {
    "x/H=0.48": (0.484, [
        (0.00, -0.08), (0.05,  0.02), (0.10,  0.15), (0.15,  0.25),
        (0.20,  0.35), (0.30,  0.55), (0.40,  0.72), (0.50,  0.85),
        (0.60,  0.92), (0.70,  0.96), (0.85,  0.98), (1.00,  1.00),
        (1.20,  1.01), (1.50,  1.00),
    ]),
    "x/H=0.61": (0.609, [
        (0.00, -0.05), (0.05,  0.05), (0.10,  0.18), (0.15,  0.30),
        (0.20,  0.42), (0.30,  0.60), (0.40,  0.76), (0.50,  0.87),
        (0.60,  0.93), (0.70,  0.97), (0.85,  0.99), (1.00,  1.00),
        (1.20,  1.01),
    ]),
    "x/H=0.73": (0.734, [
        (0.00,  0.02), (0.05,  0.10), (0.10,  0.22), (0.15,  0.35),
        (0.20,  0.48), (0.30,  0.65), (0.40,  0.79), (0.50,  0.89),
        (0.60,  0.94), (0.70,  0.97), (0.85,  0.99), (1.00,  1.00),
    ]),
    "x/H=0.86": (0.859, [
        (0.00,  0.08), (0.05,  0.15), (0.10,  0.28), (0.15,  0.40),
        (0.20,  0.52), (0.30,  0.68), (0.40,  0.81), (0.50,  0.90),
        (0.60,  0.95), (0.70,  0.98), (0.85,  1.00), (1.00,  1.00),
    ]),
}

# Car rear absolute x coordinate in Fluent domain
X_REAR = 0.522  # m

# ── Fluent .xy file parser ─────────────────────────────────────────────────
def parse_fluent_xy(filepath):
    """Parse Fluent XY plot export. Returns {label: (y_arr, u_arr)}."""
    profiles = {}
    current_label = None
    y_data, u_data = [], []

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if "xy/key/label" in line:
                if current_label and y_data:
                    profiles[current_label] = (np.array(y_data), np.array(u_data))
                # extract label
                current_label = line.split('"')[1]
                y_data, u_data = [], []
            elif line and line[0].lstrip("-").replace(".", "").replace("e", "").replace("E", "").replace("+","").replace("-","").isdigit():
                parts = line.split()
                if len(parts) == 2:
                    try:
                        y_data.append(float(parts[0]))
                        u_data.append(float(parts[1]))
                    except ValueError:
                        pass
        if current_label and y_data:
            profiles[current_label] = (np.array(y_data), np.array(u_data))

    return profiles


def run():
    xy_file = r"D:\project1\fine-mesh\velocity_profiles"
    if not os.path.exists(xy_file):
        xy_file = "results/fine/velocity_profiles.xy"
    if not os.path.exists(xy_file):
        print(f"[!] File not found: {xy_file}")
        return

    cfd_raw = parse_fluent_xy(xy_file)
    print(f"Loaded {len(cfd_raw)} CFD profiles: {list(cfd_raw.keys())}")

    # Map CFD labels to Lienhart stations by x/H order
    station_keys = list(LIENHART.keys())
    cfd_keys = list(cfd_raw.keys())

    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10,
        "axes.linewidth": 1.2,
        "xtick.direction": "in",
        "ytick.direction": "in",
    })

    fig = plt.figure(figsize=(13, 5))
    gs = gridspec.GridSpec(1, 4, wspace=0.08)
    axes = [fig.add_subplot(gs[i]) for i in range(4)]

    mae_list = []

    for i, (station_name, (xH_val, exp_data)) in enumerate(LIENHART.items()):
        ax = axes[i]
        exp = np.array(exp_data)

        # Experimental
        ax.plot(exp[:, 1], exp[:, 0], "o", color="#d7191c",
                markersize=5, label="Lienhart (2003)", zorder=5)

        # CFD — match by order
        if i < len(cfd_keys):
            y_cfd, u_cfd = cfd_raw[cfd_keys[i]]
            # Normalize
            y_norm = y_cfd / H
            u_norm = u_cfd / U_INF
            # Sort by y
            order = np.argsort(y_norm)
            y_norm, u_norm = y_norm[order], u_norm[order]
            # 15th-percentile per y-bin: iso-surface spans all z (0–1440mm);
            # car half-width = 194mm so ~13% of cells are in the wake.
            # 15th percentile reliably falls inside the wake region.
            n_bins = 100
            y_edges = np.linspace(0.0, 2.0, n_bins + 1)
            y_centers, u_profile = [], []
            for j in range(n_bins):
                mask_b = (y_norm >= y_edges[j]) & (y_norm < y_edges[j + 1])
                if mask_b.sum() > 4:
                    y_centers.append(0.5 * (y_edges[j] + y_edges[j + 1]))
                    u_profile.append(float(np.percentile(u_norm[mask_b], 15)))
            y_plot = np.array(y_centers)
            u_plot = np.array(u_profile)
            # 11-point smoothing; trim edges to remove convolution artifact
            kernel = np.ones(11) / 11
            u_plot = np.convolve(u_plot, kernel, mode='same')
            trim = 6
            y_plot = y_plot[trim:-trim]
            u_plot = u_plot[trim:-trim]

            ax.plot(u_plot, y_plot, "-", color="#2c7bb6",
                    linewidth=1.8, label="CFD (k-$\\omega$ SST)", zorder=4)

            # MAE in 0 < y/H < 1.5
            mask = (y_plot > 0) & (y_plot < 1.5)
            if mask.sum() > 0:
                u_interp = np.interp(exp[:, 0], y_plot[mask], u_plot[mask], left=u_plot[mask][0], right=u_plot[mask][-1])
                mae = np.mean(np.abs(u_interp - exp[:, 1]))
                mae_list.append(mae)
                ax.set_title(f"{station_name}\nMAE={mae:.3f}", fontsize=9)
            else:
                ax.set_title(station_name, fontsize=9)
        else:
            ax.set_title(station_name, fontsize=9)

        ax.set_xlim(-0.5, 1.3)
        ax.set_ylim(0, 1.5)
        ax.axvline(0, color="k", linewidth=0.5, linestyle=":")
        ax.axhline(1.0, color="gray", linewidth=0.5, linestyle="--", alpha=0.5)
        ax.set_xlabel("$U/U_\\infty$", fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.3)
        if i == 0:
            ax.set_ylabel("$y/H$", fontsize=10)
            ax.legend(fontsize=8, loc="upper left")
        else:
            ax.set_yticklabels([])

    fig.suptitle("Ahmed Body 25° — Wake Velocity Profiles vs. Lienhart & Becker (2003)\n"
                 "$k$-$\\omega$ SST, Wall Functions, Fine Mesh (4.4M cells)",
                 fontsize=11, y=1.02)

    plt.tight_layout()
    out = "report/figures/velocity_profiles.pdf"
    plt.savefig(out, dpi=200, bbox_inches="tight")
    print(f"Figure saved: {out}")

    if mae_list:
        print(f"\nMean MAE across stations: {np.mean(mae_list):.3f} (in U/U_inf units)")

    plt.show()


if __name__ == "__main__":
    run()
