n = int(input())

for _ in range(n):
    s = input().strip()
    digits = "".join(c for c in s if c.isdigit())

    if len(digits) == 11:
        digits = "7" + digits[1:]
    elif len(digits) == 10:
        digits = "7" + digits

    code = digits[1:4]
    a = digits[4:7]
    b = digits[7:9]
    c = digits[9:11]

    print(f"+7 ({code}) {a}-{b}-{c}")
