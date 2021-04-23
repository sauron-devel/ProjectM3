while(True):
    with open("ai-out", "r") as FIFO_IN:
        print(FIFO_IN.read())