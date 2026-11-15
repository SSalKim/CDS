"""Seasonal precipitation exports; standalone panels share pixels with both layouts."""
import hashlib
from pathlib import Path
from PIL import Image
from .chart_style import winter_season

COMPONENTS={"acptot":("acptot_rain","acptot_snow","acptot_snowdepth"),
            "acrain":("acrain_rain","acrain_snow","acrain_snowdepth")}


def precipitation_plan(model,cycle,domain):
    if domain=="asia":
        return {"surfce":("surfce",)}
    winter=winter_season(cycle) and model in {"aifs","gfs","cmc"}
    plan={"surfce":("surfce",)}
    for product,components in COMPONENTS.items():
        chosen=components if winter else components[:1]
        plan[product]=chosen
        plan[product+"1"]=chosen
    return plan


def compose_panels(paths,target,*,vertical):
    paths=[Path(path) for path in paths]
    if not paths or len(paths) not in (1,3):
        raise ValueError("Precipitation exports require exactly one or three panels")
    panels=[]
    for path in paths:
        with Image.open(path) as source:
            panels.append(source.convert("RGB"))
    width,height=panels[0].size
    if any(image.size!=(width,height) for image in panels):
        raise ValueError("All precipitation panels must have identical dimensions")
    size=(width,height*len(panels)) if vertical else (width*len(panels),height)
    canvas=Image.new("RGB",size,"white")
    for index,panel in enumerate(panels):
        canvas.paste(panel,(0,index*height) if vertical else (index*width,0))
    target=Path(target)
    target.parent.mkdir(parents=True,exist_ok=True)
    temporary=target.with_suffix(".tmp")
    canvas.save(temporary,format="PNG")
    temporary.replace(target)
    return {"size":list(size),"panels":len(panels),"orientation":"vertical" if vertical else "horizontal",
            "panel_sha256":[hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]}
