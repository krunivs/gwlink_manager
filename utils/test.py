if __name__ == "__main__":
    a = ['1', '2', '3', '4', '7', '8']
    b = ['3', '4', '8']

    delete_items = []

    deleted = False
    first = True
    while True:
        if not deleted and not first:
            break
        first = False
        for index in range(0, len(a)):
            deleted = False
            if a[index] not in b:
                delete_items.append(a.pop(index))
                deleted = True
                break
    print(a)
    print(b)
    print(delete_items)




