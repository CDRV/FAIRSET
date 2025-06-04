import pandas as pd
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm

from analysis.data.data_loader import DataLoader
from analysis.data.datatypes import FACTORS, DiscreteFactorEnum
from analysis.stats.discrete_group_factors import DiscreteGroupFactors


class NGroupAnalysis(DiscreteGroupFactors):
    def __init__(self, data_loader: DataLoader, factor: str):
        super().__init__(data_loader, factor)

    def one_way_anova(self, kp_id: int):
        records = []
        for group in FACTORS[self._factor]:
            errors = self.data_loader.get_errors_by_group(self._factor, group, kp_id)
            for err in errors:
                if isinstance(group, DiscreteFactorEnum):
                    group_name = group.name
                else:
                    group_name = str(group)
                records.append({"group": group_name, "error": err})

        df = pd.DataFrame(records, columns=["error", "group"])
        model = ols("error ~ C(group)", data=df).fit()

        anova_results = anova_lm(model, typ=2)

        return {"F": anova_results.loc["C(group)", "F"], "p": anova_results.loc["C(group)", "PR(>F)"]}
