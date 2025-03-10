#!/usr/bin/env python3

# Tyler Baxter and Jack Herberger

from collections import OrderedDict
import sys

# Helper functions

def processInput(filename):
    file = open(filename, "r")
    input = file.read()
    file.close()
    lines = input.split("\n")
    while lines[-1] == "":
        lines.pop(-1)
    print(lines)
    return lines

def parseAddress(address):
    offset = address & 255
    page = (address >> 8) & 255
    return (page, offset)

def getPageFromBackingStore(page):
    file = open("BACKING_STORE.bin", "rb")
    file.seek(page * 256)
    return list(file.read(256))

    
# Main program

def main():

    if (len(sys.argv) != 4):
        print("Usage: ./memSim <reference-sequence-file.txt> <FRAMES> <PRA>")
        sys.exit(1)

    frame = -1
    numPageFaults = 0
    numTLBMisses = 0
    numTLBHits = 0
    numAccesses = 0

    FRAMES = int(sys.argv[2])  # Total frames in physical memory
    PRA = sys.argv[3]  # Page replacement algorithm

    # TLB
    # (page # -> page frame #)
    # Max size: 16
    tlb = OrderedDict()

    # Page Table
    # (page # -> [page frame #, present bit])
    # constant size: 256
    pageTable = {}
    for i in range(256):
        pageTable[i] = (None, 0)
    queue = []

    # Physical Memory
    # Constant size: 256 * FRAMES
    physicalMemory = [None] * FRAMES * 256  # Each entry is 256 bytes

    input = processInput(sys.argv[1])

    # Create oir remaining list for the OPT algo
    remaining = input.copy()
    remaining = [parseAddress(int(fullAddress.strip(), 10))[0] for fullAddress in remaining]

    for fullAddress in input:
        fullAddress = fullAddress.strip()
        numAccesses += 1

        # Remove from our remaining list
        remaining.pop(0)
      
        current = parseAddress(int(fullAddress, 10))        
        page = current[0]
        offset = current[1]
        

        if page in tlb:
            frame = tlb[page]
            numTLBHits += 1
            if PRA == "LRU":
                queue.pop(queue.index(frame))
                queue.append(frame)
        else:
            numTLBMisses += 1
            if pageTable[page][1] == 1:  # Page is in page table and present
                frame = pageTable[page][0]
                if PRA == "LRU":
                    queue.pop(queue.index(frame))
                    queue.append(frame)

                tlb[page] = frame
                if len(tlb) > 16:
                    tlb.popitem(last=False) 

            else:
                numPageFaults += 1

                pageData = getPageFromBackingStore(page)

                if None in physicalMemory: 
                    frame = physicalMemory.index(None) // 256
                    queue.append(frame)
                else: # Memory is full, must use a PRA!
                    if PRA == "FIFO":
                        frame = queue.pop(0)
                        pageTable[frame] = (None, 0)
                    elif PRA == "LRU":
                        frame = queue.pop(0)
                        pageTable[frame] = (None, 0)   
                    elif PRA == "OPT":
                        # remove the frame that will not be used for the longest time
                        # we know the future from our remaining list

                        # find the frame that either will not be used or will not be used for the longest time
                        max_future = -1
                        frame = -1

                        for page, frame_content in pageTable.items():
                            if frame_content[1] == 1:
                                if page in remaining:  # page is in remaining list
                                    future_index = remaining.index(page)
                                    if future_index > max_future:
                                        max_future = future_index
                                        frame = frame_content[0]
                                else: # page is not going to be used again, we can replace it
                                    frame = frame_content[0]
                                    break


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

                # Update Page Table
                pageTable[page] = (frame, 1)

                # Add to queue
                queue.append(frame)

        referencedByteValue = physicalMemory[frame * 256 + offset]
        if referencedByteValue > 127: # needed for sign
            referencedByteValue -= 256

        # Print the output for each address
        print(f"{fullAddress}, {referencedByteValue}, {frame}, ") 
        print("".join([f"{x:02x}" for x in physicalMemory[frame * 256:frame * 256 + 256]])) # converts from binary to hex (got this from chat)

        
       

    print("Number of Translated Addresses =", numAccesses)
    print("Page Faults =", numPageFaults)
    print(f"Page Fault Rate = {numPageFaults / numAccesses * 100:.2f}%")
    print("TLB Hits =", numTLBHits)
    print("TLB Misses =", numTLBMisses)
    print(f"TLB Hit Rate = {numTLBHits / numAccesses * 100:.2f}%")
    print()
    


if __name__ == "__main__":
    main()
