from typing import Dict
from abccalculation import ABCCalculation
from scipy.sparse import csr_matrix
from scipy.linalg import eigh
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
        self.number_of_elements = []
        self.element_matrices = []
        self.k_glob = []
        self.m_glob = []

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

        num_elem = len(self.element_matrices)
        # Pre-allocate lists for the sparse matrix data.
        # i_g and j_g are used to index the global matrices
        # k_g and m_g will contain the element matrices in vector format
        i_g = []
        j_g = []
        k_g = []
        m_g = []
        num_dofs = 0

        # Convert the element stiffness and mass matrices to vector format (k_g and m_g) and define the corresponding
        # indices i_g and j_g in the global mass/stiffness matrix
        for i in range(num_elem):
            dof_i = self.element_matrices[i]['DOFs']
            k_i = self.element_matrices[i]['K']
            m_i = self.element_matrices[i]['M']
            dof_i_len = len(dof_i)
            mesh1, mesh2 = np.meshgrid(range(dof_i_len), range(dof_i_len), indexing='ij')
            ii = mesh1.ravel()
            jj = mesh2.ravel()
            i_g.extend(dof_i[ii])
            j_g.extend(dof_i[jj])
            k_g.extend(k_i.ravel())
            m_g.extend(m_i.ravel())
            max_dof_i = max(dof_i)
            num_dofs = max(num_dofs, max_dof_i)

        # Create sparse matrices for K and M
        k_glob = csr_matrix((k_g, (np.array(i_g) - 1, np.array(j_g) - 1)), shape=(num_dofs, num_dofs))
        m_glob = csr_matrix((m_g, (np.array(i_g) - 1, np.array(j_g) - 1)), shape=(num_dofs, num_dofs))

        # Assemble discrete masses and springs (TODO...)

        # Assemble boundary conditions (TODO: Bottom is clamped. Has to be changed if the springs are implemented.)
        # TODO: Bad workaround to delete rows and columns of csr matrix. Maybe implement function from https://stackoverflow.com/questions/13077527/is-there-a-numpy-delete-equivalent-for-sparse-matrices ?
        k_glob = np.delete(np.delete(k_glob.toarray(), range(6),0), range(6),1)
        m_glob = np.delete(np.delete(m_glob.toarray(), range(6), 0), range(6), 1)
        # Return global stiffness and mass matrix
        return k_glob, m_glob


    def solve_system(self):
        """
        Solves for eigenfrequencies and the respective nodes displacement
        :return:
        """
        # Solve the generalized eigenvalue problem
        [eigenvalues_sq, eigenvector] = eigh(self.k_glob, self.m_glob, subset_by_index=[0, self.calculation_param['fem_nbr_eigen_freq']-1])
        eigenfrequencies = np.sqrt(eigenvalues_sq).real
        return eigenfrequencies, eigenvector


    def start_calc(self):
        min_height = min(section['sec_height'] for section in self.sections.values())
        dofs = np.arange(-5, 7)
        # Extract the section parameters in the first loop and discretize each section into a subset of elements.
        # Calculate the cross-section radii in the middle of each element
        for sefc_id, section_values in self.sections.items():
            section_height = section_values['sec_height']
            self.number_of_elements.append((self.calculation_param['fem_density'] * round(section_height / min_height)))
            num_elements = self.number_of_elements[sefc_id]
            element_length = section_height / num_elements
            section_t = section_values['sec_thickness']
            section_ra_bot = section_values['sec_ra_bot']
            section_ra_top = section_values['sec_ra_top']
            element_ra_mid = section_ra_bot - (section_ra_bot - section_ra_top) / section_height * element_length * (np.arange(1, num_elements+1) - 0.5)
            section_e = section_values['sec_E']
            section_g = section_values['sec_G']
            section_rho = section_values['sec_rho']
            # Calcualte the element stiffness, mass matrix and the connectivity for each element. TODO: Implement excentricity
            for index in range(len(element_ra_mid)):
                element_k_matrix, element_m_matrix = Elements(element_length, section_t, element_ra_mid[index],  section_e, section_g, section_rho).calc_element_matrix()
                dofs = dofs + 6
                self.element_matrices.append({'DOFs': dofs, 'K': element_k_matrix, 'M': element_m_matrix})

        # Assemble global matrices
        self.k_glob, self.m_glob = self.assembly_system_matrix()

        # Solve eigenvalue problem to calculate eigenfrequencies and eigenmodes
        eigenfrequencies, eigenvector = self.solve_system()
        print(f'The first {len(eigenfrequencies)} eigenfrequencies are:')
        print(eigenfrequencies)

        # self.return_solution()


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
        # units: [N], [m] , [kg]
        element_ri_mid = self.element_ra_mid - self.element_t * 10 ** (-2)
        ele_a = math.pi * (self.element_ra_mid ** 2 - element_ri_mid ** 2)
        ele_iy = (math.pi / 4) * (self.element_ra_mid ** 4 - element_ri_mid ** 4)   # Iy = Iz
        ele_it = (math.pi / 2) * (self.element_ra_mid ** 4 - element_ri_mid ** 4)
        ele_ip = 2 * ele_iy
        ea = self.element_e * ele_a * 10 ** 6
        ei_y = self.element_e * ele_iy * 10 ** 6
        ei_z = self.element_e * ele_iy * 10 ** 6
        gi_t = self.element_g * ele_it * 10 ** 6
        l = self.element_length
        m = ele_a * self.element_rho
        k_loc = np.array([
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
        m_loc = (m * l / 420) * np.array([
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
        return k_loc, m_loc


if __name__ == "__main__":
    sections = {0: {'sec_number': 0,
                    'sec_height': 50,
                    'sec_ra_bot': 5,
                    'sec_ra_top': 5,
                    'sec_thickness': 30,
                    'sec_E': 210000,
                    'sec_G': 81000,
                    'sec_rho': 7850},
                1: {'sec_number': 1,
                    'sec_height': 50,
                    'sec_ra_bot': 5,
                    'sec_ra_top': 5,
                    'sec_thickness': 30,
                    'sec_E': 210000,
                    'sec_G': 81000,
                    'sec_rho': 7850}}
    springs = {}
    masses = {}
    forces = {}
    excentricity = {}
    calculation_param = {'fem_density': 50,
                         'fem_nbr_eigen_freq': 20,
                         'fem_dmas': 0.05,
                         'fem_exc': 1}

    calc = Calculation(sections, springs, masses, forces, excentricity, calculation_param)
    calc.start_calc()