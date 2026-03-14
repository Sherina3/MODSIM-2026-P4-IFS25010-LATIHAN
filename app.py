import numpy as np
from scipy.integrate import solve_ivp
import streamlit as st
import plotly.graph_objects as go
from dataclasses import dataclass

# ====================
# 1. KONFIGURASI SISTEM
# ====================

@dataclass
class TankConfig:
    
    # Dimensi tangki
    radius: float = 1.5          # meter
    height: float = 5.0          # meter
    
    # Debit aliran
    Qin: float = 0.02            # m3/s (air masuk)
    Qout: float = 0.01           # m3/s (air keluar)
    
    # Kondisi awal
    initial_volume: float = 0.0  # m3
    
    # Waktu simulasi
    simulation_time: float = 200 # detik

    def tank_area(self):
        return np.pi * self.radius**2
    
    def max_volume(self):
        return self.tank_area() * self.height


# ====================
# 2. MODEL SISTEM FISIKA
# ====================

class WaterTankModel:
    
    def __init__(self, config: TankConfig):
        self.config = config
        
    def volume_change(self, t, V):
        """
        Persamaan diferensial sistem tangki air
        
        dV/dt = Qin - Qout
        """
        
        Qin = self.config.Qin
        Qout = self.config.Qout
        
        dVdt = Qin - Qout
        
        return dVdt


# ====================
# 3. SIMULATOR
# ====================

class WaterTankSimulator:
    
    def __init__(self, config: TankConfig):
        
        self.config = config
        self.model = WaterTankModel(config)
        
        self.time = None
        self.volume = None
        self.height = None
        
    def run_simulation(self):
        
        t_span = (0, self.config.simulation_time)
        t_eval = np.linspace(0, self.config.simulation_time, 500)
        
        solution = solve_ivp(
            self.model.volume_change,
            t_span,
            [self.config.initial_volume],
            t_eval=t_eval
        )
        
        self.time = solution.t
        self.volume = solution.y[0]
        
        # hitung tinggi air
        area = self.config.tank_area()
        self.height = self.volume / area
        
        return {
            "time": self.time,
            "volume": self.volume,
            "height": self.height
        }


# ====================
# 4. VISUALISASI
# ====================

class Visualization:
    
    @staticmethod
    def plot_water_height(sim):
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=sim.time,
            y=sim.height,
            mode='lines',
            name='Tinggi Air'
        ))
        
        fig.update_layout(
            title="Perubahan Tinggi Air dalam Tangki",
            xaxis_title="Waktu (detik)",
            yaxis_title="Tinggi Air (meter)"
        )
        
        return fig


# ====================
# 5. APLIKASI STREAMLIT
# ====================

def create_sidebar():
    
    st.sidebar.title("Parameter Tangki")
    
    radius = st.sidebar.slider("Radius Tangki (m)", 0.5, 5.0, 1.5)
    height = st.sidebar.slider("Tinggi Tangki (m)", 1.0, 10.0, 5.0)
    
    Qin = st.sidebar.slider("Debit Masuk Qin (m3/s)", 0.0, 0.05, 0.02)
    Qout = st.sidebar.slider("Debit Keluar Qout (m3/s)", 0.0, 0.05, 0.01)
    
    simulation_time = st.sidebar.slider("Waktu Simulasi", 10, 500, 200)
    
    config = TankConfig(
        radius=radius,
        height=height,
        Qin=Qin,
        Qout=Qout,
        simulation_time=simulation_time
    )
    
    return config


def main():
    
    st.title("Simulasi Sistem Water Tank Asrama")
    
    st.markdown("""
    Studi kasus ini mensimulasikan sistem **pam air pada asrama**  
    yang menyimpan air dalam tangki sebelum didistribusikan ke seluruh lantai.
    
    Model matematis:
    dV/dt = Qin − Qout
    """)
    
    config = create_sidebar()
    
    simulator = WaterTankSimulator(config)
    simulator.run_simulation()
    
    fig = Visualization.plot_water_height(simulator)
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Informasi Sistem")
    
    st.write("Volume Maksimum Tangki :", config.max_volume(), "m3")
    
    if config.Qin > config.Qout:
        st.success("Tangki akan terisi.")
    elif config.Qin < config.Qout:
        st.warning("Tangki akan kosong.")
    else:
        st.info("Volume air stabil.")


if __name__ == "__main__":
    main()