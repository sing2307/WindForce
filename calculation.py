from typing import Dict
from abccalculation import ABCCalculation
from scipy.sparse import csr_array
from scipy.sparse.linalg import eigsh
import numpy as np
import math


# Function to delete rows and columns from csr matrix
# From https://stackoverflow.com/questions/13077527/is-there-a-numpy-delete-equivalent-for-sparse-matrices
# TODO: Place function in different .py file?
def delete_from_csr(mat, row_indices=[], col_indices=[]):
    """
    Remove the rows and columns  from the CSR sparse matrix `mat`.
    WARNING: Indices of altered axes are reset in the returned matrix
    """
    if not isinstance(mat, csr_array):
        raise ValueError("works only for CSR format -- use .tocsr() first")

    rows = []
    cols = []
    if row_indices:
        rows = list(row_indices)
    if col_indices:
        cols = list(col_indices)

    if len(rows) > 0 and len(cols) > 0:
        row_mask = np.ones(mat.shape[0], dtype=bool)
        row_mask[rows] = False
        col_mask = np.ones(mat.shape[1], dtype=bool)
        col_mask[cols] = False
        return mat[row_mask][:, col_mask]
    elif len(rows) > 0:
        mask = np.ones(mat.shape[0], dtype=bool)
        mask[rows] = False
        return mat[mask]
    elif len(cols) > 0:
        mask = np.ones(mat.shape[1], dtype=bool)
        mask[cols] = False
        return mat[:, mask]
    else:
        return mat


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
        self.k_glob = np.array([0], dtype=np.float64)
        self.m_glob = np.array([0], dtype=np.float64)
        self.nodes = np.array([0], dtype=np.float64)
        self.solution = {}


    def return_solution(self):
        """
        ...
        :return:
        """
        self.start_calc()
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
        k_glob = csr_array((k_g, (np.array(i_g) - 1, np.array(j_g) - 1)), shape=(num_dofs, num_dofs), dtype=np.float64)
        m_glob = csr_array((m_g, (np.array(i_g) - 1, np.array(j_g) - 1)), shape=(num_dofs, num_dofs), dtype=np.float64)

        # Assemble discrete masses and springs (TODO...)

        # Assemble boundary conditions (TODO: Bottom is clamped. Has to be changed if the springs are implemented.)
        k_glob = delete_from_csr(k_glob, row_indices=[range(6)], col_indices=[range(6)])
        m_glob = delete_from_csr(m_glob, row_indices=[range(6)], col_indices=[range(6)])

        # Return global stiffness and mass matrix
        return k_glob, m_glob

    def solve_system(self):
        """
        Solves for eigenfrequencies and the respective nodes displacement
        :return:
        """
        # Solve the generalized eigenvalue problem
        [eigenvalues_sq, eigenvector] = eigsh(self.k_glob, k=self.calculation_param['fem_nbr_eigen_freq'],
                                              M=self.m_glob, which='SM')
        eigenfrequencies = np.sqrt(eigenvalues_sq).real
        return eigenfrequencies, eigenvector

    def start_calc(self):
        min_height = min(section['sec_height'] for section in self.sections.values())
        dofs = np.arange(-5, 7)
        # Extract the section parameters in the first loop and discretize each section into a subset of elements.
        # Calculate the cross-section radii in the middle of each element
        for sefc_id, section_values in self.sections.items():
            sefc_id = int(sefc_id)
            section_height = section_values['sec_height']
            self.number_of_elements.append((self.calculation_param['fem_density'] * round(section_height / min_height)))
            num_elements = self.number_of_elements[sefc_id]
            element_length = section_height / num_elements
            max_nodes = max(self.nodes)
            self.nodes = np.append(self.nodes, np.arange(element_length, section_height + element_length,
                                                         element_length) + max_nodes)
            section_t = section_values['sec_thickness'] * 10 ** (-2)  # unit conversion cm -> m
            section_ra_bot = section_values['sec_ra_bot']
            section_ra_top = section_values['sec_ra_top']
            element_ra_mid = section_ra_bot - (section_ra_bot - section_ra_top) / section_height * element_length * (
                    np.arange(1, num_elements + 1) - 0.5)
            section_e = section_values['sec_E'] * 10 ** 6  # unit conversion MPa -> N/mm²
            section_g = section_values['sec_G'] * 10 ** 6  # unit conversion MPa -> N/mm²
            section_rho = section_values['sec_rho']
            # Calculate the element stiffness, mass matrix and the connectivity for each section element.
            # units: [N], [m] , [kg]
            for index in range(len(element_ra_mid)):
                element_ri_mid = element_ra_mid[index] - section_t
                ele_a = math.pi * (element_ra_mid[index] ** 2 - element_ri_mid ** 2)
                ele_iy = (math.pi / 4) * (element_ra_mid[index] ** 4 - element_ri_mid ** 4)  # Iy = Iz
                ele_it = (math.pi / 2) * (element_ra_mid[index] ** 4 - element_ri_mid ** 4)
                ele_ip = 2 * ele_iy
                ea = section_e * ele_a
                ei_y = section_e * ele_iy
                ei_z = section_e * ele_iy
                gi_t = section_g * ele_it
                m = ele_a * section_rho
                element_k_matrix, element_m_matrix = Elements(element_length, ele_a, ea, ei_y, ei_z, gi_t, ele_ip, m,
                                                              'vertical').calc_element_matrix()
                dofs = dofs + 6
                self.element_matrices.append({'DOFs': dofs, 'K': element_k_matrix, 'M': element_m_matrix})
        # Calculate node matrix "node_seg_ele" containing the nodes of each element of the sections.
        nodes_seg_ele = np.column_stack((np.zeros(self.nodes.size), np.zeros(self.nodes.size), self.nodes))
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
                (nodes_exc, np.zeros(nodes_exc.size), np.ones(nodes_exc.size) * np.max(nodes_seg_ele)))
            self.nodes = np.append(nodes_seg_ele, nodes_exc[1:, :], axis=0)
        else:
            self.nodes = nodes_seg_ele

        # Assemble global matrices
        self.k_glob, self.m_glob = self.assembly_system_matrix()

        # Solve eigenvalue problem to calculate eigenfrequencies and eigenmodes
        eigenfrequencies, eigenvectors = self.solve_system()
        # Calculate node displacements. The max displacement for each eigenmode is set to 1
        displacements = np.array(eigenvectors)
        displacements = np.append(np.zeros((6, len(eigenfrequencies))), displacements, axis=0)
        max_disp_per_mode = np.max(np.abs(displacements), axis=0)
        displacements = np.transpose(np.transpose(displacements) / max_disp_per_mode.reshape(-1, 1))
        displacement_ux = displacements[0::6, :]
        displacement_uy = displacements[1::6, :]
        displacement_uz = displacements[2::6, :]
        # Save solution
        for freq_number, (eigenfreq, solution) in enumerate(zip(eigenfrequencies, eigenvectors)):
            self.solution[freq_number] = {
                'eigenfreq': eigenfreq,
                'solution': self.nodes + np.hstack((displacement_ux[:, freq_number].reshape(-1, 1),
                                                    displacement_uy[:, freq_number].reshape(-1, 1),
                                                    displacement_uz[:, freq_number].reshape(-1, 1)))
            }


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
        ], dtype=np.float64)
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
        ], dtype=np.float64)
        transform_vertical = np.array([
            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0]
        ], dtype=np.float64)
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
    excentricity = {'exc_ex': 0,
                    'exc_EA': 10000000000000,
                    'exc_EIy': 10000000000000,
                    'exc_EIz': 10000000000000,
                    'exc_GIt': 10000000000000,
                    'exc_mass': 2,
                    'exc_area': 10,
                    'exc_Ip': 10}
    calculation_param = {'fem_density': 2,
                         'fem_nbr_eigen_freq': 20,
                         'fem_dmas': 0.05,
                         'fem_exc': 1}

    calc = Calculation(sections, springs, masses, forces, excentricity, calculation_param)
    calc.start_calc()
    solution = calc.return_solution()
    print(solution)
