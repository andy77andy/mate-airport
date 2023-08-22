def histogram(results: list) -> str:

    res = ""
    for count in range((len(results)), 0, -1):
        if 0 < results[count - 1] <= 100:
            res += f"{count}| {'#'*results[count - 1]}{results[count - 1]}\n"
        elif results[count - 1] == 0:
            res += f"{count}| \n"
    return f'"""{res}"""'

print(histogram([0, 0, 7, 0, 8, 0]))
