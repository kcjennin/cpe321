import random

NUM_TRIALS = 20

prime_list = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
              31, 37, 41, 43, 47, 53, 59, 61, 67,
              71, 73, 79, 83, 89, 97, 101, 103,
              107, 109, 113, 127, 131, 137, 139,
              149, 151, 157, 163, 167, 173, 179,
              181, 191, 193, 197, 199, 211, 223,
              227, 229, 233, 239, 241, 251, 257,
              263, 269, 271, 277, 281, 283, 293,
              307, 311, 313, 317, 331, 337, 347, 349]


def n_bit_random(n: int) -> int:
    """Get a random number in the top half for the length of the input

    Args:
        n (int): bit length

    Returns:
        int: random number
    """
    return random.randrange(2**(n-1)+1, 2**n-1)


def get_low_level_prime(n: int) -> int:
    """Get a `prime` number that passes the low level primality test

    Args:
        n (int): length

    Returns:
        int: the `prime`
    """
    while True:
        # get a number
        candidate = n_bit_random(n)

        # check all the low level primes
        for prime in prime_list:
            # if it is divisible by the prime find a new number
            if candidate % prime == 0 and prime ** 2 <= candidate:
                break
        else:
            # if the for loop exits normally, return the candidate
            return candidate



def check_miller_rabin(candidate: int, num_trials=NUM_TRIALS) -> bool:
    max_div_2 = 0
    even_comp = candidate - 1

    # check how many times the number is divisible by 2
    while even_comp % 2 == 0:
        even_comp >>= 1
        max_div_2 += 1
    
    # make sure the math above didn't do weird stuff
    assert 2 ** max_div_2 * even_comp == candidate - 1

    def trial_composite(round_tester):
        # make sure that round_tester ** even_comp % candidate == 1
        if pow(round_tester, even_comp, candidate) == 1:
            return False
        for i in range(max_div_2):
            if pow(round_tester, 2 ** i * even_comp, candidate) == candidate - 1:
                return False
        return True
    
    # do the tests
    for i in range(num_trials):
        round_tester = random.randrange(2, candidate)
        if trial_composite(round_tester):
            return False
    return True


def get_large_prime(n=1024) -> int:
    """Get a large prime, you can specify the bit length

    Args:
        n (int): bit length

    Returns:
        int: the prime
    """
    while True:
        candidate = get_low_level_prime(n)
        if not check_miller_rabin(candidate):
            continue
        else:
            return candidate


if __name__ == "__main__":
    import sys
    import time
    
    t0 = time.time()
    print(get_large_prime(int(sys.argv[1])))
    print(f"Time elapsed: {time.time() - t0}")
