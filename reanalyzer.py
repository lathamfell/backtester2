import pandas as pd
from statistics import mean, median

PRINT_ID_NUMS = False


def main():
    id_num = None
    reset_configs = {}
    all_means_trail = []
    all_medians_trail = []
    all_means_nontrail = []
    all_medians_nontrail = []

    avg_mean_trail = None
    avg_median_trail = None
    avg_mean_nontrail = None
    avg_median_nontrail = None

    #analysis_file = "btcoll_prod_with_one_reset_pt.csv"
    #analysis_file = "btcoll_prod_with_two_reset_pts.csv"
    #analysis_file = "btcoll_prod_with_three_reset_pts.csv"
    #analysis_file = "btcoll_prod_with_four_reset_pts.csv"
    #analysis_file = "btcoll_prod_with_five_reset_pts.csv"
    analysis_file = "btcoll_prod_with_all_reset_pts.csv"

    df = pd.read_csv(filepath_or_buffer=analysis_file)
    for row in df.itertuples():
        mean_profit = getattr(row, "mean_profit")
        median_profit = getattr(row, "median_profit")
        trail = row[9]
        if PRINT_ID_NUMS:
            id_num = getattr(row, "id_num")
        if trail:
            all_means_trail.append(mean_profit)
            all_medians_trail.append(median_profit)
        else:
            all_means_nontrail.append(median_profit)
            all_medians_nontrail.append(median_profit)

        reset_config_as_str = row[5]
        if reset_config_as_str in reset_configs:
            reset_configs[reset_config_as_str]["mean_median_trail_ids"].append((mean_profit, median_profit, trail, id_num))
        else:
            reset_configs[reset_config_as_str] = {
                "mean_median_trail_ids": [(mean_profit, median_profit, trail, id_num)]
            }

    #avg_mean_trail = mean(all_means_trail)
    #avg_median_trail = median(all_medians_trail)
    avg_mean_nontrail = mean(all_means_nontrail)
    avg_median_nontrail = median(all_medians_nontrail)

    #print(f"avg mean trail: {round(avg_mean_trail, 3)}")
    #print(f"avg median trail: {round(avg_median_trail, 3)}")
    print(f"avg mean nontrail: {round(avg_mean_nontrail, 3)}")
    print(f"avg median nontrail: {round(avg_median_nontrail, 3)}")

    for rc in reset_configs:
        mean_and_median_count_above_avg_trail = 0
        mean_and_median_count_above_avg_nontrail = 0
        trail_strat_ids = []
        nontrail_strat_ids = []
        for _mean, _median, trail, id_num in reset_configs[rc]["mean_median_trail_ids"]:
            if trail:
                if _mean > avg_mean_trail and _median > avg_median_trail and _mean > _median:
                    mean_and_median_count_above_avg_trail += 1
                    if PRINT_ID_NUMS:
                        trail_strat_ids.append(id_num)
            else:
                if _mean > avg_mean_nontrail and _median > avg_median_nontrail and _mean > _median:
                    mean_and_median_count_above_avg_nontrail += 1
                    if PRINT_ID_NUMS:
                        nontrail_strat_ids.append(id_num)
        reset_configs[rc]["mean_and_median_count_above_avg_trail"] = mean_and_median_count_above_avg_trail
        reset_configs[rc]["mean_and_median_count_above_avg_nontrail"] = mean_and_median_count_above_avg_nontrail
        reset_configs[rc]["trail_strat_ids"] = trail_strat_ids
        reset_configs[rc]["nontrail_strat_ids"] = nontrail_strat_ids

    mean_and_median_rankings_trail = []
    mean_and_median_rankings_nontrail = []
    for rc in reset_configs:
        mean_and_median_rankings_trail.append({
            "sl_reset_points": rc,
            "mean_and_median_count_above_avg_trail": reset_configs[rc]["mean_and_median_count_above_avg_trail"],
            "trail_strat_ids": reset_configs[rc]["trail_strat_ids"]
        })
        mean_and_median_rankings_nontrail.append({
            "sl_reset_points": rc,
            "mean_and_median_count_above_avg_nontrail": reset_configs[rc]["mean_and_median_count_above_avg_nontrail"],
            "nontrail_strat_ids": reset_configs[rc]["nontrail_strat_ids"]
        })

    sorted_mean_and_median_rankings_trail = sorted(
        mean_and_median_rankings_trail, key=lambda k: k["mean_and_median_count_above_avg_trail"], reverse=True)
    sorted_mean_and_median_rankings_nontrail = sorted(
        mean_and_median_rankings_nontrail, key=lambda k: k["mean_and_median_count_above_avg_nontrail"], reverse=True)

    #print("trailing rankings")
    #for ranking in sorted_mean_and_median_rankings_trail:
    #    print(ranking)
    print("\nnontrailing rankings")
    for ranking in sorted_mean_and_median_rankings_nontrail:
        print(ranking)


if __name__ == "__main__":
    main()
