FIRST_RESETS = [[0.5, -0.25], [1, -0.25], [1, -0.5], [1, -0.75], [1.5, -0.75], [1.5, -1], [1.5, -1.25], [2, -1.25], [2, -1.5], [2, -1.75]]
SECOND_RESETS = [[2, -0.5], [2, -1], [2, -1.5], [3, -1.5], [3, -2], [3, -2.5], [4, -2.5], [4, -3], [4, -3.5]]
THIRD_RESETS = [[3, -0.75], [3, -1.5], [3, -2.25], [4.5, -2.25], [4.5, -3], [4.5, -3.75], [6, -3.75], [6, -4.5], [6, -5.25]]
FOURTH_RESETS = [[4, -1], [4, -2], [4, -3], [6, -3], [6, -4], [6, -5], [8, -5], [8, -6], [8, -7]]


def main():

    double_sls = []
    for i in FIRST_RESETS:
        for j in SECOND_RESETS:
            if i[0] >= j[0]:  # previous trigger >= next, e.g. do not want [1, -0.5], [1, -0.75] or [1.5, -0.5], [1, -0.75]
                continue
            if i[1] <= j[1]:  # previous floor not <= next (flipped b/c floors are negative) e.g. do not want [1, -0.5], [1.5, -0.5] or [1, -0.75], [1.5, -0.5]
                continue
            if [i[0], j[0]] in double_sls:  # dupe
                continue
            double_sls.append([i, j])
    print(f"\ndoubles: {double_sls}  doubles")

    triple_sls = []
    for i in double_sls:
        for j in THIRD_RESETS:
            if i[1][0] >= j[0]: # previous trigger >= next
                continue
            if i[1][1] <= j[1]: # previous floor not <= next
                continue
            if [i[0], i[1], j[0]] in triple_sls:  # dupe
                continue
            triple_sls.append([i[0], i[1], j])
    print(f"\ntriples: {triple_sls}  triples")

    quad_sls = []
    for i in triple_sls:
        for j in FOURTH_RESETS:
            if i[2][0] >= j[0]:
                continue
            if i[2][0] <= j[1]:
                continue
            if [i[0], i[1], i[2], j[0]] in quad_sls:
                continue
            quad_sls.append([i[0], i[1], i[2], j])
    print(f"\nquads: {quad_sls}  quads")
    print("done")


if __name__ == "__main__":
    main()
