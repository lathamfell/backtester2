# generate list of all possible reset points up to a limit of count and highest trigger

RESET_COUNT = 3  # highest number of reset points
RESET_TRIGGER_LIMIT = 5  # highest trigger to generate. eg. 1.5, 12, 36

# trigger is what price movement triggers the reset
# gap is how far away from the trigger to find first reset point. Example 10 trigger, 6 gap, first reset is [10, 4]
# increment is space between points from bottom of gap to trigger.
#   Example 10 trigger, 6 gap, 0.5 increment, first two resets are [10, 4], [10, 4.5]
POINTS = [
    {"trigger": 0.5, "start": 0.25, "increment": 0.25},
    {"trigger": 1, "start": 0.25, "increment": 0.25},
    {"trigger": 1.5, "start": 0.25, "increment": 0.25},
    {"trigger": 2, "start": 0.5, "increment": 0.5},
    {"trigger": 2.5, "start": 0.5, "increment": 0.5},
    {"trigger": 3, "start": 0.5, "increment": 0.5},
    {"trigger": 3.5, "start": 0.5, "increment": 0.5},
    {"trigger": 4, "start": 0.5, "increment": 0.5},
    {"trigger": 4.5, "start": 0.5, "increment": 0.5},
    {"trigger": 5, "start": 1, "increment": 0.5},
    {"trigger": 6, "start": 2, "increment": 0.5},
    {"trigger": 7, "start": 3, "increment": 0.5},
    {"trigger": 8, "start": 4, "increment": 1},
    {"trigger": 10, "start": 5, "increment": 1},
    {"trigger": 12, "start": 6, "increment": 1.5},
    {"trigger": 14, "start": 7, "increment": 2},
    {"trigger": 16, "start": 8, "increment": 2},
    {"trigger": 20, "start": 10, "increment": 2.5},
    {"trigger": 24, "start": 12, "increment": 3},
    {"trigger": 28, "start": 14, "increment": 3.5},
    {"trigger": 32, "start": 16, "increment": 4},
    {"trigger": 36, "start": 18, "increment": 6}
]


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
        if trig_p > RESET_TRIGGER_LIMIT:
            break
        gap = gaps[i]
        increment = increments[i]
        for j in [x * increment for x in range(1, int(trig_p * (1 / increment)))]:
            if trig_p - abs(j) <= gap:
                single_sls.append([[trig_p, -1 * j]])
                if j == 0.5:
                    # also add a 0.2 version
                    single_sls.append([[trig_p, -0.2]])
    print(f"singles: {single_sls}  singles")

    if RESET_COUNT == 1:
        return

    double_sls = []
    for i in single_sls:
        for j in single_sls:
            if (
                i[0][0] < j[0][0]
                and i[0][1] > j[0][1]
                and [i[0], j[0]] not in double_sls
            ):
                double_sls.append([i[0], j[0]])
    print(f"\ndoubles: {double_sls}  doubles")

    if RESET_COUNT == 2:
        return

    triple_sls = []
    for i in single_sls:
        for j in single_sls:
            for k in single_sls:
                if (
                    i[0][0] < j[0][0] < k[0][0]
                    and i[0][1] > j[0][1] > k[0][1]
                    and [i[0], j[0], k[0]] not in triple_sls
                ):
                    triple_sls.append([i[0], j[0], k[0]])
    print(f"\ntriples: {triple_sls}  triples")
    pass



















    """
    sls = [[[]]]

    if RESET_COUNT == 0:
        return sls

    if RESET_COUNT > 0:
        for p in POINTS:
            if p["trigger"] > RESET_TRIGGER_LIMIT:
                break
            for slp in [x/100 for x in range(int(p["start"] * 100), int(p["trigger"] * 100), int(p["increment"] * 100))]:
                sls.append([[p["trigger"], -1 * slp]])

    if RESET_COUNT > 1:
        for sl in sls[1:]:
            done_with_this_sl = False
            for p in POINTS:
                if done_with_this_sl:
                    break
                if p["trigger"] > RESET_TRIGGER_LIMIT:
                    break
                if p["trigger"] <= sl[0][0]:
                    continue
                for slp in [x / 100 for x in range(int(p["start"] * 100), int(p["trigger"] * 100), int(p["increment"] * 100))]:
                    if -1 * slp < sl[0][1]:
                        sl.append([p["trigger"], -1 * slp])
                        done_with_this_sl = True
                        break
    """
    """
    for i, trig_p in enumerate(TRIGGER_POINTS):
        if trig_p > RESET_TRIGGER_LIMIT:
            break
        gap = GAPS[i]
        increment = INCREMENTS[i]
        for j in [x * increment for x in range(1, int(trig_p * (1 / increment)))]:
            if trig_p - abs(j) >= gap:
                sls.append([[trig_p, -1 * j]])
                
    """
    #print(sls)



if __name__ == "__main__":
    main()
