import csv, json
from collections import defaultdict, Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent
for folder in ('fruits_360','healthy_rotten_diseases','vegnet'):
    d=ROOT/folder
    rows=list(csv.DictReader((d/'dataset_manifest.csv').open(encoding='utf-8-sig')))
    exc=list(csv.DictReader((d/'exclusion_manifest.csv').open(encoding='utf-8-sig')))
    unresolved=list(csv.DictReader((d/'unresolved_manifest.csv').open(encoding='utf-8-sig')))
    mapping=json.loads((d/'class_mapping.json').read_text(encoding='utf-8'))
    groups=defaultdict(list)
    for r in rows+exc:
        if r.get('sha256'): groups[r['sha256']].append(r)
    cross_labels=[g for g in groups.values() if len({r.get('label','') for r in g})>1]
    split_hash=defaultdict(set); leakage=[]
    for r in rows:
        if r['sha256'] in split_hash[r['split']]: pass
        for split, hashes in split_hash.items():
            if split!=r['split'] and r['sha256'] in hashes: leakage.append(r['sha256'])
        split_hash[r['split']].add(r['sha256'])
    bad_paths=sum(not Path(r['source_path']).exists() for r in rows)
    ext=Counter((r['extension'],r['actual_format']) for r in rows if r['extension'].lstrip('.').upper()!=r['actual_format'].upper() and not (r['extension'] in ('.jpg','.jpeg') and r['actual_format']=='JPEG'))
    unresolved_hash_groups=defaultdict(list)
    for r in unresolved:
        if r.get('sha256'): unresolved_hash_groups[r['sha256']].append(r)
    print(json.dumps({'dataset':folder,'manifest_rows':len(rows),'exclusions':len(exc),'unresolved_rows':len(unresolved),'unresolved_hash_groups':len(unresolved_hash_groups),'mapping_classes':len(mapping.get('classes',[])),'cross_label_duplicate_groups_in_candidate_manifests':len(cross_labels),'cross_split_hash_overlap':len(set(leakage)),'missing_source_paths':bad_paths,'format_mismatches':sum(ext.values()),'mismatch_pairs':{str(k):v for k,v in ext.items()}},ensure_ascii=False))
    if cross_labels:
        print(json.dumps({'cross_label_groups':[{'hash':g[0]['sha256'],'members':[{'path':r['relative_path'],'label':r['label'],'split':r.get('split','')} for r in g]} for g in cross_labels]},ensure_ascii=False))

d=ROOT/'fruits_vegetables_detection'
errors=list(csv.DictReader((d/'annotation_validation.csv').open(encoding='utf-8-sig')))
manifest=list(csv.DictReader((d/'dataset_manifest.csv').open(encoding='utf-8-sig')))
print(json.dumps({'detection_manifest_images':len(manifest),'detection_unresolved_images':sum(r.get('record_status')=='unresolved' for r in manifest),'annotation_issue_lines':len(errors),'annotation_issue_images':len({e['image'] for e in errors}),'detection_annotation_issues':errors},ensure_ascii=False))
