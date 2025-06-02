import numpy as np
from scipy.stats import levene, shapiro, skew, kurtosis
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import pandas as pd

from analysis.data.datatypes import FACTORS
from analysis.data.data_loader import DataLoader


class DiscreteGroupFactors:
    def __init__(self, data_loader: DataLoader, factor: str):
        if factor not in FACTORS.keys():
            raise ValueError(f"Invalid factor: {factor}")
        self.data_loader = data_loader
        self._factor = factor

    def skew_and_kurtosis(self, kp_id):
        results = {}
        for group in FACTORS[self._factor]:
            group_nmes = self.data_loader.get_errors_by_group(self._factor, group, kp_id)
            results[group] = {"skew": skew(group_nmes), "kurtosis": kurtosis(group_nmes)}
        return results

    def shapiro_wilk(self, kp_id):
        results = {}
        for group in FACTORS[self._factor]:
            group_nmes = self.data_loader.get_errors_by_group(self._factor, group, kp_id)
            stat, p_value = shapiro(group_nmes)
            results[group] = {"stat": stat, "p_value": p_value}
        return results

    def n_samples(self, kp_id):
        results = {}
        for group in FACTORS[self._factor]:
            group_nmes = self.data_loader.get_errors_by_group(self._factor, group, kp_id)
            results[group] = len(group_nmes)
        return results

    def levene_test(self, kp_id):
        stat, p_value = levene(*[self.data_loader.get_errors_by_group(self._factor, group, kp_id)
                               for group in FACTORS[self._factor]])
        return {"stat": stat, "p_value": p_value}

    def tukey_post_hoc(self, kp_id):
        values, groups = [], []
        for group in FACTORS[self._factor]:
            group_values = self.data_loader.get_errors_by_group(self._factor, group, kp_id)
            values.extend(group_values)
            groups.extend([group.name] * len(group_values))
        tukey = pairwise_tukeyhsd(endog=np.array(values), groups=np.array(groups), alpha=0.05)
        return tukey.summary()
