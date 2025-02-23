from collections import OrderedDict

# Helper functions

def processInput(filename):
    file = open(filename, "r")
    input = file.read()
    file.close()
    lines = input.split("\n")
    return lines

def parseAddress(address):
    offset = address & 255  # 255 is 0000000011111111 in binary
    page = (address >> 8) & 255
    return (page, offset)

def getPageFromBackingStore(page):
    file = open("BACKING_STORE.bin", "rb")
    file.seek(page * 256)
    return list(file.read(256))
    


# Main program

def main():
    # Variables we're trying to track
    referencedByteValue = -1
    frame = -1
    numPageFaults = 0
    numTLBMisses = 0
    numTLBHits = 0
    numAccesses = 0

    FRAMES = 10  # Total frames in physical memory
    PRA = "FIFO"  # Page replacement algorithm

    # TLB
    # [page # -> page frame #]
    # Max size: 16
    tlb = OrderedDict()

    # Page Table
    # [page # -> (page frame #, present bit)]
    # Max size: 256
    pageTable = OrderedDict()

    # Physical Memory
    # Constant size: 256 * FRAMES
    physicalMemory = [None] * FRAMES * 256  # Each entry is 256 bytes

    input = processInput("input.txt")
    for fullAddress in input:
        numAccesses += 1
        current = parseAddress(int(fullAddress, 10))
        page = current[0]
        offset = current[1]

        if page in tlb:
            frame = tlb[page]
            referencedByteValue = physicalMemory[frame * 256 + offset]
            numTLBHits += 1
        else:
            numTLBMisses += 1

            if page in pageTable and pageTable[page][1] == 1:  # Page is in page table and present
                frame = pageTable[page][0]
                referencedByteValue = physicalMemory[frame * 256 + offset]
            else:
                numPageFaults += 1

                pageData = getPageFromBackingStore(page)

                if None in physicalMemory: # Memory is not full!
                    frame = physicalMemory.index(None) // 256
                else: 
                    if PRA == "FIFO":
                        evictedPage = next(iter(pageTable))
                        evictedFrame = pageTable[evictedPage][0]
                        frame = evictedFrame
                        pageTable[evictedPage] = (evictedFrame, 0)
                    elif PRA == "LRU":
                        pass   
                    elif PRA == "OPT":
                        pass

                # Load the page into physical memory
                startAddress = frame * 256
                endAddress = startAddress + 256
                physicalMemory[startAddress:endAddress] = pageData

                # Update TLB
                tlb[page] = frame
                if len(tlb) > 16:
                    tlb.popitem(last=False)

                # Update Page Table
                pageTable[page] = (frame, 1)

                referencedByteValue = physicalMemory[frame * 256 + offset]

        # Print the output for each address
        print(f"{fullAddress}, {referencedByteValue}, {frame}, ")
        print("".join([f"{x:02x}" for x in physicalMemory[frame * 256:frame * 256 + 256]])) # converts from binary to hex (got this from chat)

    # these might be slightly wrong
    print("Number of Translated Addresses =", numAccesses)
    print("Page Faults =", numPageFaults)
    print("Page Fault Rate =", numPageFaults / numAccesses * 100)
    print("TLB Hits =", numTLBHits)
    print("TLB Misses =", numTLBMisses)
    print("TLB Hit Rate =", numTLBHits / (numAccesses) * 100)
    


if __name__ == "__main__":
    main()
