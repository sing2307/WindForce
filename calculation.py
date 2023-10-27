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
        self.nodes = np.array([0])
        self.solution = {}

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
        # TODO: Bad workaround to delete rows and columns of csr matrix.
        #  Maybe implement function from
        #  https://stackoverflow.com/questions/13077527/is-there-a-numpy-delete-equivalent-for-sparse-matrices ?
        k_glob = np.delete(np.delete(k_glob.toarray(), range(6), 0), range(6), 1)
        m_glob = np.delete(np.delete(m_glob.toarray(), range(6), 0), range(6), 1)
        # Return global stiffness and mass matrix
        return k_glob, m_glob

    def solve_system(self):
        """
        Solves for eigenfrequencies and the respective nodes displacement
        :return:
        """
        # Solve the generalized eigenvalue problem
        [eigenvalues_sq, eigenvector] = eigh(self.k_glob, self.m_glob,
                                             subset_by_index=[0, self.calculation_param['fem_nbr_eigen_freq'] - 1])
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
            max_nodes = max(self.nodes)
            self.nodes = np.append(self.nodes, np.arange(element_length, section_height + element_length,
                                                         element_length) + max_nodes)
            section_t = section_values['sec_thickness']
            section_ra_bot = section_values['sec_ra_bot']
            section_ra_top = section_values['sec_ra_top']
            element_ra_mid = section_ra_bot - (section_ra_bot - section_ra_top) / section_height * element_length * (
                    np.arange(1, num_elements + 1) - 0.5)
            section_e = section_values['sec_E']
            section_g = section_values['sec_G']
            section_rho = section_values['sec_rho']
            # Calculate the element stiffness, mass matrix and the connectivity for each section element.
            # units: [N], [m] , [kg]
            for index in range(len(element_ra_mid)):
                element_ri_mid = element_ra_mid[index] - section_t * 10 ** (-2)
                ele_a = math.pi * (element_ra_mid[index] ** 2 - element_ri_mid ** 2)
                ele_iy = (math.pi / 4) * (element_ra_mid[index] ** 4 - element_ri_mid ** 4)  # Iy = Iz
                ele_it = (math.pi / 2) * (element_ra_mid[index] ** 4 - element_ri_mid ** 4)
                ele_ip = 2 * ele_iy
                ea = section_e * ele_a * 10 ** 6
                ei_y = section_e * ele_iy * 10 ** 6
                ei_z = section_e * ele_iy * 10 ** 6
                gi_t = section_g * ele_it * 10 ** 6
                m = ele_a * section_rho
                element_k_matrix, element_m_matrix = Elements(element_length, ele_a, ea, ei_y, ei_z, gi_t, ele_ip, m,
                                                              'vertical').calc_element_matrix()
                dofs = dofs + 6
                self.element_matrices.append({'DOFs': dofs, 'K': element_k_matrix, 'M': element_m_matrix})
        # Calculate node matrix "node_seg_ele" containing the nodes of each element of the sections.
        nodes_seg_ele = np.column_stack((np.zeros(self.nodes.size), self.nodes, np.zeros(self.nodes.size)))
        # Calculate the element stiffness, mass matrix and the connectivity for each excentricity element.
        # element_length_exc is the element length of the excentricity.
        # The discretization [elements/m] equals the discretization of the shortest segment.
        l_exc = self.excentricity['exc_ex']
        if l_exc > 0:
            num_elements_exc = max(round(self.calculation_param['fem_density'] * l_exc / min_height), 1)
            element_length_exc = l_exc / num_elements_exc
            exc_k_matrix, exc_element_m_matrix = Elements(element_length_exc, self.excentricity['exc_area'],
                                                          self.excentricity['exc_EA'], self.excentricity['exc_EIy'],
                                                          self.excentricity['exc_EIz'],
                                                          self.excentricity['exc_GIt'], self.excentricity['exc_Ip'],
                                                          self.excentricity['exc_mass'],
                                                          'horizontal').calc_element_matrix()
            for index in range(num_elements_exc):
                dofs = dofs + 6
                self.element_matrices.append({'DOFs': dofs, 'K': exc_k_matrix, 'M': exc_element_m_matrix})
            # Construct node matrix "nodes_exc".
            nodes_exc = np.arange(0, l_exc + element_length_exc, element_length_exc)
            nodes_exc = np.column_stack(
                (nodes_exc, np.ones(nodes_exc.size) * np.max(nodes_seg_ele), np.zeros(nodes_exc.size)))
            self.nodes = np.append(nodes_seg_ele, nodes_exc[1:, :], axis=0)
        else:
            self.nodes = nodes_seg_ele

        # Assemble global matrices
        self.k_glob, self.m_glob = self.assembly_system_matrix()

        # Solve eigenvalue problem to calculate eigenfrequencies and eigenmodes
        eigenfrequencies, eigenvectors = self.solve_system()
        print(f'The first {len(eigenfrequencies)} eigenfrequencies [rad/s] are:')
        print(eigenfrequencies)
        # Save solution
        for freq_number, (eigenfreq, solution) in enumerate(zip(eigenfrequencies, eigenvectors)):
            self.solution[freq_number] = {
                'eigenfreq': eigenfreq,
                'solution': solution
            }
        # self.return_solution()


class Elements:
    """
    Computation of system matrices and solution
    """

    def __init__(self, element_length, ele_a, ea, ei_y, ei_z, gi_t, ele_ip, m, orientation):
        """
        ...
        :param element_parameters:
        """
        self.len = element_length
        self.ele_a = ele_a
        self.ea = ea
        self.ei_y = ei_y
        self.ei_z = ei_z
        self.gi_t = gi_t
        self.ele_ip = ele_ip
        self.m = m
        self.orientation = orientation

    def calc_element_matrix(self):
        """
        Calculates element stiffness and mass matrix
        :return:
        """
        # units: [N], [m] , [kg]
        # For conciseness of matrices:
        l = self.len
        ele_a = self.ele_a
        ea = self.ea
        ei_y = self.ei_y
        ei_z = self.ei_z
        gi_t = self.gi_t
        ele_ip = self.ele_ip
        m = self.m
        # element stiffness and mass matrix:
        k_loc = np.array([
            [ea / l, 0, 0, 0, 0, 0, -ea / l, 0, 0, 0, 0, 0],
            [0, (12 * ei_z) / (l ** 3), 0, 0, 0, 6 * ei_z / (l ** 2), 0, -12 * ei_z / (l ** 3), 0, 0, 0,
             6 * ei_z / (l ** 2)],
            [0, 0, 12 * ei_y / (l ** 3), 0, -6 * ei_y / (l ** 2), 0, 0, 0, -12 * ei_y / (l ** 3), 0,
             -6 * ei_y / (l ** 2), 0],
            [0, 0, 0, gi_t / l, 0, 0, 0, 0, 0, -gi_t / l, 0, 0],
            [0, 0, -6 * ei_y / (l ** 2), 0, 4 * ei_y / l, 0, 0, 0, 6 * ei_y / (l ** 2), 0, 2 * ei_y / l, 0],
            [0, 6 * ei_z / (l ** 2), 0, 0, 0, 4 * ei_z / l, 0, -6 * ei_z / (l ** 2), 0, 0, 0, 2 * ei_z / l],
            [-ea / l, 0, 0, 0, 0, 0, ea / l, 0, 0, 0, 0, 0],
            [0, (-12 * ei_z) / (l ** 3), 0, 0, 0, -6 * ei_z / (l ** 2), 0, 12 * ei_z / (l ** 3), 0, 0, 0,
             -6 * ei_z / (l ** 2)],
            [0, 0, -12 * ei_y / (l ** 3), 0, 6 * ei_y / (l ** 2), 0, 0, 0, 12 * ei_y / (l ** 3), 0, 6 * ei_y / (l ** 2),
             0],
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
        transform_vertical = np.array([
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        ])
        if self.orientation == 'vertical':
            k_loc = transform_vertical @ k_loc @ np.transpose(transform_vertical)
            m_loc = transform_vertical @ m_loc @ np.transpose(transform_vertical)
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
    excentricity = {'exc_ex': 2,
                    'exc_EA': 10000000000000,
                    'exc_EIy': 10000000000000,
                    'exc_EIz': 10000000000000,
                    'exc_GIt': 10000000000000,
                    'exc_mass': 0.02,
                    'exc_area': 10,
                    'exc_Ip': 10}
    calculation_param = {'fem_density': 20,
                         'fem_nbr_eigen_freq': 20,
                         'fem_dmas': 0.05,
                         'fem_exc': 1}

    calc = Calculation(sections, springs, masses, forces, excentricity, calculation_param)
    calc.start_calc()
