import access
from calc import HSR


def main():
    access.update()

    result = HSR.debuff_chance([65, 100], [120, 140, 157], 'arcana', 'phantylia', 95)

    for key, value in result.items():
        print(f'{key} => {value}')

    return


if __name__ == '__main__':
    main()
