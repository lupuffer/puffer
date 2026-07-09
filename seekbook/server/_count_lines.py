import os

results = []
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, encoding='utf-8', errors='ignore') as fh:
                count = sum(1 for _ in fh)
            rel = os.path.relpath(path, '.')
            results.append((count, rel))

results.sort(key=lambda x: -x[0])
for count, rel in results:
    flag = ' *** OVER 180' if count > 180 else (' !!! OVER 200' if count > 200 else '')
    print(f'{count:>5} {rel}{flag}')