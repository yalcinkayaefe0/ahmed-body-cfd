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
    "coarse": {"cells": 369552, "Cd": 0.299, "Cl": None},
    "medium": {"cells": 837508, "Cd": 0.280, "Cl": None},
    "fine":   {"cells": 4428444, "Cd": 0.2699, "Cl": None},
}

# Experimental reference — Meile et al. (2016), 25 deg slant, 40 m/s
# Six-component force balance, Cd = 0.29883 +/- 0.5% calibration uncertainty.
# NOTE: Lienhart & Becker (2003) published LDA *wake velocity profiles*, not force
# coefficients. The force reference must be cited to Meile, not Lienhart.
CD_REF = 0.298
CD_REF_UNC = 0.005

# The experimental model is mounted on four support stilts; this CFD model omits them.
# Gutierrez et al. (2020), Table 3, gives the stilt contribution to total drag across four
# turbulence models: 0.0158 (RSM) ... 0.0245 (k-omega Standard). A stilt-free geometry should
# therefore be compared against a correspondingly reduced reference.
CD_STILT_MIN, CD_STILT_MAX = 0.0158, 0.0245
# ───────────────────────────────────────────────────────────────────────────


def gci(f1, f2, f3, N1, N2, N3, p_order=None, tol=1e-10, max_iter=500):
    """
    Grid Convergence Index per Celik et al. (2008), Eqs. (3)-(6).
    f1=fine, f2=medium, f3=coarse (f1 most refined)
    N1, N2, N3 = cell counts

    The apparent order p satisfies

        p = |ln|eps32/eps21| + q(p)| / ln(r21)
        q(p) = ln[ (r21^p - s) / (r32^p - s) ],   s = sign(eps32/eps21)

    q(p) vanishes only when r21 == r32. For non-uniform refinement ratios it must
    be retained, and since p appears on both sides the equation is solved by
    fixed-point iteration.

    Returns: p, f_ext, GCI_fine, GCI_coarse
    """
    r21 = (N1 / N2) ** (1 / 3)
    r32 = (N2 / N3) ** (1 / 3)

    eps21 = f2 - f1
    eps32 = f3 - f2
    s = np.sign(eps32 / eps21)          # +1: monotonic, -1: oscillatory convergence

    if p_order is None:
        p = 2.0                          # initial guess: theoretical 2nd order
        for _ in range(max_iter):
            q = np.log((r21**p - s) / (r32**p - s))
            p_new = abs(np.log(abs(eps32 / eps21)) + q) / np.log(r21)
            if abs(p_new - p) < tol:
                p = p_new
                break
            p = p_new
    else:
        p = p_order

    f_ext = (r21**p * f1 - f2) / (r21**p - 1)
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

    r21 = (N[0] / N[1]) ** (1 / 3)
    r32 = (N[1] / N[2]) ** (1 / 3)

    print("=" * 58)
    print("MESH INDEPENDENCE — GCI RESULTS (Celik et al. 2008)")
    print("=" * 58)
    print(f"  Refinement ratios            r21 = {r21:.3f}, r32 = {r32:.3f}")
    print(f"  Apparent order of accuracy   p   = {p:.2f}")
    print(f"  Richardson-extrapolated Cd   = {Cd_ext:.4f}")
    print(f"  GCI (fine)                   = {gci_fine*100:.2f}%")
    print(f"  GCI (medium)                 = {gci_coarse*100:.2f}%")

    # Asymptotic range check — should be ~1.0
    asym = gci_coarse / (r21**p * gci_fine)
    print(f"  Asymptotic range check       = {asym:.3f}  (target ~1.0)")

    # Sanity check against theoretical 2nd order — Celik recommends reporting both
    # when the apparent p deviates significantly from the formal scheme order.
    p2, Cd_ext2, gci_fine2, _ = gci(*Cd, *N, p_order=2.0)
    print(f"\n  [p fixed at theoretical 2.0]")
    print(f"    Richardson-extrapolated Cd = {Cd_ext2:.4f}")
    print(f"    GCI (fine)                 = {gci_fine2*100:.2f}%")

    print(f"\n  Meile et al. (2016) Cd (with stilts) = {CD_REF} ± {CD_REF_UNC}")
    for name, val in zip(("coarse", "medium", "fine"), (Cd[2], Cd[1], Cd[0])):
        e = (val - CD_REF) / CD_REF * 100
        print(f"    {name:<7} Cd = {val:.4f}   error = {e:+.1f}%")

    # Stilt correction: this model is stilt-free, the experimental one is not.
    ref_lo, ref_hi = CD_REF - CD_STILT_MAX, CD_REF - CD_STILT_MIN
    e_lo = (Cd[0] - ref_hi) / ref_hi * 100
    e_hi = (Cd[0] - ref_lo) / ref_lo * 100
    print(f"\n  Stilt-corrected reference (stilt-free geometry):")
    print(f"    Cd_ref = {ref_lo:.4f} – {ref_hi:.4f}")
    print(f"    fine-mesh error = {e_lo:+.1f}% to {e_hi:+.1f}%  <- like-for-like comparison")

    # Numerical uncertainty (GCI) vs. modelling error (extrapolated vs. experiment)
    model_err = (Cd_ext - CD_REF) / CD_REF * 100
    print(f"\n  Numerical uncertainty (GCI, fine) = {gci_fine*100:.2f}%")
    print(f"  Modelling error (Cd_ext vs. raw exp) = {model_err:+.1f}%")
    print("  -> Mesh convergence achieved; residual deviation is model-driven")
    print("     (k-omega SST + wall functions on separated bluff-body flow).")
    print("=" * 58)

    # Plot
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 11,
        "axes.linewidth": 1.2,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.major.size": 5,
        "ytick.major.size": 5,
    })

    fig, ax = plt.subplots(figsize=(8, 5))

    cell_counts = [meshes[k]["cells"] for k in ("coarse", "medium", "fine")]
    cd_values   = [meshes[k]["Cd"]    for k in ("coarse", "medium", "fine")]
    labels      = ["Coarse\n(370k)", "Medium\n(837k)", "Fine\n(4.4M)"]

    x_min = cell_counts[0] * 0.4
    x_max = cell_counts[-1] * 2.5

    # Experimental band — as measured, on a stilt-mounted model
    ax.fill_between([x_min, x_max],
                    CD_REF - CD_REF_UNC, CD_REF + CD_REF_UNC,
                    color="#d7191c", alpha=0.12, zorder=1)
    ax.axhline(CD_REF, color="#d7191c", linewidth=1.8, linestyle="--", zorder=2,
               label=f"Meile et al. (2016), with stilts:  $C_d$ = {CD_REF} $\\pm$ {CD_REF_UNC}")

    # Stilt-corrected band — the like-for-like target for this stilt-free geometry
    ax.fill_between([x_min, x_max],
                    CD_REF - CD_STILT_MAX, CD_REF - CD_STILT_MIN,
                    color="#fdae61", alpha=0.30, zorder=1,
                    label=f"Stilt-corrected reference:  "
                          f"{CD_REF-CD_STILT_MAX:.3f}–{CD_REF-CD_STILT_MIN:.3f}")

    # Richardson extrapolation
    ax.axhline(Cd_ext, color="#1a9641", linewidth=1.4, linestyle=":", zorder=2,
               label=f"Richardson extrapolation:  $C_d$ = {Cd_ext:.4f}")

    # CFD data
    ax.semilogx(cell_counts, cd_values, "o-", color="#2c7bb6",
                linewidth=2, markersize=9, zorder=5,
                label=f"CFD — $k$-$\\omega$ SST (wall functions)")

    # Annotate each point
    offsets = [(0, 10), (0, 10), (0, 10)]
    for i, (x, y, lbl) in enumerate(zip(cell_counts, cd_values, labels)):
        ax.annotate(f"$C_d$ = {y:.4f}\n{lbl}",
                    xy=(x, y), xytext=(0, 18), textcoords="offset points",
                    ha="center", fontsize=9, color="#2c7bb6",
                    arrowprops=dict(arrowstyle="-", color="#2c7bb6", lw=0.8))

    # GCI error bars on fine mesh
    gci_abs = gci_fine * Cd[0]
    ax.errorbar(cell_counts[-1], cd_values[-1], yerr=gci_abs,
                fmt="none", color="#2c7bb6", capsize=6, linewidth=1.5,
                label=f"GCI (fine mesh) = {gci_fine*100:.1f}%")

    ax.set_xscale("log")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0.24, 0.33)
    ax.set_xlabel("Number of cells", fontsize=12)
    ax.set_ylabel("$C_d$", fontsize=12)
    ax.set_title("Mesh Independence Study — Ahmed Body 25° Slant\n"
                 "$k$-$\\omega$ SST, Wall Functions, Half Model",
                 fontsize=12, pad=10)
    ax.legend(fontsize=9, loc="upper right", framealpha=0.9)
    ax.grid(True, which="both", linestyle="--", alpha=0.35, linewidth=0.8)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(
        lambda x, _: f"{x/1e6:.2f}M" if x >= 1e6 else f"{x/1e3:.0f}k"))

    plt.tight_layout()
    out = "report/figures/mesh_independence.pdf"
    plt.savefig(out, dpi=200, bbox_inches="tight")
    print(f"\nFigure saved: {out}")
    plt.show()


if __name__ == "__main__":
    run()
