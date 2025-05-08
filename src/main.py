import access
from calc import HSR


def main():
    access.update()

    result = HSR.debuff_chance([75, 100], [77.76, 95.76], 'imprisonment', 'automaton', 95)

    for key, value in result.items():
        print(f'{key} => {value}')

    return


if __name__ == '__main__':
    main()
