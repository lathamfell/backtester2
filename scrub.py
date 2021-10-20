from time import sleep


def main():
    p = 0.0025
    l = []
    while True:
        l.append(p)
        p += 0.0025
        p = round(p, 4)
        print(p)
        sleep(.1)
        if p > 0.2:
            break
    print(l)


if __name__ == "__main__":
    main()
