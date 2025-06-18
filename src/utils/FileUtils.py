from os import path


def reformVideoFileName(name) -> str:
    if path.exists(f"..\\.{name}"):
        name = name + "_1"
    extraNumber = 1
    while path.exists(f"..\\.{name}"):
        extraNumber += 1
        name = name[:-1] + str(extraNumber)

    return name
