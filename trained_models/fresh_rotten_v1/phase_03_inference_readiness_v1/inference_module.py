from __future__ import annotations
import json, math, re
from pathlib import Path
from typing import Any, Sequence
import torch
from PIL import Image, UnidentifiedImageError
from torch import nn

ARTIFACT_ROOT=Path(r"C:\Users\nirma\OneDrive\Desktop\logistic\datasets\trained_models\fresh_rotten_v1")
ARTIFACTS={
 "baseline":{"name":"fresh_rotten_v1_baseline","root":ARTIFACT_ROOT,"checkpoint":ARTIFACT_ROOT/"best_checkpoint.pt","mapping":ARTIFACT_ROOT/"class_to_idx.json","config":ARTIFACT_ROOT/"training_config.json","script":ARTIFACT_ROOT/"train_baseline.py","policy":"stretch","resize":"PIL bilinear RGB"},
 "candidate":{"name":"fresh_rotten_v1_aspect_preserving_96_experiment_v1","root":ARTIFACT_ROOT/"aspect_preserving_96_experiment_v1","checkpoint":ARTIFACT_ROOT/"aspect_preserving_96_experiment_v1"/"best_checkpoint.pt","mapping":ARTIFACT_ROOT/"aspect_preserving_96_experiment_v1"/"class_to_idx.json","config":ARTIFACT_ROOT/"aspect_preserving_96_experiment_v1"/"training_config.json","script":ARTIFACT_ROOT/"aspect_preserving_96_experiment_v1"/"train_aspect_preserving.py","policy":"aspect_preserving","resize":"PIL bilinear RGB; aspect-preserving fit within 96x96, center-pad RGB(127,127,127)"},
}
class SmallCNN(nn.Module):
 def __init__(self,nclasses:int):
  super().__init__()
  self.features=nn.Sequential(
   nn.Conv2d(3,24,3,padding=1,bias=False),nn.BatchNorm2d(24),nn.ReLU(inplace=True),nn.MaxPool2d(2),
   nn.Conv2d(24,48,3,padding=1,bias=False),nn.BatchNorm2d(48),nn.ReLU(inplace=True),nn.MaxPool2d(2),
   nn.Conv2d(48,96,3,padding=1,bias=False),nn.BatchNorm2d(96),nn.ReLU(inplace=True),nn.MaxPool2d(2),
   nn.Conv2d(96,128,3,padding=1,bias=False),nn.BatchNorm2d(128),nn.ReLU(inplace=True),nn.AdaptiveAvgPool2d((1,1)))
  self.head=nn.Sequential(nn.Flatten(),nn.Dropout(.25),nn.Linear(128,nclasses))
 def forward(self,x): return self.head(self.features(x))

def _details(name:str)->tuple[str,str]:
 m=re.fullmatch(r"(Fresh|Rotten)(.+)",name)
 if not m: raise ValueError(f"Unparseable verified class name: {name!r}")
 return m.group(2),m.group(1)

def _read_mapping(path:Path)->dict[str,int]:
 try: raw=json.loads(path.read_text(encoding="utf-8"))
 except Exception as e: raise ValueError(f"Cannot read class mapping {path}: {e}") from e
 if not isinstance(raw,dict) or not raw or any(not isinstance(k,str) or isinstance(v,bool) or not isinstance(v,int) for k,v in raw.items()):
  raise ValueError(f"Invalid class mapping: {path}")
 mapping={k:int(v) for k,v in raw.items()}
 if sorted(mapping.values())!=list(range(len(mapping))): raise ValueError("Class indices must be contiguous from zero.")
 for name in mapping: _details(name)
 return mapping

def _preprocess(image:Image.Image,policy:str)->torch.Tensor:
 image=image.convert("RGB")
 if policy=="stretch":
  image=image.resize((96,96),Image.Resampling.BILINEAR)
 elif policy=="aspect_preserving":
  scale=min(96/image.width,96/image.height)
  size=(max(1,round(image.width*scale)),max(1,round(image.height*scale)))
  image=image.resize(size,Image.Resampling.BILINEAR)
  canvas=Image.new("RGB",(96,96),(127,127,127))
  canvas.paste(image,((96-image.width)//2,(96-image.height)//2))
  image=canvas
 else: raise ValueError(f"Unsupported preprocessing policy: {policy}")
 raw=bytearray(image.tobytes())
 x=torch.frombuffer(raw,dtype=torch.uint8).reshape(96,96,3)
 x=x.permute(2,0,1).contiguous().to(dtype=torch.float32).div_(255.)
 x.sub_(.5).div_(.5)
 if tuple(x.shape)!=(3,96,96) or not bool(torch.isfinite(x).all()): raise ValueError("Invalid preprocessed tensor.")
 return x

def _preprocess_description(policy:str)->dict[str,Any]:
 return {"color_format":"RGB","output_dimensions":[96,96],"interpolation":"Pillow bilinear","normalization":"float32 [0,1], then (x - 0.5) / 0.5, approximately [-1,1]","resize_policy":"Direct stretch to square 96x96." if policy=="stretch" else "Aspect-preserving fit inside 96x96; centered canvas.","padding_rgb":None if policy=="stretch" else [127,127,127]}

class Predictor:
 def __init__(self,version:str,artifact:dict,mapping:dict,model:SmallCNN):
  self.model_version=version; self.model_name=artifact["name"]
  self.checkpoint_path=artifact["checkpoint"].resolve()
  self.class_to_idx=dict(mapping); self.idx_to_class={i:n for n,i in mapping.items()}
  self.policy=artifact["policy"]; self.preprocessing=_preprocess_description(self.policy)
  self.device="cpu"; self.model=model.to("cpu").eval()

 def _load(self,value:str|Path):
  if not isinstance(value,(str,Path)): raise TypeError("Image input must be a string or pathlib.Path.")
  path=Path(value).expanduser()
  if not path.exists(): raise FileNotFoundError(f"Image file does not exist: {path}")
  if not path.is_file(): raise ValueError(f"Image input is not a regular file: {path}")
  try:
   with Image.open(path) as im:
    im.load(); width,height=im.size
    if width<1 or height<1: raise ValueError(f"Invalid image dimensions: {path}")
    tensor=_preprocess(im,self.policy)
  except (UnidentifiedImageError,OSError) as e: raise ValueError(f"Invalid or unsupported image {path}: {e}") from e
  return path.resolve(),{"width":width,"height":height},tensor

 def predict_one(self,image_path:str|Path,top_k:int=5)->dict[str,Any]:
  return self.predict_batch([image_path],top_k=top_k)[0]

 def predict_batch(self,image_paths:Sequence[str|Path],top_k:int=5,batch_size:int=8)->list[dict[str,Any]]:
  if isinstance(image_paths,(str,bytes,Path)) or not isinstance(image_paths,Sequence): raise TypeError("Batch input must be a sequence of image paths.")
  if isinstance(top_k,bool) or not isinstance(top_k,int) or top_k<1: raise ValueError("top_k must be a positive integer.")
  if isinstance(batch_size,bool) or not isinstance(batch_size,int) or batch_size<1: raise ValueError("batch_size must be a positive integer.")
  if not image_paths: return []
  loaded=[self._load(p) for p in image_paths]; results=[]; k=min(top_k,len(self.idx_to_class))
  for start in range(0,len(loaded),batch_size):
   chunk=loaded[start:start+batch_size]; batch=torch.stack([x[2] for x in chunk])
   with torch.inference_mode():
    logits=self.model(batch.to("cpu"))
    if logits.ndim!=2 or logits.shape[1]!=len(self.idx_to_class): raise RuntimeError("Output shape does not match class mapping.")
    scores=torch.softmax(logits,dim=1)
   if not bool(torch.isfinite(scores).all()) or bool(((scores<0)|(scores>1)).any()): raise RuntimeError("Invalid softmax scores.")
   vals,inds=torch.topk(scores,k=k,dim=1)
   for row,(path,dims,_) in enumerate(chunk):
    idx=int(inds[row,0].item()); name=self.idx_to_class[idx]; produce,freshness=_details(name)
    top=[]
    for score,class_idx in zip(vals[row].tolist(),inds[row].tolist()):
     cname=self.idx_to_class[int(class_idx)]; ptype,label=_details(cname); score=float(score)
     if not math.isfinite(score) or not 0<=score<=1: raise RuntimeError("Invalid top-k score.")
     top.append({"class_name":cname,"produce_type":ptype,"freshness_label":label,"raw_softmax_score":score})
    results.append({"input_identifier":str(path),"model_name":self.model_name,"model_version":self.model_version,"selected_checkpoint":str(self.checkpoint_path),"predicted_class_name":name,"produce_type":produce,"freshness_label":freshness,"raw_predicted_class_softmax_score":float(scores[row,idx].item()),"top_k_predictions":top,"input_dimensions":dims,"preprocessing_config":dict(self.preprocessing),"inference_status":"success"})
  return results

def load_predictor(model_version:str="candidate")->Predictor:
 if model_version not in ARTIFACTS: raise ValueError("model_version must be 'candidate' or 'baseline'.")
 a=ARTIFACTS[model_version]
 missing=[str(a[k]) for k in ("checkpoint","mapping","config","script") if not a[k].is_file()]
 if missing: raise FileNotFoundError("Missing model artifact(s): "+", ".join(missing))
 mapping=_read_mapping(a["mapping"])
 try: config=json.loads(a["config"].read_text(encoding="utf-8"))
 except Exception as e: raise ValueError(f"Cannot read training config: {e}") from e
 if config.get("class_to_idx")!=mapping: raise ValueError("Training config and sidecar mappings differ.")
 if config.get("input_size")!=[3,96,96] or config.get("resize")!=a["resize"]: raise ValueError("Checkpoint config does not match this inference pipeline.")
 source=a["script"].read_text(encoding="utf-8")
 required=["return tensor.sub_(.5).div_(.5)"]
 required += ["image=image.convert(\"RGB\").resize((IMAGE_SIZE,IMAGE_SIZE),Image.Resampling.BILINEAR)"] if model_version=="baseline" else ["image=image.resize(resized,Image.Resampling.BILINEAR)","Image.new(\"RGB\",(IMAGE_SIZE,IMAGE_SIZE),(127,127,127))"]
 if not all(token in source for token in required): raise ValueError("Training script preprocessing could not be verified.")
 try: ckpt=torch.load(a["checkpoint"],map_location="cpu",weights_only=False)
 except Exception as e: raise RuntimeError(f"Checkpoint load failed: {e}") from e
 if not isinstance(ckpt,dict) or "model_state_dict" not in ckpt: raise ValueError("Checkpoint lacks model_state_dict.")
 if ckpt.get("class_to_idx")!=mapping: raise ValueError("Checkpoint and sidecar class mappings differ.")
 saved=ckpt.get("config")
 if not isinstance(saved,dict) or saved.get("class_to_idx")!=mapping or saved.get("resize")!=a["resize"] or saved.get("input_size")!=[3,96,96]:
  raise ValueError("Checkpoint metadata is incompatible with configured preprocessing/mapping.")
 model=SmallCNN(len(mapping))
 try: model.load_state_dict(ckpt["model_state_dict"],strict=True)
 except Exception as e: raise ValueError(f"Checkpoint architecture mismatch: {e}") from e
 torch.set_num_threads(int(config.get("cpu_threads",2)))
 return Predictor(model_version,a,mapping,model)