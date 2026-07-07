import json
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else 'data/specs/spec_pairs.jsonl'

with open(path, 'r') as f:
    content = f.read()

decoder = json.JSONDecoder()
entries = []
idx = 0
n = len(content)

while idx < n:
    # Skip whitespace and track how much we skip
    match = re.match(r'\s*', content[idx:])
    idx += match.end()
    if idx >= n:
        break
    obj, end = decoder.raw_decode(content, idx)
    entries.append(obj)
    idx = end

seen = {}
for entry in entries:
    seen[entry['task_id']] = entry

with open(path, 'w') as f:
    for entry in seen.values():
        f.write(json.dumps(entry) + '\n')

print(f'Flattened and deduplicated: {len(seen)} unique entries')
for task_id in seen:
    print(f'  {task_id}')
