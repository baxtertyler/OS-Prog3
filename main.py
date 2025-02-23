# reads from file and puts addresses in an array
def processInput(filename):
    file = open(filename, "r")
    input = file.read()
    file.close()
    lines = input.split("\n")
    return lines

def getAddress(address):
    offset = address & 255 # 255 is 11111111 in binary
    page = (address >> 8) & 255
    return (page, offset)


# main program
def main():
    for line in processInput("input.txt"):
        print(getAddress(int(line, 10)))

if __name__ == "__main__":
    main()