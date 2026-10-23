from pathlib import Path
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import csv, hashlib, json, os, random, re, sys, platform, time

DATASETS = Path(r'C:\Users\nirma\OneDrive\Desktop\logistic\datasets')
OUT = Path(__file__).resolve().parent
EXTS = {'.jpg','.jpeg','.png','.bmp','.webp','.tif','.tiff','.gif','.jfif','.avif'}
SEED = 2048

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()
def rel(path, root):
    return path.relative_to(root).as_posix()
def write_csv(path, rows, fields):
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        w=csv.DictWriter(f, fieldnames=fields, extrasaction='ignore'); w.writeheader(); w.writerows(rows)
def img_record(p, root, label, split, records, exclusions):
    r={'source_path':str(p.resolve()),'relative_path':rel(p,root),'label':label,'source_split':split or '', 'split':split or '', 'width':'','height':'','actual_format':'','extension':p.suffix.lower(),'size_bytes':p.stat().st_size,'sha256':'','record_status':'excluded','reason':''}
    try:
        data=p.read_bytes()
        r['sha256']=hashlib.sha256(data).hexdigest()
        with Image.open(BytesIO(data)) as im:
            r['actual_format']=im.format or ''
            r['width'],r['height']=im.size
            im.load()
        r['record_status']='candidate'
        records.append(r)
    except Exception as e:
        r['reason']='decode_error: '+type(e).__name__+': '+str(e)[:180]
        exclusions.append(r.copy())
def group_duplicates(records, official, exclusions, unresolved=None):
    unresolved=unresolved if unresolved is not None else []
    groups={}
    for r in records: groups.setdefault(r['sha256'],[]).append(r)
    kept=[]; duplicates=0; leakage_groups=0
    for digest, g in groups.items():
        if len(g)==1: kept.extend(g); continue
        duplicates += len(g)-1
        if len({x['label'] for x in g})>1:
            for x in g:
                y=x.copy(); y.update(record_status='unresolved',reason='exact_duplicate_group_has_conflicting_folder_labels:'+','.join(sorted({z['label'] for z in g}))); unresolved.append(y)
            continue
        splits={x['source_split'] for x in g if x['source_split']}
        if official and len(splits)>1:
            leakage_groups+=1
            for x in g:
                y=x.copy(); y.update(record_status='excluded',reason='exact_duplicate_group_crosses_official_splits:'+','.join(sorted(splits))); exclusions.append(y)
            continue
        canon=sorted(g,key=lambda x:x['relative_path'].casefold())[0]
        kept.append(canon)
        for x in g:
            if x is not canon:
                y=x.copy(); y.update(record_status='excluded',reason='exact_duplicate_of:'+canon['relative_path']); exclusions.append(y)
    return kept,duplicates,leakage_groups

def create_splits(records, official, stratified=True):
    if official: return records
    by={}
    for r in records: by.setdefault(r['label'],[]).append(r)
    rng=random.Random(SEED)
    for label, items in sorted(by.items()):
        items.sort(key=lambda x:x['relative_path'].casefold()); rng.shuffle(items)
        n=len(items)
        ntr=int(n*.8); nva=int(n*.1)
        if n>=3:
            nva=max(1,nva); ntr=min(n-2,ntr)
        elif n==2: ntr=1; nva=0
        else: ntr=1; nva=0
        for i,r in enumerate(items): r['split']='train' if i<ntr else ('validation' if i<ntr+nva else 'test')
    return records

def make_classification(name, source, outname, taxonomy, official_splits=None, description=''):
    # This output root was created by this run after an absence check; allow safe
    # regeneration of its own derived artifacts after an audit correction.
    target=OUT/outname; target.mkdir(parents=True,exist_ok=True)
    records=[]; exclusions=[]; unresolved=[]; source=Path(source)
    candidates=[]
    if official_splits:
        for split_name, split_dir in official_splits.items():
            base=source/split_dir
            if not base.exists(): continue
            for cls in sorted([p for p in base.iterdir() if p.is_dir()],key=lambda p:p.name.casefold()):
                for p in sorted(cls.rglob('*'),key=lambda p:p.as_posix().casefold()):
                    if p.is_file() and p.suffix.lower() in EXTS: candidates.append((p,cls.name,split_name))
    else:
        for cls in sorted([p for p in source.iterdir() if p.is_dir()],key=lambda p:p.name.casefold()):
            for p in sorted(cls.rglob('*'),key=lambda p:p.as_posix().casefold()):
                if p.is_file() and p.suffix.lower() in EXTS: candidates.append((p,cls.name,''))
    def scan(item):
        p,label,split=item
        good=[]; bad=[]; img_record(p,source,label,split,good,bad)
        return (good,bad)
    with ThreadPoolExecutor(max_workers=8) as pool:
        for i,(good,bad) in enumerate(pool.map(scan,candidates),1):
            records.extend(good); exclusions.extend(bad)
            if i % 25000 == 0: print(f'{name}: inspected {i}/{len(candidates)} images',flush=True)
    before=len(records)
    records,dup_count,leakage=group_duplicates(records,bool(official_splits),exclusions,unresolved)
    create_splits(records,bool(official_splits))
    source_label_aliases={}
    if name=='Fruits-360':
        # Folder spelling differs only by capitalization for one class across
        # official partitions. Keep training spelling as canonical and preserve
        # the exact source folder string in source_label.
        for r in sorted(records,key=lambda x:(0 if x['source_split']=='train' else 1,x['label'].casefold(),x['label'])):
            source_label_aliases.setdefault(r['label'].casefold(),set()).add(r['label'])
        canonical={k:sorted(v,key=lambda x:(x.casefold(),x))[0] for k,v in source_label_aliases.items()}
        train_names={r['label'].casefold():r['label'] for r in records if r['source_split']=='train'}
        canonical.update(train_names)
        for r in records:
            r['source_label']=r['label']; r['label']=canonical[r['label'].casefold()]
    labels=sorted({r['label'] for r in records},key=lambda x:(x.casefold(),x))
    mapping=[{'class_id':i,'class_name':lab,'original_label':lab,'source_label_variants':sorted(source_label_aliases.get(lab.casefold(),{lab})),'semantics':taxonomy.get(lab,'folder-derived category; no further semantic assertion')} for i,lab in enumerate(labels)]
    for r in records: r['class_id']=next(m['class_id'] for m in mapping if m['class_name']==r['label']); r['record_status']='accepted'; r['reason']=''
    fields=['source_path','relative_path','label','source_label','class_id','source_split','split','width','height','actual_format','extension','size_bytes','sha256','record_status','reason']
    write_csv(target/'dataset_manifest.csv',records,fields)
    write_csv(target/'exclusion_manifest.csv',exclusions,fields)
    write_csv(target/'unresolved_manifest.csv',unresolved,fields)
    (target/'class_mapping.json').write_text(json.dumps({'label_semantics':description,'classes':mapping},indent=2,ensure_ascii=False),encoding='utf-8')
    dist={}
    for r in records: dist.setdefault(r['label'],{}).setdefault(r['split'],0); dist[r['label']][r['split']]+=1
    fmt={}
    extmis=0
    for r in records:
        fmt[r['actual_format']]=fmt.get(r['actual_format'],0)+1
        if r['extension'].lstrip('.').upper()!=r['actual_format'].upper() and not (r['extension']=='.jpg' and r['actual_format']=='JPEG') and not (r['extension']=='.jpeg' and r['actual_format']=='JPEG'): extmis+=1
    status='PREPARED_WITH_LIMITATIONS' if leakage or exclusions or unresolved else 'PREPARED'
    if not records: status='BLOCKED'
    duplicate_copies_excluded=sum(1 for x in exclusions if str(x.get('reason','')).startswith('exact_duplicate_of:'))
    meta={'dataset':name,'source_root':str(source.resolve()),'created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'status':status,'seed':SEED if not official_splits else None,'split_method':'official source directories preserved' if official_splits else 'deterministic per-class 80/10/10 assignment after exact-duplicate grouping','source_split_names':official_splits or {},'candidate_decodable_images_before_duplicate_handling':before,'accepted_images':len(records),'excluded_records':len(exclusions),'unresolved_records':len(unresolved),'exact_duplicate_files_removed':duplicate_copies_excluded,'exact_duplicate_file_excess_count':dup_count,'conflicting_duplicate_groups_unresolved':len({x['sha256'] for x in unresolved if x.get('sha256')}),'cross_official_split_duplicate_groups_excluded':leakage,'class_count':len(labels),'class_distribution_by_split':dist,'actual_format_counts':fmt,'extension_format_mismatches':extmis,'decode_failure_count':sum(1 for x in exclusions if str(x.get('reason','')).startswith('decode_error')),'environment':{'python':platform.python_version(),'pillow':Image.__version__},'preprocessing':'No pixels written or transformed; manifests reference original files. Pillow decode verification only.'}
    (target/'preparation_metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf-8')
    md=[f'# {name} preparation summary','',f'- Status: **{status}**',f'- Source: `{source}`',f'- Decodable candidates before duplicate handling: {before}',f'- Accepted unique images: {len(records)}',f'- Excluded records: {len(exclusions)} (exact duplicates removed: {dup_count}; cross-split duplicate groups: {leakage}; decode failures: {meta["decode_failure_count"]})',f'- Unresolved records: {len(unresolved)} (duplicate byte groups with conflicting labels require review).',f'- Classes: {len(labels)}',f'- Extension/actual-format mismatches: {extmis}',f'- Split policy: {meta["split_method"]}.','', '## Class counts by split','', '| Class | train | validation | test | total |','|---|---:|---:|---:|---:|']
    for lab in labels:
        c=dist.get(lab,{}); md.append(f'| {lab} | {c.get("train",0)} | {c.get("validation",0)} | {c.get("test",0)} | {sum(c.values())} |')
    md += ['', '## Limitations','',description,'','Counts reflect files decoded during this pass. Folder-derived labels are preserved, not adjudicated. Image decoding does not establish semantic label correctness or production readiness.']
    (target/'dataset_summary.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    return {'dataset':name,'output':str(target),'status':status,'images':len(records),'candidates':before,'classes':len(labels),'excluded':len(exclusions),'unresolved':len(unresolved),'duplicates_removed':duplicate_copies_excluded,'duplicate_excess_count':dup_count,'leakage_groups':leakage,'dist':dist,'format_mismatches':extmis}

def detection():
    name='Fruits and Vegetables Detection Dataset'; source=DATASETS/'Fruits-And-Vegetables-Detection-Dataset-main'/'Fruits-And-Vegetables-Detection-Dataset-main'/'LVIS_Fruits_And_Vegetables'; target=OUT/'fruits_vegetables_detection'; target.mkdir(parents=True,exist_ok=True)
    yaml=source/'data.yaml'; text=yaml.read_text(encoding='utf-8',errors='replace')
    names={}
    in_names=False
    for line in text.splitlines():
        if re.match(r'^names\s*:',line): in_names=True; continue
        if in_names:
            m=re.match(r'^\s*(\d+)\s*:\s*(.*?)\s*$',line)
            if m: names[int(m.group(1))]=m.group(2).strip().strip('\"\'')
    imgs=[]; ann_errors=[]; exclusions=[]
    for split in ('train','val','test'):
        idir=source/'images'/split; ldir=source/'labels'/split
        if not idir.exists(): continue
        for p in sorted(idir.rglob('*'),key=lambda x:x.as_posix().casefold()):
            if not p.is_file(): continue
            if p.suffix.lower() not in EXTS:
                if p.suffix.lower()=='.zip':
                    payload=p.read_text(encoding='utf-8',errors='replace') if p.stat().st_size<4096 else ''
                    if payload.startswith('version https://git-lfs.github.com/spec/v1'):
                        m=re.search(r'oid sha256:([0-9a-f]+)\s+size (\d+)',payload)
                        exclusions.append({'source_path':str(p.resolve()),'relative_path':rel(p,source),'label':'','class_id':'','source_split':split,'split':split,'width':'','height':'','actual_format':'Git LFS pointer','extension':p.suffix.lower(),'size_bytes':p.stat().st_size,'sha256':sha(p),'record_status':'excluded','reason':'missing_git_lfs_payload; expected_bytes='+ (m.group(2) if m else 'unknown')+', oid_sha256='+(m.group(1) if m else 'unknown')})
                continue
            rec={'source_path':str(p.resolve()),'relative_path':rel(p,source),'label':'','class_id':'','source_split':split,'split':split,'width':'','height':'','actual_format':'','extension':p.suffix.lower(),'size_bytes':p.stat().st_size,'sha256':'','annotation_path':'','annotation_count':0,'annotation_status':'','record_status':'accepted','reason':''}
            try:
                rec['sha256']=sha(p)
                with Image.open(p) as im: rec['actual_format']=im.format or ''; rec['width'],rec['height']=im.size; im.load()
            except Exception as e:
                rec['record_status']='excluded'; rec['reason']='decode_error:'+type(e).__name__+':'+str(e)[:160]; exclusions.append(rec.copy()); continue
            a=ldir/(p.stem+'.txt'); rec['annotation_path']=str(a.resolve()) if a.exists() else ''; rec['annotation_status']='missing' if not a.exists() else 'valid'
            if not a.exists(): ann_errors.append({'image':rec['relative_path'],'split':split,'issue':'missing_annotation'}); rec['annotation_status']='missing'; rec['record_status']='unresolved'; rec['reason']='missing_annotation';
            else:
                lines=a.read_text(encoding='utf-8',errors='replace').splitlines(); count=0
                for lineno,line in enumerate(lines,1):
                    if not line.strip(): continue
                    parts=line.split()
                    try:
                        if len(parts)!=5: raise ValueError('expected 5 YOLO fields')
                        cid=int(parts[0]); x,y,w,h=map(float,parts[1:])
                        if cid not in names: raise ValueError('class_id_not_in_names:'+str(cid))
                        if not all(map(lambda z: z==z and abs(z)!=float('inf'),[x,y,w,h])): raise ValueError('non_finite_box_value')
                        if not (0<=x<=1 and 0<=y<=1 and 0<w<=1 and 0<h<=1): raise ValueError('normalized_box_out_of_bounds_or_nonpositive')
                        if x-w/2< -1e-6 or y-h/2< -1e-6 or x+w/2>1+1e-6 or y+h/2>1+1e-6: raise ValueError('box_corners_out_of_bounds')
                        count+=1
                    except Exception as e: ann_errors.append({'image':rec['relative_path'],'split':split,'annotation':rel(a,source),'line':lineno,'issue':str(e)}); rec['annotation_status']='invalid'; rec['record_status']='unresolved'; rec['reason']='invalid_annotation'
                rec['annotation_count']=count
                if not lines or not any(line.strip() for line in lines): rec['annotation_status']='empty_valid_negative'; rec['record_status']='accepted'; rec['reason']=''
                if rec['annotation_status']=='invalid': rec['record_status']='unresolved'; rec['reason']='invalid_annotation'
            imgs.append(rec)
    # Label archive placeholders are separate required payloads and are not
    # discovered by walking the image directories above.
    for split in ('train','val'):
        ldir=source/'labels'/split
        for p in sorted(ldir.rglob('*.zip'),key=lambda x:x.as_posix().casefold()) if ldir.exists() else []:
            payload=p.read_text(encoding='utf-8',errors='replace') if p.stat().st_size<4096 else ''
            if payload.startswith('version https://git-lfs.github.com/spec/v1'):
                m=re.search(r'oid sha256:([0-9a-f]+)\s+size (\d+)',payload)
                exclusions.append({'source_path':str(p.resolve()),'relative_path':rel(p,source),'label':'','class_id':'','source_split':split,'split':split,'width':'','height':'','actual_format':'Git LFS pointer','extension':p.suffix.lower(),'size_bytes':p.stat().st_size,'sha256':sha(p),'annotation_path':'','annotation_count':0,'annotation_status':'missing_payload','record_status':'excluded','reason':'missing_git_lfs_payload; expected_bytes='+(m.group(2) if m else 'unknown')+', oid_sha256='+(m.group(1) if m else 'unknown')})
    # exact duplicate report only; keep official source partitions unchanged
    hashes={}
    for r in imgs: hashes.setdefault(r['sha256'],[]).append(r)
    dup_groups=[g for g in hashes.values() if len(g)>1]
    duplicate_rows=[]
    for g in dup_groups:
        for r in g: duplicate_rows.append({'sha256':r['sha256'],'relative_path':r['relative_path'],'source_split':r['source_split'],'duplicate_group_size':len(g),'cross_split':len({x['source_split'] for x in g})>1})
    fields=['source_path','relative_path','label','class_id','source_split','split','width','height','actual_format','extension','size_bytes','sha256','annotation_path','annotation_count','annotation_status','record_status','reason']
    write_csv(target/'dataset_manifest.csv',imgs,fields); write_csv(target/'exclusion_manifest.csv',exclusions,fields); write_csv(target/'annotation_validation.csv',ann_errors,['image','split','annotation','line','issue']); write_csv(target/'duplicate_report.csv',duplicate_rows,['sha256','relative_path','source_split','duplicate_group_size','cross_split'])
    write_csv(target/'unresolved_manifest.csv',[r for r in imgs if r['record_status']=='unresolved'],fields)
    # config and mapping evidence, preserving original class IDs
    mapping=[{'class_id':i,'class_name':names[i],'original_label':names[i],'semantics':'source YOLO object class'} for i in sorted(names)]
    (target/'class_mapping.json').write_text(json.dumps({'source_config':str(yaml.resolve()),'classes':mapping},indent=2,ensure_ascii=False),encoding='utf-8')
    # Actual files and LFS placeholder state
    dirs={}
    for split in ('train','val','test'):
        ip=source/'images'/split; lp=source/'labels'/split
        dirs[split]={'image_files':sum(1 for p in ip.rglob('*') if p.is_file() and p.suffix.lower() in EXTS) if ip.exists() else 0,'label_txt_files':sum(1 for p in lp.rglob('*.txt') if p.is_file()) if lp.exists() else 0,'image_zip_entries':sum(1 for p in ip.rglob('*.zip') if p.is_file()) if ip.exists() else 0,'label_zip_entries':sum(1 for p in lp.rglob('*.zip') if p.is_file()) if lp.exists() else 0}
    cfg={'configured_path':'LVIS_Fruits_And_Vegetables','train':'images/train','val':'images/test','test':'images/test','configured_path_exists_from_repository_root':(source.parent/'LVIS_Fruits_And_Vegetables').exists(),'train_path_exists':(source/'images'/'train').exists(),'val_path_exists':(source/'images'/'val').exists(),'test_path_exists':(source/'images'/'test').exists(),'val_and_test_same_configured_path':True,'note':'YAML train/val comments conflict with actual available payloads; train/val directories contain LFS pointer files instead of ZIP payloads.'}
    invalid=sum(1 for x in ann_errors if x['issue']!='missing_annotation'); missing=sum(1 for x in ann_errors if x['issue']=='missing_annotation')
    status='BLOCKED' if any(v['image_zip_entries'] or v['label_zip_entries'] for k,v in dirs.items() if k in ('train','val')) else 'PREPARED_WITH_LIMITATIONS'
    # Missing LFS payload means train/val blocked; available test subset has manifest only.
    status='BLOCKED'
    meta={'dataset':name,'source_root':str(source.resolve()),'status':status,'created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'class_count':len(names),'class_id_contiguous':sorted(names)==list(range(len(names))),'split_directories':dirs,'yaml_path_checks':cfg,'available_decoded_images':len(imgs),'available_test_images':sum(r['source_split']=='test' for r in imgs),'annotation_issue_count':len(ann_errors),'missing_annotations':missing,'invalid_annotation_lines':invalid,'exact_duplicate_groups':len(dup_groups),'duplicate_file_rows':len(duplicate_rows),'lfs_pointer_exclusions':len(exclusions),'environment':{'python':platform.python_version(),'pillow':Image.__version__},'safety':'Source YAML and image/label files were not modified. Test is available as a small labeled subset; no complete training split is available.'}
    (target/'preparation_metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf-8')
    (target/'dataset_summary.md').write_text('# Detection dataset validation\n\n- Status: **BLOCKED** for complete training preparation.\n- Configured class count: '+str(len(names))+'; contiguous IDs: '+str(meta['class_id_contiguous'])+'.\n- Available decoded images: '+str(len(imgs))+' (test: '+str(meta['available_test_images'])+').\n- Train/validation ZIP paths are Git LFS pointer text files, not archive payloads; expected sizes are captured in `exclusion_manifest.csv`.\n- `data.yaml` points validation and test to the same `images/test` directory. Its comments state 7,221 validation and 180 test, but the available test directory contains 180 images.\n- Annotation issues: '+str(len(ann_errors))+' (missing '+str(missing)+', malformed/out-of-range/unknown-class '+str(invalid)+'). Empty annotation files are retained as valid negative images.\n- Exact duplicate groups: '+str(len(dup_groups))+'; see `duplicate_report.csv`.\n\nNo annotation was invented and no source files/config were changed. Restore the original LFS payloads and correct configuration only in a separately reviewed future phase before training.\n',encoding='utf-8')
    return {'dataset':name,'output':str(target),'status':status,'images':len(imgs),'classes':len(names),'annotation_issues':len(ann_errors),'missing':missing,'invalid':invalid,'duplicates':len(dup_groups),'dirs':dirs,'yaml':cfg,'lfs':len(exclusions)}

def main():
    names=['fruits_360','healthy_rotten_diseases','vegnet','fruits_vegetables_detection']
    selected=['healthy_rotten_diseases'] if '--healthy-only' in sys.argv else (['fruits_vegetables_detection'] if '--detection-only' in sys.argv else names)
    occupied=[n for n in selected if (OUT/n).exists()]
    if occupied and '--replace-derived' not in sys.argv:
        raise SystemExit('Refusing to overwrite existing Phase 04 outputs: '+', '.join(occupied)+'. Copy this script into a new versioned output directory to repeat preparation.')
    results=[]
    fruits=DATASETS/'fruits_360'/'fruits-360_100x100'/'fruits-360'
    if '--healthy-only' in sys.argv:
        healthy=DATASETS/'healty_&_rotten'/'Fruit And Vegetable Diseases Dataset'
        tax={}
        for p in healthy.iterdir():
            if p.is_dir():
                suffix=p.name.rsplit('__',1)[-1]
                tax[p.name]=f'Folder-derived condition: {suffix}; source parent names this a Diseases Dataset. Not independently verified as food safety or shelf-life label.'
        return [make_classification('Healthy & Rotten / Fruit And Vegetable Diseases Dataset',healthy,'healthy_rotten_diseases',tax,None,'Folder taxonomy pairs 14 produce types with Healthy/Rotten labels. Source root names this a Diseases Dataset; no documentation establishes that “Rotten” is equivalent to Freshness ground truth. No official split exists; deterministic grouped 80/10/10 splits use seed 2048 after conflicting duplicate groups are held unresolved.')]
    if '--detection-only' in sys.argv:
        return [detection()]
    results.append(make_classification('Fruits-360',fruits,'fruits_360',{ },{'train':'Training','test':'Test'},'Variety/category recognition with folder labels; README documents 268 classes and 190,876 images. Official folders preserved; the dataset has controlled white-background images and does not encode freshness, shelf life, or food safety.'))
    healthy=DATASETS/'healty_&_rotten'/'Fruit And Vegetable Diseases Dataset'
    tax={}
    for p in healthy.iterdir():
        if p.is_dir():
            suffix=p.name.rsplit('__',1)[-1]
            tax[p.name]=f'Folder-derived condition: {suffix}; source parent names this a Diseases Dataset. Not independently verified as food safety or shelf-life label.'
    results.append(make_classification('Healthy & Rotten / Fruit And Vegetable Diseases Dataset',healthy,'healthy_rotten_diseases',tax,None,'Folder taxonomy pairs 13 produce types with Healthy/Rotten labels. Source root calls this a Diseases Dataset; no documentation establishes that “Rotten” is equivalent to Freshness ground truth. No official splits were present, so deterministic exact-duplicate-grouped 80/10/10 class-stratified manifests were assigned.'))
    veg=DATASETS/'vegetable_quality'/'vegnet'/'VegNet Vegetable Dataset with quality (Unripe, Ripe, Old, Dried and Damaged)'/'VegNet (Unripe, Ripe, Old, Dried and Damaged)'/'New VegNet'
    tax={}
    for v in veg.iterdir():
        if v.is_dir():
            for q in v.iterdir():
                if q.is_dir(): tax[f'{v.name}/{q.name}']=f'Folder-derived quality state “{q.name}” for produce category “{v.name}”; source directory title lists Unripe, Ripe, Old, Dried and Damaged.'
    # labels are relative folder paths, preserve exact folder strings by supplying a custom nested class reader through path adapter
    # create a temporary virtual root is avoided; custom function below via symlink-free recursive function.
    results.append(make_vegnet(veg,tax))
    results.append(detection())
    write_csv(OUT/'dataset_registry.csv',results,['dataset','status','images','candidates','classes','excluded','unresolved','duplicates_removed','leakage_groups','format_mismatches','annotation_issues','output'])
    (OUT/'README.md').write_text('''# Phase 04 image dataset preparation\n\nThis directory contains read-only audits and manifests for the four Phase 04 datasets. CSV paths point to original files; no image files were copied, transformed, renamed, relabeled, or deleted. Exact duplicates are grouped by SHA-256; redundant same-label copies are listed in `exclusion_manifest.csv`, while conflicting-label duplicate groups and invalid detection records are listed in `unresolved_manifest.csv`. Official partitions are preserved. Unsplit classification data uses seed 2048 for deterministic per-label 80/10/10 assignments after duplicate groups with conflicting labels are held unresolved.\n\nTo repeat safely, copy this script to a fresh versioned output directory under `datasets/prepared` and run it there with `py -3 prepare_phase04.py`; it refuses to overwrite an existing dataset output unless explicitly passed `--replace-derived`. It requires the already installed Pillow package and writes only derived artifacts. Do not treat image decoding as proof of label validity or production readiness. The detection dataset remains blocked pending restoration of its Git LFS payloads and correction of its validation configuration.\n''',encoding='utf-8')
    summaries=['# Phase 04 image dataset preparation summary','','No model training or inference was run. The source files are unchanged; the outputs are path-referencing manifests and reports.','','| Dataset | Status | Accepted images | Classes | Exclusions / findings |','|---|---|---:|---:|---|']
    for x in results:
        finding=('duplicate files: '+str(x.get('duplicates_removed',0))+'; excluded: '+str(x.get('excluded',0))+'; unresolved: '+str(x.get('unresolved',0)))
        if x['dataset']=='Fruits and Vegetables Detection Dataset': finding=f"available images {x.get('images',0)}; annotation issues {x.get('annotation_issues',0)}; LFS pointers {x.get('lfs',0)}; train/val blocked"
        summaries.append(f"| {x['dataset']} | {x['status']} | {x.get('images',0)} | {x.get('classes',0)} | {finding} |")
    summaries += ['', '## Recommended next phase', '', 'Restore the missing detection dataset LFS objects, reconcile its `data.yaml` split paths and class documentation, then re-run only its annotation audit. For classification, conduct label-semantics review before treating Healthy/Rotten or VegNet quality labels as operational cold-chain outcomes. Model training should be separately authorized after those reviews.']
    (OUT/'phase_04_summary.md').write_text('\n'.join(summaries)+'\n',encoding='utf-8')
    return results

def make_vegnet(source,taxonomy):
    target=OUT/'vegnet'; target.mkdir(parents=True,exist_ok=True); records=[]; exclusions=[]; unresolved=[]; folder_labels=[]
    candidates=[]
    for veg in sorted([p for p in source.iterdir() if p.is_dir()],key=lambda x:x.name.casefold()):
        for quality in sorted([p for p in veg.iterdir() if p.is_dir()],key=lambda x:x.name.casefold()):
            label=f'{veg.name}/{quality.name}'
            folder_labels.append(label)
            for p in sorted(quality.rglob('*'),key=lambda x:x.as_posix().casefold()):
                if p.is_file() and p.suffix.lower() in EXTS: candidates.append((p,label,''))
    def scan(item):
        p,label,split=item
        good=[]; bad=[]; img_record(p,source,label,split,good,bad)
        return (good,bad)
    with ThreadPoolExecutor(max_workers=8) as pool:
        for good,bad in pool.map(scan,candidates): records.extend(good); exclusions.extend(bad)
    before=len(records); records,dups,leak=group_duplicates(records,False,exclusions,unresolved); create_splits(records,False)
    labels=sorted(set(folder_labels),key=str.casefold); mapp=[{'class_id':i,'class_name':lab,'original_label':lab,'semantics':taxonomy.get(lab,'folder-derived label')} for i,lab in enumerate(labels)]
    byid={m['class_name']:m['class_id'] for m in mapp}
    for r in records: r['class_id']=byid[r['label']]; r['record_status']='accepted'; r['reason']=''
    fields=['source_path','relative_path','label','class_id','source_split','split','width','height','actual_format','extension','size_bytes','sha256','record_status','reason']; write_csv(target/'dataset_manifest.csv',records,fields); write_csv(target/'exclusion_manifest.csv',exclusions,fields); write_csv(target/'unresolved_manifest.csv',unresolved,fields)
    (target/'class_mapping.json').write_text(json.dumps({'label_semantics':'Original produce/quality folder hierarchy preserved; no collapse to Fresh/Rotten.','classes':mapp},indent=2,ensure_ascii=False),encoding='utf-8')
    dist={}
    for lab in labels: dist[lab]={'train':0,'validation':0,'test':0}
    for r in records: dist.setdefault(r['label'],{}).setdefault(r['split'],0); dist[r['label']][r['split']]+=1
    fm={}; mismatch=0
    for r in records:
        fm[r['actual_format']]=fm.get(r['actual_format'],0)+1
        if r['extension'].lstrip('.').upper()!=r['actual_format'].upper() and not (r['extension'] in ('.jpg','.jpeg') and r['actual_format']=='JPEG'): mismatch+=1
    status='PREPARED_WITH_LIMITATIONS'
    meta={'dataset':'VegNet','source_root':str(source.resolve()),'created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'status':status,'seed':SEED,'split_method':'deterministic per-label 80/10/10 after exact-hash grouping','candidate_decodable_images_before_duplicate_handling':before,'accepted_images':len(records),'excluded_records':len(exclusions),'exact_duplicate_files_removed':dups,'class_count':len(labels),'populated_class_count':len({r['label'] for r in records}),'class_distribution_by_split':dist,'actual_format_counts':fm,'extension_format_mismatches':mismatch,'decode_failure_count':sum(1 for x in exclusions if str(x.get('reason','')).startswith('decode_error')),'empty_quality_folders':[lab for lab in labels if not any(r['label']==lab for r in records)],'environment':{'python':platform.python_version(),'pillow':Image.__version__},'notes':'No source documentation found in inspected VegNet subtree; quality semantics inferred only from the folder hierarchy and dataset title.'}
    (target/'preparation_metadata.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf-8')
    md=['# VegNet preparation summary','','- Status: **'+status+'**','- Source: `'+str(source)+'`','- Decodable candidates: '+str(before),'- Accepted unique images: '+str(len(records)),'- Excluded (including duplicates): '+str(len(exclusions)),'- Folder labels including empty: '+str(len(labels))+'; populated: '+str(len({r["label"] for r in records})),'- Extension/format mismatches: '+str(mismatch),'- Deterministic class-stratified 80/10/10 split, seed 2048, after exact hash grouping.','','## Class counts by split','','| Produce / quality | train | validation | test | total |','|---|---:|---:|---:|---:|']
    for lab in labels:
        c=dist[lab]; md.append(f'| {lab} | {c.get("train",0)} | {c.get("validation",0)} | {c.get("test",0)} | {sum(c.values())} |')
    md+=['','## Limitations','','Tomato/Dried has no images (and therefore is absent from the observed class mapping). Class counts are imbalanced. No source documentation was found to define visual criteria for the five quality labels; folder names are retained verbatim. No image was transformed or copied.']
    (target/'dataset_summary.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
    return {'dataset':'VegNet','output':str(target),'status':status,'images':len(records),'candidates':before,'classes':len(labels),'excluded':len(exclusions),'duplicates_removed':dups,'leakage_groups':leak,'format_mismatches':mismatch,'dist':dist}

if __name__=='__main__':
    results=main()
    print(json.dumps([{k:v for k,v in x.items() if k not in ('dist','dirs','yaml')} for x in results],ensure_ascii=False,indent=2))
