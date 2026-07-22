"""First cell height estimation for a target y+.

Flat-plate (Schlichting) correlation used to size the first boundary-layer cell.
Kinematic viscosity is fixed at the value used by the reference experiment
(ERCOFTAC Case 082, nu = 15e-6 m^2/s) so that the Reynolds numbers quoted here,
in the report and in ercoftac_wake_reference.py all agree.
"""

import math

# Flow conditions
U_inf = 40.0        # m/s — freestream velocity
L     = 1.044       # m   — Ahmed body length
H     = 0.288       # m   — Ahmed body height (ERCOFTAC reference length)
nu    = 15e-6       # m²/s — kinematic viscosity, per ERCOFTAC Case 082
rho   = 1.204       # kg/m³ — air at 20°C

Re_L = U_inf * L / nu
Re_H = U_inf * H / nu

print(f"Reynolds number (on body length L = {L} m): {Re_L:.3e}")
print(f"Reynolds number (on body height H = {H} m): {Re_H:.3e}")
print("  ERCOFTAC Case 082 quotes Re_H = 7.68e5 - matches.")

# Skin friction coefficient — flat plate approximation (Schlichting), valid to Re ~1e7
Cf = 0.074 / Re_L**0.2
print(f"\nCf (flat plate estimate): {Cf:.6f}")

# Wall shear stress and friction velocity
tau_w = 0.5 * rho * U_inf**2 * Cf
u_tau = math.sqrt(tau_w / rho)
print(f"u_tau (friction velocity): {u_tau:.4f} m/s")

# First cell height for target y+
print("\n--- First cell height for target y+ ---")
for y_plus_target in [1, 5, 15, 30, 100, 300]:
    delta_y = y_plus_target * nu / u_tau
    print(f"  y+ = {y_plus_target:>4}  ->  dy = {delta_y*1000:.4f} mm")

# Two valid near-wall strategies. They are mutually exclusive: the buffer layer
# (5 < y+ < 30) is resolved correctly by neither, so a mesh must sit clearly on
# one side or the other.
print("\n--- Near-wall treatment ---")
print("  (a) Wall functions      : target y+ 30-300, ideally 30-100")
print("      Log-law is valid; the viscous sublayer is modelled, not resolved.")
for yp in (30, 100):
    print(f"        y+ = {yp:>3}  ->  dy = {yp * nu / u_tau * 1000:.4f} mm")
print("  (b) Low-Re resolution   : target y+ < 1")
print("      Viscous sublayer resolved directly; needs many more layers.")
print(f"        y+ =   1  ->  dy = {1 * nu / u_tau * 1000:.4f} mm")

print("\n  This study uses (a), wall functions, but the aspect-ratio-based layer")
print("  sizing produced y+ ~15-30 - inside the buffer layer rather than clear of")
print("  it. See the mesh independence discussion: this is the likely cause of the")
print("  inconsistent y+ across mesh levels and the apparent order p = 3.53.")
