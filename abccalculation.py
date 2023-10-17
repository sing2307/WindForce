"""
Definition of abstract base class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class ABCCalculation(ABC):
    """
    Abstract base class with input parameters from GUI -> Output: Calculation results for visualization and text output
    ...
    """

    def __init__(self, sections: Dict, springs: Dict,
                 masses: Dict, forces: Dict, excentricity: Dict,
                 calculation_param: Dict):
        """

        :param sections: Defines the sections of the beam with the following parameter:
                            sec_number      []
                            sec_height      [m]
                            sec_ra          [m]
                            sec_thickness   [cm]
                            sec_E           [MPa]
                            sec_G           [MPa]
                            sec_rho         [kg/m^3]
                        ->
                        sections = {n=0: {'sec_number': n,
                                        'sec_height': val,
                                        'sec_ra': val,
                                        'sec_thickness': val,
                                        'sec_E': val,
                                        'sec_G': val,
                                        'sec_rho': val},
                                    n + 1: {...},
                                    n_max: {....}}
        :param springs: Defines the elasticity values for base and head of tower:
                            base_cx         [N/m]
                            base_cy         [N/m]
                            base_phix       [N/m]
                            base_phiy       [N/m]
                            head_cx         [N/m]
                            ->
                            springs = {'base_cx': val,
                                       'base_cy': val,
                                       'base_phix': val,
                                       'base_phiy': val,
                                       'head_cx': val}
        :param masses: Defines the masses for base and head of tower:
                            base_m          [kg]
                            head_m          [kg]
                            ->
                            masses = {'base_m': val,
                                       'head_m': val}
        :param forces: Defines the forces:
                            freq_excite     [Hz]
                            f_head          [N]
                            m_head          [Nm]
                            freq_rotor      [Hz]
                            qu_impulse      [N/m]
                            qo_impulse      [N/m]
                            nbr_periods     []
                            delta_t         [s]
                            num_1           []
                            num_2           []
                            ->
                            forces = {'f_excite': val,
                                       'f_head': val,
                                       'm_head': val,
                                       'f_rotor': val,
                                       'qu_impulse': val,
                                       'qo_impulse': val,
                                       'nbr_periods': val,
                                       'delta_t': val,
                                       'num_1': val,
                                       'num_2': val}
        :param excentricity: Defines the excentricity at tower head
                            exc_ex          [m]
                            exc_EA          [N]
                            exc_EIy         [Nm^2]
                            exc_EIz         [Nm^2]
                            exc_GIt         [Nm^2]
                            exc_mass_unit   [kg/m]
                            exc_area        [m^2]
                            exc_Ip          [m^4]
                            ->
                            excentricity = {'exc_ex': val,
                                            'exc_EA': val,
                                            'exc_EIy': val,
                                            'exc_EIz': val,
                                            'exc_GIt': val,
                                            'exc_mass': val,
                                            'exc_area': val,
                                            'exc_Ip': val}
        :param calculation_param: Defines the calculation parameters
                            fem_density         [???] # todo: maybe density between 0...1?
                            fem_nbr_eigen_freq  []
                            fem_dmas            []
                            fem_exc             []
                            ->
                            calculation_param = {'fem_density': val,
                                                 'fem_nbr_eigen_freq': val,
                                                 'fem_dmas': val,
                                                 'fem_exc': val}
        """

        self.sections = sections
        self.springs = springs
        self.masses = masses
        self.forces = forces
        self.excentricity = excentricity
        self.calculation_param = calculation_param

    @abstractmethod
    def return_solution(self):
        """
        :return: Dict[Dict[...]] -> Dict for eigenfrequencies: interpolation nodes and their respective
        displacement
        ->
        return {0: {'eigenfreq': 123,
                    'solution': [[0,0],[x1, y1],[x_max, y_max},
                1: {...},
                eigenfreq_mnax: {...}
               }
               todo: connectivity matrix needed?
        """

        pass
