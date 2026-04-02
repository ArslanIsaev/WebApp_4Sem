import time


def process_list(arr):
    if not isinstance(arr, list) or not 1 <= len(arr) <= 10**3:
        raise ValueError("arr должен быть списком длиной от 1 до 10^3")
    return [i**2 if i % 2 == 0 else i**3 for i in arr]


def process_list_gen(arr):
    if not isinstance(arr, list) or not 1 <= len(arr) <= 10**3:
        raise ValueError("arr должен быть списком длиной от 1 до 10^3")
    for i in arr:
        yield i**2 if i % 2 == 0 else i**3



if __name__ == '__main__':
    test_arr = list(range(1, 1001))  # 1 <= len(arr) <= 10^3
    
    start = time.perf_counter()
    result_list = process_list(test_arr)
    list_time = time.perf_counter() - start
    
    start = time.perf_counter()
    result_gen = list(process_list_gen(test_arr))  
    gen_time = time.perf_counter() - start
    
    print(f"process_list({len(test_arr)}): {list_time:.4f} сек")
    print(f"process_list_gen({len(test_arr)}): {gen_time:.4f} сек")
    print(f"List comprehension: {list_time/gen_time:.1f}x {'быстрее' if list_time < gen_time else 'медленнее'}")
