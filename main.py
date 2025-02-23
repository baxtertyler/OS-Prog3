from collections import OrderedDict

# helper functions

def processInput(filename):
    file = open(filename, "r")
    input = file.read()
    file.close()
    lines = input.split("\n")
    return lines

def parseAddress(address):
    offset = address & 255 # 255 is 0000000011111111 in binary
    page = (address >> 8) & 255
    return (page, offset)

def getPageFromBackingStore(page):
    with open("BACKING_STORE.bin", "rb") as f:
        f.seek(page * 256)
        pageData = f.read(256)
    return list(pageData)


# main program

def main():
    # what we are trying to get
    referencedByteValue = -1
    frame = -1
    numPageFaults = 0
    numTLBMisses = 0
    numAccesses = 0

    FRAMES = 256 

    # TLB
    # [page # -> page frame #]
    # max size: 16
    tlb = OrderedDict() 

    # Page Talbe
    # [page # -> (page frame #, present bit)]
    # max size: 256
    pageTable = OrderedDict() 

    # Physical Memory
    # constant size: 256 * FRAMES
    physicalMemory = [None] * FRAMES * 256

    input = processInput("input.txt")
    for fullAddress in input:
        numAccesses += 1
        current = parseAddress(int(fullAddress, 10))
        page = current[0]
        offset = current[1]

        if page in tlb:
            frame = tlb[page]
            referencedByteValue = physicalMemory[frame * 256 + offset]
        else:
            numTLBMisses += 1

            if page in pageTable and pageTable[page][1] == 1: # page is in page table and present bit is yes 
                frame = pageTable[page][0]
                referencedByteValue = physicalMemory[frame * 256 + offset]
            else: 
                numPageFaults += 1

                # find the page in the backing store
                _page = getPageFromBackingStore(page)

                # update the page table and physical memory

                # update TLB
                tlb[page] = frame
                if len(tlb) >= 16:
                    tlb.popitem(last=False)

                # update page table
                if len(pageTable) >= 256:
                    pageTable.popitem(last=False)
                pageTable[page] = (frame, 1)

        print(fullAddress, referencedByteValue, frame, )

if __name__ == "__main__":
    main()