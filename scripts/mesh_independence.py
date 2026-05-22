"""
Mesh Independence Study — GCI Method
Celik et al. (2008), Journal of Fluids Engineering

Usage:
  Edit the RESULTS section below with your Cd values and cell counts,
  then run: python scripts/mesh_independence.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ── RESULTS: fill these after running simulations ──────────────────────────
meshes = {
    "coarse": {"cells": None, "Cd": None, "Cl": None},
    "medium": {"cells": None, "Cd": None, "Cl": None},
    "fine":   {"cells": None, "Cd": None, "Cl": None},
}

# Lienhart & Becker (2003) experimental reference
CD_REF = 0.299
CD_REF_UNC = 0.005  # uncertainty
# ───────────────────────────────────────────────────────────────────────────


def gci(f1, f2, f3, N1, N2, N3, p_order=None):
    """
    Grid Convergence Index per Celik et al. (2008).
    f1=fine, f2=medium, f3=coarse (f1 most refined)
    N1, N2, N3 = cell counts
    Returns: p (order), f_ext (extrapolated value), GCI_fine, GCI_coarse
    """
    r21 = (N1 / N2) ** (1 / 3)
    r32 = (N2 / N3) ** (1 / 3)

    eps21 = f2 - f1
    eps32 = f3 - f2
    q = np.log(abs(eps32 / eps21) + 1e-16)

    # Iterative solve for p
    if p_order is None:
        p = abs(np.log(abs(eps32 / eps21)) / np.log(r21))
    else:
        p = p_order

    f_ext = f1 + (f1 - f2) / (r21**p - 1)
    e21_a  = abs((f1 - f2) / f1)
    GCI_fine   = 1.25 * e21_a / (r21**p - 1)
    GCI_coarse = 1.25 * abs((f2 - f3) / f2) / (r32**p - 1)
    return p, f_ext, GCI_fine, GCI_coarse


def check_data():
    for name, m in meshes.items():
        if m["cells"] is None or m["Cd"] is None:
            print(f"[!] '{name}' mesh data is missing. Edit the RESULTS section first.")
            return False
    return True


def run():
    if not check_data():
        return

    N = [meshes[k]["cells"] for k in ("fine", "medium", "coarse")]
    Cd = [meshes[k]["Cd"]   for k in ("fine", "medium", "coarse")]

    p, Cd_ext, gci_fine, gci_coarse = gci(*Cd, *N)

    print("=" * 50)
    print("MESH INDEPENDENCE — GCI RESULTS")
    print("=" * 50)
    print(f"  Observed order of accuracy p = {p:.2f}")
    print(f"  Richardson-extrapolated Cd   = {Cd_ext:.4f}")
    print(f"  GCI (fine→medium)            = {gci_fine*100:.2f}%")
    print(f"  GCI (medium→coarse)          = {gci_coarse*100:.2f}%")
    print(f"  Lienhart reference Cd        = {CD_REF} ± {CD_REF_UNC}")
    err = abs(Cd[0] - CD_REF) / CD_REF * 100
    print(f"  Fine mesh vs. experiment     = {err:.2f}%")
    if err < 5:
        print("  [PASS] Within 5% tolerance")
    else:
        print("  [WARN] Outside 5% tolerance — check turbulence model/BCs")
    print("=" * 50)

    # Plot
    fig, ax = plt.subplots(figsize=(7, 4))
    cell_counts = [meshes[k]["cells"] for k in ("coarse", "medium", "fine")]
    cd_values   = [meshes[k]["Cd"]    for k in ("coarse", "medium", "fine")]

    ax.semilogx(cell_counts, cd_values, "o-", color="#2c7bb6",
                linewidth=2, markersize=8, label="CFD (k-$\\omega$ SST)")
    ax.axhline(CD_REF, color="#d7191c", linewidth=1.5, linestyle="--",
               label=f"Lienhart et al. (2003): $C_d$ = {CD_REF}")
    ax.fill_between([cell_counts[0]*0.5, cell_counts[-1]*2],
                    CD_REF - CD_REF_UNC, CD_REF + CD_REF_UNC,
                    color="#d7191c", alpha=0.15, label=f"Exp. uncertainty ±{CD_REF_UNC}")
    ax.axhline(Cd_ext, color="#1a9641", linewidth=1.2, linestyle=":",
               label=f"Richardson extrapolation: {Cd_ext:.4f}")

    ax.set_xlabel("Number of cells", fontsize=12)
    ax.set_ylabel("$C_d$", fontsize=12)
    ax.set_title("Mesh Independence Study — Ahmed Body 25°", fontsize=13)
    ax.legend(fontsize=9)
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))

    plt.tight_layout()
    out = "report/figures/mesh_independence.pdf"
    plt.savefig(out, dpi=150)
    print(f"\nFigure saved: {out}")
    plt.show()


if __name__ == "__main__":
    run()
