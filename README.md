# Ahmed Body CFD Analysis — Mesh Independence & Validation

25° slant angle | ANSYS Fluent | k-ω SST (wall functions) | Half model | Validated against Lienhart & Becker (2003)

## Reference
- **Experimental data:** Lienhart & Becker, SAE 2003-01-0656
- **Target Cd:** 0.299 ± 0.005
- **Flow conditions:** U∞ = 40 m/s, Re ≈ 2.9×10⁶, L = 1.044 m

## Mesh Independence Summary

| Mesh | Cells | Cd | GCI (%) |
|------|-------|----|---------|
| Coarse | 370k | 0.2990 | 23.3 |
| Medium | 837k | 0.2800 | — |
| Fine | 4.4M | 0.2699 | 5.3 |

Richardson-extrapolated Cd = **0.2584**  
Observed order of accuracy p = **1.14**

## Results vs. Literature

| | CFD (fine mesh) | Lienhart (2003) | Error |
|-|----------------|-----------------|-------|
| Cd | 0.2699 | 0.299 ± 0.005 | 9.7% |
| Cl | −0.323 | −0.082 ± 0.008 | — |

> Cd underprediction is consistent with known k-ω SST + wall function limitations for bluff body aerodynamics. GCI of 5.3% on the fine mesh indicates the solution is approaching but has not fully reached mesh independence — attributed to inconsistent y⁺ values across mesh levels due to aspect-ratio-based BL sizing.

## Mesh Setup

| Parameter | Value |
|-----------|-------|
| Solver | ANSYS Fluent 2024 |
| Mesh type | Poly-hexcore (Watertight Geometry) |
| Turbulence model | k-ω SST |
| Wall treatment | Wall functions (y⁺ ≈ 15–30) |
| BL layers | 8, AR = 40, growth rate 1.2 |
| Inlet velocity | 40 m/s |
| Ground | Moving wall, 40 m/s |
| Symmetry | Half model (z = 0 plane) |

## Repository Structure
```
ahmed-body-cfd/
├── geometry/          # CAD files (.step, .stl)
├── mesh/              # Mesh quality screenshots
├── results/
│   ├── coarse/        # 370k cells
│   ├── medium/        # 837k cells
│   └── fine/          # 4.4M cells
├── scripts/
│   ├── y_plus_calculator.py     # First cell height for target y+
│   ├── mesh_independence.py     # GCI analysis + convergence plot
│   └── lienhart_comparison.py   # Velocity profile validation
└── report/
    └── figures/
        └── mesh_independence.pdf
```

## Scripts
| Script | Purpose |
|--------|---------|
| `scripts/y_plus_calculator.py` | First cell height estimation for target y⁺ |
| `scripts/mesh_independence.py` | GCI calculation + convergence plot |
| `scripts/lienhart_comparison.py` | Cd + velocity profile validation vs. Lienhart |
