from typing import Dict
from abccalculation import ABCCalculation
import numpy as np

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

        all_element_matrices = list()
        for sefc_id, section_values in self.sections.items():
            section_height = section_values['sec_height']
            element_matrix = Elements(section_height).calc_element_matrix()
            all_element_matrices.append(element_matrix)
        for elem in all_element_matrices:
            print(elem)

        system_matrix = self.assembly_system_matrix()
        print(system_matrix)
        self.solution = [[1, 3], [4, 5], [5, 6]]
        self.return_solution()


class Elements():
    """
    Computation of system matrices and solution
    """

    def __init__(self, element_parameters):
        """
        ...
        :param element_parameters:
        """
        self.element_parameters = element_parameters

    def calc_element_matrix(self):
        """
        Calculates element matrix
        :return:
        """

        return np.array([[self.element_parameters * 11, 12], [21, 22]])

if __name__ == "__main__":
    sections = {0: {'sec_number': 0,
                    'sec_height': 1},
                1: {'sec_number': 1,
                    'sec_height': 2}}
    springs = {}
    masses = {}
    forces = {}
    excentricity = {}
    calculation_param = dict()
    calc = Calculation(sections, springs, masses, forces, excentricity, calculation_param)
    calc.start_calc()


