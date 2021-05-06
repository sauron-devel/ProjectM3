def crcRemainder(message, divisor, initFiller):
    curShift = 0
    divisor = divisor.lstrip('0')
    lenMessage = len(message)
    padding = (len(divisor) - 1) * initFiller
    messagePadded = list(message + padding)

    while '1' in messagePadded[:lenMessage]:
        curShift = messagePadded.index('1')
        for i in range(len(divisor)):
            messagePadded[curShift + i] = str(int(divisor[i] != messagePadded[curShift + i]))
    return ''.join(messagePadded)[lenMessage:]

def crcCheck(message, divisor, initFiller):
    curShift = 0
    divisor = divisor.lstrip('0')
    lenMessage = len(message)
    padding = (len(divisor) - 1) * initFiller
    messagePadded = list(message + padding)

    while '1' in messagePadded[:lenMessage]:
        curShift = messagePadded.index('1')
        for i in range(len(divisor)):
            messagePadded[curShift + i] \
            = str(int(divisor[i] != messagePadded[curShift + i]))
    return ('1' not in ''.join(messagePadded)[lenMessage:])

