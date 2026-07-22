# Ahmed Body CFD Analysis — Mesh Independence & Validation

**25° slant angle | ANSYS Fluent 2024 | k-ω SST | Poly-hexcore | Half model**

**Experimental references.** Two separate sources are used, and they are not interchangeable:
- **Force coefficients** — Meile et al. (2016): `Cd = 0.29883 ± 0.5%` (six-component balance, 40 m/s);
  Meile et al. (2011): `Cl = +0.345`.
- **Wake velocity profiles** — Lienhart & Becker (2003), SAE 2003-01-0656 (LDA). *This paper does not
  report force coefficients and must not be cited for Cd or Cl.*

**Headline result** (fine mesh, stationary ground, matching the experimental configuration):
`Cd = 0.27908` — inside the stilt-corrected experimental band — and `Cl = +0.35525`, **+3.0%** from
the measured value.

> **Scope.** This study validates the **force coefficients** (Cd, Cl) against measurement. Wake
> profile validation is out of scope — an earlier attempt was withdrawn as unsound and the reasoning
> is kept on the record in [Known Issues](#known-issues), along with two setup errors (Cl sign
> inversion, ground-condition mismatch) that were found and resolved rather than deleted.

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

> **Note on y⁺.** The achieved range sits in the buffer layer (5 < y⁺ < 30), where neither near-wall
> strategy is strictly valid — wall functions assume y⁺ > 30, low-Re resolution needs y⁺ < 1. This
> follows from sizing the first layer by aspect ratio rather than absolute thickness, and is the
> likely cause of the inconsistent y⁺ across mesh levels. `scripts/y_plus_calculator.py` reports the
> first-cell height for both strategies.

**Reynolds number:** Re_L = 2.78×10⁶ on body length, Re_H = 7.68×10⁵ on body height, using the
reference experiment's kinematic viscosity ν = 15×10⁻⁶ m²/s — which reproduces the Re_H quoted in
ERCOFTAC Case 082 exactly. All Re figures in this repository use this value.

| Parameter | Value |
|-----------|-------|
| Solver | ANSYS Fluent 2024 |
| Mesh type | Poly-hexcore (Watertight Geometry) |
| Turbulence model | k-ω SST |
| Wall treatment | Wall functions (y⁺ ≈ 15–30) |
| BL layers | 8, AR = 40, growth rate 1.2 |
| Inlet velocity | 40 m/s |
| Ground | **Stationary wall** (matching the experiments — see [issue 3](#known-issues); mesh independence study was run on a moving wall) |
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

### Mesh Quality

Reported by Fluent (`/mesh/quality`) on the volume mesh:

| Metric | Coarse (370k) | Medium (837k) | Fine (4.4M) | Acceptable |
|---|---|---|---|---|
| Min orthogonal quality | 0.1638 | 0.1637 | 0.1537 | > 0.01 required, > 0.1 good |
| Max tangent skewness \* | 6.022 | 6.025 | 6.427 | see note |
| Max aspect ratio | **122.21** | **122.72** | **122.21** | High values expected in prism layers |

> \* Fluent's *tangent-skewness* measure as printed by `/mesh/quality` — **not** the conventional
> skewness bounded on [0, 1], so it must not be read against the usual < 0.95 guideline.

**The aspect ratio is essentially identical across all three levels — despite a 12× increase in cell
count.** This is not a coincidence but a direct measurement of how the mesh family was built: the
boundary-layer settings (8 layers, first AR 40, growth rate 1.2) were held fixed at every level, so
refinement acted **only on the hexcore freestream cells while the prism layers stayed put**.

That matters for the GCI. The apparent order p = 3.53 exceeds the scheme's formal 2nd-order
accuracy, and the report attributes this to a mesh family that is not self-similar — prism and
freestream cells refining at different rates, leaving y⁺ un-held across levels. These numbers are
the quantitative evidence for that argument, which until now rested on reasoning alone. A fixed
first-layer *thickness* instead of a fixed aspect ratio would refine both regions together.

**Where the worst cells sit.** All three meshes place them at the same location — coarse
`(0.506, 0.0499, 0.178)`, medium `(0.522, 0.0586, 0.186)`, fine `(0.518, 0.0500, 0.190)`, all in
zone 308. Read against the geometry: `y ≈ 0.050 m` is exactly the 50 mm ground clearance,
`x ≈ 0.51 m` is mid-body (L = 1.044 m), and `z ≈ 0.18 m` is near the side edge (half-width
0.194 m) — i.e. the **lower side edge of the underbody**, where the prism stack is squeezed into a
sharp dihedral corner. In each mesh the worst orthogonal-quality cell is also the worst-skewness
cell, with the worst-aspect-ratio cell a fraction of a millimetre away. Refinement relocates
nothing, because the constraint is geometric rather than resolution-driven.

Given GCI_fine = 0.77%, these cells do not measurably affect the solution.

> Aspect ratio ~122 against a target first-layer AR of 40 is expected: the target governs the first
> layer, while the reported maximum is taken over the whole boundary-layer stack.

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

### Coarse Mesh (370k cells — Cd = 0.299, Cl = **+0.3357**)

This run had the correct lift force vector from the start; the medium and fine cases did not, which
is how the sign error in [issue 1](#known-issues) was caught.

<p align="center">
  <img src="results/coarse/cd_cl_initial.png" width="55%" alt="Coarse mesh Cd/Cl"/>
</p>

### Medium Mesh (837k cells — Cd = 0.280, Cl = **+0.32349** sign-corrected)

<p align="center">
  <img src="results/medium/cd_cl.png" width="55%" alt="Medium mesh Cd/Cl"/>
</p>

### Fine Mesh (4.4M cells — Cd = 0.270, Cl = **+0.32319** sign-corrected)

<p align="center">
  <img src="results/fine/screenshots/cd_convergence_early.png" width="48%" alt="Fine mesh Cd convergence"/>
  <img src="results/fine/screenshots/cd_cl_final.png" width="48%" alt="Fine mesh Cd/Cl final"/>
</p>

---

## Validation vs. Experiment

Final configuration — fine mesh, **stationary ground** (matching the experiments), sign-corrected Cl:

| | CFD (fine mesh) | Experiment | Error |
|-|----------------|------------|-------|
| Cd (vs. stilt-corrected ref.) | **0.27908** | 0.2735 – 0.2822 | **within range** (−1.1% to +2.0%) |
| Cd (vs. raw, stilted model) | 0.27908 | 0.298 ± 0.5% (Meile 2016) | −6.4% |
| Cl | **+0.35525** | +0.345 (Meile 2011) | **+3.0%** |

Both coefficients agree with experiment once the two like-for-like corrections are applied — the
geometry difference (no stilts on the CFD model) and the ground condition (stationary, as in the
tunnels). Reaching this required fixing two setup errors rather than tuning the physics; see
[Known Issues](#known-issues) for both, kept on the record.

> The fine-mesh GCI is 0.77%, so the solution is mesh independent and these residuals are physical
> rather than numerical. For reference, the earlier moving-ground configuration gave Cd = 0.2699 and
> Cl = +0.32319 — the ground condition alone accounts for a 9.9% shift in Cl.

---

## Known Issues

**1. Cl sign inversion — ✅ RESOLVED.**
The experimental Cl for a 25° slant is **positive** (+0.345, Meile et al. 2011; Gutierrez et al.
2020 obtain +0.363 and +0.376). Physically, the slow flow between road and underbody keeps the
underbody pressure higher than the upper-surface pressure, producing net positive lift. The medium
and fine meshes originally reported a *negative* Cl of the same magnitude.

**Cause:** the lift report definition's force vector had been set to `(0, −1, 0)` on the medium and
fine cases, against `(0, 1, 0)` on the coarse case — the vertical axis entered with the wrong sign
between the coarse and medium runs. A post-processing error, not a physical one, exactly as the
magnitude agreement predicted.

**Fix:** the force vector was corrected to `(0, 1, 0)` and Cl re-extracted from the existing
converged solutions. No re-iteration was needed, so the flow fields are unchanged.

| Mesh | Cl (as-reported) | Cl (corrected) | Deviation from exp. |
|---|---|---|---|
| Coarse (370k) | +0.3357 | +0.3357 *(was already correct)* | −2.7% |
| Medium (837k) | −0.3235 | **+0.32349** | −6.2% |
| Fine (4.4M) | −0.3232 | **+0.32319** | −6.3% |

The corrected magnitudes match the originals to five significant figures — confirming the sign was
the only defect. All three meshes now agree on both sign and magnitude.

> The corrected +0.323 is still a *moving-ground* result compared against a *fixed-ground*
> measurement. Matching the ground condition (issue 3) subsequently moved it to **+0.35525**,
> i.e. **+3.0%** from experiment.

**2. The wake comparison was withdrawn (not corrected) — now out of scope.**
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

Fixing the reference alone wouldn't have made the comparison valid, so it was removed.

**Wake validation is out of scope for this study**, which validates the *force coefficients* against
measurement. These are separate claims: Cd and Cl test the integrated surface loads; wake profiles
test the resolved flow structure. Only the former is claimed here.

The experimental data is included unmodified in `data/ercoftac/`, with
`scripts/ercoftac_wake_reference.py` to read and plot it. What follow-on work would need to add is a
re-export of the CFD symmetry-plane profiles at the four measured stations — with care over the
coordinate mapping, since the ERCOFTAC origin sits at the **rear face** of the body and does not
coincide with the Fluent case origin. Mismapping those axes is what invalidated the withdrawn
comparison.

**3. Ground boundary condition mismatch — ✅ RESOLVED.**
The original CFD used a **moving wall at 40 m/s** to emulate a rolling road. Both experimental
sources used here ran on a **stationary floor**:

| Source | Facility | Ground |
|---|---|---|
| Lienhart & Becker (ERCOFTAC 082) | LSTM, 3/4-open test section | Fixed ground plate; model on 30 mm stilts through the plate, 50 mm clearance |
| Meile et al. (2011, 2016) | Graz ISW | Fixed floor, six-component balance |

This is not a cosmetic difference. Strachan et al. (2007) measured the same geometry over both a
fixed and a moving ground and found the moving plane thins the underbody boundary layer, raises
underbody flow speed, and shifts the near-wake vortex structure — which acts directly on the
underbody pressure that sets **Cl**, the very coefficient flagged in issue 1.

**Resolution.** The fine mesh was rerun with the ground set to a stationary wall, restarted from the
converged moving-ground solution with **no other setting changed**, so the ground condition is the
single isolated variable. It settled to residuals ~10⁻⁶ in 70–80 iterations:

| | Moving ground | **Stationary ground** | Experiment | Deviation (stationary) |
|---|---|---|---|---|
| **Cl** | +0.32319 | **+0.35525** | +0.345 (Meile 2011) | **+3.0%** |
| **Cd** | 0.2699 | **0.27908** | 0.2735 – 0.2822 (stilt-corrected) | **within the range** |

Matching the ground condition improved both coefficients:

- **Cl** moved from −6.3% to **+3.0%** of the measured value — less than half the deviation, and now
  slightly *above* rather than below experiment.
- **Cd** rose to 0.27908, placing it inside the stilt-corrected experimental band (0.2735–0.2822)
  rather than below it.
- **Cl changed by 9.9%, Cd by only 3.4%.** Lift is roughly three times more sensitive to the ground
  condition than drag — exactly what Strachan's mechanism predicts, since the underbody pressure it
  perturbs acts primarily on the vertical force.

> **Asymmetry worth stating.** Cd is compared against a *stilt-corrected* reference; Cl is compared
> against the *raw* measured value. The reason is that the stilts are slender vertical cylinders —
> their direct contribution to vertical force is small, unlike their streamwise contribution. But
> they do disturb the underbody flow, so an indirect effect on lift can't be excluded. Gutierrez et
> al. (2020) decompose drag by surface but give no usable lift equivalent, so no correction is
> attempted. The +3.0% carries that residual uncertainty, making the Cl comparison marginally less
> like-for-like than the Cd one.

The practical conclusion: a meaningful part of what would otherwise have been written off as
"k-ω SST limitations" was a **boundary-condition mismatch**, not turbulence modelling. With the
ground condition matched and the stilt difference accounted for, the fine mesh agrees with
experiment to +3.0% on Cl and to within the reference band on Cd.

> **Scope.** Only the fine mesh was rerun on a stationary ground; the mesh independence study
> (GCI = 0.77%) was carried out on the moving-ground configuration. The GCI is a property of the
> spatial discretisation and no mesh parameter changed, so it is expected to carry over, but this
> has not been demonstrated.
>
> **Convergence caveat.** The restart met the residual criterion (10⁻⁶ vs. the 10⁻⁵ target) but ran
> shorter than the 200-iteration window over which this study's force-monitor criterion
> (ΔCd < 0.001) is defined. The coefficients were steady over the iterations available, but the
> criterion *as written* was not demonstrated across a full window. This matters because Meile et
> al. (2016) report a non-symmetric bi-stable wake for this geometry — though the half-model's
> imposed symmetry plane excludes any asymmetric mode by construction, which is a limitation of the
> idealisation in its own right.

### Experimental Wake Reference

The genuine Lienhart & Becker wake measurements (ERCOFTAC Case 082) are included in
`data/ercoftac/`, unmodified. Measurement planes: x = 0, 80, 200, 500 mm behind the body. They are
provided as a reference dataset for follow-on work; no CFD comparison against them is claimed here
(see [issue 2](#known-issues)).

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
- **Strachan, R.K., Knowles, K. & Lawson, N.J. (2007).** *The vortex structure behind an Ahmed reference model in the presence of a moving ground plane.* Experiments in Fluids, 42(5), 659–669. — Moving vs. fixed ground effect on underbody flow and wake vortices.
- **Celik, I.B. et al. (2008).** *Procedure for estimation and reporting of uncertainty due to discretization in CFD applications.* J. Fluids Eng., 130(7), 078001. — GCI methodology.
- **Ahmed, S.R., Ramm, G. & Faltin, G. (1984).** *Some salient features of the time-averaged ground vehicle wake.* SAE 840300.
