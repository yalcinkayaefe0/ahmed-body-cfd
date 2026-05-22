# Ahmed Body CFD Analysis — Mesh Independence & Validation

25° slant angle | ANSYS Fluent | k-ω SST | Validated against Lienhart & Becker (2003)

## Reference
- **Experimental data:** Lienhart & Becker, SAE 2003-01-0656
- **Target Cd:** 0.299 ± 0.005
- **Flow conditions:** U∞ = 40 m/s, Re ≈ 2.9×10⁶

## Repository Structure
```
ahmed-body-cfd/
├── geometry/          # CAD files (.step, .stl)
├── mesh/              # Mesh files and mesh quality reports
├── results/
│   ├── coarse/        # ~1.5M cells
│   ├── medium/        # ~4M cells
│   └── fine/          # ~10M cells
├── scripts/           # Python post-processing scripts
└── report/            # LaTeX report and figures
    └── figures/
```

## Scripts
| Script | Purpose |
|--------|---------|
| `scripts/y_plus_calculator.py` | First cell height estimation for target y⁺ |
| `scripts/mesh_quality.py` | Plot mesh quality metrics from ANSYS export |
| `scripts/mesh_independence.py` | GCI calculation + convergence plot |
| `scripts/lienhart_comparison.py` | Cd + velocity profile validation |
| `scripts/export_latex_tables.py` | Auto-generate LaTeX tables from results |

## Mesh Independence Summary
*(filled after simulations)*

| Mesh | Cells | Cd | GCI (%) |
|------|-------|----|---------|
| Coarse | — | — | — |
| Medium | — | — | — |
| Fine | — | — | — |

## Results vs. Literature
*(filled after simulations)*
