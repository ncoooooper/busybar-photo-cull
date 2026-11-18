"""Contact-sheet browser with a saved selection. Original photographs are read only."""
import hashlib,json,os
from pathlib import Path
from PIL import Image,ImageOps
class Session:
    def __init__(self,folder):
        if not folder.is_dir():raise ValueError("Choose a photo folder")
        self.folder=folder;self.files=sorted((p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in (".jpg",".jpeg",".png",".tif",".tiff",".webp",".bmp")),key=lambda p:p.name.casefold())
        if not self.files:raise ValueError("No supported photographs in this folder")
        self.at=0;self.state=folder/".busybar-photo-selection.json";self.export=folder/"busybar-selection.txt";self.notice="Wheel: photo / Click: select";self.cache={}
        self.kept=set(json.loads(self.state.read_text()) if self.state.is_file() else []);self.kept.intersection_update(p.name for p in self.files)
    def replace(self,file,text):
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile("w",encoding="utf-8",dir=self.folder,delete=False) as f:f.write(text);temp=Path(f.name)
        try:os.replace(temp,file)
        finally:temp.unlink(missing_ok=True)
    def action(self,key):
        name=self.files[self.at].name
        if key in ("up","down"):self.at=(self.at+(1 if key=="up" else -1))%len(self.files);self.notice="Wheel: photo / Click: select"
        elif key=="ok":
            kept=self.kept.symmetric_difference([name]);self.replace(self.state,json.dumps(sorted(kept),ensure_ascii=False));self.kept=kept;self.notice="Selected" if name in kept else "Unselected"
        elif key=="start":
            self.replace(self.export,"".join(p.name+"\n" for p in self.files if p.name in self.kept));self.notice="Saved busybar-selection.txt"
    def thumb(self,path):
        key=(path.name,path.stat().st_mtime_ns)
        if key not in self.cache:
            with Image.open(path) as raw:
                im=ImageOps.contain(ImageOps.exif_transpose(raw).convert("RGB"),(40,16));canvas=Image.new("RGB",(40,16));canvas.paste(im,((40-im.width)//2,(16-im.height)//2))
                pic=canvas.quantize(colors=8,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE);pal=pic.getpalette()
                colors=["#%02X%02X%02X"%tuple(pal[3*i:3*i+3]) for i in range(8)];pixels=list(pic.getdata());rows=["".join(str(v) for v in pixels[y*40:y*40+40]) for y in range(16)]
            if len(self.cache)>15:self.cache.clear()
            self.cache[key]="\n".join(["! XPM2","40 16 8 1",*[str(i)+" c "+c for i,c in enumerate(colors)],*rows])
        return self.cache[key]
    def snapshot(self):
        p=self.files[self.at];bitmap=self.thumb(p);yes=p.name in self.kept
        return dict(caption="KEEP" if yes else "SHOT",value=str(self.at+1),bitmap=bitmap,lines=[p.name[:27],f"Photo {self.at+1} of {len(self.files)}",f"{len(self.kept)} marked for export",self.notice,"Start: export list"],version=str(self.at)+"/"+str(yes))
