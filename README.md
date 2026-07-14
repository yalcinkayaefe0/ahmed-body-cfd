# Ahmed Body CFD Analysis — Mesh Independence & Validation

**25° slant angle | ANSYS Fluent 2024 | k-ω SST | Poly-hexcore | Half model**

**Experimental references.** Two separate sources are used, and they are not interchangeable:
- **Force coefficients** — Meile et al. (2016): `Cd = 0.29883 ± 0.5%` (six-component balance, 40 m/s);
  Meile et al. (2011): `Cl = +0.345`.
- **Wake velocity profiles** — Lienhart & Becker (2003), SAE 2003-01-0656 (LDA). *This paper does not
  report force coefficients and must not be cited for Cd or Cl.*

> ⚠️ **Open issues — see [Known Issues](#known-issues) before using these results.** The Cl sign is
> inverted on the medium/fine meshes, and the wake comparison has been withdrawn pending re-export
> of the CFD profiles at the correct experimental stations.

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

Three mesh levels solved with identical physics settings. GCI per Celik et al. (2008), with the
apparent order `p` solved by fixed-point iteration (the `q(p)` term is retained — the refinement
ratios are non-uniform: r21 = 1.742, r32 = 1.314).

| Mesh | Cells | Cd | GCI (%) | Error vs. raw exp. |
|------|-------|----|---------|--------------------|
| Coarse | 370k | 0.2990 | — | +0.3% |
| Medium | 837k | 0.2800 | 5.25 | −6.0% |
| Fine | 4.4M | 0.2699 | **0.77** | −9.4% |

Richardson-extrapolated Cd = **0.2682** | Apparent order p = **3.53** | Asymptotic range check = **0.96**

> With `p` fixed at the theoretical 2nd order: Cd_ext = 0.2649, GCI_fine = 2.30% — same conclusion.
> The fine-mesh numerical uncertainty (<1%) is an order of magnitude smaller than the deviation
> from experiment, so the residual error is **modelling error, not discretisation error**.

### Stilt correction — the like-for-like comparison

The experimental model sits on four support stilts. **This CFD model has none**, so comparing it
directly against the measured 0.298 charges it with drag it never generated. Gutierrez et al. (2020,
Table 3) decompose drag by surface and give the stilt contribution as ΔCd = 0.0158 (RSM) to 0.0245
(k-ω Standard):

| Reference | Cd | Fine-mesh error |
|---|---|---|
| Raw measured (with stilts) | 0.298 | −9.4% |
| **Stilt-corrected (stilt-free)** | **0.2735 – 0.2822** | **−1.3% to −4.4%** |

The coarse mesh looks almost exact against the raw value (+0.3%) purely through compensating
errors — excess numerical diffusion inflates its drag, offsetting both the model's underprediction
and the missing stilt drag. Agreement on an unconverged mesh is not evidence of a correct solution.

<p align="center">
  <img src="results/fine/screenshots/mesh_independence_plot.png" width="80%" alt="Mesh independence convergence plot"/>
</p>

---

## Results

### Coarse Mesh (370k cells — Cd = 0.299, Cl = **+0.336**)

Note the **positive** Cl here — matching the experimental +0.345 to within 2.6%. The sign inverts on
the finer meshes; see [Known Issues](#known-issues).

<p align="center">
  <img src="results/coarse/cd_cl_initial.png" width="55%" alt="Coarse mesh Cd/Cl"/>
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

## Validation vs. Experiment

| | CFD (fine mesh) | Experiment | Error |
|-|----------------|------------|-------|
| Cd (vs. stilt-corrected ref.) | 0.2699 | 0.2735 – 0.2822 | **−1.3% to −4.4%** |
| Cl | −0.323 ⚠️ | +0.345 (Meile 2011) | **sign error — see below** |

> Cd underprediction is consistent with known k-ω SST + wall function limitations for separated
> bluff-body aerodynamics. Crucially, the fine-mesh GCI is 0.77% — the solution *is* mesh
> independent, so the residual deviation is model error, not a resolution problem.

---

## Known Issues

**1. Cl sign is inverted on the medium and fine meshes.**
The experimental Cl for a 25° slant is **positive** (+0.345, Meile et al. 2011; Gutierrez et al.
2020 obtain +0.363 and +0.376). Physically, the slow flow between road and underbody keeps the
underbody pressure higher than the upper-surface pressure, producing net positive lift.

The evidence that this is a post-processing error is internal to this study:

| Mesh | Cl | Sign | Deviation from exp. (\|Cl\|) |
|---|---|---|---|
| Coarse (370k) | **+0.3357** | correct | −2.6% |
| Medium (837k) | −0.3235 | inverted | −6.2% |
| Fine (4.4M) | −0.3232 | inverted | −6.3% |

All three runs agree on the **magnitude**; only the sign flips after the coarse run. A physical
modelling deficiency would corrupt the magnitude, not negate it while preserving it. The cause is a
change to the lift force report definition (direction vector) made between the coarse and medium
runs.

Sign-corrected, the fine-mesh value is **Cl = +0.323** (−6.3% from experiment) — the same order as
the Cd deviation. **Action:** verify the lift direction vector in Fluent and re-extract Cl for the
medium and fine meshes.

**2. The wake comparison was withdrawn (not corrected).**
An earlier revision plotted CFD wake profiles against a hand-entered "Lienhart & Becker" table at
stations x/H = 0.48, 0.61, 0.73, 0.86. Checking against the real source — **ERCOFTAC Classic
Collection, [Case 082](http://cfd.mace.manchester.ac.uk/ercoftac/doku.php?id=cases:case082)** —
showed two problems:

- Those stations **do not exist** in the experiment. The measured planes are at x = 0, 80, 200,
  500 mm (x/H = 0, 0.28, 0.69, 1.74). The tabulated values didn't match the real data either: the
  experiment shows reverse flow reaching **U/U∞ = −0.34** at x = 80 mm, an order of magnitude
  stronger than what had been tabulated.
- The Fluent export (`results/fine/velocity_profiles.xy`) labels its blocks `wake_x1`–`wake_x4` and
  **records no streamwise coordinate**, so the computed profiles cannot be located either.

Fixing the reference alone wouldn't have made the comparison valid, so it was removed. The genuine
ERCOFTAC data is now in `data/ercoftac/` and `scripts/ercoftac_wake_reference.py` reads it directly.
**Next step:** re-export the CFD symmetry-plane profiles at the four experimental stations.

### Experimental Wake Reference

The genuine Lienhart & Becker wake measurements (ERCOFTAC Case 082) are included in
`data/ercoftac/`, unmodified. Measurement planes: x = 0, 80, 200, 500 mm behind the body.
A CFD comparison against them is the next step — see [Known Issues](#known-issues).

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/y_plus_calculator.py` | First cell height for target y⁺ |
| `scripts/mesh_independence.py` | GCI calculation + convergence plot → `report/figures/mesh_independence.pdf` |
| `scripts/ercoftac_wake_reference.py` | Plots the experimental wake reference from `data/ercoftac/` (ERCOFTAC Case 082) |

```bash
python scripts/y_plus_calculator.py
python scripts/mesh_independence.py
python scripts/ercoftac_wake_reference.py
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
│   └── ercoftac_wake_reference.py
├── data/
│   └── ercoftac/             # ERCOFTAC Case 082 experimental data (unmodified)
└── report/
    ├── main.tex
    └── figures/
        ├── mesh_independence.pdf
        └── velocity_profiles.pdf
```

---

## References

- **Lienhart, H. & Becker, S. (2003).** *Flow and turbulence structure in the wake of a simplified car model.* SAE 2003-01-0656. — LDA wake velocity profiles. **Does not report force coefficients.**
- **Meile, W., Brenn, G., Reppenhagen, A. & Fuchs, A. (2011).** *Experiments and numerical simulations on the aerodynamics of the Ahmed body.* CFD Letters, 3(1), 32–39. — Cl = +0.345.
- **Meile, W., Ladinek, T., Brenn, G., Reppenhagen, A. & Fuchs, A. (2016).** *Non-symmetric bi-stable flow around the Ahmed body.* Int. J. Heat and Fluid Flow, 57, 34–47. — Cd = 0.29883 ± 0.5%.
- **Chavez Gutierrez, J.E., Vera Duarte, L.E., Oliveira Jr., A.A.M. & Cancino, L.R. (2020).** *The Ahmed body's external aerodynamics at 25° slant angle rear surface.* ENCIT 2020, ENC-2020-0060. — Surface-by-surface drag/lift decomposition (stilt contribution).
- **Celik, I.B. et al. (2008).** *Procedure for estimation and reporting of uncertainty due to discretization in CFD applications.* J. Fluids Eng., 130(7), 078001. — GCI methodology.
- **Ahmed, S.R., Ramm, G. & Faltin, G. (1984).** *Some salient features of the time-averaged ground vehicle wake.* SAE 840300.
