from pathlib import Path
from PIL import Image, ImageOps
import csv, json, hashlib, re, sys, platform, collections, itertools

ROOT = Path(r'C:\Users\nirma\OneDrive\Desktop\logistic\datasets\Door Open-Close.v1i.yolov8')
OUT = Path(r'C:\Users\nirma\OneDrive\Desktop\logistic\datasets\prepared\phase_05_door_open_close_v1')
SPLITS = ('train','valid','test')
EXTS = {'.jpg','.jpeg','.png','.bmp','.webp','.tif','.tiff'}
NAMES = {0:'Door-Close',1:'Door-Open'}

def write_csv(name, rows, fields):
    with (OUT/name).open('w', newline='', encoding='utf-8-sig') as f:
        w=csv.DictWriter(f, fieldnames=fields, extrasaction='ignore'); w.writeheader(); w.writerows(rows)

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

manifest=[]; exclusions=[]; unresolved=[]; dup_inputs=[]; split_summary={}; all_label_files=[]
for split in SPLITS:
    idir=ROOT/split/'images'; ldir=ROOT/split/'labels'
    images=sorted((p for p in idir.iterdir() if p.is_file() and p.suffix.lower() in EXTS), key=lambda p:p.name.lower()) if idir.exists() else []
    labels=sorted((p for p in ldir.iterdir() if p.is_file() and p.suffix.lower()=='.txt'), key=lambda p:p.name.lower()) if ldir.exists() else []
    all_label_files.extend(labels)
    by_stem={p.stem:p for p in labels}
    img_stems={p.stem for p in images}
    for lp in labels:
        if lp.stem not in img_stems:
            exclusions.append({'split':split,'relative_path':lp.relative_to(ROOT).as_posix(),'reason':'orphan label: no same-stem image'})
    inst=collections.Counter(); perimage=collections.Counter(); empty=0
    for p in images:
        rel=p.relative_to(ROOT).as_posix(); label=by_stem.get(p.stem)
        rec={'relative_path':rel,'split':split,'label_path':label.relative_to(ROOT).as_posix() if label else '', 'extension':p.suffix.lower(),'format':'','width':'','height':'','file_size_bytes':p.stat().st_size,'sha256':'','ahash':'','image_status':'','annotation_status':'','object_count':0,'class_ids':'','class_names':'','duplicate_group':'','preparation_inclusion_status':'','source_group':''}
        problems=[]
        try:
            with Image.open(p) as im:
                fmt=im.format or ''; im.load(); w,h=im.size
                im_rgb=ImageOps.exif_transpose(im).convert('RGB')
                # 8x8 average hash for efficient near-duplicate screening only.
                sm=im_rgb.convert('L').resize((8,8),Image.Resampling.LANCZOS)
                vals=list(sm.get_flattened_data()); avg=sum(vals)/64
                ah=''.join('1' if v>=avg else '0' for v in vals)
                rec.update(format=fmt,width=w,height=h,sha256=sha(p),ahash=ah,image_status='decoded')
                if p.suffix.lower()=='.jpg' and fmt!='JPEG': problems.append('extension/format mismatch')
                if p.suffix.lower() in {'.png'} and fmt!='PNG': problems.append('extension/format mismatch')
        except Exception as e:
            rec['image_status']='decode_error'; problems.append('image decode error: '+type(e).__name__)
        parsed=[]
        if not label:
            rec['annotation_status']='missing_label'; problems.append('missing same-stem label file')
        else:
            try:
                lines=label.read_text(encoding='utf-8-sig').splitlines()
                for line_no,line in enumerate(lines,1):
                    line=line.strip()
                    if not line: continue
                    cells=line.split()
                    if len(cells)!=5: raise ValueError(f'line {line_no}: expected 5 YOLO detection fields, got {len(cells)}')
                    cls=int(cells[0]); nums=[float(x) for x in cells[1:]]
                    if cls not in NAMES: raise ValueError(f'line {line_no}: unknown class id {cls}')
                    cx,cy,bw,bh=nums
                    if not all(0<=x<=1 for x in nums): raise ValueError(f'line {line_no}: normalized values out of range')
                    if bw<=0 or bh<=0: raise ValueError(f'line {line_no}: non-positive bbox width/height')
                    # YOLO normalized center/size boxes may touch image edges; actual bounds must remain in [0,1].
                    if cx-bw/2 < -1e-6 or cy-bh/2 < -1e-6 or cx+bw/2 > 1+1e-6 or cy+bh/2 > 1+1e-6:
                        raise ValueError(f'line {line_no}: bbox extends outside image bounds')
                    parsed.append(cls)
                rec['annotation_status']='valid' if parsed else 'empty_annotation'
                if not parsed: empty+=1
            except Exception as e:
                rec['annotation_status']='invalid'; problems.append('annotation parse/validation error: '+str(e))
        ids=sorted(set(parsed)); rec['object_count']=len(parsed); rec['class_ids']=';'.join(map(str,ids)); rec['class_names']=';'.join(NAMES[i] for i in ids)
        for c in parsed: inst[c]+=1
        for c in ids: perimage[c]+=1
        if not rec['sha256']: rec['sha256']=''
        # Source video group inferred from Roboflow filename stem; grouping is a heuristic.
        m=re.match(r'(.+?)_mp4-\d+_jpg(?:\.rf\.[^.]+)?$', p.stem, re.I)
        group=m.group(1) if m else ''
        rec['source_group']=group
        manifest.append(rec); dup_inputs.append(rec)
        for problem in problems:
            unresolved.append({'relative_path':rel,'split':split,'issue':problem})
        rec['preparation_inclusion_status']='included' if rec['image_status']=='decoded' and rec['annotation_status'] in {'valid','empty_annotation'} else 'excluded_pending_review'
    split_summary[split]={'images':len(images),'label_files':len(labels),'matched_images':sum(1 for p in images if p.stem in by_stem),'orphan_labels':sum(1 for p in labels if p.stem not in img_stems),'missing_labels':sum(1 for p in images if p.stem not in by_stem),'empty_annotations':empty,'instances_by_class':{NAMES[c]:inst[c] for c in NAMES},'images_by_class':{NAMES[c]:perimage[c] for c in NAMES}}

# Exact duplicates across any splits and same split.
sha_groups=collections.defaultdict(list)
for r in manifest:
    if r['sha256']: sha_groups[r['sha256']].append(r)
dups=[]; duplicate_ids={}
for digest, group in sha_groups.items():
    if len(group)>1:
        gid='SHA256-'+digest[:12]; duplicate_ids[digest]=gid
        for r in group:
            r['duplicate_group']=gid
            dups.append({'duplicate_group':gid,'match_type':'exact_sha256','sha256':digest,'relative_path':r['relative_path'],'split':r['split'],'source_group':r['source_group'],'class_names':r['class_names']})
# Approximate aHash search (candidate screening; collisions require visual review).
near=[]; valid_hash=[r for r in manifest if r['ahash']]
for a,b in itertools.combinations(valid_hash,2):
    if a['sha256']==b['sha256']: continue
    dist=sum(x!=y for x,y in zip(a['ahash'],b['ahash']))
    if dist<=4:
        near.append({'match_type':'aHash_candidate_hamming_le_4','hamming_distance':dist,'path_a':a['relative_path'],'split_a':a['split'],'path_b':b['relative_path'],'split_b':b['split'],'cross_split':a['split']!=b['split'],'source_group_a':a['source_group'],'source_group_b':b['source_group']})
# Capture source-group overlap across partitions, separately from pixel duplication.
groups=collections.defaultdict(set)
for r in manifest:
    if r['source_group']: groups[r['source_group']].add(r['split'])
source_overlap=[{'source_group':g,'splits':';'.join(sorted(ss)),'split_count':len(ss),'interpretation':'filename-derived shared source video/session candidate; verify provenance'} for g,ss in groups.items() if len(ss)>1]
for item in source_overlap:
    representatives=[]
    for split_name in item['splits'].split(';'):
        representatives.append(next(r['relative_path'] for r in manifest if r['source_group']==item['source_group'] and r['split']==split_name))
    unresolved.append({'relative_path':';'.join(representatives),'split':item['splits'],'issue':'split integrity: source-group '+item['source_group']+' appears in multiple partitions; these are representative paths; group all frames from this recording before model evaluation'})
unresolved.append({'relative_path':str(ROOT/'data.yaml'),'split':'all','issue':'label semantics: class names are provided but documentation does not define annotation policy or establish cold-chain domain; human verification required'})

write_csv('dataset_manifest.csv',manifest,list(manifest[0].keys()) if manifest else ['relative_path'])
write_csv('exclusion_manifest.csv',[dict(x,issue_type='orphan_annotation') for x in exclusions],['split','relative_path','issue_type','reason'])
write_csv('unresolved_manifest.csv',unresolved,['relative_path','split','issue'])
write_csv('duplicate_report.csv',dups,['duplicate_group','match_type','sha256','relative_path','split','source_group','class_names'])
# Pairwise aHash is intentionally aggregated: static surveillance footage makes
# the loose perceptual threshold generate a very large, low-confidence pair list.
near_summary=collections.Counter((x['hamming_distance'],x['split_a'],x['split_b']) for x in near)
write_csv('near_duplicate_candidates.csv',[{'method':'64-bit average hash; Hamming <=4','hamming_distance':d,'split_a':sa,'split_b':sb,'candidate_pair_count':n,'interpretation':'weak visual-similarity screen only; not confirmed duplicates'} for (d,sa,sb),n in sorted(near_summary.items())],['method','hamming_distance','split_a','split_b','candidate_pair_count','interpretation'])
write_csv('source_group_overlap_report.csv',source_overlap,['source_group','splits','split_count','interpretation'])

status='PREPARED_WITH_LIMITATIONS'
meta={'dataset_name':'Door Open-Close.v1i.yolov8','source_root':str(ROOT),'source_documentation':{'README.dataset.txt':'Roboflow v1 export; 706 images reported; YOLOv8; no augmentation; CC BY 4.0','data.yaml':'nc=2; names Door-Close and Door-Open; configured paths train: ../train/images, val: ../valid/images, test: ../test/images'},'class_mapping':{str(k):v for k,v in NAMES.items()},'split_summary':split_summary,'total_images':len(manifest),'image_decode_failures':sum(r['image_status']!='decoded' for r in manifest),'annotation_invalid':sum(r['annotation_status']=='invalid' for r in manifest),'missing_labels':sum(r['annotation_status']=='missing_label' for r in manifest),'empty_annotations':sum(r['annotation_status']=='empty_annotation' for r in manifest),'exact_duplicate_groups':len({r['duplicate_group'] for r in dups}),'exact_duplicate_files':len(dups),'near_duplicate_pairs_candidate':len(near),'cross_split_near_duplicate_candidates':sum(x['cross_split'] for x in near),'near_duplicate_candidate_histogram':{f'{d}:{sa}-{sb}':n for (d,sa,sb),n in sorted(near_summary.items())},'filename_source_groups_spanning_splits':len(source_overlap),'readiness_status':status,'pixel_hash':'SHA-256 exact file bytes','near_duplicate_method':'64-bit average hash after EXIF transpose + RGB conversion; Hamming distance <=4; candidate-only, not confirmation; summarized by distance and split pair because static footage produces many weak pair candidates','runtime':{'python':sys.version,'platform':platform.platform(),'pillow':Image.__version__},'created_by':'phase_05_audit.py','note':'No source images or annotations copied or modified.'}
(OUT/'class_mapping.json').write_text(json.dumps({'class_id_to_name':{str(k):v for k,v in NAMES.items()},'source':'data.yaml'},indent=2),encoding='utf-8')
(OUT/'annotation_validation_report.json').write_text(json.dumps({'rules':['YOLO detection row must have class_id cx cy width height','class id must be declared in data.yaml','normalized coordinates in [0,1]','width and height > 0','box extents within image bounds'],'summary':{s:{'images':v['images'],'instances_by_class':v['instances_by_class'],'images_by_class':v['images_by_class']} for s,v in split_summary.items()},'invalid_rows_or_files':[x for x in unresolved if 'annotation' in x['issue']],'missing_labels':[x for x in unresolved if 'missing same-stem label' in x['issue']],'empty_annotations':[r['relative_path'] for r in manifest if r['annotation_status']=='empty_annotation'],'overall_invalid_annotation_files':meta['annotation_invalid']},indent=2),encoding='utf-8')
(OUT/'dataset_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
(OUT/'proposed_data.yaml').write_text('path: ../../Door Open-Close.v1i.yolov8\ntrain: train/images\nval: valid/images\ntest: test/images\nnc: 2\nnames:\n  0: Door-Close\n  1: Door-Open\n',encoding='utf-8')

summary=['# Phase 05 dataset preparation summary','',f'- Source: `{ROOT}`',f'- Images inventoried: {len(manifest)}',f'- Declared classes: 0 Door-Close; 1 Door-Open','- Source splits preserved: train / valid / test.','- Image decoding uses Pillow full decode; no images copied.','- Annotations checked for format, class IDs, normalized coordinates, positive box sizes, and image bounds.','', '## Split counts']
for s,v in split_summary.items(): summary.append(f"- {s}: {v['images']} images, {v['label_files']} labels; instances {v['instances_by_class']}; labeled images {v['images_by_class']}; empty labels {v['empty_annotations']}; missing {v['missing_labels']}; orphan {v['orphan_labels']}.")
summary += ['',f"- Exact duplicate groups/files: {meta['exact_duplicate_groups']} / {meta['exact_duplicate_files']}.",f"- Near duplicate candidates (aHash distance <=4): {len(near)}; cross-split candidates: {meta['cross_split_near_duplicate_candidates']}.",f"- Filename-derived source groups spanning splits: {len(source_overlap)} (candidate leakage; verify video/session provenance).",f"- Image decode errors: {meta['image_decode_failures']}; invalid annotations: {meta['annotation_invalid']}; unresolved records: {len(unresolved)}.",'','## Configuration finding','The source `data.yaml` paths resolve relative to the YAML directory to a sibling `train/valid/test` tree, while this export actually stores split directories under the dataset root. `proposed_data.yaml` supplies a separate corrected relative configuration for this prepared output directory. Original configuration remains unchanged.','', '## Limitations','Near-duplicate screening is a lightweight aHash candidate search and does not establish visual identity. Filename-derived source groups are heuristic indicators of correlated frames and do not establish capture provenance. No annotations were semantically adjudicated. See CSV/JSON reports for per-file records.']
(OUT/'dataset_summary.md').write_text('\n'.join(summary)+'\n',encoding='utf-8')
(OUT/'README.md').write_text('# Phase 05 prepared audit outputs\n\nGenerated from the existing Door Open-Close YOLO export. This directory contains metadata and manifests only; source images and labels remain in place. `phase_05_audit.py` reproduces the inventory and validation. Read `dataset_summary.md` first. `dataset_manifest.csv` has one row per source image; `exclusion_manifest.csv` lists orphan label files; `unresolved_manifest.csv` lists defects requiring review. Near-duplicate pairs are candidates only.\n',encoding='utf-8')
(OUT/'phase_05_summary.md').write_text('# Phase 05 status\n\n**'+status+'**\n\n'+ '\n'.join(summary[2:])+'\n\nNo model training, inference, external API calls, or source edits were performed. A human review of class semantics and capture-level split leakage is still required before training.\n',encoding='utf-8')
print(json.dumps({'out':str(OUT),'total_images':len(manifest),'split_summary':split_summary,'decode_failures':meta['image_decode_failures'],'invalid_annotations':meta['annotation_invalid'],'missing_labels':meta['missing_labels'],'orphan_labels':len(exclusions),'empty_annotations':meta['empty_annotations'],'exact_duplicate_groups':meta['exact_duplicate_groups'],'exact_duplicate_files':meta['exact_duplicate_files'],'near_duplicate_pairs':len(near),'cross_split_near_candidates':meta['cross_split_near_duplicate_candidates'],'source_groups_cross_split':len(source_overlap),'unresolved_count':len(unresolved),'status':status},indent=2))
