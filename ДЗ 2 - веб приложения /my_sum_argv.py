import sys

def my_sum(*args):
    return sum(args)

if __name__ == '__main__':
    nums = map(float, sys.argv[1:])
    print(int(my_sum(*nums)))
