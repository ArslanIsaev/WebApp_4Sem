import sys
import os

if len(sys.argv) < 2:
    print("не найден")
else:
    filename = sys.argv[1]

    if not os.path.exists(filename):
        print("не найден")
    else:
        with open(filename, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i == 5:
                    break
                print(line.strip())
