import csv,json,hashlib,time,platform
from pathlib import Path
from collections import Counter
from PIL import Image
import torch
from torch import nn
from torch.utils.data import Dataset,DataLoader
MODEL_DIR=Path(r"C:\Users\nirma\OneDrive\Desktop\logistic\datasets\trained_models\fresh_rotten_v1")
PREP_DIR=Path(r"C:\Users\nirma\OneDrive\Desktop\logistic\datasets\prepared\fresh_rotten_v1")
DATASET_ROOT=Path(r"C:\Users\nirma\OneDrive\Desktop\logistic\datasets\Fruits-Vegetables-Dataset-main\Fruits-Vegetables-Dataset-main\split_dataset")
OUTPUT=Path(__file__).resolve().parent
DEVICE=torch.device("cpu")
class SmallCNN(nn.Module):
 def __init__(self,n):
  super().__init__()
  self.features=nn.Sequential(nn.Conv2d(3,24,3,padding=1,bias=False),nn.BatchNorm2d(24),nn.ReLU(inplace=True),nn.MaxPool2d(2),nn.Conv2d(24,48,3,padding=1,bias=False),nn.BatchNorm2d(48),nn.ReLU(inplace=True),nn.MaxPool2d(2),nn.Conv2d(48,96,3,padding=1,bias=False),nn.BatchNorm2d(96),nn.ReLU(inplace=True),nn.MaxPool2d(2),nn.Conv2d(96,128,3,padding=1,bias=False),nn.BatchNorm2d(128),nn.ReLU(inplace=True),nn.AdaptiveAvgPool2d((1,1)))
  self.head=nn.Sequential(nn.Flatten(),nn.Dropout(.25),nn.Linear(128,n))
 def forward(self,x):return self.head(self.features(x))
def image_tensor(path,size):
 with Image.open(path) as im:
  im=im.convert("RGB").resize((size,size),Image.Resampling.BILINEAR);raw=bytearray(im.tobytes())
 x=torch.frombuffer(raw,dtype=torch.uint8).reshape(size,size,3).permute(2,0,1).contiguous().float().div_(255.)
 return x.sub_(.5).div_(.5)
class TestImages(Dataset):
 def __init__(self,rows,mapping,size):self.rows=rows;self.mapping=mapping;self.size=size
 def __len__(self):return len(self.rows)
 def __getitem__(self,i):
  r=self.rows[i]
  return image_tensor(DATASET_ROOT.joinpath(*r["relative_path"].split("/")),self.size),self.mapping[r["class"]]
def save_json(path,obj):
 with path.open("w",encoding="utf-8") as f:json.dump(obj,f,indent=2,ensure_ascii=False)
def main():
 if torch.cuda.is_available():raise RuntimeError("Unexpected CUDA availability; CPU evaluation expected")
 with (PREP_DIR/"dataset_manifest.csv").open(newline="",encoding="utf-8-sig") as f:allrows=list(csv.DictReader(f))
 with (MODEL_DIR/"training_config.json").open(encoding="utf-8") as f:config=json.load(f)
 with (MODEL_DIR/"class_to_idx.json").open(encoding="utf-8") as f:mapping=json.load(f)
 with (MODEL_DIR/"final_validation_metrics.json").open(encoding="utf-8") as f:val=json.load(f)
 rows=[r for r in allrows if r["assigned_split"]=="test"]
 classes=sorted({r["class"] for r in allrows if r["assigned_split"] in ("train","validation","test")},key=str.casefold)
 if len(rows)!=2408 or len(classes)!=20:raise RuntimeError(f"Unexpected test size/classes {len(rows)}/{len(classes)}")
 if mapping!={c:i for i,c in enumerate(classes)} or config["class_to_idx"]!=mapping:raise RuntimeError("Class mapping mismatch")
 if len({r["class"] for r in rows})!=20:raise RuntimeError("Test split missing a class")
 if val.get("best_epoch")!=12:raise RuntimeError("Validation reference does not match frozen epoch")
 hs={s:set() for s in ("train","validation","test")}
 for r in allrows:
  if r["assigned_split"] in hs:hs[r["assigned_split"]].add(r["sha256"])
 overlaps={f"{a}_{b}":len(hs[a]&hs[b]) for a,b in (("train","validation"),("train","test"),("validation","test"))}
 if any(overlaps.values()):raise RuntimeError(f"Manifest hash overlap: {overlaps}")
 size=config["input_size"][1];ck=torch.load(MODEL_DIR/"best_checkpoint.pt",map_location="cpu",weights_only=False)
 if ck["epoch"]!=12 or ck["class_to_idx"]!=mapping:raise RuntimeError("Checkpoint epoch/class mapping mismatch")
 model=SmallCNN(len(classes));model.load_state_dict(ck["model_state_dict"],strict=True);model.to(DEVICE).eval()
 batch=int(config["batch_size"]);loader=DataLoader(TestImages(rows,mapping,size),batch_size=batch,shuffle=False,num_workers=0,drop_last=False)
 conf=[[0 for _ in classes] for _ in classes];seen=0;correct=0;started=time.perf_counter()
 with torch.inference_mode():
  for images,targets in loader:
   preds=model(images.to(DEVICE)).argmax(dim=1).tolist();truth=targets.tolist()
   for t,p in zip(truth,preds):conf[t][p]+=1;correct+=int(t==p)
   seen+=len(truth)
   if seen%512==0:print(f"inferred {seen}/{len(rows)} test images",flush=True)
 elapsed=time.perf_counter()-started
 if seen!=len(rows):raise RuntimeError(f"Test loader count mismatch {seen}/{len(rows)}")
 support=[sum(conf[i]) for i in range(len(classes))];per=[];recalls=[];f1s=[]
 for i,c in enumerate(classes):
  tp=conf[i][i];fp=sum(conf[j][i] for j in range(len(classes)))-tp;fn=support[i]-tp
  p=tp/(tp+fp) if tp+fp else 0.;r=tp/(tp+fn) if tp+fn else 0.;f=2*p*r/(p+r) if p+r else 0.
  per.append({"class":c,"support":support[i],"precision":p,"recall":r,"f1":f});recalls.append(r);f1s.append(f)
 bad=[]
 for i,t in enumerate(classes):
  for j,p in enumerate(classes):
   if i!=j and conf[i][j]:bad.append({"true_class":t,"predicted_class":p,"count":conf[i][j]})
 bad.sort(key=lambda x:(-x["count"],x["true_class"],x["predicted_class"]))
 acc=correct/seen;macro=sum(f1s)/len(classes);bal=sum(recalls)/len(classes)
 v={"loss":val["validation_loss"],"macro_f1":val["macro_f1"],"balanced_accuracy":val["balanced_accuracy"]}
 metrics={"evaluation":"independent held-out test evaluation","checkpoint_epoch":ck["epoch"],"samples":seen,"classes":classes,"class_to_idx":mapping,"accuracy_top1":acc,"macro_f1":macro,"balanced_accuracy":bal,"validation_reference":v,"test_minus_validation":{"macro_f1":macro-v["macro_f1"],"balanced_accuracy":bal-v["balanced_accuracy"]},"per_class":per,"confusion_matrix":conf,"confusion_matrix_class_order":classes,"misclassification_total":seen-correct,"top_confusions":bad[:20],"all_nonzero_confusions":bad,"test_used_for_inference_only":True,"test_used_for_model_selection":False,"inference_seconds":elapsed}
 save_json(OUTPUT/"test_metrics.json",metrics)
 with (OUTPUT/"per_class_report.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=["class","support","precision","recall","f1"]);w.writeheader();w.writerows(per)
 with (OUTPUT/"confusion_matrix.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.writer(f);w.writerow(["true_class/predicted_class"]+classes)
  for c,row in zip(classes,conf):w.writerow([c]+row)
 with (OUTPUT/"class_confusions.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=["true_class","predicted_class","count"]);w.writeheader();w.writerows(bad)
 checkpoint_hash=hashlib.sha256((MODEL_DIR/"best_checkpoint.pt").read_bytes()).hexdigest()
 manifest_hash=hashlib.sha256((PREP_DIR/"dataset_manifest.csv").read_bytes()).hexdigest()
 summary=["# Fresh/Rotten baseline - held-out test evaluation","",f"- Frozen checkpoint epoch {ck['epoch']}; SHA-256: {checkpoint_hash}.",f"- Test set: {seen} images across {len(classes)} classes; all test images loaded successfully.",f"- Top-1 accuracy: {acc:.4f}.",f"- Macro-F1: {macro:.4f} (validation {v['macro_f1']:.4f}; delta {macro-v['macro_f1']:+.4f}).",f"- Balanced accuracy: {bal:.4f} (validation {v['balanced_accuracy']:.4f}; delta {bal-v['balanced_accuracy']:+.4f}).",f"- Misclassified {seen-correct}/{seen}; inference time {elapsed:.1f} seconds.",f"- Manifest SHA-256: {manifest_hash}; cross-split hash-overlap counts: {overlaps}.","- Test data was used for inference/reporting only, not training, checkpoint selection, or hyperparameter selection.","- No pre-existing acceptance thresholds were documented; no acceptance conclusion is inferred from these metrics.","- Dataset label provenance and deployment-domain representativeness remain unverified.","","See test_metrics.json, per_class_report.csv, confusion_matrix.csv, and class_confusions.csv for detailed results."]
 (OUTPUT/"evaluation_summary.md").write_text("\n".join(summary)+"\n",encoding="utf-8")
 meta={"evaluation_status":"completed","runtime":{"python":platform.python_version(),"pytorch":torch.__version__,"device":"CPU","cuda_available":False,"num_workers":0,"batch_size":batch,"input_size":size,"numpy_bridge_used":False},"checkpoint":{"path":str(MODEL_DIR/"best_checkpoint.pt"),"sha256":checkpoint_hash,"epoch":ck["epoch"]},"manifest":{"path":str(PREP_DIR/"dataset_manifest.csv"),"sha256":manifest_hash},"test_inference_count":seen,"hash_overlap_counts":overlaps,"duration_seconds":elapsed}
 save_json(OUTPUT/"evaluation_metadata.json",meta)
 required=["evaluate_test.py","test_metrics.json","per_class_report.csv","confusion_matrix.csv","class_confusions.csv","evaluation_summary.md","evaluation_metadata.json"]
 missing=[x for x in required if not (OUTPUT/x).is_file() or not (OUTPUT/x).stat().st_size]
 if missing:raise RuntimeError("Missing/empty outputs: "+repr(missing))
 print(json.dumps({"status":"completed","output":str(OUTPUT),"samples":seen,"accuracy_top1":acc,"macro_f1":macro,"balanced_accuracy":bal,"validation":v,"misclassification_total":seen-correct,"top_confusions":bad[:12],"inference_seconds":elapsed,"outputs":required},indent=2),flush=True)
if __name__=="__main__":main()
