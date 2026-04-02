n = int(input())
people = []

if not (1 <= n <= 10):
    print("ошибка")
else:
    people = [] 

    for _ in range(n):
        first, last, age, gender = input().split()
        people.append((last, first, gender))

    people.sort()

    for last, first, gender in people:
        prefix = "Mr." if gender == "M" else "Ms."
        print(f"{prefix} {first} {last}")
