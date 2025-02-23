def processInput(filename):
    file = open(filename, "r")
    input = file.read()
    file.close()
    lines = input.split("\n")
    return lines


def main():
    lines = processInput("input.txt")
    print(lines)

if __name__ == "__main__":
    main()