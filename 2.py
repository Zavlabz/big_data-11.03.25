from collections.abc import Sequence
def check_fi(data: Sequence[int]) -> bool:

    if len(data) < 3:
        return True
    for i in range(2, len(data)):
        if data[i] != data[i - 1] + data[i - 2]:
            return False
    return True

print(check_fi("228"))