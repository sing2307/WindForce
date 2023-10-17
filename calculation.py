from typing import Dict
from abccalculation import ABCCalculation


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
        print("kek")
        #return NotImplemented

    def assembly_system_matrix(self):
        """
        Calculates element matrices for every section, assembly system
        :return:
        """
        return NotImplemented

    def solve_system(self):
        """
        Solves for eigenfrequencies and the respective nodes displacement
        :return:
        """
        return NotImplemented

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

    def element_matrix(self):
        """
        Calculates element matrix
        :return:
        """
        return NotImplementedError


element_parameters = {1: {'length': 1, 'diameter': 0.5},
                      2: {'length': 2, 'diameter': 0.25}}
calc = Calculation(element_parameters)

