import {surface,panel,label,type Frame,type Key} from "@shared/surface";
import {loadValues} from "@shared/settings";
type Data={caption:string;value:string;lines:string[];version:string;bitmap?:string;error?:string};
let addr="",closed=false,busy=false,reading:Data|undefined,failed=false;const commands:Key[]=[];
let timer:ReturnType<typeof setTimeout>|undefined;
function draw():Frame{
 const p=reading,frame:Frame=[];if(p?.bitmap){
   frame.push({id:"thumbnail",type:"xpmbitmap",data:p.bitmap,x:1,y:0,display:"front",align:"top_left"});
   frame.push(label("side",p.caption,51,0,"#90CAB0"+"FF","front","tiny"),label("n",p.value,52,6,"#FFF2D7FF","front","small"));
 }else frame.push(label("head",p?.caption||"Photo Cull",1,0,"#90CAB0"+"FF","front","tiny"),label("n",p?.value||(addr?"Offline":"Set URL"),1,6,"#FFF2D7FF"));
 return frame.concat(panel("Photo Cull".toUpperCase(),failed?["Companion unavailable",...(p?p.lines.slice(0,4):["Check host and local URL"])]:p?.lines||["Set companion URL in settings","Start the local reader"]));}
async function next(){
 if(!addr||busy||closed)return;if(timer!==undefined)clearTimeout(timer);timer=undefined;busy=true;
 const key=commands.shift();try{
 const res=await fetch(addr,key?{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({key})}:undefined);
 if(!res.ok)throw Error("HTTP "+res.status);const data=await res.json() as Data;if(data.error||typeof data.value!=="string"||!Array.isArray(data.lines))throw Error("Bad frame");
 const changed=!!reading&&reading.version!==data.version;reading=data;failed=false;if(!closed)refresh(changed?"change":undefined);
 }catch(e){failed=true;if(!closed)refresh();}finally{busy=false;if(!closed)timer=setTimeout(()=>{timer=undefined;void next();},commands.length?5:failed?1800:1400);}
}
const refresh=surface(draw,k=>{if(!addr)return;if(commands.length<32)commands.push(k);void next();},()=>{closed=true;if(timer!==undefined)clearTimeout(timer);},{enabled:false});
void loadValues().then(v=>{if(closed)return;addr=String(v?.bridge||"").trim();refresh();void next();});
