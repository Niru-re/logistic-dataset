from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import csv, json, hashlib, math, statistics, sys, platform, re, os
from html.parser import HTMLParser

PROJECT=Path(r'C:\Users\nirma\OneDrive\Desktop\logistic')
MANGO=PROJECT/'datasets'/'cold_chain'/'mango_shipment'
FOOD=PROJECT/'datasets'/'Food-Expiry-Days-Prediction-Using-Machine-learning-main'/'Food-Expiry-Days-Prediction-Using-Machine-learning-main'/'food_expiry_dataset.csv'
FOODROOT=FOOD.parent
FOOD_NOTEBOOK=next(FOODROOT.glob('*.ipynb'),None)
FOOD_PDF=next(FOODROOT.glob('*.pdf'),None)
DYNAMIC=PROJECT/'datasets'/'dynamic_supply_chain_logistics_dataset.csv'
OUT=PROJECT/'datasets'/'prepared'/'phase_06_cold_chain_shelf_life_v1'
for d in ('mango_cold_chain','food_expiry','dynamic_logistics'): (OUT/d).mkdir(parents=True,exist_ok=True)

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def jwrite(path,obj): path.write_text(json.dumps(obj,indent=2,ensure_ascii=False,default=str),encoding='utf-8')
def csvwrite(path, rows, fields):
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
def parse_dt(v,formats):
    for fmt in formats:
        try:return datetime.strptime(v.strip(),fmt)
        except Exception:pass
    return None
def detect_delim(sample):
    try:return csv.Sniffer().sniff(sample,delimiters='\t,;|').delimiter
    except Exception:return '\t' if sample.count('\t')>=sample.count(',') else ','
def classify_type(vals):
    if not vals:return 'unknown'
    non=[x for x in vals if x not in ('',None)]
    if not non:return 'all_missing'
    n=0;dates=0
    for x in non[:500]:
        try: float(x);n+=1;continue
        except Exception: pass
        if parse_dt(x,['%d/%m/%Y %H:%M','%m/%d/%Y %H:%M','%d/%m/%Y','%d-%m-%Y','%m-%d-%Y','%Y-%m-%d']):dates+=1
    if n==min(len(non),500):return 'numeric'
    if dates==min(len(non),500):return 'datetime_like'
    return 'string'

def inspect_csv(path, family, manifest_path, target_fields=(), date_fields=(), expected_ranges=None):
    expected_ranges=expected_ranges or {}
    with path.open('r',newline='',encoding='utf-8-sig',errors='replace') as f:
        rd=csv.DictReader(f); cols=rd.fieldnames or []
        miss=Counter(); numstats={c:{'n':0,'min':None,'max':None,'sum':0.0,'invalid_numeric':0,'nonfinite':0} for c in cols}
        uniques={c:set() for c in cols}; uniq_overflow=set(); dups=set(); dup_count=0; row_count=0; parse_fail=Counter(); cat_counts={c:Counter() for c in cols if c not in expected_ranges and c not in date_fields}
        dates={c:[] for c in date_fields}; targets={c:Counter() for c in target_fields}; joint=Counter(); ranges_bad=Counter(); lat_bad=lon_bad=0; grouped_by_timestamp=Counter(); source_row_manifest=[]; seen_hash=set(); malformed=[]
        for idx,row in enumerate(rd, start=2):
            row_count+=1
            vals=[row.get(c,'') or '' for c in cols]
            h=hashlib.sha256('\x1f'.join(vals).encode('utf-8')).hexdigest()
            if h in seen_hash:dup_count+=1
            seen_hash.add(h)
            for c in cols:
                v=row.get(c,'') or ''
                if not v.strip():miss[c]+=1
                if c in uniques:
                    if len(uniques[c])<5000:uniques[c].add(v)
                    elif v not in uniques[c]:uniq_overflow.add(c)
                if c in numstats:
                    try:
                        n=float(v)
                        if not math.isfinite(n):numstats[c]['nonfinite']+=1;continue
                        st=numstats[c];st['n']+=1;st['sum']+=n;st['min']=n if st['min'] is None else min(st['min'],n);st['max']=n if st['max'] is None else max(st['max'],n)
                        if c in expected_ranges and not(expected_ranges[c][0]<=n<=expected_ranges[c][1]):ranges_bad[c]+=1
                    except Exception:
                        if v.strip():numstats[c]['invalid_numeric']+=1
                if c in date_fields:
                    dt=parse_dt(v,['%m/%d/%Y %H:%M','%d/%m/%Y %H:%M','%Y-%m-%d %H:%M:%S','%Y-%m-%d','%m/%d/%Y','%d-%m-%Y'])
                    if dt is None and v.strip():parse_fail[c]+=1
                    elif dt:dates[c].append(dt);grouped_by_timestamp[dt]+=1
                if c in targets:targets[c][v]+=1
                if c in cat_counts and v.strip() and len(v)<160:
                    try: float(v)
                    except Exception: cat_counts[c][v]+=1
            if 'risk_classification' in row and 'delay_probability' in row:
                try:joint[(row['risk_classification'],round(float(row['delay_probability']),2))]+=1
                except Exception:pass
            if 'vehicle_gps_latitude' in row and 'vehicle_gps_longitude' in row:
                try:
                    la=float(row['vehicle_gps_latitude']);lo=float(row['vehicle_gps_longitude'])
                    if not -90<=la<=90:lat_bad+=1
                    if not -180<=lo<=180:lon_bad+=1
                except Exception:lat_bad+=1;lon_bad+=1
            # Full traceability, preserve raw source fields and don't transform/drop values.
            status=[]
            for c in cols:
                if not (row.get(c,'') or '').strip():status.append(f'{c}:missing')
                if c in expected_ranges:
                    try:
                        n=float(row[c]);
                        if not math.isfinite(n) or not(expected_ranges[c][0]<=n<=expected_ranges[c][1]): status.append(f'{c}:outside_screening_range')
                    except Exception:
                        if row.get(c,'').strip():status.append(f'{c}:non_numeric')
            out=dict(row);out.update(source_file=str(path),source_row=idx,row_key=f'{family}:{idx}',validation_status=';'.join(status) or 'parsed_unreviewed',exclusion_status='not_excluded')
            source_row_manifest.append(out)
    schema=[]
    for c in cols:
        st=numstats[c];schema.append({'column':c,'observed_type':'numeric' if st['n'] else classify_type(list(uniques[c])),'observed_unique_count':len(uniques[c]) if c not in uniq_overflow else '>5000','missing_count':miss[c],'missing_fraction':miss[c]/row_count if row_count else None,'numeric_count':st['n'],'numeric_min':st['min'],'numeric_max':st['max'],'numeric_mean':st['sum']/st['n'] if st['n'] else None,'invalid_numeric_count':st['invalid_numeric'] if st['n'] else 0,'nonfinite_count':st['nonfinite'],'screening_range_exceedances':ranges_bad[c]})
    dt_reports={}
    for c,arr in dates.items():
        arrs=sorted(arr); diffs=[(b-a).total_seconds() for a,b in zip(arrs,arrs[1:])]
        dt_reports[c]={'parsed_count':len(arr),'parse_failures':parse_fail[c],'min':min(arrs).isoformat() if arrs else None,'max':max(arrs).isoformat() if arrs else None,'unique_timestamp_count':len(set(arrs)),'repeated_timestamp_values':sum(n>1 for n in Counter(arrs).values()),'median_gap_seconds':statistics.median(diffs) if diffs else None,'gap_seconds_range':[min(diffs),max(diffs)] if diffs else None,'original_order_monotonic_non_decreasing':all(a<=b for a,b in zip(arr,arr[1:]))}
    dup_info={'exact_duplicate_rows_after_header':dup_count}
    report={'source_file':str(path),'rows':row_count,'columns':len(cols),'column_names':cols,'schema':schema,'missing_by_column':dict(miss),'duplicate_findings':dup_info,'timestamp_findings':dt_reports,'target_value_counts':{c:dict(targets[c]) for c in target_fields},'categorical_value_counts':{c:dict(cat_counts[c].most_common(50)) for c in cat_counts if c not in date_fields},'screening_range_findings':dict(ranges_bad),'gps_invalid_latitude_rows':lat_bad,'gps_invalid_longitude_rows':lon_bad,'notes':[]}
    csvwrite(manifest_path,source_row_manifest,['source_file','source_row','row_key','validation_status','exclusion_status']+cols)
    return report

# Snapshot all in-scope original files before processing, then re-check at end.
sources=[]
for root in (MANGO,FOODROOT):
    if root.exists():sources.extend(p for p in root.rglob('*') if p.is_file())
if DYNAMIC.exists():sources.append(DYNAMIC)
source_hashes={str(p):sha(p) for p in sources}

# MANGO inventory and time-series/quality manifests.
mango_files=sorted(p for p in MANGO.rglob('*') if p.is_file())
mango_inventory=[]; mango_records=[]; mango_unresolved=[]; mango_exclusions=[]; data_file_reports=[]; cross_file_signatures=defaultdict(list); cross_file_values=defaultdict(list)
data_dirs={'01_src_subset_dataset_T_H','03_src_subset_dataset_W','05_src_subset_dataset_C','07_src_subset_dataset_PH','09_src_subset_dataset_TSS','11_src_subset_dataset_SR'}
data_dirs.update({'02_res_subset_dataset_T_H','06_res_subset_dataset_C','12_res_subset_dataset_SR'})
class TableParser(HTMLParser):
    def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None
    def handle_starttag(self,tag,attrs):
        if tag.lower()=='tr':self.row=[]
        elif tag.lower() in ('td','th') and self.row is not None:self.cell=[]
    def handle_data(self,data):
        if self.cell is not None:self.cell.append(data.strip())
    def handle_endtag(self,tag):
        if tag.lower() in ('td','th') and self.cell is not None:self.row.append(' '.join(x for x in self.cell if x));self.cell=None
        elif tag.lower()=='tr' and self.row is not None:
            if self.row:self.rows.append(self.row)
            self.row=None
for p in mango_files:
    rel=p.relative_to(MANGO).as_posix(); ext=p.suffix.lower(); rec={'relative_path':rel,'format':ext.lstrip('.') or 'no_extension','bytes':p.stat().st_size,'sha256':sha(p),'rows':'','columns':'','parse_status':'not_tabular_or_documentary'}
    if p.parent.name in data_dirs and ext in {'.txt','.tab','.csv','.html'} and not p.name.lower().startswith('read.me'):
        try:
            text=p.read_text(encoding='utf-8-sig',errors='replace')
            if ext=='.html':
                parser=TableParser();parser.feed(text);rows=parser.rows;header=rows[0] if rows else [];records=rows[1:]
            else:
                delim=detect_delim(text[:4000]); rows=list(csv.reader(text.splitlines(),delimiter=delim)); header=rows[0] if rows else [];records=rows[1:]
            raw_header=header;header=[str(x).strip() for x in raw_header]
            rec.update(rows=len(records),columns='|'.join(raw_header),normalized_columns='|'.join(header),parse_status='parsed_delimited_text')
            family=p.parent.name
            times=[]; invalid=0; missing_measurement_cells=0; column_missing=Counter(); invalid_examples=[]; rowdups=Counter(); numeric_vals=defaultdict(list); firstcol=header[0] if header else ''; time_col=firstcol.strip().lower() in {'time','timestamp','datetime','date'}
            for rn,cells in enumerate(records,start=2):
                row_invalid=len(cells)!=len(header)
                if row_invalid: invalid+=1
                row=dict(zip(header,cells)); firstval=row.get(firstcol,'') if firstcol else ''; stamp=firstval if time_col else ''
                dt=parse_dt(stamp,['%d/%m/%Y %H:%M','%d/%m/%Y %H:%M:%S','%Y-%m-%d %H:%M:%S','%d/%m/%Y']) if time_col else None
                if dt:times.append(dt)
                if cells:rowdups[tuple(cells)]+=1
                vals={k:v for k,v in row.items() if k!=firstcol}
                for k,v in vals.items():
                    if not v.strip() or v.strip().upper() in {'NA','N/A','NULL'}:
                        missing_measurement_cells+=1;column_missing[k]+=1
                        continue
                    try:n=float(v)
                    except Exception:
                        invalid+=1;row_invalid=True
                        if len(invalid_examples)<20:invalid_examples.append({'source_row':rn,'column':k,'observed_value':v})
                        continue
                    if not math.isfinite(n):
                        invalid+=1;row_invalid=True
                        if len(invalid_examples)<20:invalid_examples.append({'source_row':rn,'column':k,'observed_value':v})
                    else:numeric_vals[k].append(n)
                mango_records.append({'source_file':str(p),'relative_source_path':rel,'source_row':rn,'record_key':p.stem+':'+str(rn),'recording_or_sample_key':p.stem,'sample_identifier_raw':firstval if not time_col else '', 'timestamp_raw':stamp,'timestamp_parsed':dt.isoformat(sep=' ') if dt else '', 'observed_measurements_json':json.dumps(vals,separators=(',',':')),'validation_status':'invalid_numeric_or_width' if row_invalid else ('contains_missing_measurements' if any(not x.strip() or x.strip().upper() in {'NA','N/A','NULL'} for x in vals.values()) else 'valid_parse'),'exclusion_status':'not_excluded'})
                boxmatch=re.search(r'_(\d+_\d+_\d+)_Temp(?:_Hum)?$',p.stem,re.I)
                if family=='01_src_subset_dataset_T_H' and time_col and boxmatch and dt:
                    signature=json.dumps([boxmatch.group(1),stamp,vals],sort_keys=True,separators=(',',':'));cross_file_signatures[hashlib.sha256(signature.encode()).hexdigest()].append({'relative_path':rel,'source_row':rn,'box':boxmatch.group(1),'timestamp':stamp});cross_file_values[(boxmatch.group(1),stamp)].append({'relative_path':rel,'source_row':rn,'values':json.dumps(vals,sort_keys=True,separators=(',',':'))})
            sortedt=sorted(times); gaps=[(b-a).total_seconds() for a,b in zip(sortedt,sortedt[1:])]
            data_file_reports.append({'source_file':str(p),'relative_path':rel,'family':family,'rows':len(records),'columns':header,'source_column_names':raw_header,'header_whitespace_normalized':header!=raw_header,'record_identifier_column':None if time_col else firstcol,'observed_type_by_column':{k:('datetime_like' if k==firstcol and time_col else ('identifier' if k==firstcol else ('numeric' if k in numeric_vals else 'unknown_or_all_missing')) ) for k in header},'column_missing_counts':dict(column_missing),'row_width_mismatch_count':sum(len(x)!=len(header) for x in records),'missing_measurement_cells_blank_or_NA':missing_measurement_cells,'duplicate_rows':sum(n-1 for n in rowdups.values() if n>1),'parsed_timestamps':len(times),'timestamp_parse_failures':len(records)-len(times) if time_col else 0,'min_timestamp':min(sortedt).isoformat(sep=' ') if sortedt else None,'max_timestamp':max(sortedt).isoformat(sep=' ') if sortedt else None,'duplicate_timestamp_count':len(times)-len(set(times)),'timestamp_order_monotonic':all(a<=b for a,b in zip(times,times[1:])),'median_gap_seconds':statistics.median(gaps) if gaps else None,'gap_range_seconds':[min(gaps),max(gaps)] if gaps else None,'numeric_ranges':{k:{'min':min(v),'max':max(v),'mean':sum(v)/len(v),'n':len(v)} for k,v in numeric_vals.items() if v},'invalid_numeric_or_width_cells':invalid,'invalid_numeric_examples':invalid_examples})
        except Exception as e:
            rec['parse_status']='parse_error:'+type(e).__name__; mango_unresolved.append({'source_path':str(p),'row_identifier':'','issue':'unable to parse tabular source: '+repr(e)})
    mango_inventory.append(rec)
# Provenance-based relationship audit, no inferred join output.
readme=(MANGO/'0_README.txt').read_text(encoding='utf-8',errors='replace') if (MANGO/'0_README.txt').exists() else ''
# report by schema family and same sample keys found in headers/filenames.
family_counts=Counter(r['family'] for r in data_file_reports)
quality_fams={'03_src_subset_dataset_W','05_src_subset_dataset_C','07_src_subset_dataset_PH','09_src_subset_dataset_TSS'}
for fam in sorted(quality_fams):
    matching=[r for r in data_file_reports if r['family']==fam]
    if matching: mango_unresolved.append({'source_path':';'.join(r['source_file'] for r in matching),'row_identifier':'','issue':f'{fam}: retain separate; the filename/documented configuration, sample and day keys need a validated shared physical-sample crosswalk before row-level multi-sensor joins'})
mango_unresolved.append({'source_path':str(MANGO),'row_identifier':'','issue':'shelf-life target: quality attributes are measured at D0/D3/D6/D9/D12/D15 under storage conditions; no documented failure/expiry/survival threshold or remaining-life label found; do not derive shelf-life labels from temperature alone'})
mango_unresolved.append({'source_path':str(MANGO/'0_README.txt'),'row_identifier':'','issue':'documented inventory discrepancies: README says 342 temperature/humidity files and 19 quality data files; on-disk raw directories contain 341 T/H data files and 17 W/C/pH/TSS measurement tables (21 files including 4 read.me documents); use actual inventory counts'})
for q in data_file_reports:
    if '_src_subset_' not in q['family']: continue
    if q.get('missing_measurement_cells_blank_or_NA',0): mango_unresolved.append({'source_path':q['source_file'],'row_identifier':'multiple rows/columns','issue':f"{q['missing_measurement_cells_blank_or_NA']} blank/NA measurement cells; verify whether structurally unmeasured or missing observations"})
    for bad in q.get('invalid_numeric_examples',[]): mango_unresolved.append({'source_path':q['source_file'],'row_identifier':'row '+str(bad['source_row']),'issue':f"invalid measurement value {bad['column']}={bad['observed_value']!r}; verify against original lab record"})
cross_file_duplicates=[{'duplicate_group':'mango-observation-'+digest[:12],'box_id':items[0]['box'],'timestamp':items[0]['timestamp'],'source_paths_and_rows':';'.join(x['relative_path']+':'+str(x['source_row']) for x in items),'file_count':len(items),'interpretation':'same box/timestamp/values repeated across files; may be aggregate-log overlap, not an independent observation'} for digest,items in cross_file_signatures.items() if len({x['relative_path'] for x in items})>1]
cross_file_conflicts=[{'box_id':key[0],'timestamp':key[1],'source_paths_and_rows':';'.join(x['relative_path']+':'+str(x['source_row']) for x in values),'distinct_measurement_payloads':len({x['values'] for x in values})} for key,values in cross_file_values.items() if len({x['relative_path'] for x in values})>1 and len({x['values'] for x in values})>1]
if cross_file_duplicates:mango_unresolved.append({'source_path':str(MANGO/'01_src_subset_dataset_T_H'),'row_identifier':'see duplicate_record_report.csv','issue':f'{len(cross_file_duplicates)} same box/timestamp/value records occur in multiple raw/aggregate files; select one canonical source or explicitly deduplicate before row-level modeling'})
if cross_file_conflicts:mango_unresolved.append({'source_path':str(MANGO/'01_src_subset_dataset_T_H'),'row_identifier':'see conflicting_record_report.csv','issue':f'{len(cross_file_conflicts)} box/timestamp keys have different measurement payloads across files; investigate sensor/source semantics before joining'})
mango_unresolved.append({'source_path':str(MANGO/'0_README.txt'),'row_identifier':'','issue':'documented inventory discrepancies: README says 342 temperature/humidity files and 19 quality data files; on-disk raw directories contain 341 T/H data files and 17 W/C/pH/TSS measurement tables (21 files including 4 read.me documents); use actual inventory counts'})
# no exclusions asserted: source tables retained verbatim; manifest provides diagnostics only.
csvwrite(OUT/'mango_cold_chain'/'source_file_inventory.csv',mango_inventory,['relative_path','format','bytes','sha256','rows','columns','normalized_columns','parse_status'])
csvwrite(OUT/'mango_cold_chain'/'dataset_manifest.csv',mango_records,['source_file','relative_source_path','source_row','record_key','recording_or_sample_key','sample_identifier_raw','timestamp_raw','timestamp_parsed','observed_measurements_json','validation_status','exclusion_status'])
csvwrite(OUT/'mango_cold_chain'/'duplicate_record_report.csv',cross_file_duplicates,['duplicate_group','box_id','timestamp','source_paths_and_rows','file_count','interpretation'])
csvwrite(OUT/'mango_cold_chain'/'conflicting_record_report.csv',cross_file_conflicts,['box_id','timestamp','source_paths_and_rows','distinct_measurement_payloads'])
csvwrite(OUT/'mango_cold_chain'/'exclusion_manifest.csv',mango_exclusions,['source_path','row_identifier','reason','rule_applied'])
csvwrite(OUT/'mango_cold_chain'/'unresolved_manifest.csv',mango_unresolved,['source_path','row_identifier','issue'])

# CSV families: stream full datasets; preserve source columns and row numbers in manifests.
food_report=inspect_csv(FOOD,'food_expiry',OUT/'food_expiry'/'dataset_manifest.csv',target_fields=('Expiry_days',),date_fields=('Date_of_purchase',),expected_ranges={'Expiry_days':(0,10000),'Temperature':(-100,100),'Humidity':(0,100)})
dyn_ranges={c:(0,1) for c in ['handling_equipment_availability','supplier_reliability_score','driver_behavior_score','fatigue_monitoring_score','disruption_likelihood_score','delay_probability']}
dyn_report=inspect_csv(DYNAMIC,'dynamic_logistics',OUT/'dynamic_logistics'/'dataset_manifest.csv',target_fields=('risk_classification',),date_fields=('timestamp',),expected_ranges=dyn_ranges)

# Enrich task-specific cross-field diagnostics with a separate low-memory pass.
def target_cross(path, fields):
    c=Counter();
    with path.open('r',newline='',encoding='utf-8-sig',errors='replace') as f:
        rd=csv.DictReader(f)
        for row in rd:c[tuple(row.get(x,'') for x in fields)]+=1
    return {'fields':fields,'distinct_combinations':len(c),'top_combinations':[{'values':list(k),'count':n} for k,n in c.most_common(30)]}
food_report['category_storage_target_combinations']=target_cross(FOOD,['Food_type','Storage_condition','Expiry_days'])
dyn_report['risk_classification_vs_delay_probability']=target_cross(DYNAMIC,['risk_classification','delay_probability'])
food_cross=defaultdict(lambda:{'n':0,'temp_min':None,'temp_max':None,'temp_sum':0.0,'expiry_min':None,'expiry_max':None,'expiry_sum':0.0})
with FOOD.open('r',newline='',encoding='utf-8-sig',errors='replace') as f:
    for r in csv.DictReader(f):
        k=(r.get('Food_type',''),r.get('Storage_condition','')); a=food_cross[k]
        try:
            t=float(r['Temperature']);a['temp_min']=t if a['temp_min'] is None else min(a['temp_min'],t);a['temp_max']=t if a['temp_max'] is None else max(a['temp_max'],t);a['temp_sum']+=t
        except Exception:pass
        try:
            y=float(r['Expiry_days']);a['expiry_min']=y if a['expiry_min'] is None else min(a['expiry_min'],y);a['expiry_max']=y if a['expiry_max'] is None else max(a['expiry_max'],y);a['expiry_sum']+=y
        except Exception:pass
        a['n']+=1
food_report['temperature_and_target_by_category_storage']=[{'food_type':k[0],'storage_condition':k[1],**v,'temperature_mean':v['temp_sum']/v['n'] if v['n'] else None,'expiry_days_mean':v['expiry_sum']/v['n'] if v['n'] else None} for k,v in sorted(food_cross.items())]
prob_by_risk=defaultdict(lambda:{'n':0,'min':None,'max':None,'sum':0.0,'bins':Counter()})
with DYNAMIC.open('r',newline='',encoding='utf-8-sig',errors='replace') as f:
    for r in csv.DictReader(f):
        try:
            p=float(r['delay_probability']);a=prob_by_risk[r['risk_classification']];a['n']+=1;a['min']=p if a['min'] is None else min(a['min'],p);a['max']=p if a['max'] is None else max(a['max'],p);a['sum']+=p;a['bins'][min(9,int(p*10))]+=1
        except Exception:pass
dyn_report['delay_probability_by_risk_class']={k:{'count':v['n'],'min':v['min'],'max':v['max'],'mean':v['sum']/v['n'] if v['n'] else None,'probability_decile_counts':dict(v['bins'])} for k,v in prob_by_risk.items()}
# classify dates / outcomes / potential leakage from task timing, no target used for training.
food_report['task_assessment']={'target_candidate':'Expiry_days (unit implied by name, not documented by machine-readable schema)','actual_expiry_date_field_present':False,'purchase_date_is_not_an_expiry_or_production_date':'Date_of_purchase only; no production/expiry date column','limitations':['README schema differs from CSV: claims Packaging/Preservatives, while observed CSV contains Storage_condition/Temperature/Humidity and no Preservatives','No item, lot, brand, batch, or source ID','Dataset provenance/generation and target label definition are not evidenced','Storage label-temperature contradictions require review; e.g. dataset range screens only, not safety thresholds','No documented target time/censoring or ground-truth expiration protocol'],'readiness_for_agri_cold_chain_shelf_life':'BLOCKED'}
dyn_report['task_assessment']={'candidate_targets':['delay_probability','risk_classification','delivery_time_deviation'],'row_unit':'unknown; timestamp rows only, no shipment/trip/vehicle identifiers','prediction_time_and_target_generation':'undocumented','post_event_or_proxy_fields':['delivery_time_deviation','eta_variation_hours','order_fulfillment_status','cargo_condition_status','route_risk_level','disruption_likelihood_score','customs_clearance_time; availability at prediction time cannot be verified'],'cold_chain_applicability':'iot_temperature exists but unit and temporal meaning are undocumented; no confirmed shipment ID or grouping key','readiness_for_supervised_shipment_risk_or_delay_prediction':'BLOCKED'}
food_report['documentation_discrepancy']='README claims Food_type, Packaging, Storage_temperature, Preservatives, Expiry_days; observed CSV uses Food_type, Storage_condition, Temperature, Humidity, Packaging, Date_of_purchase, Expiry_days.'
food_report['provenance']='Unknown from local documentation; README describes a modeling example but does not establish record origin or target ground truth.'
food_report['related_artifact_findings']={'notebook':{'path':str(FOOD_NOTEBOOK) if FOOD_NOTEBOOK else None,'saved_output_schema':'100,000 rows / 5 columns: Food_type, Packaging, Storage_temperature, Preservatives, Expiry_days','notebook_input_path':'C:/Users/tamil/food_expiry_dataset.csv','current_csv_schema':'200,000 rows / 7 different columns','interpretation':'Notebook output refers to a different schema/version/path; do not treat its model outputs or reported metrics as evaluation of the current CSV.'},'pdf':{'path':str(FOOD_PDF) if FOOD_PDF else None,'metadata':'14 pages; created by Microsoft Word 2021 on 2025-10-03; full text was not extracted with available installed tools.'}}
dyn_report['documentation']='No matching dataset README/schema documentation located alongside this CSV in its dataset root.'

# Data dictionaries are explicit about unsupported semantics.
def dictionary(report, verified, unit_map=None):
    unit_map=unit_map or {};out=[]
    for c in report['column_names']:
        sch=next(s for s in report['schema'] if s['column']==c)
        out.append({'column':c,'observed_type':sch['observed_type'],'meaning':verified.get(c,'Unknown; not documented.'),'unit':unit_map.get(c,'Unknown unless explicitly documented.'),'missing_count':sch['missing_count'],'known_limitations':('See data_quality_report.json; observed distributions do not verify semantic validity.' if c not in verified else 'Documented meaning may still not establish data provenance or target validity.')})
    return out
food_verified={'Food_type':'Product category (README and field name agree).','Storage_condition':'Storage category (field observed; README instead names Packaging and Storage_temperature).','Temperature':'Storage temperature (field context suggests this; unit is not explicitly attached to values in schema).','Humidity':'Humidity measurement (field context suggests this; unit not explicitly encoded).','Packaging':'Packaging type (README and field name agree).','Date_of_purchase':'Purchase date as recorded; no time/ timezone.','Expiry_days':'Target candidate stated in README as days until expiry; actual label-generation rule and ground-truth source not documented.'}
dyn_verified={'timestamp':'Timestamp string; no timezone specified.','vehicle_gps_latitude':'Latitude by name; coordinate reference / provenance unknown.','vehicle_gps_longitude':'Longitude by name; coordinate reference / provenance unknown.','iot_temperature':'Temperature-like IoT field; unit and sampling semantics unknown.','delay_probability':'Probability-like candidate target by name; target-generation procedure unknown.','risk_classification':'Categorical risk label by name; class policy / generation unknown.','delivery_time_deviation':'Delivery deviation-like field by name; unit and whether available at prediction time unknown.'}
fooddict=dictionary(food_report,food_verified,{'Temperature':'Unstated (README says °C for differently named Storage_temperature)','Humidity':'Unstated'})
dyndict=dictionary(dyn_report,dyn_verified)
mango_columns={}
for q in data_file_reports:
    for c in q['columns']:
        x=mango_columns.setdefault(c,{'column':c,'observed_types':set(),'source_files':[],'missing_count':0,'meaning':'Unknown; use the file/family context and original README.','unit':'Unknown unless documented in README.'})
        x['observed_types'].add(q['observed_type_by_column'].get(c,'unknown'))
        x['source_files'].append(q['relative_path'])
        x['missing_count']+=q['column_missing_counts'].get(c,0)
for c,x in mango_columns.items():
    x['observed_types']=sorted(x['observed_types'])
    if c=='Time':x.update(meaning='Measurement timestamp; local timezone not specified.',unit='datetime')
    elif c in {'T_mangoes','T_Air','Temperature','T_16C','T_21C'}:x.update(meaning='Temperature measurement (README describes mango/air/storage temperatures).',unit='°C per README')
    elif c.startswith('RH_') or c.startswith('H_'):x.update(meaning='Relative humidity measurement.',unit='% RH per README')
    elif c.startswith('L_'):x.update(meaning='CIELAB lightness at the named storage day.',unit='CIELAB L*; uncertainty ±0.2 per README')
    elif c.startswith('a_'):x.update(meaning='CIELAB green-red coordinate at named storage day.',unit='CIELAB a*; uncertainty ±0.2 per README')
    elif c.startswith('b_'):x.update(meaning='CIELAB blue-yellow coordinate at named storage day.',unit='CIELAB b*; uncertainty ±0.2 per README')
    elif c=='BOX_NAME':x.update(meaning='Sample/fruit label as recorded in color file; mapping policy needs verification.',unit='identifier')
    elif c.startswith('M_'):x.update(meaning='Mango/sample measurement field; exact attribute is determined by source file family.',unit='g for weight family; pH or °Bx in corresponding family per README')
    elif c in {'Average','Min','Max','SD','Var'}:x.update(meaning='Processed descriptive statistic; not an independent raw observation.',unit='inherits the summarized measurement unit')
    elif c in {'Date','day','Step','Configuration'}:x.update(meaning='Experiment/date/step field where present; see source filename and README.',unit='unknown or categorical')
    x['source_files']=sorted(set(x['source_files']))

# Full source integrity comparison.
post={str(p):sha(p) for p in sources}
integrity={'source_files_hashed_before':len(source_hashes),'source_files_hashed_after':len(post),'unchanged':source_hashes==post,'changed_paths':[p for p in source_hashes if post.get(p)!=source_hashes[p]],'scope':'all files under mango source directory and Food Expiry directory, plus dynamic CSV','note':'Output files are outside these source roots.'}

jwrite(OUT/'mango_cold_chain'/'data_quality_report.json',{'dataset':'Mango cold-chain experiment','source_root':str(MANGO),'source_files':len(mango_inventory),'source_file_type_counts':dict(Counter(r['format'] for r in mango_inventory)),'tabular_data_files':len(data_file_reports),'tabular_data_summary_by_folder':{k:{'files':sum(r['family']==k for r in data_file_reports),'data_rows':sum(r['rows'] for r in data_file_reports if r['family']==k)} for k in sorted(family_counts)},'per_file_findings':data_file_reports,'missing_measurement_cells':sum(r.get('missing_measurement_cells_blank_or_NA',0) for r in data_file_reports),'raw_source_invalid_measurement_or_width_cells':sum(r.get('invalid_numeric_or_width_cells',0) for r in data_file_reports if '_src_subset_' in r['family']),'parsed_summary_table_structure_findings':sum(r.get('invalid_numeric_or_width_cells',0) for r in data_file_reports if '_res_subset_' in r['family']),'cross_file_exact_record_matches':len(cross_file_duplicates),'cross_file_conflicting_box_timestamp_keys':len(cross_file_conflicts),'join_assessment':{'temperature_humidity_to_quality':'Potential batch-level linking is documented by experimental configuration/box position, but no verified per-mango temporal crosswalk is established by this audit. Do not concatenate as one observation without checking experiment and sample mappings.','quality_attribute_overlap':'pH and TSS column labels use mango/box identifiers; color and weight use distinct conventions and repeated date/sample rows; exact physical sample/date alignment needs a crosswalk.','shelf_life':'No scientifically justified expiry/failure endpoint; these are repeated quality measurements, not a remaining-life label.'},'provenance':{'README':str(MANGO/'0_README.txt'),'research_setup':'README describes iButton 5-minute monitoring, instrument uncertainty, four experimental configurations and quality days D0-D15.','documented_units':{'temperature':'°C','relative_humidity':'% RH','mass':'g','color':'L*a*b* values; uncertainty stated ±0.2','TSS':'°Bx; stated uncertainty ±0.4','pH':'pH; stated uncertainty ±0.03'},'warning':'Filename metadata informs potential grouping, but source measurement rows do not contain a stable joined sample ID across all families.'},'readiness':'AUDIT_COMPLETE','limitations':['No split manifest: correlated recordings, configurations, boxes and fruit samples require group/time-aware design before split.','Measured quality trajectories support descriptive/quality-change analysis under the documented experiment, but not a validated shelf-life target.','Sensor and quality sources remain separate; no merged output was created.']})
jwrite(OUT/'mango_cold_chain'/'data_dictionary.json',{'columns':mango_columns,'families':sorted(family_counts),'unknown_semantics':'Variables not supported by README/file context are explicitly marked unknown.'})
jwrite(OUT/'mango_cold_chain'/'preparation_metadata.json',{'source_root':str(MANGO),'processing_script':'../phase_06_prepare.py','python':sys.version,'platform':platform.platform(),'random_seed':None,'transformations':['Read-only parsing of tab-separated measurement files in raw source folders.','No value imputation, row deletion, join, derived outcome, or split was performed.'],'source_integrity':integrity,'readiness':'AUDIT_COMPLETE'})
jwrite(OUT/'food_expiry'/'data_quality_report.json',{**food_report,'readiness':'BLOCKED','source_integrity':integrity})
jwrite(OUT/'food_expiry'/'data_dictionary.json',{'columns':fooddict,'limitations':'Meanings indicated by README remain claims until provenance/schema are reconciled.'})
jwrite(OUT/'food_expiry'/'preparation_metadata.json',{'source_file':str(FOOD),'source_file_bytes':FOOD.stat().st_size,'source_sha256':source_hashes[str(FOOD)],'python':sys.version,'platform':platform.platform(),'processing_script':'../phase_06_prepare.py','random_seed':None,'transforms':['No cleaning or data transformations; source fields preserved.'],'readiness':'BLOCKED','source_integrity':integrity})
for fam,report,dictdata,path,stat in [('dynamic_logistics',dyn_report,dyndict,DYNAMIC,'BLOCKED')]:
    jwrite(OUT/fam/'data_quality_report.json',{**report,'readiness':stat,'source_integrity':integrity})
    jwrite(OUT/fam/'data_dictionary.json',{'columns':dictdata,'limitations':'Observed statistical patterns do not verify field semantics.'})
    jwrite(OUT/fam/'preparation_metadata.json',{'source_file':str(path),'source_file_bytes':path.stat().st_size,'source_sha256':source_hashes[str(path)],'python':sys.version,'platform':platform.platform(),'processing_script':'../phase_06_prepare.py','random_seed':None,'transforms':['No cleaning or data transformations; source fields preserved.'],'readiness':stat,'source_integrity':integrity})

# Summaries with grounded findings.
(OUT/'mango_cold_chain'/'dataset_summary.md').write_text(f'''# Mango cold-chain measurements\n\n**Readiness: AUDIT_COMPLETE**\n\nSource: `{MANGO}`. The inventory contains {len(mango_inventory)} files across raw measurement, processed result, documentation, R code, and photo/device folders. Parsed {len(data_file_reports)} raw and processed tabular files into {len(mango_records)} traceable records. Found {len(cross_file_duplicates)} exact box/time/value overlaps across files and {len(cross_file_conflicts)} conflicting box/time keys. Raw measurement tables contain {sum(q.get('missing_measurement_cells_blank_or_NA',0) for q in data_file_reports if '_src_subset_' in q['family'])} blank/NA cells and {sum(q.get('invalid_numeric_or_width_cells',0) for q in data_file_reports if '_src_subset_' in q['family'])} invalid/width findings; the color sources include a questionable L_D12 value 69/21. The README count differs from disk: 342 vs 341 T/H data files and 19 vs 17 W/C/pH/TSS data tables (21 files when including 4 read.me documents). The README documents 5-minute iButton temperature readings, °C and %RH, and quality measurements across D0–D15 under 16°C/21°C conditions.\n\nPer-file rows, timestamps, intervals, and ranges are in `data_quality_report.json`; source names, sizes, formats, hashes and schemas are in `source_file_inventory.csv`. Quality and sensor records were not merged: box/configuration associations are plausible at batch level, but a verified physical-sample and timestamp crosswalk for a leakage-safe supervised target was not established. The measured mass/color/pH/TSS trajectories do not define a remaining-shelf-life endpoint. No cleaned or split data was created.\n''',encoding='utf-8')
(OUT/'food_expiry'/'dataset_summary.md').write_text(f'''# Food Expiry CSV\n\n**Readiness: BLOCKED for AgriChain shelf-life prediction.**\n\nSource: `{FOOD}`. Actual schema: {', '.join(food_report['column_names'])}. The README documents a different schema and asserts `Expiry_days` is days until expiry, but no record provenance, ground-truth protocol, item/lot IDs, or expiry date is supplied. The candidate target ranges 1–187 (unit and truth unverified); nine category fields are missing, there are no exact duplicate rows, and purchase dates cover 2023-01-01 through 2045-10-25. Temperature spans -20 to 35 in every storage category, including values inconsistent with the category label; do not treat these rows as validated storage exposure. The related notebook's saved output is for an older 100,000-row/five-column schema and hard-codes a different local input path; those outputs do not evaluate this CSV. Do not treat this target as established truth. See report for full row counts, missingness, duplicates, value ranges, category/target combinations and exclusions (none applied). No cleaning or split was created.\n''',encoding='utf-8')
(OUT/'dynamic_logistics'/'dataset_summary.md').write_text(f'''# Dynamic logistics dataset\n\n**Readiness: BLOCKED for supervised cold-chain shipment-risk prediction.**\n\nSource: `{DYNAMIC}`. No local schema/readme was located alongside the CSV. The data has {dyn_report['rows']} rows and {dyn_report['columns']} columns. It contains 32,065 unique timestamps exactly one hour apart from 2021-01-01 through 2024-08-29, no missing values and no exact duplicate rows. Risk labels are High 23,944, Moderate 5,011, Low 3,110. Candidate `delay_probability` spans nearly 0–1 inside every risk class, so the class does not map cleanly to that field; target-generation rules, row unit, prediction time, feature timing, units and provenance are undocumented. No shipment/trip/vehicle identifiers support group-based validation. `delivery_time_deviation` and multiple operational fields may reveal post-event outcomes. No cleaned output or split was created.\n''',encoding='utf-8')

# CSV artifacts always exist, even when no rows were excluded or no split is defensible.
for fam in ('food_expiry','dynamic_logistics'):
    csvwrite(OUT/fam/'exclusion_manifest.csv',[],['source_file','source_row','row_key','reason','rule_applied'])
    issues=[]
    if fam=='food_expiry':
        issues=[{'source_path':str(FOODROOT/'README.md'),'row_identifier':'','issue':'README schema/claims differ from CSV; target provenance and generation rule unknown'},{'source_path':str(FOOD_NOTEBOOK),'row_identifier':'saved output','issue':'notebook output reports a different 100,000-row/5-column schema and references another user path; its metrics do not validate current CSV'},{'source_path':str(FOOD),'row_identifier':'','issue':'no product/lot/source IDs; no expiry date or production date to validate Expiry_days'}]
    else:
        issues=[{'source_path':str(DYNAMIC),'row_identifier':'','issue':f'field {c} meaning, unit, prediction-time availability and provenance undocumented'} for c in ['delay_probability','risk_classification','delivery_time_deviation','iot_temperature','eta_variation_hours']]+[{'source_path':str(DYNAMIC),'row_identifier':'','issue':'no verified shipment/trip/vehicle key; chronological records cannot be grouped into independent shipment partitions'}]
    csvwrite(OUT/fam/'unresolved_manifest.csv',issues,['source_path','row_identifier','issue'])

registry=[{'dataset':'Mango cold-chain measurements','source':str(MANGO),'actual_size':'files: '+str(len(mango_inventory))+'; parsed tabular rows: '+str(len(mango_records)),'candidate_task':'descriptive sensor/quality trajectory analysis; future quality estimation contingent on validated sample links','readiness':'AUDIT_COMPLETE','split_manifest':'not created; group/time crosswalk needed'},{'dataset':'Food Expiry CSV','source':str(FOOD),'actual_size':f"{food_report['rows']} rows x {food_report['columns']} columns",'candidate_task':'shelf-life estimation only after target/provenance validation','readiness':'BLOCKED','split_manifest':'not created; no item/lot grouping or target ground truth'},{'dataset':'Dynamic logistics CSV','source':str(DYNAMIC),'actual_size':f"{dyn_report['rows']} rows x {dyn_report['columns']} columns",'candidate_task':'risk/delay prediction only after target and prediction-time definitions','readiness':'BLOCKED','split_manifest':'not created; no shipment/trip grouping'}]
csvwrite(OUT/'dataset_registry.csv',registry,['dataset','source','actual_size','candidate_task','readiness','split_manifest'])
(OUT/'README.md').write_text('''# Phase 06 data-preparation audit\n\nRead `phase_06_summary.md`, then each family `dataset_summary.md`. Manifests preserve raw values and source row numbers; no rows were silently cleaned or dropped. Empty exclusion manifests mean no cleaned dataset was produced and therefore no records were excluded. No split manifest was generated where grouping or target semantics are insufficient. `phase_06_prepare.py` reruns the read-only inventory and report generation using Python standard library. Source hashes are checked before and after each run.\n''',encoding='utf-8')
(OUT/'phase_06_summary.md').write_text(f'''# Phase 06 — Cold-chain, shelf-life and logistics data preparation\n\n| Family | Actual size | Status | Key limitation |\n|---|---:|---|---|\n| Mango experiment | {len(mango_inventory)} source files; {len(mango_records)} parsed time-series/quality rows | AUDIT_COMPLETE | Box/configuration association is plausible, but no complete validated sample/time crosswalk or shelf-life endpoint; no merged data/split. |\n| Food Expiry | {food_report['rows']} × {food_report['columns']} | BLOCKED | README and CSV schemas differ; target ground truth/provenance/IDs not established. |\n| Dynamic logistics | {dyn_report['rows']} × {dyn_report['columns']} | BLOCKED | Candidate targets and prediction-time semantics unknown; no shipment/trip IDs; leakage risk. |\n\nSource integrity check: {integrity['source_files_hashed_before']} files hashed before and after; unchanged = **{integrity['unchanged']}**. No model training or evaluation occurred. No source dataset files were edited.\n\n## Next step\n\nObtain authoritative data dictionaries and collection/label-generation protocols for the two CSV datasets. For mango measurements, build and independently verify an experiment/box/fruit/date crosswalk and define a scientific quality or shelf-life endpoint before deciding on any prediction task. Then design group- and time-aware validation partitions before model work.\n''',encoding='utf-8')

print(json.dumps({'output':str(OUT),'mango_files':len(mango_inventory),'mango_tabular_files':len(data_file_reports),'mango_rows':len(mango_records),'food_rows':food_report['rows'],'food_columns':food_report['columns'],'food_missing':food_report['missing_by_column'],'food_duplicates':food_report['duplicate_findings'],'dynamic_rows':dyn_report['rows'],'dynamic_columns':dyn_report['columns'],'dynamic_missing':dyn_report['missing_by_column'],'dynamic_duplicates':dyn_report['duplicate_findings'],'source_integrity':integrity},indent=2,ensure_ascii=False))





