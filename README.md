# Ahmed Body CFD Analysis — Mesh Independence & Validation

**25° slant angle | ANSYS Fluent 2024 | k-ω SST | Poly-hexcore | Half model**  
Validated against Lienhart & Becker, SAE 2003-01-0656

---

## Geometry

Standard Ahmed body: L = 1044 mm, H = 288 mm, W = 389 mm, ground clearance = 50 mm, slant = 25°.  
Half model with symmetry at z = 0.

<p align="center">
  <img src="geometry/ahmed_body_isometric.png" width="48%" alt="Ahmed body isometric"/>
  <img src="geometry/ahmed_body_side.png" width="48%" alt="Ahmed body side view"/>
</p>

### Computational Domain

Upstream: 5H | Downstream: 15H | Lateral: 5H | Top: 5H

<p align="center">
  <img src="geometry/domain_rear_dimensions.png" width="48%" alt="Domain rear — 4320 mm downstream, 50 mm clearance"/>
  <img src="geometry/domain_overview.png" width="48%" alt="Domain overview"/>
</p>

---

## Mesh

**Tool:** ANSYS Fluent Meshing 2024 — Watertight Geometry workflow, poly-hexcore fill.  
**Boundary layer:** 8 layers, aspect ratio = 40, growth rate = 1.2 → y⁺ ≈ 15–30 (wall functions).

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

<p align="center">
  <img src="mesh/screenshots/watertight_workflow.png" width="32%" alt="Watertight workflow"/>
  <img src="mesh/screenshots/volume_mesh_coarse_settings.png" width="32%" alt="Volume mesh settings"/>
  <img src="mesh/screenshots/surface_mesh_ahmed_body.png" width="32%" alt="Surface mesh"/>
</p>

<p align="center">
  <img src="mesh/screenshots/describe_geometry.png" width="32%" alt="Describe geometry"/>
  <img src="mesh/screenshots/boundary_types.png" width="32%" alt="Boundary types"/>
  <img src="mesh/screenshots/boundary_layer_settings.png" width="32%" alt="Boundary layer settings"/>
</p>

<p align="center">
  <img src="mesh/screenshots/y_plus_calculation.png" width="40%" alt="y+ calculation — Re and first cell height"/>
</p>

---

## Mesh Independence Study

Three mesh levels solved with identical physics settings. GCI per Celik et al. (2008).

| Mesh | Cells | Cd | GCI (%) |
|------|-------|----|---------|
| Coarse | 370k | 0.2990 | 23.3 |
| Medium | 837k | 0.2800 | — |
| Fine | 4.4M | 0.2699 | 5.3 |

Richardson-extrapolated Cd = **0.2584** | Observed order p = **1.14**

<p align="center">
  <img src="results/fine/screenshots/mesh_independence_plot.png" width="80%" alt="Mesh independence convergence plot"/>
</p>

---

## Results

### Coarse Mesh (370k cells — Cd = 0.299)

<p align="center">
  <img src="results/coarse/cd_cl_corrected.png" width="55%" alt="Coarse mesh Cd/Cl"/>
</p>

### Medium Mesh (837k cells — Cd = 0.280)

<p align="center">
  <img src="results/medium/cd_cl.png" width="55%" alt="Medium mesh Cd/Cl"/>
</p>

### Fine Mesh (4.4M cells — Cd = 0.270)

<p align="center">
  <img src="results/fine/screenshots/cd_convergence_early.png" width="48%" alt="Fine mesh Cd convergence"/>
  <img src="results/fine/screenshots/cd_cl_final.png" width="48%" alt="Fine mesh Cd/Cl final"/>
</p>

---

## Validation vs. Lienhart & Becker (2003)

| | CFD (fine mesh) | Lienhart (2003) | Error |
|-|----------------|-----------------|-------|
| Cd | 0.2699 | 0.299 ± 0.005 | −9.7% |
| Cl | −0.323 | −0.082 ± 0.008 | — |

> Cd underprediction is consistent with known k-ω SST + wall function limitations for separated bluff-body aerodynamics. GCI = 5.3% on the fine mesh indicates the solution is approaching but has not fully reached mesh independence — attributed to inconsistent y⁺ values across mesh levels from aspect-ratio BL sizing.

### Wake Velocity Profiles

Streamwise velocity at x/H = 0.48, 0.61, 0.73, 0.86 downstream of body rear.  
Red circles: Lienhart (2003) experimental data. Blue line: CFD k-ω SST.

<p align="center">
  <img src="results/fine/screenshots/velocity_profiles_final.png" width="90%" alt="Wake velocity profiles vs Lienhart"/>
</p>

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/y_plus_calculator.py` | First cell height for target y⁺ |
| `scripts/mesh_independence.py` | GCI calculation + convergence plot → `report/figures/mesh_independence.pdf` |
| `scripts/lienhart_comparison.py` | Wake profile validation → `report/figures/velocity_profiles.pdf` |

```bash
python scripts/y_plus_calculator.py
python scripts/mesh_independence.py
python scripts/lienhart_comparison.py   # requires results/fine/velocity_profiles.xy
```

---

## Repository Structure

```
ahmed-body-cfd/
├── geometry/
│   ├── ahmed_body_isometric.png
│   ├── ahmed_body_side.png
│   ├── domain_rear_dimensions.png
│   └── domain_overview.png
├── mesh/
│   └── screenshots/          # Fluent Meshing workflow, BL settings, surface mesh
├── results/
│   ├── coarse/               # Cd = 0.299
│   ├── medium/               # Cd = 0.280
│   └── fine/
│       ├── velocity_profiles.xy
│       └── screenshots/      # Convergence, Cd/Cl, post-processing
├── scripts/
│   ├── y_plus_calculator.py
│   ├── mesh_independence.py
│   └── lienhart_comparison.py
└── report/
    ├── main.tex
    └── figures/
        ├── mesh_independence.pdf
        └── velocity_profiles.pdf
```

---

## Reference

Lienhart, H. & Becker, S. (2003). *Flow and turbulence structure in the wake of a simplified car model.* SAE 2003-01-0656.
