def writeFile(obj):
    with open('output.txt', 'a') as f:
        f.write(str(obj))
        f.write('\n')