import numpy as np
from dataclasses import dataclass, asdict


@dataclass
class InitShootNitrogen:
    Nm_root_shoot_xylem: float = 0
    AA_root_shoot_xylem: float = 0
    AA_root_shoot_phloem: float = 0
    cytokinins_root_shoot_xylem: float = 0

@dataclass
class InitShootWater:
    water_root_shoot_xylem: float = 0

@dataclass
class WTransport:
    axial_water_conductivity: float = 1e-18     # m4.s-1.Pa-1


class ShootModel:
    def __init__(self, Nm_root_shoot_xylem, AA_root_shoot_xylem, AA_root_shoot_phloem, cytokinins_root_shoot_xylem,
                 water_root_shoot_xylem):
        self.keywords = dict(
            Nm_root_shoot_xylem=Nm_root_shoot_xylem,
            AA_root_shoot_xylem=AA_root_shoot_xylem,
            AA_root_shoot_phloem=AA_root_shoot_phloem,
            cytokinins_root_shoot_xylem=cytokinins_root_shoot_xylem,
            water_root_shoot_xylem=water_root_shoot_xylem
        )

        for name in self.keywords:
            setattr(self, name, self.keywords[name])

    def transportN(self, root_xylem_Nm, root_xylem_AA, collar_struct_mass, root_xylem_water, root_phloem_AA, root_radius):
        axial_diffusion_xylem: float = 2.5e-4   # g.m-2.s-1
        axial_diffusion_phloem: float = 1e-4  # g.m-2.s-1
        shoot_xylem_Nm = 1e-5   # mol.g-1 DW
        shoot_xylem_AA = 1e-5   # mol.g-1 DW
        shoot_phloem_AA = 2e-3  # mol.g-1 DW
        xylem_cross_area_ratio: float = 0.84 * (0.36 ** 2)  # (adim) apoplasmic cross-section area ratio * stele radius ratio^2

        if self.water_root_shoot_xylem >= 0:
            Nm_water_conc = root_xylem_Nm * collar_struct_mass * xylem_cross_area_ratio / root_xylem_water
            AA_water_conc = root_xylem_AA * collar_struct_mass * xylem_cross_area_ratio / root_xylem_water

        else:
            Nm_water_conc = 1e-6
            AA_water_conc = 1e-6

        Nm_collar_advection = Nm_water_conc * self.water_root_shoot_xylem
        AA_collar_advection = AA_water_conc * self.water_root_shoot_xylem

        # note, gradients are not computed in the same way for xylem and phloem, we have an a priori on flow directions
        Nm_collar_xylem_diffusion = axial_diffusion_xylem * (root_xylem_Nm - shoot_xylem_Nm) * np.pi * root_radius**2
        AA_collar_xylem_diffusion = axial_diffusion_xylem * (root_xylem_AA - shoot_xylem_AA) * np.pi * root_radius**2

        AA_collar_phloem_diffusion = axial_diffusion_phloem * (shoot_phloem_AA - root_phloem_AA) * np.pi * root_radius ** 2

        self.Nm_root_shoot_xylem = Nm_collar_advection + Nm_collar_xylem_diffusion
        self.AA_root_shoot_xylem = AA_collar_advection + AA_collar_xylem_diffusion

        self.AA_root_shoot_phloem = AA_collar_phloem_diffusion

        self.cytokinins_root_shoot_xylem = 0

        # Output flows
        class NFlows(object): pass
        N_flows = NFlows()
        N_flows.Nm_root_shoot_xylem = self.Nm_root_shoot_xylem
        N_flows.AA_root_shoot_xylem = self.AA_root_shoot_xylem
        N_flows.AA_root_shoot_phloem = self.AA_root_shoot_phloem
        N_flows.cytokinins_root_shoot_xylem = self.cytokinins_root_shoot_xylem
        return N_flows.__dict__

    def transportW(self, axial_water_conductivity, root_xylem_pressure, root_radius, segment_length):
        shoot_xylem_pressure = -2e6  # (Pa)
        sap_viscosity = 1.3e6
        # only hydrostatic for tests
        self.water_root_shoot_xylem = ((np.pi * (root_radius**4))/(8*sap_viscosity)) * (root_xylem_pressure - shoot_xylem_pressure) / segment_length
        # Output flows
        class WFlows(object): pass
        W_flows = WFlows()
        W_flows.water_root_shoot_xylem = self.water_root_shoot_xylem
        return W_flows.__dict__

    def exchanges_and_balance(self, root_xylem_Nm, root_xylem_AA, collar_struct_mass, root_xylem_water,
                              root_xylem_pressure, root_phloem_AA, root_radius, segment_length):
        # Water flow first for advection computation
        W_flows = self.transportW(root_xylem_pressure=root_xylem_pressure, root_radius=root_radius, segment_length=segment_length,
                                  **asdict(WTransport()))
        N_flows = self.transportN(root_xylem_Nm=root_xylem_Nm, root_xylem_AA=root_xylem_AA, collar_struct_mass=collar_struct_mass,
                                  root_xylem_water=root_xylem_water, root_phloem_AA=root_phloem_AA, root_radius=root_radius)
        return N_flows, W_flows