
def r_enumerate(container):
    i = len(container)
    for item in reversed(container):
        i -= 1
        yield i, item

def count_paths(grid):
    
    for i, val in enumerate(grid):
        grid[3][i] = 1
        grid[i][3] = 1

    for i, row in r_enumerate(grid):
        for j, col in r_enumerate(grid):
            if grid[i][j] == 0:
                grid[i][j] = grid[i+1][j] + grid[i][j+1]

    return grid

if __name__ == '__main__':
    grid = [[0 for x in range(4)] for x in range(4)]
    new_grid = count_paths(grid)
    print(new_grid[0][0])










from math import sqrt

def greatest_common_divisor(*args):
    primes = esieve(min(args)/2)
    prime_factors = []
    for arg in args:
        prime_factors(p_factors(arg, primes))
    
def p_factors(num, primes):
    factors = []
    for p in primes:
        while num % p == 0:
            factors.append(p)
    
    return factors
    
def esieve(limit):
    upper_bound = int(sqrt(limit))
    numbers = [True for x in range(limit+1)]
    numbers[0], numbers[1] = False,False
    for i, num in enumerate(numbers[:upperbound+1]):
        if num:
            for j, mult in enumerate(numbers[i*2::i]):
                numbers[j] = False
                
    primes = [i for i, num in enumerate(numbers) if num]
    return primes