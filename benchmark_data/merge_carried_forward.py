"""Carry PassLLM's per-profile rows forward into a fresh benchmark run.

PassLLM needs a GPU pass that this environment cannot do, but its per-profile
metrics (candidate count, throughput, PII embedding rate, length distribution,
dataset hits) are properties of PassLLM's own output and are unaffected by any
change to CCUPP or to the aggregation code. They are carried forward rather
than dropped, and the merge is recorded in the exported JSON.

PassLLM never appeared in the paired (_academic_paired) section, so nothing
there is merged.
"""
import json
import sys

old_path, new_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
old = json.loads(open(old_path, encoding='utf-8').read())
new = json.loads(open(new_path, encoding='utf-8').read())

TOOL = 'PassLLM'
SECTIONS = ('results', 'dataset_evals', 'pii_embedding_rate', 'length_distribution')

def fresh_dataset_keys(profile):
    """Dataset keys this run used, taken from a tool it actually ran."""
    for tool, evals in new[profile].get('dataset_evals', {}).items():
        if tool != TOOL:
            return list(evals)
    return []


carried = []
renamed_keys = {}
size_deltas = {}

for profile, old_pb in old.items():
    if profile.startswith('_') or profile not in new:
        continue
    for section in SECTIONS:
        row = old_pb.get(section, {}).get(TOOL)
        if row is None:
            continue
        if section == 'dataset_evals':
            # The old run named the wordlist by filename; align the key so the
            # tool lands in the same column, and record the size difference
            # rather than papering over it.
            fresh = fresh_dataset_keys(profile)
            aligned = {}
            for ds_name, ev in row.items():
                match = next(
                    (f for f in fresh if f == ds_name or f == ds_name.rsplit('.', 1)[0]),
                    ds_name,
                )
                if match != ds_name:
                    renamed_keys[ds_name] = match
                other = new[profile]['dataset_evals'].get(
                    next(t for t in new[profile]['dataset_evals'] if t != TOOL), {},
                ).get(match)
                if other and other['dataset_size'] != ev['dataset_size']:
                    size_deltas[match] = {
                        'this_run': other['dataset_size'],
                        f'{TOOL}_run': ev['dataset_size'],
                    }
                aligned[match] = ev
            row = aligned
        new[profile].setdefault(section, {})[TOOL] = row
    if any(new[profile].get(s, {}).get(TOOL) is not None for s in SECTIONS):
        carried.append(profile)

# Restore the tool ordering the previous report used, so the published tables
# do not reshuffle their columns across an update.
for profile in carried:
    order = [t for t in old[profile]['results'] if t in new[profile]['results']]
    order += [t for t in new[profile]['results'] if t not in order]
    for section in SECTIONS:
        section_data = new[profile].get(section)
        if section_data:
            new[profile][section] = {
                t: section_data[t] for t in order if t in section_data
            }

if TOOL in old.get('_academic_paired', {}):
    sys.exit(f'unexpected: {TOOL} present in _academic_paired; merge logic needs updating')

meta_note_extra = ''
if renamed_keys:
    meta_note_extra += (
        f' Dataset keys from that run were aligned to this run\'s names: '
        f'{renamed_keys}.'
    )
if size_deltas:
    meta_note_extra += (
        f' The wordlist differs slightly in size between the two runs: '
        f'{size_deltas}.'
    )

new['_meta'] = {
    'note': (
        f'{TOOL} rows in the per-profile sections are carried forward from the '
        f'previous run ({old_path}); it requires a GPU pass not available in the '
        f'environment this run was produced in. Its metrics are properties of '
        f'{TOOL} output alone and are unaffected by changes to CCUPP or to the '
        f'aggregation code. Every other number in this file is from a single '
        f'fresh run.' + meta_note_extra
    ),
    'carried_forward': {TOOL: carried},
}

open(out_path, 'w', encoding='utf-8').write(
    json.dumps(new, ensure_ascii=False, indent=2) + '\n')
print(f'carried {TOOL} forward for {len(carried)} profiles: {", ".join(carried)}')
