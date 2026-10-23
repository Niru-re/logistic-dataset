import csv,json,os,platform,random,time,ctypes,ctypes.wintypes
from collections import defaultdict
from pathlib import Path
from PIL import Image,ImageOps
import torch
from torch import nn
from torch.utils.data import Dataset,DataLoader
DATASET_ROOT=Path(r"C:\Users\nirma\OneDrive\Desktop\logistic\datasets\Fruits-Vegetables-Dataset-main\Fruits-Vegetables-Dataset-main\split_dataset")
MANIFEST=Path(r"C:\Users\nirma\OneDrive\Desktop\logistic\datasets\prepared\fresh_rotten_v1\dataset_manifest.csv")
OUTPUT=Path(__file__).resolve().parent
SEED=2048;IMAGE_SIZE=96;BATCH_SIZE=16;MAX_EPOCHS=12;PATIENCE=4;LEARNING_RATE=.001;WEIGHT_DECAY=.0001;CPU_THREADS=2
def memory_gib():
 try:
  class MEM(ctypes.Structure):
   _fields_=[("dwLength",ctypes.wintypes.DWORD),("dwMemoryLoad",ctypes.wintypes.DWORD),("ullTotalPhys",ctypes.c_ulonglong),("ullAvailPhys",ctypes.c_ulonglong),("ullTotalPageFile",ctypes.c_ulonglong),("ullAvailPageFile",ctypes.c_ulonglong),("ullTotalVirtual",ctypes.c_ulonglong),("ullAvailVirtual",ctypes.c_ulonglong),("ullAvailExtendedVirtual",ctypes.c_ulonglong)]
  s=MEM();s.dwLength=ctypes.sizeof(s)
  if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s)):return None
  return {"total_gib":round(s.ullTotalPhys/1024**3,2),"available_gib":round(s.ullAvailPhys/1024**3,2)}
 except Exception:return None
def tensor_from_pil(image):
 image=image.convert("RGB")
 scale=min(IMAGE_SIZE/image.width,IMAGE_SIZE/image.height)
 resized=(max(1,round(image.width*scale)),max(1,round(image.height*scale)))
 image=image.resize(resized,Image.Resampling.BILINEAR)
 canvas=Image.new("RGB",(IMAGE_SIZE,IMAGE_SIZE),(127,127,127))
 canvas.paste(image,((IMAGE_SIZE-image.width)//2,(IMAGE_SIZE-image.height)//2))
 raw=bytearray(canvas.tobytes());tensor=torch.frombuffer(raw,dtype=torch.uint8).reshape(IMAGE_SIZE,IMAGE_SIZE,3)
 tensor=tensor.permute(2,0,1).contiguous().float().div_(255.)
 return tensor.sub_(.5).div_(.5)
class ManifestImages(Dataset):
 def __init__(self,rows,class_to_idx,augment):self.rows=rows;self.class_to_idx=class_to_idx;self.augment=augment
 def __len__(self):return len(self.rows)
 def __getitem__(self,index):
  row=self.rows[index];path=DATASET_ROOT.joinpath(*row["relative_path"].split("/"))
  with Image.open(path) as im:image=im.convert("RGB")
  if self.augment and random.random()<.5:image=ImageOps.mirror(image)
  return tensor_from_pil(image),self.class_to_idx[row["class"]]
class SmallCNN(nn.Module):
 def __init__(self,nclasses):
  super().__init__()
  self.features=nn.Sequential(nn.Conv2d(3,24,3,padding=1,bias=False),nn.BatchNorm2d(24),nn.ReLU(inplace=True),nn.MaxPool2d(2),nn.Conv2d(24,48,3,padding=1,bias=False),nn.BatchNorm2d(48),nn.ReLU(inplace=True),nn.MaxPool2d(2),nn.Conv2d(48,96,3,padding=1,bias=False),nn.BatchNorm2d(96),nn.ReLU(inplace=True),nn.MaxPool2d(2),nn.Conv2d(96,128,3,padding=1,bias=False),nn.BatchNorm2d(128),nn.ReLU(inplace=True),nn.AdaptiveAvgPool2d((1,1)))
  self.head=nn.Sequential(nn.Flatten(),nn.Dropout(.25),nn.Linear(128,nclasses))
 def forward(self,x):return self.head(self.features(x))
def metrics_from_confusion(conf):
 n=len(conf);support=[sum(conf[i]) for i in range(n)];per=[];recalls=[];f1s=[]
 for i in range(n):
  tp=conf[i][i];fp=sum(conf[j][i] for j in range(n))-tp;fn=support[i]-tp
  precision=tp/(tp+fp) if tp+fp else 0.;recall=tp/(tp+fn) if tp+fn else 0.;f1=2*precision*recall/(precision+recall) if precision+recall else 0.
  per.append({"class_index":i,"support":support[i],"precision":precision,"recall":recall,"f1":f1});recalls.append(recall);f1s.append(f1)
 return {"macro_f1":sum(f1s)/n,"balanced_accuracy":sum(recalls)/n,"per_class":per}
def run_epoch(model,loader,criterion,optimizer=None):
 training=optimizer is not None;model.train(training);running_loss=0.;seen=0
 confusion=[[0 for _ in range(len(class_to_idx))] for _ in range(len(class_to_idx))]
 with (torch.enable_grad() if training else torch.no_grad()):
  for inputs,targets in loader:
   inputs=inputs.to("cpu");targets=targets.to("cpu")
   if training:optimizer.zero_grad(set_to_none=True)
   logits=model(inputs);loss=criterion(logits,targets)
   if training:loss.backward();optimizer.step()
   batch=targets.size(0);running_loss+=float(loss.item())*batch;seen+=batch
   for truth,guess in zip(targets.tolist(),logits.argmax(dim=1).tolist()):confusion[truth][guess]+=1
 if not seen:raise RuntimeError("Loader produced zero samples")
 return running_loss/seen,metrics_from_confusion(confusion),confusion,seen
def save_json(path,obj):
 with path.open("w",encoding="utf-8") as f:json.dump(obj,f,indent=2,ensure_ascii=False)
def main():
 global class_to_idx
 started=time.perf_counter();random.seed(SEED);torch.manual_seed(SEED);torch.set_num_threads(CPU_THREADS);torch.use_deterministic_algorithms(True)
 if torch.cuda.is_available():raise RuntimeError("Unexpected CUDA availability; script expects CPU")
 with MANIFEST.open(newline="",encoding="utf-8-sig") as f:all_rows=list(csv.DictReader(f))
 train_rows=[r for r in all_rows if r["assigned_split"]=="train"];val_rows=[r for r in all_rows if r["assigned_split"]=="validation"]
 classes=sorted({r["class"] for r in train_rows+val_rows},key=str.casefold);class_to_idx={name:i for i,name in enumerate(classes)}
 if len(train_rows)!=7497 or len(val_rows)!=1876 or len(classes)!=20:raise RuntimeError(f"Manifest mismatch: train={len(train_rows)} val={len(val_rows)} classes={len(classes)}")
 if set(r["class"] for r in train_rows)!=set(classes) or set(r["class"] for r in val_rows)!=set(classes):raise RuntimeError("Class missing from training or validation split")
 for row in train_rows+val_rows:
  if not DATASET_ROOT.joinpath(*row["relative_path"].split("/")).is_file():raise FileNotFoundError(row["relative_path"])
 gen=torch.Generator();gen.manual_seed(SEED)
 train_loader=DataLoader(ManifestImages(train_rows,class_to_idx,True),batch_size=BATCH_SIZE,shuffle=True,num_workers=0,generator=gen,drop_last=False)
 val_loader=DataLoader(ManifestImages(val_rows,class_to_idx,False),batch_size=BATCH_SIZE,shuffle=False,num_workers=0,drop_last=False)
 model=SmallCNN(len(classes)).to("cpu");criterion=nn.CrossEntropyLoss()
 optimizer=torch.optim.AdamW(model.parameters(),lr=LEARNING_RATE,weight_decay=WEIGHT_DECAY)
 scheduler=torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer,mode="min",factor=.5,patience=1,min_lr=1e-5)
 config={"task":"20-class Fresh/Rotten produce image classification","dataset_manifest":str(MANIFEST),"dataset_root":str(DATASET_ROOT),"train_samples":len(train_rows),"validation_samples":len(val_rows),"test_split_used":False,"class_to_idx":class_to_idx,"model":"SmallCNN from scratch; Conv-BN-ReLU channels 24/48/96/128; adaptive average pooling; dropout 0.25","input_size":[3,IMAGE_SIZE,IMAGE_SIZE],"resize":"PIL bilinear RGB; aspect-preserving fit within 96x96, center-pad RGB(127,127,127)","augmentation":"random horizontal mirror on training split only","batch_size":BATCH_SIZE,"max_epochs":MAX_EPOCHS,"early_stopping_patience":PATIENCE,"optimizer":"AdamW","learning_rate":LEARNING_RATE,"weight_decay":WEIGHT_DECAY,"loss":"cross_entropy","seed":SEED,"deterministic_algorithms":True,"cpu_threads":CPU_THREADS,"num_workers":0}
 save_json(OUTPUT/"training_config.json",config);save_json(OUTPUT/"class_to_idx.json",class_to_idx)
 best_loss=float("inf");best_epoch=0;stale=0;history=[]
 for epoch in range(1,MAX_EPOCHS+1):
  et=time.perf_counter();tl,tm,_,tn=run_epoch(model,train_loader,criterion,optimizer);vl,vm,vc,vn=run_epoch(model,val_loader,criterion,None)
  if tn!=len(train_rows) or vn!=len(val_rows):raise RuntimeError(f"Data loading mismatch: {tn}/{len(train_rows)} train, {vn}/{len(val_rows)} validation")
  scheduler.step(vl);rec={"epoch":epoch,"train_loss":tl,"validation_loss":vl,"train_macro_f1":tm["macro_f1"],"train_balanced_accuracy":tm["balanced_accuracy"],"validation_macro_f1":vm["macro_f1"],"validation_balanced_accuracy":vm["balanced_accuracy"],"learning_rate":optimizer.param_groups[0]["lr"],"epoch_seconds":time.perf_counter()-et};history.append(rec)
  with (OUTPUT/"epoch_metrics.csv").open("w",newline="",encoding="utf-8") as f:
   w=csv.DictWriter(f,fieldnames=list(history[0]));w.writeheader();w.writerows(history)
  print(json.dumps(rec),flush=True)
  if vl<best_loss:
   best_loss=vl;best_epoch=epoch;stale=0;torch.save({"epoch":epoch,"model_state_dict":model.state_dict(),"class_to_idx":class_to_idx,"config":config,"best_validation_loss":best_loss},OUTPUT/"best_checkpoint.pt")
  else:
   stale+=1
  if stale>=PATIENCE:print(f"Early stopping at epoch {epoch}; best epoch {best_epoch}",flush=True);break
 if not best_epoch:raise RuntimeError("Best checkpoint was not produced")
 payload=torch.load(OUTPUT/"best_checkpoint.pt",map_location="cpu",weights_only=False);model.load_state_dict(payload["model_state_dict"])
 fl,fm,fc,fn=run_epoch(model,val_loader,criterion,None)
 if fn!=len(val_rows):raise RuntimeError("Final validation pass did not cover all rows")
 validation={"best_epoch":best_epoch,"validation_loss":fl,"macro_f1":fm["macro_f1"],"balanced_accuracy":fm["balanced_accuracy"],"per_class":[{"class":classes[x["class_index"]],**{k:v for k,v in x.items() if k!="class_index"}} for x in fm["per_class"]],"confusion_matrix":fc,"class_order":classes}
 save_json(OUTPUT/"final_validation_metrics.json",validation)
 with (OUTPUT/"per_class_metrics.csv").open("w",newline="",encoding="utf-8") as f:
  fields=["class","support","precision","recall","f1"];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(validation["per_class"])
 with (OUTPUT/"confusion_matrix.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.writer(f);w.writerow(["true_class/predicted_class"]+classes)
  for cls,row in zip(classes,fc):w.writerow([cls]+row)
 elapsed=time.perf_counter()-started
 metadata={"run_status":"completed","duration_seconds":elapsed,"best_epoch":best_epoch,"epochs_completed":len(history),"train_samples_seen_per_epoch":len(train_rows),"validation_samples_seen_per_epoch":len(val_rows),"test_split_loaded_or_evaluated":False,"runtime":{"python":platform.python_version(),"pytorch":torch.__version__,"pillow":Image.__version__,"numpy_version":"2.2.6 (PyTorch NumPy bridge unavailable; training path avoids NumPy)","device":"CPU","cuda_available":False,"cpu":platform.processor(),"cpu_threads":torch.get_num_threads(),"ram_at_completion":memory_gib()},"limitations":["PyTorch reports a NumPy 1.x/2.2.6 ABI incompatibility and torch.from_numpy is unavailable; training uses PIL bytes and torch.frombuffer, which passed smoke testing.","GPU/VRAM and driver were unavailable; CUDA reports unavailable.","Labels are folder-derived class names; dataset provenance and capture conditions are not independently established.","No held-out test evaluation was performed."]}
 metadata["experiment"]="Aspect-preserving 96x96 preprocessing comparison"; metadata["pre_registered_criteria"]=json.loads((OUTPUT/"experiment_protocol.json").read_text(encoding="utf-8"))["criteria"]; metadata["baseline_validation_macro_f1"]=0.810803044032772; metadata["baseline_validation_balanced_accuracy"]=0.8107859315314657; metadata["test_split_loaded_or_evaluated"]=False
 save_json(OUTPUT/"run_metadata.json",metadata)
 required=["train_aspect_preserving.py","best_checkpoint.pt","class_to_idx.json","training_config.json","epoch_metrics.csv","final_validation_metrics.json","per_class_metrics.csv","confusion_matrix.csv","run_metadata.json"]
 missing=[n for n in required if not (OUTPUT/n).is_file() or not (OUTPUT/n).stat().st_size]
 if missing:raise RuntimeError("Missing or empty artifacts: "+repr(missing))
 print(json.dumps({"completion":"completed","output":str(OUTPUT),"best_epoch":best_epoch,"epochs_completed":len(history),"duration_seconds":elapsed,"validation_loss":fl,"macro_f1":fm["macro_f1"],"balanced_accuracy":fm["balanced_accuracy"],"outputs":required},indent=2),flush=True)
if __name__=="__main__":main()
