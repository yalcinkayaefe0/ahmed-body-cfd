"""
Ahmed body 25 deg — wake velocity profiles from the ERCOFTAC Classic Collection.

Source: ERCOFTAC Classic Collection, Case 082 — "Flow Around a Simplified Car Body
(Ahmed Body)", experiments by H. Lienhart, S. Becker and C. Stoots (LSTM Erlangen).
    http://cfd.mace.manchester.ac.uk/ercoftac/doku.php?id=cases:case082

Data files live in data/ercoftac/ and are the unmodified originals downloaded from
that page. Nothing here is digitised or hand-entered.

ERCOFTAC coordinate system (see the .dat headers):
    x = 0  -> rear face of the body (streamwise, positive downstream)
    y = 0  -> symmetry plane        (lateral)
    z = 0  -> ground plane          (vertical)

NOTE this is NOT the coordinate convention used in the Fluent case, where the
symmetry plane is z = 0 and y is vertical. Map axes before comparing.

Measurement planes available downstream of the body (25 deg slant):
    x = 0, 80, 200, 500 mm    -> H = 288 mm, so x/H = 0, 0.28, 0.69, 1.74

Flow parameters: U_bulk = 40 m/s, H = 288 mm, Re_H = 768,000, nu = 15e-6 m^2/s.

--- STATUS ---
The CFD wake profiles previously in this repository were compared against stations
(x/H = 0.48, 0.61, 0.73, 0.86) that do not exist in this dataset, and the exported
Fluent profiles (results/fine/velocity_profiles.xy) carry no station coordinates at
all. That comparison was therefore removed rather than corrected.

To rebuild it properly, re-export the CFD profiles on the symmetry plane at the four
station locations above, then run this script.
"""

import numpy as np
import matplotlib.pyplot as plt

U_INF = 40.0    # m/s, bulk velocity
H = 288.0       # mm, body height

STATIONS = {
    "x = 0 mm  (x/H = 0.00)":   "data/ercoftac/ahmed-25-xp000-yz.dat",
    "x = 80 mm  (x/H = 0.28)":  "data/ercoftac/ahmed-25-xp080-yz.dat",
    "x = 200 mm (x/H = 0.69)":  "data/ercoftac/ahmed-25-xp200-yz.dat",
    "x = 500 mm (x/H = 1.74)":  "data/ercoftac/ahmed-25-xp500-yz.dat",
}

# Columns: x, y, z, U, V, W, urms, vrms, wrms, uv, uw, ...
COL_Y, COL_Z, COL_U = 1, 2, 3


def load_symmetry_plane(path, y_tol=1.0):
    """Return (z [mm], U [m/s]) on the symmetry plane (y = 0) for one station."""
    d = np.loadtxt(path, comments="#")
    sym = d[np.abs(d[:, COL_Y]) < y_tol]
    order = np.argsort(sym[:, COL_Z])
    return sym[order, COL_Z], sym[order, COL_U]


def main():
    fig, axes = plt.subplots(1, len(STATIONS), figsize=(13, 4.2), sharey=True)

    for ax, (label, path) in zip(axes, STATIONS.items()):
        z, u = load_symmetry_plane(path)
        ax.plot(u / U_INF, z / H, "o", ms=3.5, color="#d7191c",
                label="Lienhart & Becker (ERCOFTAC C.82)")
        ax.axvline(0.0, color="k", lw=0.7, ls="--")
        ax.set_title(label, fontsize=9)
        ax.set_xlabel(r"$U/U_\infty$")
        ax.grid(alpha=0.3, ls="--")
        ax.set_xlim(-0.5, 1.3)

        # --- CFD overlay goes here once profiles are re-exported at these stations ---
        # z_cfd, u_cfd = load_cfd(station)
        # ax.plot(u_cfd / U_INF, z_cfd / H, "-", color="#2c7bb6", label="CFD (k-omega SST)")

    axes[0].set_ylabel(r"$z/H$")
    axes[0].legend(fontsize=7, loc="upper left")
    fig.suptitle("Ahmed Body 25° — Experimental Wake Velocity Profiles, Symmetry Plane\n"
                 "ERCOFTAC Classic Collection Case 082 (Lienhart, Becker & Stoots)",
                 fontsize=10)
    plt.tight_layout()
    out = "report/figures/ercoftac_wake_reference.pdf"
    plt.savefig(out, dpi=200, bbox_inches="tight")
    print(f"Figure saved: {out}")

    for label, path in STATIONS.items():
        z, u = load_symmetry_plane(path)
        print(f"  {label:26} {len(z):3d} points   "
              f"z = {z.min():6.1f}–{z.max():6.1f} mm   "
              f"U/U_inf = {u.min()/U_INF:+.2f}–{u.max()/U_INF:+.2f}")


if __name__ == "__main__":
    main()
