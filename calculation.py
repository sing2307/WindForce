from typing import Dict
from abccalculation import ABCCalculation
import numpy as np
import math

class Calculation(ABCCalculation):
    """
    Concrete class for calculation
    """

    def __init__(self, sections, springs: Dict, masses: Dict,
                 forces: Dict, excentricity: Dict, calculation_param: Dict):
        """
        ...
        :param element_parameters:
        """
        super().__init__(sections, springs, masses, forces, excentricity, calculation_param)

    def return_solution(self):
        """
        ...
        :return:
        """

        return self.solution

    def assembly_system_matrix(self):
        """
        Calculates element matrices for every section, assembly system
        :return:
        """
        return np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

    def solve_system(self):
        """
        Solves for eigenfrequencies and the respective nodes displacement
        :return:
        """
        return NotImplemented

    def start_calc(self):
        all_element_k_matrices = list()
        all_element_m_matrices = list()
        min_height = min(section['sec_height'] for section in self.sections.values())
        number_of_elements = {}
        for sefc_id, section_values in self.sections.items():
            section_height = section_values['sec_height']
            number_of_elements[sefc_id] = self.calculation_param['fem_density'] * round(section_height / min_height)
            num_elements = number_of_elements[sefc_id]
            element_length = section_height / num_elements
            section_t = section_values['sec_thickness']
            section_ra_bot = section_values['sec_ra']
            section_ra_top = self.sections[sefc_id + 1]['sec_ra']
            element_ra_mid = section_ra_bot - (section_ra_bot - section_ra_top) / section_height * element_length * (np.array(list(range(1, num_elements+1))) - 0.5)
            section_e = section_values['sec_E']
            section_g = section_values['sec_G']
            section_rho = section_values['sec_rho']
            for ra_mid in element_ra_mid:
                element_k_matrix, element_m_matrix = Elements(element_length, section_t, ra_mid,  section_e, section_g, section_rho).calc_element_matrix()
                all_element_k_matrices.append(element_k_matrix)
                all_element_m_matrices.append(element_m_matrix)
        for elem in all_element_k_matrices :
            print(elem)

        system_matrix = self.assembly_system_matrix()
        print(system_matrix)
        self.solution = [[1, 3], [4, 5], [5, 6]]
        self.return_solution()


class Elements():
    """
    Computation of system matrices and solution
    """

    def __init__(self, element_length, section_t, element_ra_mid,  section_e, section_g, section_rho):
        """
        ...
        :param element_parameters:
        """
        self.element_length = element_length
        self.element_t = section_t
        self.element_ra_mid = element_ra_mid
        self.element_e = section_e
        self.element_g = section_g
        self.element_rho = section_rho
    def calc_element_matrix(self):
        """
        Calculates element stiffness and mass matrix
        :return:
        """
        element_ri_mid = self.element_ra_mid - self.element_t * 10 ** (-2)
        ele_a = math.pi * (self.element_ra_mid ** 2 - element_ri_mid ** 2)
        ele_iy = (math.pi / 4) * (self.element_ra_mid ** 4 - element_ri_mid ** 4)   # Iy = Iz
        ele_it = (math.pi / 2) * (self.element_ra_mid ** 4 - element_ri_mid ** 4)
        ele_ip = 2 * ele_iy
        ea = self.element_e * ele_a * 10 ** 3
        ei_y = self.element_e * ele_iy * 10 ** 3
        ei_z = self.element_e * ele_iy * 10 ** 3
        gi_t = self.element_g * ele_it * 10 ** 3
        l = self.element_length
        m = ele_a * self.element_rho
        k_lok = np.array([
            [ea / l, 0, 0, 0, 0, 0, -ea / l, 0, 0, 0, 0, 0],
            [0, (12 * ei_z) / (l ** 3), 0, 0, 0, 6 * ei_z / (l ** 2), 0, -12 * ei_z / (l ** 3), 0, 0, 0, 6 * ei_z / (l ** 2)],
            [0, 0, 12 * ei_y / (l ** 3), 0, -6 * ei_y / (l ** 2), 0, 0, 0, -12 * ei_y / (l ** 3), 0, -6 * ei_y / (l ** 2), 0],
            [0, 0, 0, gi_t / l, 0, 0, 0, 0, 0, -gi_t / l, 0, 0],
            [0, 0, -6 * ei_y / (l ** 2), 0, 4 * ei_y / l, 0, 0, 0, 6 * ei_y / (l ** 2), 0, 2 * ei_y / l, 0],
            [0, 6 * ei_z / (l ** 2), 0, 0, 0, 4 * ei_z / l, 0, -6 * ei_z / (l ** 2), 0, 0, 0, 2 * ei_z / l],
            [-ea / l, 0, 0, 0, 0, 0, ea / l, 0, 0, 0, 0, 0],
            [0, (-12 * ei_z) / (l ** 3), 0, 0, 0, -6 * ei_z / (l ** 2), 0, 12 * ei_z / (l ** 3), 0, 0, 0, -6 * ei_z / (l ** 2)],
            [0, 0, -12 * ei_y / (l ** 3), 0, 6 * ei_y / (l ** 2), 0, 0, 0, 12 * ei_y / (l ** 3), 0, 6 * ei_y / (l ** 2), 0],
            [0, 0, 0, -gi_t / l, 0, 0, 0, 0, 0, gi_t / l, 0, 0],
            [0, 0, -6 * ei_y / (l ** 2), 0, 2 * ei_y / l, 0, 0, 0, 6 * ei_y / (l ** 2), 0, 4 * ei_y / l, 0],
            [0, 6 * ei_z / (l ** 2), 0, 0, 0, 2 * ei_z / l, 0, -6 * ei_z / (l ** 2), 0, 0, 0, 4 * ei_z / l]
        ])
        m_lok = (m * l / 420) * np.array([
            [140, 0, 0, 0, 0, 0, 70, 0, 0, 0, 0, 0],
            [0, 156, 0, 0, 0, 22 * l, 0, 54, 0, 0, 0, -13 * l],
            [0, 0, 156, 0, -22 * l, 0, 0, 0, 54, 0, 13 * l, 0],
            [0, 0, 0, 140 * ele_ip / ele_a, 0, 0, 0, 0, 0, 70 * ele_ip / ele_a, 0, 0],
            [0, 0, -22 * l, 0, 4 * l ** 2, 0, 0, 0, -13 * l, 0, -3 * l ** 2, 0],
            [0, 22 * l, 0, 0, 0, 4 * l ** 2, 0, 13 * l, 0, 0, 0, -3 * l ** 2],
            [70, 0, 0, 0, 0, 0, 140, 0, 0, 0, 0, 0],
            [0, 54, 0, 0, 0, 13 * l, 0, 156, 0, 0, 0, -22 * l],
            [0, 0, 54, 0, -13 * l, 0, 0, 0, 156, 0, 22 * l, 0],
            [0, 0, 0, 70 * ele_ip / ele_a, 0, 0, 0, 0, 0, 140 * ele_ip / ele_a, 0, 0],
            [0, 0, 13 * l, 0, -3 * l ** 2, 0, 0, 0, 22 * l, 0, 4 * l ** 2, 0],
            [0, -13 * l, 0, 0, 0, -3 * l ** 2, 0, -22 * l, 0, 0, 0, 4 * l ** 2]
        ])
        return k_lok, m_lok

if __name__ == "__main__":
    sections = {0: {'sec_number': 0,
                    'sec_height': 50,
                    'sec_ra': 5,
                    'sec_thickness': 30,
                    'sec_E': 210000,
                    'sec_G': 81000,
                    'sec_rho': 7850},
                1: {'sec_number': 1,
                    'sec_height': 50,
                    'sec_ra': 5,
                    'sec_thickness': 30,
                    'sec_E': 210000,
                    'sec_G': 81000,
                    'sec_rho': 7850}}
    springs = {}
    masses = {}
    forces = {}
    excentricity = {}
    calculation_param = {'fem_density': 2,
                         'fem_nbr_eigen_freq': 2,
                         'fem_dmas': 0.05,
                         'fem_exc': 1}

    calc = Calculation(sections, springs, masses, forces, excentricity, calculation_param)
    calc.start_calc()