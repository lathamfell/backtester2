import config_common as cc

ONE_RESETS = cc.SLS_BTC_7PCT_RESETS_ONE_RESET
TWO_RESETS = cc.SLS_BTC_7PCT_RESETS_TWO_RESETS
THREE_RESETS = cc.SLS_BTC_7PCT_RESETS_THREE_RESETS

FIRST_RESETS = [[0.5, -0.25], [1, -0.25], [1, -0.5], [1, -0.75], [1.5, -0.75], [1.5, -1], [1.5, -1.25], [2, -1.25], [2, -1.5], [2, -1.75]]
SECOND_RESETS = [[2, -0.5], [2, -1], [2, -1.5], [3, -1.5], [3, -2], [3, -2.5], [4, -2.5], [4, -3], [4, -3.5]]
THIRD_RESETS = [[3, -0.75], [3, -1.5], [3, -2.25], [4.5, -2.25], [4.5, -3], [4.5, -3.75], [6, -3.75], [6, -4.5], [6, -5.25]]
FOURTH_RESETS = [[4, -1], [4, -2], [4, -3], [6, -3], [6, -4], [6, -5], [8, -5], [8, -6], [8, -7]]
FIFTH_RESETS = [[5, -1.25], [5, -2.5], [5, -3.75], [7.5, -3.75], [7.5, -5], [7.5, -6.25], [10, -6.25], [10, -7.5], [10, -8.75]]
SIXTH_RESETS = [[6, -1.5], [6, -3], [6, -4.5], [9, -4.5], [9, -6], [9, -7.5], [12, -7.5], [12, -9], [12, -10.5]]
SEVENTH_RESETS = [[7, -1.75], [7, -3.5], [7, -5.25], [10.5, -5.25], [10.5, -7], [10.5, -8.75], [14, -8.75], [14, -10.5], [14, -12.25]]


def main():

    single_sls = ONE_RESETS
    print(f"\nsingles: {single_sls}  singles")

    double_sls = TWO_RESETS
    for i in single_sls:
        for j in SECOND_RESETS:
            if i[0][0] >= j[0]:  # previous trigger >= next, e.g. do not want [1, -0.5], [1, -0.75] or [1.5, -0.5], [1, -0.75]
                continue
            if i[0][1] <= j[1]:  # previous floor not <= next (flipped b/c floors are negative) e.g. do not want [1, -0.5], [1.5, -0.5] or [1, -0.75], [1.5, -0.5]
                continue
            if [i[0], j] in double_sls:  # dupe
                continue
            double_sls.append([i[0], j])
    print(f"\ndoubles: {double_sls}  doubles")

    triple_sls = THREE_RESETS
    for i in double_sls:
        for j in THIRD_RESETS:
            if i[1][0] >= j[0]:  # previous trigger >= next
                continue
            if i[1][1] <= j[1]:  # previous floor not <= next
                continue
            if [i[0], i[1], j] in triple_sls:  # dupe
                continue
            triple_sls.append([i[0], i[1], j])
    print(f"\ntriples: {triple_sls}  triples")
    #for p in triple_sls:
    #    print(p)

    quad_sls = []
    for i in triple_sls:
        for j in FOURTH_RESETS:
            if i[2][0] >= j[0]:
                continue
            if i[2][1] <= j[1]:
                continue
            if [i[0], i[1], i[2], j] in quad_sls:
                continue
            quad_sls.append([i[0], i[1], i[2], j])
    print(f"\nquads: {quad_sls}  quads")
    #for p in quad_sls:
    #    print(p)

    quint_sls = []
    for i in quad_sls:
        for j in FIFTH_RESETS:
            if i[3][0] >= j[0]:
                continue
            if i[3][1] <= j[1]:
                continue
            if [i[0], i[1], i[2], i[3], j] in quint_sls:
                continue
            quint_sls.append([i[0], i[1], i[2], i[3], j])
    print(f"\nquints: {quint_sls}  quints")
    #for p in quint_sls:
    #    print(p)

    seis_sls = []
    for i in quint_sls:
        for j in SIXTH_RESETS:
            if i[4][0] >= j[0]:
                continue
            if i[4][1] <= j[1]:
                continue
            if [i[0], i[1], i[2], i[3], i[4], j] in seis_sls:
                continue
            seis_sls.append([i[0], i[1], i[2], i[3], i[4], j])
    print(f"\nseis: {seis_sls}  seis")
    # for p in seis_sls:
    #    print(p)

    siete_sls = []
    for i in seis_sls:
        for j in SEVENTH_RESETS:
            if i[5][0] >= j[0]:
                continue
            if i[5][1] <= j[1]:
                continue
            if [i[0], i[1], i[2], i[3], i[4], i[5], j] in siete_sls:
                continue
            siete_sls.append([i[0], i[1], i[2], i[3], i[4], i[5], j])
    print(f"\nsiete: {siete_sls}  siete")
    # for p in siete_sls:
    #    print(p)
    print("done")


if __name__ == "__main__":
    main()
