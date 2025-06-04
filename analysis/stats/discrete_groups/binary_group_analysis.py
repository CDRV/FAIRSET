from scipy.stats import ttest_ind

from analysis.data.data_loader import DataLoader
from analysis.data.datatypes import FACTORS
from analysis.stats.discrete_group_factors import DiscreteGroupFactors


class BinaryGroupAnalysis(DiscreteGroupFactors):
    def __init__(self, data_loader: DataLoader, factor: str):
        super().__init__(data_loader, factor)

    def t_test(self):
        return ttest_ind(
            self.data_loader.get_errors_by_group(self._factor, FACTORS[self._factor][0]),
            self.data_loader.get_errors_by_group(self._factor, FACTORS[self._factor][1]),
            equal_var=False,
        )
