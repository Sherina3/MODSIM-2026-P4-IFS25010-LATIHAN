import numpy as np
from scipy.integrate import solve_ivp
import streamlit as st
import plotly.graph_objects as go

# =====================================
# 1. PARAMETER SISTEM TANGKI AIR
# =====================================

class TankConfig:

    def __init__(self):

        # Dimensi tangki
        self.radius = 1.0
        self.height = 3.0

        # Debit air
        self.inlet_flow = 0.05
        self.outlet_flow = 0.03

        # Kondisi awal
        self.initial_height = 0.5

        # waktu simulasi
        self.simulation_time = 200


# =====================================
# 2. MODEL FISIKA
# =====================================

class TankModel:

    def __init__(self, config):
        self.config = config

    def tank_area(self):
        return np.pi * self.config.radius**2

    def dh_dt(self, t, h):

        A = self.tank_area()

        Qin = self.config.inlet_flow
        Qout = self.config.outlet_flow

        dh = (Qin - Qout) / A

        return dh


# =====================================
# 3. SIMULASI
# =====================================

class TankSimulator:

    def __init__(self, config):

        self.config = config
        self.model = TankModel(config)

    def run(self):

        t_span = (0, self.config.simulation_time)

        t_eval = np.linspace(0, self.config.simulation_time, 500)

        sol = solve_ivp(
            self.model.dh_dt,
            t_span,
            [self.config.initial_height],
            t_eval=t_eval
        )

        height = sol.y[0]

        # batasi tinggi air
        height = np.clip(height, 0, self.config.height)

        return sol.t, height


# =====================================
# 4. PERHITUNGAN ANALISIS
# =====================================

def time_to_fill(config):

    A = np.pi * config.radius**2

    net_flow = config.inlet_flow - config.outlet_flow

    if net_flow <= 0:
        return None

    volume_needed = A * (config.height - config.initial_height)

    return volume_needed / net_flow


def time_to_empty(config):

    A = np.pi * config.radius**2

    net_flow = config.outlet_flow - config.inlet_flow

    if net_flow <= 0:
        return None

    volume = A * config.initial_height

    return volume / net_flow


# =====================================
# 5. VISUALISASI
# =====================================

def plot_height(time, height, config):

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=time,
        y=height,
        mode='lines',
        name='Ketinggian Air'
    ))

    fig.add_hline(
        y=config.height,
        line_dash="dash",
        line_color="red",
        annotation_text="Batas Tangki"
    )

    fig.update_layout(
        title="Profil Ketinggian Air dalam Tangki",
        xaxis_title="Waktu (detik)",
        yaxis_title="Ketinggian Air (m)",
        template="plotly_white"
    )

    return fig


# =====================================
# 6. STREAMLIT APP
# =====================================

def main():

    st.title("Simulasi Sistem Tangki Air")

    config = TankConfig()

    st.sidebar.header("Parameter")

    config.radius = st.sidebar.slider("Radius Tangki (m)",0.5,3.0,1.0)
    config.height = st.sidebar.slider("Tinggi Tangki (m)",1.0,5.0,3.0)

    config.inlet_flow = st.sidebar.slider("Debit Inlet (m3/s)",0.01,0.1,0.05)
    config.outlet_flow = st.sidebar.slider("Debit Outlet (m3/s)",0.01,0.1,0.03)

    config.initial_height = st.sidebar.slider("Ketinggian Awal (m)",0.0,config.height,0.5)

    config.simulation_time = st.sidebar.slider("Waktu Simulasi (s)",50,500,200)

    simulator = TankSimulator(config)

    time, height = simulator.run()

    st.subheader("Grafik Ketinggian Air")

    fig = plot_height(time, height, config)

    st.plotly_chart(fig)

    st.subheader("Analisis Studi Kasus")

    fill_time = time_to_fill(config)
    empty_time = time_to_empty(config)

    if fill_time:
        st.success(f"Waktu tangki penuh ≈ {fill_time:.2f} detik")

    if empty_time:
        st.warning(f"Waktu tangki kosong ≈ {empty_time:.2f} detik")

    if config.inlet_flow > config.outlet_flow:
        st.info("Debit masuk lebih besar → tangki akan penuh")

    elif config.inlet_flow < config.outlet_flow:
        st.info("Debit keluar lebih besar → tangki akan kosong")

    else:
        st.info("Debit masuk = keluar → tinggi air stabil")


if __name__ == "__main__":
    main()