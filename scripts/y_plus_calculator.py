import math

# Flow conditions (Lienhart & Becker 2003)
U_inf = 40.0        # m/s
L     = 1.044       # m — Ahmed body length (reference length)
nu    = 1.516e-5    # m²/s — kinematic viscosity of air at 20°C
rho   = 1.204       # kg/m³

Re = U_inf * L / nu
print(f"Reynolds number: {Re:.3e}")

# Skin friction coefficient — flat plate approximation (Schlichting)
Cf = 0.074 / Re**0.2
print(f"Cf (flat plate estimate): {Cf:.6f}")

# Wall shear stress
tau_w = 0.5 * rho * U_inf**2 * Cf
u_tau = math.sqrt(tau_w / rho)
print(f"u_tau (friction velocity): {u_tau:.4f} m/s")

# First cell height for target y+
print("\n--- First cell height for target y+ ---")
for y_plus_target in [1, 5, 30, 100, 300]:
    delta_y = y_plus_target * nu / u_tau
    print(f"  y+ = {y_plus_target:>4}  ->  dy = {delta_y*1000:.4f} mm")

print("\nRecommendation for k-w SST (low-Re, no wall functions): y+ < 5")
print("  -> Target first cell height: ~0.05-0.15 mm")
