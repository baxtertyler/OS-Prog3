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
    frame = -1
    numPageFaults = 0
    numTLBMisses = 0
    numTLBHits = 0
    numAccesses = 0

    FRAMES = 5  # Total frames in physical memory
    PRA = "LRU"  # Page replacement algorithm
    FRAMES = 5  # Total frames in physical memory
    PRA = "LRU"  # Page replacement algorithm

    # TLB
    # (page # -> page frame #)
    # Max size: 16
    tlb = OrderedDict()

    # Page Table
    # (page # -> [page frame #, present bit])
    # Max size: 256
    pageTable = {}
    queue = []
    queue = []

    # Physical Memory
    # Constant size: 256 * FRAMES
    physicalMemory = [None] * FRAMES * 256  # Each entry is 256 bytes

    input = processInput("tests/lru2.txt")
    input = processInput("tests/lru2.txt")

    for fullAddress in input:
        if fullAddress == "":
            continue
        fullAddress = fullAddress.strip()
        fullAddress = fullAddress.strip()
        numAccesses += 1

        current = parseAddress(int(fullAddress, 10))        

        current = parseAddress(int(fullAddress, 10))        
        page = current[0]
        offset = current[1]

        if page in tlb:
            frame = tlb[page]
            numTLBHits += 1
            if PRA == "LRU":
                queue.pop(queue.index((frame, 1)))
                queue.append((frame, 1))
            if PRA == "LRU":
                queue.pop(queue.index((frame, 1)))
                queue.append((frame, 1))
        else:
            numTLBMisses += 1
            if page in pageTable and pageTable[page][1] == 1:  # Page is in page table and present
                frame = pageTable[page][0]
                if PRA == "LRU":
                    queue.pop(queue.index((frame, 1)))
                    queue.append((frame, 1))
                
                tlb[page] = frame
                if len(tlb) > 16:
                    tlb.popitem(last=False)
                
            else:
                numPageFaults += 1

                pageData = getPageFromBackingStore(page)

                if None in physicalMemory: 
                    frame = physicalMemory.index(None) // 256
                    queue.append((frame, 1))
                else: # Memory is full, must use a PRA!
                    if PRA == "FIFO":
                        item = queue.pop(0)
                        frame = item[0]
                        pageTable[item[0]] = (None, 0)
                        item = queue.pop(0)
                        frame = item[0]
                        pageTable[item[0]] = (None, 0)
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
                if len(tlb) > min(16, FRAMES):
                    item = tlb.popitem(last=False)
                    if len(tlb) > FRAMES-1: 
                        # if an item was removed from TLB, it must be removed from page table 
                        # ONLY IF we removed from TLB due to not enough memory instead of hitting max TLB size
                        # (real world frames will always be greater than TLB size)
                        # i'd like to refactor this
                        pageTable[item[0]] = (None, 0)
                if len(tlb) > min(16, FRAMES):
                    item = tlb.popitem(last=False)
                    if len(tlb) > FRAMES-1: 
                        # if an item was removed from TLB, it must be removed from page table 
                        # ONLY IF we removed from TLB due to not enough memory instead of hitting max TLB size
                        # (real world frames will always be greater than TLB size)
                        # i'd like to refactor this
                        pageTable[item[0]] = (None, 0)

                # Update Page Table
                pageTable[page] = (frame, 1)

        referencedByteValue = physicalMemory[frame * 256 + offset]
        if referencedByteValue > 127: # needed for sign
            referencedByteValue -= 256
        referencedByteValue = physicalMemory[frame * 256 + offset]
        if referencedByteValue > 127: # needed for sign
            referencedByteValue -= 256

        # Print the output for each address
        print(f"{fullAddress}, {referencedByteValue}, {frame}, ") 
        print("".join([f"{x:02x}" for x in physicalMemory[frame * 256:frame * 256 + 256]])) # converts from binary to hex (got this from chat)

    print("Number of Translated Addresses =", numAccesses)
    print("Page Faults =", numPageFaults)
    print(f"Page Fault Rate = {numPageFaults / numAccesses * 100:.2f}%")
    print(f"Page Fault Rate = {numPageFaults / numAccesses * 100:.2f}%")
    print("TLB Hits =", numTLBHits)
    print("TLB Misses =", numTLBMisses)
    print(f"TLB Hit Rate = {numTLBHits / numAccesses * 100:.2f}%")
    print()
    print(f"TLB Hit Rate = {numTLBHits / numAccesses * 100:.2f}%")
    print()
    


if __name__ == "__main__":
    main()