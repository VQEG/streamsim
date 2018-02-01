__author__ = 'Alexander Dethof'


def str_to_bits(str_val):
    return map(
        lambda bit: int(bit),
        reduce(
            lambda a, b: a + b,
            map(
                lambda byte: list((bin(byte))[2:].zfill(8)),
                bytearray(str_val)
            )
        )
    )


def bits_to_int(bits_list):
    return int(reduce(lambda a,b: str(a) + str(b), bits_list), 2)
