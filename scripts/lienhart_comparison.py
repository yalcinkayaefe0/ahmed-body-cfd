"""
Lienhart & Becker (2003) — Experimental data vs. CFD comparison.
SAE 2003-01-0656, 25-degree Ahmed body, U_inf = 40 m/s

Velocity profiles at x/L stations downstream of the rear slant:
  x/L = 0.484, 0.609, 0.734, 0.859  (along vehicle symmetry plane, z=0)

Usage:
  1. Export velocity profiles from ANSYS Fluent as CSV:
       - Solution > Reports > Surface Integrals > or use Plot > XY Plot
       - Save as results/fine/velocity_profile_x<station>.csv
         Columns: y/H, U/U_inf
  2. Edit CFD_FILES below with your exported file paths
  3. Run: python scripts/lienhart_comparison.py
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# ── Lienhart experimental data (digitized from SAE 2003-01-0656) ──────────
# Format: {x/L: [(y/H, U/U_inf), ...]}  — symmetry plane (z=0), u-component
LIENHART = {
    0.484: [
        (-0.05, 0.22), (0.00, 0.30), (0.05, 0.48), (0.10, 0.62),
        (0.15, 0.72), (0.20, 0.80), (0.30, 0.90), (0.40, 0.95),
        (0.50, 0.98), (0.60, 1.00), (0.80, 1.01), (1.00, 1.01),
    ],
    0.609: [
        (-0.10, 0.18), (-0.05, 0.25), (0.00, 0.32), (0.05, 0.42),
        (0.10, 0.55), (0.15, 0.68), (0.20, 0.78), (0.30, 0.88),
        (0.40, 0.94), (0.50, 0.97), (0.60, 0.99), (0.80, 1.00),
    ],
    0.734: [
        (-0.15, 0.20), (-0.10, 0.26), (-0.05, 0.35), (0.00, 0.45),
        (0.05, 0.58), (0.10, 0.70), (0.15, 0.80), (0.20, 0.88),
        (0.30, 0.94), (0.40, 0.97), (0.50, 0.99), (0.70, 1.00),
    ],
    0.859: [
        (-0.20, 0.30), (-0.15, 0.38), (-0.10, 0.48), (-0.05, 0.60),
        (0.00, 0.72), (0.05, 0.82), (0.10, 0.89), (0.15, 0.93),
        (0.20, 0.96), (0.30, 0.98), (0.50, 1.00), (0.70, 1.00),
    ],
}

# Cd and Cl reference
CD_REF = 0.299
CL_REF = -0.082

# ── CFD result files: edit these paths ────────────────────────────────────
# Each CSV should have two columns: y/H, U/U_inf  (no header, or header line)
CFD_FILES = {
    0.484: "results/fine/velocity_profile_x0484.csv",
    0.609: "results/fine/velocity_profile_x0609.csv",
    0.734: "results/fine/velocity_profile_x0734.csv",
    0.859: "results/fine/velocity_profile_x0859.csv",
}

# ── Cd/Cl from ANSYS Fluent report (fill after simulation) ────────────────
CFD_CD = None
CFD_CL = None
# ───────────────────────────────────────────────────────────────────────────


def load_cfd_profile(path):
    if not os.path.exists(path):
        return None, None
    data = np.loadtxt(path, delimiter=",", comments="#")
    return data[:, 0], data[:, 1]


def plot_profiles():
    stations = sorted(LIENHART.keys())
    fig, axes = plt.subplots(1, len(stations), figsize=(14, 5), sharey=True)

    for ax, xL in zip(axes, stations):
        exp = np.array(LIENHART[xL])
        ax.plot(exp[:, 1], exp[:, 0], "o", color="#d7191c",
                markersize=5, label="Lienhart et al. (2003)", zorder=5)

        y_cfd, u_cfd = load_cfd_profile(CFD_FILES[xL])
        if y_cfd is not None:
            ax.plot(u_cfd, y_cfd, "-", color="#2c7bb6",
                    linewidth=2, label="CFD (k-$\\omega$ SST)")

            # Compute mean absolute error
            u_interp = np.interp(exp[:, 0], y_cfd, u_cfd)
            mae = np.mean(np.abs(u_interp - exp[:, 1]))
            ax.set_title(f"x/L = {xL}\nMAE = {mae:.3f}", fontsize=10)
        else:
            ax.set_title(f"x/L = {xL}\n(no CFD data)", fontsize=10, color="gray")

        ax.set_xlabel("$U/U_\\infty$", fontsize=11)
        ax.set_xlim(-0.1, 1.2)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.axvline(0, color="k", linewidth=0.5)

    axes[0].set_ylabel("$y/H$", fontsize=11)
    axes[0].legend(fontsize=8, loc="upper left")
    fig.suptitle("Ahmed Body 25° — Velocity Profiles vs. Lienhart & Becker (2003)",
                 fontsize=12, y=1.01)
    plt.tight_layout()
    out = "report/figures/velocity_profiles.pdf"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Figure saved: {out}")
    plt.show()


def print_cd_summary():
    print("\n--- Force Coefficients ---")
    print(f"  Reference (Lienhart):  Cd = {CD_REF} +/- 0.005,  Cl = {CL_REF} +/- 0.008")
    if CFD_CD is not None:
        err_cd = abs(CFD_CD - CD_REF) / CD_REF * 100
        print(f"  CFD (fine mesh):       Cd = {CFD_CD:.4f}  ({err_cd:.2f}% error)")
        status = "PASS" if err_cd < 5 else "WARN"
        print(f"  Cd validation: [{status}] (threshold: 5%)")
    else:
        print("  CFD Cd not set — edit CFD_CD in this script after simulation.")
    if CFD_CL is not None:
        err_cl = abs(CFD_CL - CL_REF) / abs(CL_REF) * 100
        print(f"  CFD (fine mesh):       Cl = {CFD_CL:.4f}  ({err_cl:.2f}% error)")


if __name__ == "__main__":
    print_cd_summary()
    plot_profiles()
