import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- PAGE CONFIG ---
st.set_page_config(page_title="MEC Digital Twin", page_icon="⚡", layout="wide")

st.title("⚡ Microbial Electrolysis Cell (MEC) Techno-Economic Digital Twin")
st.markdown("Explore how **nanomaterial upgrades** (carbon nanotube anodes and nickel catalysts) and wastewater organic loading drive down the cost of bio-hydrogen production[cite: 1].")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🔧 Reactor Parameters")
surface_multiplier = st.sidebar.slider("Nanotube Surface Area Multiplier", 1.0, 10.0, 4.0, 0.5, 
    help="Expands active surface area and reduces electrical resistance[cite: 1].")
h2_efficiency = st.sidebar.slider("Nickel Catalyst Efficiency", 0.40, 0.95, 0.73, 0.05,
    help="Measures cathode hydrogen conversion efficiency using earth-abundant transition metals[cite: 1].")
initial_cod = st.sidebar.slider("Initial COD (mg/L)", 500, 5000, 2000, 250,
    help="Chemical Oxygen Demand representing wastewater strength.")
electricity_cost_kwh = st.sidebar.slider("Grid Electricity ($/kWh)", 0.05, 0.25, 0.10, 0.01)

# --- SIMULATION LOGIC ---
time_days = np.linspace(0, 15, 150)
dt = time_days[1] - time_days[0]

mu_max = 0.45
K_s = 100.0
Y_xs = 0.2
k_decay = 0.02

effective_mu_max = mu_max * (surface_multiplier * 0.35)

S = np.zeros_like(time_days)
X = np.zeros_like(time_days)
H2_cumulative = np.zeros_like(time_days)

S[0] = initial_cod
X[0] = 50.0

for i in range(1, len(time_days)):
    s_curr = S[i-1]
    x_curr = X[i-1]
    
    mu = effective_mu_max * (s_curr / (K_s + s_curr))
    dS_dt = - (mu * x_curr) / Y_xs
    dX_dt = (mu - k_decay) * x_curr
    
    S[i] = max(0.0, s_curr + dS_dt * dt)
    X[i] = max(0.0, x_curr + dX_dt * dt)
    
    cod_consumed = max(0.0, S[i-1] - S[i])
    h2_step = cod_consumed * h2_efficiency * 0.004
    H2_cumulative[i] = H2_cumulative[i-1] + h2_step

# --- PLOTTING ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)

ax1.plot(time_days, S, color='tab:red', linewidth=2.5, label='COD (Waste)')
ax1.set_ylabel('COD (mg/L)', color='tab:red', fontweight='bold')
ax1.tick_params(axis='y', labelcolor='tab:red')

ax1_twin = ax1.twinx()
ax1_twin.plot(time_days, X, color='tab:blue', linestyle='--', linewidth=2.5, label='Biofilm')
ax1_twin.set_ylabel('Biomass (mg/L)', color='tab:blue', fontweight='bold')
ax1_twin.tick_params(axis='y', labelcolor='tab:blue')
ax1.set_title('Biological Kinetics & Wastewater COD Degradation', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)

ax2.plot(time_days, H2_cumulative, color='tab:green', linewidth=2.5)
ax2.set_xlabel('Time (Days)', fontweight='bold')
ax2.set_ylabel('Cumulative H₂ (mmol/L)', color='tab:green', fontweight='bold')
ax2.set_title('Cumulative Bio-Hydrogen Yield (Nickel Catalyst Performance)', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3)

fig.tight_layout()

# Display plot in Streamlit
st.pyplot(fig)

# --- ECONOMIC READOUT ---
total_h2_produced = H2_cumulative[-1]
base_energy_cost = electricity_cost_kwh * 12.0
nanotech_savings_factor = 1.0 / (surface_multiplier * h2_efficiency)
estimated_mec_cost_per_kg = max(1.80, base_energy_cost * nanotech_savings_factor + 0.90)

st.markdown("---")
st.subheader("💰 Techno-Economic Cost Analysis")

col1, col2, col3 = st.columns(3)
col1.metric("Simulated Bio-H₂ Cost", f"${estimated_mec_cost_per_kg:.2f} / kg")
col2.metric("Benchmark Grey Hydrogen", "$1.50 / kg", delta="High Emissions[cite: 1]", delta_color="inverse")
col3.metric("Green Water Electrolysis", "$4.00 - $6.00 / kg", delta="High Energy Input[cite: 1]", delta_color="inverse")

if estimated_mec_cost_per_kg < 3.00:
    st.success("✅ **Commercial Viability Unlocked:** Nanomaterial surface area and nickel catalyst efficiency successfully drive MEC costs below green electrolysis benchmarks!")
else:
    st.warning("⚠️ **High Operating Overhead:** Current parameter settings keep production costs elevated above target thresholds.")
