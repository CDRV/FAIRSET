import argparse
import numpy as np
from termcolor import colored
from analysis.data.data_loader import DataLoader
from analysis.data.datatypes import Age, Sex, Skintone
from analysis.stats.discrete_groups.n_group_analysis import NGroupAnalysis
from analysis.utils import display_demog_box_plot

demographics_datatypes = {
    "age": Age,
    "sex": Sex,
    "skintone": Skintone,
}


def main(args):
    factor = args.factor

    data_loader = DataLoader()
    analysis = NGroupAnalysis(data_loader, factor)

    for kp_id in data_loader.get_keypoint_ids():
        anova = analysis.one_way_anova(kp_id)
        if anova["p"] <= 0.05 or args.all:
            if args.prerequisites:
                print(f"Prerequisites for keypoint {kp_id}:")
                shapiro_wilk = analysis.shapiro_wilk(kp_id)
                print(shapiro_wilk)
                skew_kurtosis = analysis.skew_and_kurtosis(kp_id)
                print(skew_kurtosis)
                levene = analysis.levene_test(kp_id)
                print(levene)
                n_samples = analysis.n_samples(kp_id)
                print(n_samples)
            if anova["p"] <= 0.05:
                print(colored(f"\nANOVA for keypoint {kp_id}| F: {anova['F']} p: {anova['p']}", "red"))
                post_hoc = analysis.tukey_post_hoc(kp_id)

                tukey_str = "Tukey: \n"
                for g1, g2, meandiff, p, _, _, reject in post_hoc:
                    if p.data != "p-adj" and p.data <= 0.05:
                        tukey_str += f"{g1.data}->{g2.data} diff: {meandiff.data:.4f} p: {p.data:.4f} reject: {reject.data}\n"
                print(colored(tukey_str, "yellow"))
            else:
                print(colored(f"ANOVA for keypoint {kp_id}| F: {anova['F']} p: {anova['p']}", "green"))

    if args.descriptive:
        data = data_loader.get_all_group_errors(factor)
        display_demog_box_plot(data, demographics_datatypes[factor])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analysis per keypoint on a demographic group")
    parser.add_argument(
        "-f", "--factor", action="store_true", default="age",
        help="The demographic factor on which to run the analysis (default is 'age', options are 'age', 'sex' and 'skintone')")
    parser.add_argument("-a", "--all", action="store_true", default=True,
                        help="Display all results, including non-significant keypoints")
    parser.add_argument("-p", "--prerequisites", action="store_true",
                        help="Runs and displays the prerequisites for the analysis")
    parser.add_argument("-d", "--descriptive", action="store_true", default=True,
                        help="Runs and displays the descriptive statistics for the analysis")

    args = parser.parse_args()
    main(args)
