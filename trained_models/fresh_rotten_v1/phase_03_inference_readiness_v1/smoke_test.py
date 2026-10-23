from __future__ import annotations
import datetime,hashlib,json,math,platform,tempfile,time
from pathlib import Path
import torch
from PIL import Image,ImageDraw
from inference_module import load_predictor

OUT=Path(__file__).resolve().parent
def sha256(path:Path)->str:
 h=hashlib.sha256()
 with path.open("rb") as f:
  for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
 return h.hexdigest()
def new_path(path:Path)->Path:
 if not path.exists(): return path
 for i in range(2,10000):
  p=path.with_name(f"{path.stem}_run_{i}{path.suffix}")
  if not p.exists(): return p
 raise RuntimeError(f"Cannot allocate report path for {path}")
def check_result(r):
 required={"input_identifier","model_name","model_version","selected_checkpoint","predicted_class_name","produce_type","freshness_label","raw_predicted_class_softmax_score","top_k_predictions","input_dimensions","preprocessing_config","inference_status"}
 assert required.issubset(r)
 assert r["inference_status"]=="success" and r["freshness_label"] in {"Fresh","Rotten"}
 assert r["input_dimensions"]["width"]>0 and r["input_dimensions"]["height"]>0
 s=r["raw_predicted_class_softmax_score"]
 assert math.isfinite(s) and 0<=s<=1
 assert len(r["top_k_predictions"])>0
 for x in r["top_k_predictions"]:
  assert x["freshness_label"] in {"Fresh","Rotten"}
  assert math.isfinite(x["raw_softmax_score"]) and 0<=x["raw_softmax_score"]<=1

def main():
 started=time.perf_counter(); outcomes=[]
 def run(name,fn):
  t=time.perf_counter()
  try:
   details=fn() or {}
   outcomes.append({"name":name,"status":"PASS","elapsed_seconds":round(time.perf_counter()-t,6),"details":details})
  except Exception as e: outcomes.append({"name":name,"status":"FAIL","elapsed_seconds":round(time.perf_counter()-t,6),"error":f"{type(e).__name__}: {e}"})
 before_file=OUT/"artifact_hashes_before.json"
 before=json.loads(before_file.read_text(encoding="utf-8"))
 candidate=None; baseline=None
 with tempfile.TemporaryDirectory(prefix="phase03_smoke_",dir=OUT) as temp_name:
  temp=Path(temp_name); paths=[]
  for i,(w,h) in enumerate(((160,80),(80,160),(96,96)),1):
   im=Image.new("RGB",(w,h),(40+i*25,110,170))
   draw=ImageDraw.Draw(im); draw.rectangle((w//5,h//4,w*4//5,h*3//4),fill=(220,90,35))
   p=temp/f"synthetic_{i}.png"; im.save(p,format="PNG"); paths.append(p)
  def load_candidate():
   nonlocal candidate
   candidate=load_predictor("candidate")
   assert candidate.device=="cpu" and len(candidate.class_to_idx)==20
   return {"model_name":candidate.model_name,"classes":len(candidate.class_to_idx),"device":candidate.device}
  run("candidate_checkpoint_load",load_candidate)
  def single():
   assert candidate is not None
   r=candidate.predict_one(paths[0]); check_result(r)
   assert r["input_dimensions"]=={"width":160,"height":80}
   assert r["preprocessing_config"]["padding_rgb"]==[127,127,127]
   return {"input_dimensions":r["input_dimensions"],"model_version":r["model_version"]}
  run("candidate_single_image_inference",single)
  def batch():
   assert candidate is not None
   rs=candidate.predict_batch(paths,top_k=5)
   assert len(rs)==3
   for r in rs: check_result(r)
   return {"prediction_count":len(rs)}
  run("candidate_batch_inference",batch)
  def structure_topk():
   assert candidate is not None
   r=candidate.predict_one(paths[1],top_k=100); check_result(r)
   assert len(r["top_k_predictions"])==20
   return {"required_fields_present":True,"top_k_clamped_to":20}
  run("output_structure_and_top_k_limit",structure_topk)
  def mapping():
   assert candidate is not None
   assert candidate.idx_to_class=={i:n for n,i in candidate.class_to_idx.items()}
   assert set(candidate.class_to_idx.values())==set(range(20))
   assert all(n.startswith(("Fresh","Rotten")) for n in candidate.class_to_idx)
   return {"mapping_size":20,"class_names_parseable":True}
  run("candidate_class_mapping",mapping)
  def scores():
   assert candidate is not None
   r=candidate.predict_one(paths[2],top_k=20); check_result(r)
   assert abs(sum(x["raw_softmax_score"] for x in r["top_k_predictions"])-1)<1e-5
   return {"finite_and_in_range":True,"all_class_scores_sum":1.0}
  run("finite_score_range",scores)
  def missing():
   assert candidate is not None
   try: candidate.predict_one(temp/"absent.png")
   except FileNotFoundError: return {"exception":"FileNotFoundError"}
   raise AssertionError("Missing path did not raise FileNotFoundError")
  run("missing_image_handling",missing)
  invalid=temp/"invalid.png"; invalid.write_bytes(b"not an image")
  def bad_image():
   assert candidate is not None
   try: candidate.predict_one(invalid)
   except ValueError: return {"exception":"ValueError"}
   raise AssertionError("Invalid image did not raise ValueError")
  run("invalid_image_handling",bad_image)
  def parity():
   assert candidate is not None
   a=candidate.predict_one(paths[0],top_k=5)
   b=candidate.predict_batch([paths[0]],top_k=5)[0]
   assert a["predicted_class_name"]==b["predicted_class_name"]
   assert a["top_k_predictions"]==b["top_k_predictions"]
   assert a["preprocessing_config"]==b["preprocessing_config"]
   return {"identical_prediction_and_preprocessing":True}
  run("single_batch_equivalence",parity)
  def load_baseline():
   nonlocal baseline
   baseline=load_predictor("baseline")
   r=baseline.predict_one(paths[0],top_k=3); check_result(r)
   assert baseline.preprocessing["padding_rgb"] is None
   assert baseline.policy=="stretch"
   return {"model_name":baseline.model_name,"inference":"PASS"}
  run("baseline_load_and_inference",load_baseline)
  def cpu_repeat():
   assert candidate is not None
   a=candidate.predict_one(paths[2],top_k=5); b=candidate.predict_one(paths[2],top_k=5)
   assert candidate.device=="cpu" and not torch.cuda.is_available()
   assert a["top_k_predictions"]==b["top_k_predictions"]
   return {"device":"cpu","repeated_scores_identical":True}
  run("cpu_reproducibility",cpu_repeat)
 # Hash after tests; paths are the direct baseline/candidate files only.
 groups={}; integrity="PASS"
 for group,entries in before["artifacts"].items():
  groups[group]={}
  for name,info in entries.items():
   p=Path(info["path"]); actual=sha256(p); same=actual==info["sha256"]
   groups[group][name]={"unchanged":same,"sha256_after":actual}
   if not same: integrity="FAIL"
 after=new_path(OUT/"artifact_hashes_after.json")
 after.write_text(json.dumps({"verified_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":integrity,"groups":groups},indent=2),encoding="utf-8")
 report={"generated_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"scope":"Synthetic-image functional checks only; no prepared dataset or held-out test image/label accessed.","environment":{"python":platform.python_version(),"pytorch":str(torch.__version__),"pillow":Image.__version__,"device":"CPU","cuda_available":torch.cuda.is_available(),"numpy_bridge_used":False},"tests":outcomes,"artifact_integrity":{"status":integrity,"report_file":str(after)},"passed":sum(x["status"]=="PASS" for x in outcomes),"failed":sum(x["status"]=="FAIL" for x in outcomes),"total_elapsed_seconds":round(time.perf_counter()-started,6)}
 report_path=new_path(OUT/"smoke_test_report.json"); report["report_file"]=str(report_path)
 report_path.write_text(json.dumps(report,indent=2),encoding="utf-8")
 print(json.dumps(report,indent=2))
 return 0 if report["failed"]==0 and integrity=="PASS" else 1
if __name__=="__main__": raise SystemExit(main())