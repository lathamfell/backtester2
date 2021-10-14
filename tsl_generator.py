# FIRST_RESETS_TRAIL = [[[1.5, -0.2]]]
# SECOND_RESETS_TRAIL = [[[2, -0.5]]]
# THIRD_RESETS_TRAIL = [[[2.5, -2]]]
# all nontrail below.  Each one is current champ, then variations
FIRST_RESETS = [[[1.5, -1]], [[1.5, -0.5]], [[2, -0.5]], [[2, -1]], [[2, -1.5]]]
SECOND_RESETS = [[[3.5, -2]], [[3.5, -1]], [[3.5, -1.5]]]
THIRD_RESETS = [[[4, -2.5]], [[4, -1.5]], [[4, -2]]]
FOURTH_RESETS = [[[7, -3.5]]]
FIFTH_RESETS = [[[12, -6]]]
SIXTH_RESETS = [[[14, -12]]]
SEVENTH_RESETS = [[[16, -14]]]
EIGHTH_RESETS = [[[20, -15]]]

# FIRST_RESETS = FIRST_RESETS_TRAIL + FIRST_RESETS_NONTRAIL
# SECOND_RESETS = SECOND_RESETS_TRAIL + SECOND_RESETS_NONTRAIL
# THIRD_RESETS = THIRD_RESETS_TRAIL + THIRD_RESETS_NONTRAIL


def main():
    trigger_points = [
        1,
        1.5,
        2,
        2.5,
        3,
        3.5,
        4,
        5,
        6,
        7,
        8,
        10,
        12,
        14,
        16,
        20,
        24,
        28,
        32,
        36,
    ]
    gaps = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4, 4, 4, 5, 6, 7, 8, 10, 12, 14, 16, 18]
    increments = [
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        1,
        1.5,
        2,
        2,
        2,
        2.5,
        3,
        3.5,
        4,
        6,
    ]

    single_sls = []
    for i, trig_p in enumerate(trigger_points):
        gap = gaps[i]
        increment = increments[i]
        for j in [x * increment for x in range(1, int(trig_p * (1 / increment)))]:
            if trig_p - abs(j) <= gap:
                single_sls.append([[trig_p, -1 * j]])
                if j == 0.5:
                    # also add a 0.2 version
                    single_sls.append([[trig_p, -0.2]])
    print(f"singles: {single_sls}  singles")

    double_sls = []
    for i in FIRST_RESETS:
        for j in single_sls:
            if (
                i[0][0] < j[0][0]
                and i[0][1] > j[0][1]
                and [i[0], j[0]] not in double_sls
            ):
                double_sls.append([i[0], j[0]])
    print(f"\ndoubles: {double_sls}  doubles")

    triple_sls = []
    for i in FIRST_RESETS:
        for j in SECOND_RESETS:
            for k in single_sls:
                if (
                    i[0][0] < j[0][0] < k[0][0]
                    and i[0][1] > j[0][1] > k[0][1]
                    and [i[0], j[0], k[0]] not in triple_sls
                ):
                    triple_sls.append([i[0], j[0], k[0]])
    print(f"\ntriples: {triple_sls}  triples")

    quad_sls = []
    for i in FIRST_RESETS:
        for j in SECOND_RESETS:
            for k in THIRD_RESETS:
                for l in single_sls:
                    if (
                        i[0][0] < j[0][0] < k[0][0] < l[0][0]
                        and i[0][1] > j[0][1] > k[0][1] > l[0][1]
                        and [i[0], j[0], k[0], l[0]] not in quad_sls
                    ):
                        quad_sls.append([i[0], j[0], k[0], l[0]])
    print(f"\nquads: {quad_sls}  quads")

    quint_sls = []
    for i in FIRST_RESETS:
        for j in SECOND_RESETS:
            for k in THIRD_RESETS:
                for l in FOURTH_RESETS:
                    for m in single_sls:
                        if (
                            i[0][0] < j[0][0] < k[0][0] < l[0][0] < m[0][0]
                            and i[0][1] > j[0][1] > k[0][1] > l[0][1] > m[0][1]
                            and [i[0], j[0], k[0], l[0], m[0]] not in quint_sls
                        ):
                            quint_sls.append([i[0], j[0], k[0], l[0], m[0]])
    print(f"\nquints: {quint_sls}  quints")

    seis_sls = []
    for i in FIRST_RESETS:
        for j in SECOND_RESETS:
            for k in THIRD_RESETS:
                for l in FOURTH_RESETS:
                    for m in FIFTH_RESETS:
                        for n in single_sls:
                            if (
                                i[0][0]
                                < j[0][0]
                                < k[0][0]
                                < l[0][0]
                                < m[0][0]
                                < n[0][0]
                                and i[0][1]
                                > j[0][1]
                                > k[0][1]
                                > l[0][1]
                                > m[0][1]
                                > n[0][1]
                                and [i[0], j[0], k[0], l[0], m[0], n[0]] not in seis_sls
                            ):
                                seis_sls.append([i[0], j[0], k[0], l[0], m[0], n[0]])
    print(f"\nseis: {seis_sls}  seis")

    siete_sls = []
    for i in FIRST_RESETS:
        for j in SECOND_RESETS:
            for k in THIRD_RESETS:
                for l in FOURTH_RESETS:
                    for m in FIFTH_RESETS:
                        for n in SIXTH_RESETS:
                            for o in single_sls:
                                if (
                                    i[0][0]
                                    < j[0][0]
                                    < k[0][0]
                                    < l[0][0]
                                    < m[0][0]
                                    < n[0][0]
                                    < o[0][0]
                                    and i[0][1]
                                    > j[0][1]
                                    > k[0][1]
                                    > l[0][1]
                                    > m[0][1]
                                    > n[0][1]
                                    > o[0][1]
                                    and [i[0], j[0], k[0], l[0], m[0], n[0], o[0]]
                                    not in siete_sls
                                ):
                                    siete_sls.append(
                                        [i[0], j[0], k[0], l[0], m[0], n[0], o[0]]
                                    )
    print(f"\nsiete: {siete_sls}  siete")

    ocho_sls = []
    for i in FIRST_RESETS:
        for j in SECOND_RESETS:
            for k in THIRD_RESETS:
                for l in FOURTH_RESETS:
                    for m in FIFTH_RESETS:
                        for n in SIXTH_RESETS:
                            for o in SEVENTH_RESETS:
                                for p in single_sls:
                                    if (
                                        i[0][0]
                                        < j[0][0]
                                        < k[0][0]
                                        < l[0][0]
                                        < m[0][0]
                                        < n[0][0]
                                        < o[0][0]
                                        < p[0][0]
                                        and i[0][1]
                                        > j[0][1]
                                        > k[0][1]
                                        > l[0][1]
                                        > m[0][1]
                                        > n[0][1]
                                        > o[0][1]
                                        > p[0][1]
                                        and [i[0], j[0], k[0], l[0], m[0], n[0], o[0], p[0]]
                                        not in ocho_sls
                                    ):
                                        ocho_sls.append(
                                            [i[0], j[0], k[0], l[0], m[0], n[0], o[0], p[0]]
                                        )
    print(f"\nocho: {ocho_sls}  ocho")
    """
    nueve_sls = []
    for i in FIRST_RESETS:
        for j in SECOND_RESETS:
            for k in THIRD_RESETS:
                for l in FOURTH_RESETS:
                    for m in FIFTH_RESETS:
                        for n in SIXTH_RESETS:
                            for o in SEVENTH_RESETS:
                                for p in EIGHTH_RESETS:
                                    for q in single_sls:
                                        if (
                                            i[0][0]
                                            < j[0][0]
                                            < k[0][0]
                                            < l[0][0]
                                            < m[0][0]
                                            < n[0][0]
                                            < o[0][0]
                                            < p[0][0]
                                            < q[0][0]
                                            and i[0][1]
                                            > j[0][1]
                                            > k[0][1]
                                            > l[0][1]
                                            > m[0][1]
                                            > n[0][1]
                                            > o[0][1]
                                            > p[0][1]
                                            > q[0][1]
                                            and [i[0], j[0], k[0], l[0], m[0], n[0], o[0], p[0], q[0]]
                                            not in nueve_sls
                                        ):
                                            nueve_sls.append(
                                                [i[0], j[0], k[0], l[0], m[0], n[0], o[0], p[0], q[0]]
                                            )
    print(f"\nnueve: {nueve_sls} nueve")

    diez_sls = []
    for i in FIRST_RESETS:
        for j in SECOND_RESETS:
            for k in THIRD_RESETS:
                for l in FOURTH_RESETS:
                    for m in FIFTH_RESETS:
                        for n in SIXTH_RESETS:
                            for o in SEVENTH_RESETS:
                                for p in EIGHTH_RESETS:
                                    for q in NINTH_RESETS:
                                        for r in single_sls:
                                            if (
                                                i[0][0]
                                                < j[0][0]
                                                < k[0][0]
                                                < l[0][0]
                                                < m[0][0]
                                                < n[0][0]
                                                < o[0][0]
                                                < p[0][0]
                                                < q[0][0]
                                                < r[0][0]
                                                and i[0][1]
                                                > j[0][1]
                                                > k[0][1]
                                                > l[0][1]
                                                > m[0][1]
                                                > n[0][1]
                                                > o[0][1]
                                                > p[0][1]
                                                > q[0][1]
                                                > r[0][1]
                                                and [i[0], j[0], k[0], l[0], m[0], n[0], o[0], p[0], q[0], r[0]]
                                                not in diez_sls
                                            ):
                                                diez_sls.append(
                                                    [i[0], j[0], k[0], l[0], m[0], n[0], o[0], p[0], q[0], r[0]]
                                                )
    print(f"\ndiez: {diez_sls} diez")
    """
    print("done")


if __name__ == "__main__":
    main()
