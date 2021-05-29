from watchgod import watch

for changes in watch("./"):
    print(changes)
    if len(changes) == 1:
        change, file = next(iter(changes), (None, None))
        print(change == 2)
        print(file)
