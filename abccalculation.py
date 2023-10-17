"""
Definition of abstract base class
"""

from abc import ABC, abstractmethod
from typing import Dict

class ABCCalculation(ABC):
    """
    Abstract base class with input parameters from GUI -> Output: Calculation results for visualization and text output
    ...
    """

    def __init__(self, sections: Dict[int, dict]):
        """

        :param sections: Defines the sections of the beam -> {0: {length: ..., diameter: ...}}
        """

        self.sections = sections

    @abstractmethod
    def return_solution(self):
        """
        :return: Dict[Dict[...]] -> Dict for eigenfrequencies: interpolation nodes and their respective
        displacement e.g. {0: {'eigenfreq': 123, 'solution': {0: {0,0}, 1: {0.03,0.1}, ...}}}
        """

        pass