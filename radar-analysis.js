/* Radar analysis standalone page and sidebar launcher.
   Loop/cache patch: playback skips uncached frames, avoids background UI refresh while playing,
   and retries previously failed image loads during preload/current-frame requests. */

const RADAR_CMP_IMAGE_URL='https://radar.kma.go.kr/cgi-bin/nph-rdr_cmp_img';
const RADAR_SFC_PTY_IMAGE_URL='https://radar.kma.go.kr/cgi-bin/center/nph-rdr_sfc_pty_img';
const RADAR_R2D_HAIL_IMAGE_URL='https://radar.kma.go.kr/cgi-bin/nph-rdr_r2d_hail_img';
const RADAR_R2D_HAIL_ACC_IMAGE_URL='https://radar.kma.go.kr/cgi-bin/nph-rdr_r2d_hail_acc_img';
const RADAR_LGT_DST_IMAGE_URL='https://radar.kma.go.kr/cgi-bin/tablet2/nph-lgt_dst_img';
const RADAR_SFC_OBS_IMAGE_URL='https://radar.kma.go.kr/cgi-bin/tablet2/nph-sfc_obs_img';

const RADAR_DEFAULT_PARAMS={
tm:'',
cmp:'',
qcd:'',
obs:'',
acc:'',
map:'HR',
size:'800',
xp:'-9999',
yp:'-9999',
zoom:'1',
wv:'00',
ht:'1500',
color:'C4',
topo:'1',
highway:'0',
ZRa:'',
ZRb:'',
lat:'',
lon:'',
lonlat:'0',
x1:'',
y1:'',
x2:'',
y2:'',
itv:'',
center:'0',
gc:'',
gc_itv:'10',
dbzpair:'',
echo:'0',
typ:'0',
aws:'00',
wt:'0'
};

/*
Add radar products here.

Structure:
- level 1: source. Can override baseUrl and common params.
- level 2: provider/category. Can override params.
- level 3: product. Can override params or provide urlTemplate.

Example requested by user:
HSR -> 기상청 -> 에코 maps to cmp=HSP, qcd=KMA, obs=ECHD.
*/
const RADAR_PRODUCT_CATALOG=[
{
id:'HSP',
label:'HSR(최적)',
baseUrl:RADAR_CMP_IMAGE_URL,
params:{cmp:'HSP'},
defaultLevel2:'HSO',
children:[
    {
    id:'KMA',
    label:'기상청',
    params:{qcd:'KMA'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    },
    {
    id:'EXT',
    label:'+유관',
    params:{qcd:'EXT'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    },
    {
    id:'HSL',
    label:'+480km',
    params:{qcd:'HSL'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    },
    {
    id:'HSO',
    label:'+국외',
    params:{qcd:'HSO'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    }
]
},
{
id:'HSR',
label:'HSR',
baseUrl:RADAR_CMP_IMAGE_URL,
params:{cmp:'HSR'},
defaultLevel2:'HSO',
children:[
    {
    id:'KMA',
    label:'기상청',
    params:{qcd:'KMA'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    },
    {
    id:'EXT',
    label:'+유관',
    params:{qcd:'EXT'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    },
    {
    id:'HSL',
    label:'+480km',
    params:{qcd:'HSL'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    },
    {
    id:'HSO',
    label:'+국외',
    params:{qcd:'HSO'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    }
]
},
{
id:'PPI',
label:'PPI0',
baseUrl:RADAR_CMP_IMAGE_URL,
params:{cmp:'PPI'},
defaultLevel2:'EXT',
children:[
    {
    id:'NQC',
    label:'NoQC',
    params:{qcd:'NQC'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    },
    {
    id:'QCD',
    label:'QCed',
    params:{qcd:'QCD'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    },
    {
    id:'EXT',
    label:'+유관',
    params:{qcd:'EXT'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    }
]
},
{
id:'CPP',
label:'CAPPI',
baseUrl:RADAR_CMP_IMAGE_URL,
params:{cmp:'CPP'},
defaultLevel2:'EXT',
children:[
    {
    id:'NQC',
    label:'NoQC',
    params:{qcd:'NQC'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    },
    {
    id:'QCD',
    label:'QCed',
    params:{qcd:'QCD'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    },
    {
    id:'EXT',
    label:'+유관',
    params:{qcd:'EXT'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    }
]
},
{
id:'CMX',
label:'CMAX',
baseUrl:RADAR_CMP_IMAGE_URL,
params:{cmp:'CMX'},
defaultLevel2:'EXT',
children:[
    {
    id:'NQC',
    label:'NoQC',
    params:{qcd:'NQC'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    },
    {
    id:'QCD',
    label:'QCed',
    params:{qcd:'QCD'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    },
    {
    id:'EXT',
    label:'+유관',
    params:{qcd:'EXT'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    }
]
},
{
id:'PCPH',
label:'누적강수',
baseUrl:RADAR_CMP_IMAGE_URL,
params:{cmp:'PCPH'},
defaultLevel2:'EXT',
children:[
    {
    id:'KMA',
    label:'기상청',
    params:{qcd:'KMA'},
    children:[
        {id:'1H',label:'1H',params:{acc:'60'}},
        {id:'2H',label:'2H',params:{acc:'120'}},
        {id:'3H',label:'3H',params:{acc:'180'}},
        {id:'6H',label:'6H',params:{acc:'360'}},
        {id:'12H',label:'12H',params:{acc:'720'}},
        {id:'24H',label:'24H',params:{acc:'1440'}}
    ]
    },
    {
    id:'EXT',
    label:'+유관',
    params:{qcd:'EXT'},
    children:[
        {id:'1H',label:'1H',params:{acc:'60'}},
        {id:'2H',label:'2H',params:{acc:'120'}},
        {id:'3H',label:'3H',params:{acc:'180'}},
        {id:'6H',label:'6H',params:{acc:'360'}},
        {id:'12H',label:'12H',params:{acc:'720'}},
        {id:'24H',label:'24H',params:{acc:'1440'}}
    ]
    }
]
},


{
id:'SFC',
label:'지상',
baseUrl:RADAR_SFC_PTY_IMAGE_URL,
params:{cmp:'SFC'},
defaultLevel2:'RSRA',
children:[
    {
    id:'RNEX',
    label:'강수영역',
    params:{obs:'RNEX'}
    },
    {
    id:'RNSN',
    label:'눈비영역',
    children:[
        {id:'RNSN1',label:'최적',params:{obs:'RNSN1'}},
        {id:'RNSN2',label:'레이더',params:{obs:'RNSN2'}},
        {id:'RNSN',label:'+AWS',params:{obs:'RNSN'}}
    ]
    },
    {
    id:'RSRA',
    label:'눈비영역(종합)',
    params:{obs:'RSRA'}
    },
    {
    id:'SPOT',
    baseUrl:RADAR_CMP_IMAGE_URL,
    label:'강수정체(SPOT)',
    params:{cmp:'SPT', qcd:'KMA'}
    }
]
},

{
id:'HCI',
label:'수상체',
baseUrl:RADAR_CMP_IMAGE_URL,
params:{cmp:'HCI2'},
defaultLevel2:'EXT',
children:[
    {
    id:'KMA',
    label:'기상청',
    params:{qcd:'KMA'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    },
    {
    id:'EXT',
    label:'+유관',
    params:{qcd:'EXT'},
    children:[
        {id:'ECHD',label:'에코',params:{obs:'ECHD'}},
        {id:'EBH',label:'고도',params:{obs:'EBH2'}},
        {id:'STN',label:'사이트',params:{obs:'STN2'}}
    ]
    }
]
},

{
id:'PTY',
label:'밝은띠',
baseUrl:RADAR_CMP_IMAGE_URL,
params:{cmp:'PTY', obs:'ECHD'},
children:[
    {
    id:'QCD',
    label:'---',
    params:{qcd:'QCD'}
    }
]
},

{
id:'HAIL',
label:'우박',
baseUrl:RADAR_CMP_IMAGE_URL,
defaultLevel2:'HLSP',
children:[
    {
    id:'HAIL',
    label:'우박탐지',
    params:{cmp:'HAIL', obs:'ECHD'},
    defaultLevel3:'EXT',
    children:[
        {id:'KMA',label:'기상청',params:{qcd:'KMA'}},
        {id:'EXT',label:'+유관',params:{qcd:'EXT'}}
    ]
    },
    {
    id:'HLSP',
    label:'우박가능영역',
    baseUrl:RADAR_R2D_HAIL_IMAGE_URL,
    params:{cmp:'HLSP'}
    },
    {
    id:'HAIL2',
    label:'우박위험고도',
    params:{cmp:'HAIL2', qcd:'CMAX'}
    },
    {
    id:'HAIL_ACC',
    label:'우박누적경로',
    baseUrl:RADAR_R2D_HAIL_ACC_IMAGE_URL,
    children:[
        {id:'1H',label:'1H',params:{itv:'60'}},
        {id:'2H',label:'2H',params:{itv:'120'}},
        {id:'3H',label:'3H',params:{itv:'180'}},
        {id:'6H',label:'6H',params:{itv:'360'}},
        {id:'12H',label:'12H',params:{itv:'720'}},
        {id:'24H',label:'24H',params:{itv:'1440'}}
    ]
    },



]
},

{
id:'LGT',
label:'낙뢰',
baseUrl:RADAR_LGT_DST_IMAGE_URL,
defaultLevel2:'LGT_DST_T',
children:[
    {
    id:'LGT_DST_T',
    label:'낙뢰(전체)',
    params:{obs:'lgt_dst', gc:'T'},
    defaultLevel3:'1H',
    children:[
        {id:'30m',label:'30m',params:{itv:'30'}},
        {id:'1H',label:'1H',params:{itv:'60'}},
        {id:'2H',label:'2H',params:{itv:'120'}},
        {id:'3H',label:'3H',params:{itv:'180'}},
        {id:'6H',label:'6H',params:{itv:'360'}},
        {id:'12H',label:'12H',params:{itv:'720'}},
        {id:'24H',label:'24H',params:{itv:'1440'}}
    ]
    },
    {
    id:'LGT_DST_G',
    label:'낙뢰(지면)',
    params:{obs:'lgt_dst', gc:'G'},
    defaultLevel3:'1H',
    children:[
        {id:'30m',label:'30m',params:{itv:'30'}},
        {id:'1H',label:'1H',params:{itv:'60'}},
        {id:'2H',label:'2H',params:{itv:'120'}},
        {id:'3H',label:'3H',params:{itv:'180'}},
        {id:'6H',label:'6H',params:{itv:'360'}},
        {id:'12H',label:'12H',params:{itv:'720'}},
        {id:'24H',label:'24H',params:{itv:'1440'}}
    ]
    },
    {
    id:'LGT_DST_C',
    label:'낙뢰(구름)',
    params:{obs:'lgt_dst', gc:'C'},
    defaultLevel3:'1H',
    children:[
        {id:'30m',label:'30m',params:{itv:'30'}},
        {id:'1H',label:'1H',params:{itv:'60'}},
        {id:'2H',label:'2H',params:{itv:'120'}},
        {id:'3H',label:'3H',params:{itv:'180'}},
        {id:'6H',label:'6H',params:{itv:'360'}},
        {id:'12H',label:'12H',params:{itv:'720'}},
        {id:'24H',label:'24H',params:{itv:'1440'}}
    ]
    }
]
},


{
id:'AWS',
label:'AWS',
baseUrl:RADAR_SFC_OBS_IMAGE_URL,
defaultLevel2:'rn_60m',
children:[
    {
    id:'rn_15x',
    label:'강수15분*4',
    params:{obs:'rn_15x'}
    },
    {
    id:'rn_60m',
    label:'강수60분',
    params:{obs:'rn_60m'},
    },
    {
    id:'rn_03h',
    label:'강수3H',
    params:{obs:'rn_03h'},
    },
    {
    id:'rn_06h',
    label:'강수6H',
    params:{obs:'rn_06h'},
    },
    {
    id:'rn_12h',
    label:'강수12H',
    params:{obs:'rn_12h'},
    },
    {
    id:'rn_day',
    label:'일강수',
    params:{obs:'rn_day'},
    },
    {
    id:'ta',
    label:'기온',
    params:{obs:'ta'},
    },
    {
    id:'hm',
    label:'습도',
    params:{obs:'hm'},
    },
    {
    id:'tw_win',
    label:'습구온도',
    params:{obs:'tw_win'},
    },
    {
    id:'wv_10m',
    label:'바람(10분)',
    params:{obs:'wv_10m'},
    },
    {
    id:'ws_10m',
    label:'풍속(10분)',
    params:{obs:'ws_10m'},
    }
]
},






];

const RADAR_PERIOD_OPTIONS=[
{value:30,label:'30m'},
{value:60,label:'1h'},
{value:120,label:'2h'},
{value:180,label:'3h'},
{value:360,label:'6h'},
{value:720,label:'12h'},
{value:1440,label:'1D'},
{value:2880,label:'2D'}
];

const RADAR_INTERVAL_OPTIONS=[
{value:5,label:'5m'},
{value:10,label:'10m'},
{value:15,label:'15m'},
{value:30,label:'30m'},
{value:60,label:'1h'},
{value:120,label:'2h'},
{value:180,label:'3h'},
{value:360,label:'6h'},
];

const RADAR_TIME_SHIFT_OPTIONS=[
{minutes:-1440,label:'-1D'},
{minutes:-360,label:'-6H'},
{minutes:-180,label:'-3H'},
{minutes:-60,label:'-1H'},
{minutes:-30,label:'-30m'},
{minutes:-10,label:'-10m'},
{minutes:-5,label:'-5m'},
{minutes:5,label:'+5m'},
{minutes:10,label:'+10m'},
{minutes:30,label:'+30m'},
{minutes:60,label:'+1h'},
{minutes:180,label:'+3h'},
{minutes:360,label:'+6h'},
{minutes:1440,label:'+1D'}
];

const RADAR_MAP_DEFAULTS={
DEFAULT:{xp:-9999,yp:-9999,zoom:1},
D3:{xp:340,yp:340,zoom:1},
HR:{xp:512,yp:512,zoom:1},
HC:{xp:800,yp:800,zoom:1},
H1:{xp:1200,yp:1200,zoom:1},
H3:{xp:1760,yp:1760,zoom:1},
SE:{xp:24,yp:24,zoom:1},
HL:{xp:160,yp:160,zoom:1}
};

const RADAR_WIND_SOURCE_CODES={
WISSDOM:'1',
KLAPS:'2',
VDAPS:'3'
};

const RADAR_STATION_OPTIONS=[
{value:'00',label:'없음'},
{value:'01',label:'지점명'},
{value:'02',label:'지점번호'},
{value:'03',label:'15분강수*4'},
{value:'04',label:'60분강수'},
{value:'05',label:'3H강수'},
{value:'09',label:'지점만'}
];

const RADAR_LIGHTNING_TYPES=[
{value:'T',label:'전체'},
{value:'G',label:'지면'},
{value:'C',label:'구름'}
];

const RADAR_ZOOM_LEVELS=[1,2,4,8];
const RADAR_SIZE_STEP=25;
const RADAR_MIN_IMAGE_SIZE=250;
const RADAR_MAX_IMAGE_SIZE=1500;
const RADAR_DEFAULT_IMAGE_SIZE=800;
const RADAR_IMAGE_WIDTH_MARGIN=35;
const RADAR_IMAGE_HEIGHT_MARGIN=20;
const RADAR_PUBLICATION_DELAY_MINUTES=4;
const RADAR_CACHE_REFRESH_INTERVAL_MS=5*60*1000;
const RADAR_IMAGE_LOAD_TIMEOUT_MS=30000;

const radarState={
baseTime:getLatestPublishedRadarTime(),
periodMinutes:60,
intervalMinutes:5,
frames:[],
frameLoadStates:[],
activeIndex:0,
paneCount:4,
panes:[
{level1:'HSP',level2:'HSO',level3:'ECHD'},
{level1:'PCPH',level2:'EXT',level3:'1H'},
{level1:'HAIL',level2:'HLSP'},
{level1:'SFC',level2:'SPOT'}
],
paneSizes:[
RADAR_DEFAULT_IMAGE_SIZE,
Math.round(RADAR_DEFAULT_IMAGE_SIZE/2),
Math.round(RADAR_DEFAULT_IMAGE_SIZE/2),
Math.round(RADAR_DEFAULT_IMAGE_SIZE/2)
],
common:{...RADAR_DEFAULT_PARAMS,xp:'512',yp:'512',zoom:'1',aws:'01'},
wind:{
enabled:false,
mode:'barb',
source:'WISSDOM',
height:'1500',
open:false
},
station:{
enabled:true,
density:'sparse',
label:'01',
open:false
},
lightning:{
enabled:false,
type:'T',
interval:'10',
open:false
},
root:null,
timeline:null,
timeLabel:null,
dateInput:null,
paneGrid:null,
playButton:null,
playTimer:null,
isPlaying:false,
autoRefreshButton:null,
autoRefreshTimer:null,
autoRefreshEnabled:false,
imageCache:new Map(),
preloadRunId:0,
playbackPreloadAt:0,
cacheRefreshTimer:null,
cacheRefreshRunId:0,
keyboardBound:false,
resumeBound:false,
resizeBound:false,
resizeTimer:null,
mapTool:null,
mapModeGroup:null
};

function pad2(value){
return String(value).padStart(2,'0');
}

function floorDateToFiveMinutes(date){
let out=new Date(date.getTime());
out.setSeconds(0,0);
out.setMinutes(Math.floor(out.getMinutes()/5)*5);
return out;
}

function getLatestPublishedRadarTime(date=new Date()){
return floorDateToFiveMinutes(new Date(date.getTime()-RADAR_PUBLICATION_DELAY_MINUTES*60*1000));
}

function roundDateToFiveMinutes(date){
let out=new Date(date.getTime());
let minutes=out.getMinutes();
let roundedMinutes=Math.round(minutes/5)*5;
out.setSeconds(0,0);

if(roundedMinutes>=60){
out.setMinutes(0);
out.setHours(out.getHours()+1);
}
else{
out.setMinutes(roundedMinutes);
}

return out;
}

function formatDateInput(date){
return `${date.getFullYear()}-${pad2(date.getMonth()+1)}-${pad2(date.getDate())}`;
}

function formatDateDisplayInput(date){
return `${date.getFullYear()}.${pad2(date.getMonth()+1)}.${pad2(date.getDate())}.`;
}

function formatDateTimeDisplay(date){
return `${formatDateDisplayInput(date)} ${formatTimeInput(date)}`;
}

function formatNormalizedDateDisplay(value){
let [year,month,day]=normalizeDateTextValue(value).split('-').map(Number);
return `${String(year).padStart(4,'0')}.${pad2(month)}.${pad2(day)}.`;
}

function normalizeDateTextValue(value,fallbackValue=formatDateInput(new Date())){
let raw=String(value || '').trim();
let fallback=String(fallbackValue || formatDateInput(new Date()));
let fallbackMatch=fallback.match(/^(\d{4})[-./\s]+(\d{1,2})[-./\s]+(\d{1,2})\.?$/);
let match=raw.match(/^(\d{4})[-./\s]+(\d{1,2})[-./\s]+(\d{1,2})\.?$/);

if(!match && /^\d{8}$/.test(raw)){
match=raw.match(/^(\d{4})(\d{2})(\d{2})$/);
}

if(!match && /^\d{4}$/.test(raw) && fallbackMatch){
match=[raw,raw,fallbackMatch[2],fallbackMatch[3]];
}

if(!match){
return fallbackMatch ? fallback : formatDateInput(new Date());
}

let year=Math.max(1,Math.min(9999,Number(match[1])));
let month=Math.max(1,Math.min(12,Number(match[2])));
let maxDay=new Date(year,month,0).getDate();
let day=Math.max(1,Math.min(maxDay,Number(match[3])));
return `${String(year).padStart(4,'0')}-${pad2(month)}-${pad2(day)}`;
}

function formatTimeInput(date){
return `${pad2(date.getHours())}:${pad2(date.getMinutes())}`;
}

function normalizeRadarTimeValue(value){
let raw=String(value || '').trim();
let hour;
let minute;

if(/^\d{3,4}$/.test(raw)){
hour=Number(raw.slice(0,-2));
minute=Number(raw.slice(-2));
}
else{
let match=raw.match(/^(\d{1,2})(?::(\d{1,2}))?$/);

if(!match){
return null;
}

hour=Number(match[1]);
minute=Number(match[2] ?? 0);
}

if(Number.isNaN(hour) || Number.isNaN(minute) || hour<0 || minute<0 || minute>59 || hour>24){
return null;
}

if(hour===24 && minute>0){
return null;
}

let dayOffset=0;
let roundedMinute=Math.round(minute/5)*5;

if(roundedMinute>=60){
roundedMinute=0;
hour+=1;
}

if(hour>=24){
hour-=24;
dayOffset+=1;
}

return {
hour,
minute:roundedMinute,
dayOffset,
text:`${pad2(hour)}:${pad2(roundedMinute)}`
};
}

function normalizeDateTimeText(value,fallbackDate=radarState.baseTime || new Date()){
let raw=String(value || '').trim();
let fallbackDateText=formatDateInput(fallbackDate);
let fallbackTimeText=formatTimeInput(fallbackDate);
let datePart='';
let timePart='';
let compact=raw.match(/^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})$/);

if(compact){
datePart=`${compact[1]}-${compact[2]}-${compact[3]}`;
timePart=`${compact[4]}:${compact[5]}`;
}
else{
let dateTime=raw.match(/^(\d{4})[-./\s]+(\d{1,2})[-./\s]+(\d{1,2})\.?\s+(\d{1,2})(?::?(\d{2}))?$/);

if(dateTime){
datePart=`${dateTime[1]}-${dateTime[2]}-${dateTime[3]}`;
timePart=`${dateTime[4]}:${dateTime[5] ?? '00'}`;
}
else{
datePart=raw;
}
}

let normalizedDate=normalizeDateTextValue(datePart,fallbackDateText);
let normalizedTime=normalizeRadarTimeValue(timePart || fallbackTimeText) || normalizeRadarTimeValue(fallbackTimeText);
let display=`${formatNormalizedDateDisplay(normalizedDate)} ${normalizedTime.text}`;
return {
date:normalizedDate,
time:normalizedTime.text,
display
};
}

function parseLocalDateTime(dateValue,timeValue){
let dateTime=normalizeDateTimeText(dateValue,radarState.baseTime || new Date());
let normalizedDate=dateTime.date;
let [year,month,day]=normalizedDate.split('-').map(Number);
let normalizedTime=normalizeRadarTimeValue(timeValue || dateTime.time);

if(!year || !month || !day || !normalizedTime){
return radarState.baseTime || floorDateToFiveMinutes(new Date());
}

let out=new Date(year,month-1,day,normalizedTime.hour,normalizedTime.minute,0,0);

if(normalizedTime.dayOffset){
out.setDate(out.getDate()+normalizedTime.dayOffset);
}

return roundDateToFiveMinutes(out);
}

function formatRadarTimestamp(date){
return (
String(date.getFullYear())+
pad2(date.getMonth()+1)+
pad2(date.getDate())+
pad2(date.getHours())+
pad2(date.getMinutes())
);
}

function formatRadarFrameLabel(date){
return `${pad2(date.getDate())}.${pad2(date.getHours())}:${pad2(date.getMinutes())}`;
}

function formatRadarDateLabel(date){
return `${pad2(date.getMonth()+1)}.${pad2(date.getDate())}`;
}

function formatRadarTimeLabel(date){
return `${pad2(date.getHours())}:${pad2(date.getMinutes())}`;
}

function findRadarLevel1(id){
return RADAR_PRODUCT_CATALOG.find(item=>item.id===id) || RADAR_PRODUCT_CATALOG[0];
}

function getDefaultRadarLevel2(level1){
return level1.children.find(item=>item.id===level1.defaultLevel2) || level1.children[0];
}

function hasRadarLevel3(level2){
return Array.isArray(level2?.children) && level2.children.length>0;
}

function getDefaultRadarLevel3(level2){
if(!hasRadarLevel3(level2)){
return null;
}

return level2.children.find(item=>item.id===level2.defaultLevel3) || level2.children[0];
}

function findRadarLevel2(level1Id,level2Id){
let level1=findRadarLevel1(level1Id);
return level1.children.find(item=>item.id===level2Id) || getDefaultRadarLevel2(level1);
}

function findRadarLevel3(level1Id,level2Id,level3Id){
let level2=findRadarLevel2(level1Id,level2Id);

if(!hasRadarLevel3(level2)){
return null;
}

return level2.children.find(item=>item.id===level3Id) || getDefaultRadarLevel3(level2);
}

function normalizeRadarPaneSelection(pane){
let level1=findRadarLevel1(pane.level1);
let level2=findRadarLevel2(level1.id,pane.level2);
let level3=findRadarLevel3(level1.id,level2.id,pane.level3);

pane.level1=level1.id;
pane.level2=level2.id;
pane.level3=level3 ? level3.id : '';

return {level1,level2,level3};
}

function applyRadarTemplate(template,{params,frameTime}){
return template.replace(/\{(\w+)\}/g,(match,key)=>{
if(key==='tm'){
return formatRadarTimestamp(frameTime);
}

return params[key] ?? '';
});
}

function buildRadarFrames(){
let frames=[];
let step=Math.max(5,Number(radarState.intervalMinutes)||10);
let period=Math.max(step,Number(radarState.periodMinutes)||60);
let start=radarState.baseTime.getTime()-period*60*1000;
let end=radarState.baseTime.getTime();

for(let time=start;time<=end;time+=step*60*1000){
frames.push(new Date(time));
}

radarState.frames=frames;
radarState.frameLoadStates=frames.map(()=>'loading');
radarState.activeIndex=Math.max(0,Math.min(radarState.activeIndex,frames.length-1));
}

function getRadarMapDefaults(mapId){
return RADAR_MAP_DEFAULTS[mapId] || RADAR_MAP_DEFAULTS.DEFAULT;
}

function normalizeRadarMapNumber(value,fallback){
let parsed=Number(value);
return Number.isFinite(parsed) ? parsed : fallback;
}

function getCurrentRadarZoom(){
let defaults=getRadarMapDefaults(radarState.common.map);
return normalizeRadarMapNumber(radarState.common.zoom,defaults.zoom);
}

function getRadarMapCoordinateSpan(axis,defaults,imageSize){
let centerValue=axis==='x' ? defaults.xp : defaults.yp;
let parsed=normalizeRadarMapNumber(centerValue,0);

if(parsed>0){
return parsed*2;
}

return imageSize;
}

function getNextRadarZoom(currentZoom,direction){
let current=normalizeRadarMapNumber(currentZoom,1);
let levels=RADAR_ZOOM_LEVELS;

if(direction>0){
return levels.find(level=>level>current) || levels[levels.length-1];
}

return [...levels].reverse().find(level=>level<current) || levels[0];
}

function setRadarMapTool(tool){
radarState.mapTool=radarState.mapTool===tool ? null : tool;
updateRadarMapModeButtons();
}

function updateRadarMapModeButtons(){
if(!radarState.mapModeGroup){
return;
}

radarState.mapModeGroup.querySelectorAll('.radar-mode-button[data-map-tool]').forEach(button=>{
button.classList.toggle('active',button.dataset.mapTool===radarState.mapTool);
});
}

function resetRadarMapView(mapId=radarState.common.map || RADAR_DEFAULT_PARAMS.map){
let defaults=getRadarMapDefaults(mapId);
radarState.common.map=mapId;
radarState.common.xp=String(defaults.xp);
radarState.common.yp=String(defaults.yp);
radarState.common.zoom=String(defaults.zoom);
radarState.mapTool=null;
updateRadarMapModeButtons();
reloadRadarImagesForCurrentSettings();
}

function getRadarWindValue(){
if(!radarState.wind.enabled){
return '00';
}

let sourceCode=RADAR_WIND_SOURCE_CODES[radarState.wind.source] || RADAR_WIND_SOURCE_CODES.WISSDOM;
let modePrefix=radarState.wind.mode==='barb' ? '1' : '0';
return modePrefix+sourceCode;
}

function normalizeRadarWindMode(mode){
return mode==='barb' ? 'barb' : 'vector';
}

function normalizeRadarWindSource(source){
return RADAR_WIND_SOURCE_CODES[source] ? source : 'WISSDOM';
}

function normalizeRadarWindHeight(height){
let value=String(height || '').trim();
return value || RADAR_DEFAULT_PARAMS.ht;
}

function applyRadarWindSettings({reload=true}={}){
radarState.common.wv=getRadarWindValue();
radarState.common.ht=String(radarState.wind.height || RADAR_DEFAULT_PARAMS.ht);

if(reload){
reloadRadarImagesForCurrentSettings();
}
}

function setRadarWindEnabled(enabled){
radarState.wind.enabled=!!enabled;
applyRadarWindSettings();
}

function getRadarStationValue(){
if(!radarState.station.enabled || radarState.station.label==='00'){
return '00';
}

let prefix=radarState.station.density==='full' ? '1' : '0';
let suffix=String(radarState.station.label || '01').slice(-1);
return normalizeRadarAwsValue(prefix+suffix);
}

function normalizeRadarStationDensity(density){
return density==='full' ? 'full' : 'sparse';
}

function normalizeRadarStationLabel(label){
return RADAR_STATION_OPTIONS.some(option=>option.value===label) ? label : '01';
}

function normalizeRadarAwsValue(value){
let aws=String(value ?? RADAR_DEFAULT_PARAMS.aws);
return aws==='10' ? '00' : aws;
}

function applyRadarStationSettings({reload=true}={}){
radarState.common.aws=getRadarStationValue();

if(reload){
reloadRadarImagesForCurrentSettings();
}
}

function setRadarStationEnabled(enabled){
radarState.station.enabled=!!enabled;
applyRadarStationSettings();
}

function normalizeRadarLightningType(type){
return RADAR_LIGHTNING_TYPES.some(option=>option.value===type) ? type : 'T';
}

function normalizeRadarLightningInterval(value){
let numeric=Number.parseInt(value,10);

if(!Number.isFinite(numeric) || numeric <= 0){
numeric=Number.parseInt(RADAR_DEFAULT_PARAMS.gc_itv,10) || 10;
}

numeric=Math.max(5,Math.round(numeric/5)*5);
return String(numeric);
}

function getRadarLightningType(){
if(!radarState.lightning.enabled){
return '';
}

return normalizeRadarLightningType(radarState.lightning.type);
}

function applyRadarLightningSettings({reload=true}={}){
radarState.common.gc=getRadarLightningType();
radarState.common.gc_itv=normalizeRadarLightningInterval(radarState.lightning.interval);

if(reload){
reloadRadarImagesForCurrentSettings();
}
}

function setRadarLightningEnabled(enabled){
radarState.lightning.enabled=!!enabled;
applyRadarLightningSettings();
}

function notifyRadarOverlayDropdownOpen(source){
document.dispatchEvent(new CustomEvent('radarOverlayDropdownOpen',{detail:{source}}));
}

function applyRadarMapClick(event){
if(!radarState.mapTool){
return;
}

let image=event.currentTarget;
let rect=image.getBoundingClientRect();

if(!rect.width || !rect.height){
return;
}

let defaults=getRadarMapDefaults(radarState.common.map);
let currentZoom=getCurrentRadarZoom();
let direction=radarState.mapTool==='zoomIn' ? 1 : -1;
let nextZoom=getNextRadarZoom(currentZoom,direction);
let clickX=event.clientX-rect.left;
let clickY=event.clientY-rect.top;
let scaleX=image.naturalWidth ? image.naturalWidth/rect.width : 1;
let scaleY=image.naturalHeight ? image.naturalHeight/rect.height : 1;
let naturalX=clickX*scaleX;
let naturalY=clickY*scaleY;
let mapAreaWidth=Math.max(1,(image.naturalWidth || rect.width)-RADAR_IMAGE_WIDTH_MARGIN);
let mapAreaHeight=Math.max(1,(image.naturalHeight || rect.height)-RADAR_IMAGE_HEIGHT_MARGIN);
let mapAreaTop=Math.max(0,(image.naturalHeight || rect.height)-mapAreaHeight);
let mapX=Math.max(0,Math.min(mapAreaWidth,naturalX));
let mapY=Math.max(0,Math.min(mapAreaHeight,naturalY-mapAreaTop));
let spanX=getRadarMapCoordinateSpan('x',defaults,mapAreaWidth)/currentZoom;
let spanY=getRadarMapCoordinateSpan('y',defaults,mapAreaHeight)/currentZoom;
let dx=(mapX/mapAreaWidth-.5)*spanX;
let dy=(.5-mapY/mapAreaHeight)*spanY;
let xp=normalizeRadarMapNumber(radarState.common.xp,defaults.xp);
let yp=normalizeRadarMapNumber(radarState.common.yp,defaults.yp);

radarState.common.xp=String(Math.round(xp+dx));
radarState.common.yp=String(Math.round(yp+dy));
radarState.common.zoom=String(nextZoom);
reloadRadarImagesForCurrentSettings();
}

function clampRadarImageSize(size){
let value=Number(size) || RADAR_DEFAULT_IMAGE_SIZE;
let clamped=Math.max(RADAR_MIN_IMAGE_SIZE,Math.min(RADAR_MAX_IMAGE_SIZE,value));
return Math.floor(clamped/RADAR_SIZE_STEP)*RADAR_SIZE_STEP;
}

function getRadarPaneImageSize(paneIndex){
return clampRadarImageSize(radarState.paneSizes[paneIndex] || RADAR_DEFAULT_IMAGE_SIZE);
}

function buildRadarUrl({pane,frameTime,size}){
let {level1,level2,level3}=normalizeRadarPaneSelection(pane);
let params={
...RADAR_DEFAULT_PARAMS,
...radarState.common,
...(level1.params || {}),
...(level2.params || {}),
...(level3?.params || {}),
size:String(clampRadarImageSize(size || RADAR_DEFAULT_IMAGE_SIZE)),
tm:formatRadarTimestamp(frameTime)
};

params.aws=normalizeRadarAwsValue(params.aws);

if(level3?.urlTemplate){
return applyRadarTemplate(level3.urlTemplate,{params,frameTime});
}

let baseUrl=level3?.baseUrl || level2.baseUrl || level1.baseUrl || RADAR_CMP_IMAGE_URL;
let query=new URLSearchParams();

Object.keys(RADAR_DEFAULT_PARAMS).forEach(key=>{
query.set(key,params[key] ?? '');
});

return `${baseUrl}?${query.toString()}`;
}

function updateRadarPaneSizes(){
let paneElements=getRadarPaneElements();
let nextSizes=radarState.panes.map((pane,index)=>{
let paneElement=paneElements[index];
let header=paneElement?.querySelector('.radar-pane-header');
let paneRect=paneElement?.getBoundingClientRect();
let headerRect=header?.getBoundingClientRect();
let size=radarState.paneSizes[index];

if(paneRect?.height){
let availableHeight=paneRect.height-(headerRect?.height || 0);
size=availableHeight-RADAR_IMAGE_HEIGHT_MARGIN;
}

return clampRadarImageSize(size);
});

let changed=nextSizes.some((size,index)=>size!==radarState.paneSizes[index]);
radarState.paneSizes=nextSizes;

paneElements.forEach((paneElement,index)=>{
let imageSize=getRadarPaneImageSize(index);
paneElement.style.setProperty('--radar-image-width',`${imageSize+RADAR_IMAGE_WIDTH_MARGIN}px`);
paneElement.style.setProperty('--radar-image-height',`${imageSize+RADAR_IMAGE_HEIGHT_MARGIN}px`);
});

return changed;
}

function reloadRadarImagesForSizeChange(){
if(!radarState.paneGrid){
return;
}

if(!updateRadarPaneSizes()){
return;
}

resetRadarImageCache();
loadActiveRadarFrameImages();
preloadRadarImages();
}

function scheduleRadarSizeRefresh(){
clearTimeout(radarState.resizeTimer);
radarState.resizeTimer=setTimeout(reloadRadarImagesForSizeChange,150);
}

function resetRadarImageCache(){
radarState.imageCache.clear();
radarState.preloadRunId+=1;
radarState.cacheRefreshRunId+=1;
resetRadarFrameLoadStates();
}

function reloadRadarImagesForCurrentSettings(){
resetRadarImageCache();
renderRadarPanes();
preloadRadarImages();
}

function resetRadarFrameLoadStates(){
radarState.frameLoadStates=radarState.frames.map(()=>'loading');
updateRadarTimelineLoadStates();
}

function getRadarFrameLoadState(frameIndex){
return radarState.frameLoadStates[frameIndex] || 'loading';
}

function setRadarFrameLoadState(frameIndex,state){
if(frameIndex<0 || frameIndex>=radarState.frames.length){
return;
}

if(radarState.frameLoadStates[frameIndex]===state){
return;
}

radarState.frameLoadStates[frameIndex]=state;
updateRadarTimelineFrameState(frameIndex,state);
}

function updateRadarTimelineFrameState(frameIndex,state=getRadarFrameLoadState(frameIndex)){
if(!radarState.timeline){
return;
}

let seg=radarState.timeline.querySelector(`.radar-track .compare-segment[data-index="${frameIndex}"]`);

if(!seg){
return;
}

seg.classList.remove('state-loading','state-missing','state-available');
seg.classList.add(`state-${state}`);
}

function updateRadarTimelineLoadStates(){
radarState.frameLoadStates.forEach((state,index)=>updateRadarTimelineFrameState(index,state));
}

function getRadarFrameUrl(paneIndex,frameIndex){
let frame=radarState.frames[frameIndex];
let pane=radarState.panes[paneIndex];

if(!frame || !pane){
return '';
}

return buildRadarUrl({
pane,
frameTime:frame,
size:getRadarPaneImageSize(paneIndex)
});
}

function getRadarFrameUrls(frameIndex,paneIndexes){
let seen=new Set();
let urls=[];

getRadarPaneIndexes(paneIndexes).forEach(paneIndex=>{
let url=getRadarFrameUrl(paneIndex,frameIndex);

if(url && !seen.has(url)){
seen.add(url);
urls.push(url);
}
});

return urls;
}

function getRadarFrameCacheState(frameIndex){
let urls=getRadarFrameUrls(frameIndex);

if(!urls.length){
return 'missing';
}

let entries=urls.map(url=>radarState.imageCache.get(url));

if(entries.some(entry=>!entry || entry.status==='loading')){
return 'loading';
}

return entries.every(entry=>entry.status==='loaded') ? 'available' : 'missing';
}

function refreshRadarFrameLoadState(frameIndex){
setRadarFrameLoadState(frameIndex,getRadarFrameCacheState(frameIndex));
}

function refreshAllRadarFrameLoadStates(){
radarState.frames.forEach((_,frameIndex)=>refreshRadarFrameLoadState(frameIndex));
}

function getNextRadarLoopIndex(){
let count=radarState.frames.length;

for(let offset=1;offset<count;offset++){
let index=(radarState.activeIndex+offset)%count;

if(getRadarFrameCacheState(index)==='available'){
return index;
}
}

return radarState.activeIndex;
}

function getCacheBustedRadarUrl(url){
let separator=url.includes('?') ? '&' : '?';
return `${url}${separator}_cds_cache=${Date.now()}`;
}

function loadRadarImage(url,{refresh=false}={}){
if(!url){
return Promise.resolve({status:'error',url});
}

let entry={
url,
status:'loading',
image:null,
promise:null
};

entry.promise=new Promise(resolve=>{
let image=new Image();
entry.image=image;
let settled=false;
let timeoutId=setTimeout(()=>{
finish('error');
},RADAR_IMAGE_LOAD_TIMEOUT_MS);

function finish(status){
if(settled){
return;
}

settled=true;
clearTimeout(timeoutId);
entry.status=status;
resolve(entry);
}

image.onload=()=>{
if(image.decode){
image.decode().then(()=>finish('loaded')).catch(()=>finish('loaded'));
}
else{
finish('loaded');
}
};

image.onerror=()=>{
finish('error');
};

image.src=refresh ? getCacheBustedRadarUrl(url) : url;
});

return entry;
}

function cacheRadarImage(url,{retryError=false}={}){
if(!url){
return Promise.resolve({status:'error',url});
}

let cached=radarState.imageCache.get(url);

if(cached && !(retryError && cached.status==='error')){
return cached.promise;
}

let entry=loadRadarImage(url);
radarState.imageCache.set(url,entry);
return entry.promise;
}

function createResolvedRadarCacheEntry(url,sourceEntry){
let entry={
url,
status:sourceEntry.status,
image:sourceEntry.image,
promise:null,
updatedAt:Date.now()
};

entry.promise=Promise.resolve(entry);
return entry;
}

function getRadarImageDisplaySource(url,entry){
return entry?.image?.currentSrc || entry?.image?.src || url;
}

function applyRadarImageEntry(paneElement,img,url,entry){
if(!img || !entry || entry.status!=='loaded'){
return false;
}

let source=getRadarImageDisplaySource(url,entry);

if(img.getAttribute('src')!==source){
img.src=source;
}

paneElement.dataset.renderedSrc=source;
paneElement.dataset.renderedUrl=url;
paneElement.dataset.renderedFrameIndex=paneElement.dataset.currentFrameIndex || '';
paneElement.classList.add('has-current-image');
setRadarPaneError(paneElement,'');
return true;
}

function getRadarPaneIndexes(paneIndexes){
if(Array.isArray(paneIndexes)){
return paneIndexes
.map(index=>Number(index))
.filter(index=>index>=0 && index<radarState.paneCount);
}

return Array.from({length:radarState.paneCount},(_,index)=>index);
}

function getRadarPreloadFrameOrder(playbackFirst=false){
let count=radarState.frames.length;
let active=Math.max(0,Math.min(radarState.activeIndex,count-1));
let order=[];

if(!count){
return order;
}

order.push(active);

if(playbackFirst){
for(let offset=1;offset<count;offset++){
order.push((active+offset)%count);
}

return order;
}

for(let i=active-1;i>=0;i--){
order.push(i);
}

for(let i=active+1;i<count;i++){
order.push(i);
}

return order;
}

function collectRadarPreloadJobs(paneIndexes,{playbackFirst=false}={}){
let jobs=[];
let seen=new Set();
let targetPaneIndexes=getRadarPaneIndexes(paneIndexes);
let frameOrder=getRadarPreloadFrameOrder(playbackFirst);

frameOrder.forEach(frameIndex=>{
targetPaneIndexes.forEach(paneIndex=>{
let url=getRadarFrameUrl(paneIndex,frameIndex);

if(url && !seen.has(url)){
seen.add(url);
jobs.push({url,frameIndex});
}
});
});

return jobs;
}

function preloadRadarImages(paneIndexes,options={}){
let runId=++radarState.preloadRunId;
let jobs=collectRadarPreloadJobs(paneIndexes,options);
let nextIndex=0;
let concurrency=10;

refreshAllRadarFrameLoadStates();

function loadNext(){
if(runId!==radarState.preloadRunId){
return;
}

let job=jobs[nextIndex++];

if(!job){
return;
}

cacheRadarImage(job.url,{retryError:true}).finally(()=>{
refreshRadarFrameLoadState(job.frameIndex);
loadNext();
});
}

for(let i=0;i<Math.min(concurrency,jobs.length);i++){
loadNext();
}
}

function requestRadarPlaybackPreload({force=false}={}){
let now=Date.now();

if(!force && now-radarState.playbackPreloadAt<5000){
return;
}

radarState.playbackPreloadAt=now;
preloadRadarImages(null,{playbackFirst:true});
}

function getRefreshableRadarCacheUrls(){
let seen=new Set();

radarState.frames.forEach((_,frameIndex)=>{
getRadarFrameUrls(frameIndex).forEach(url=>{
let entry=radarState.imageCache.get(url);

if(entry && entry.status!=='loading'){
seen.add(url);
}
});
});

return [...seen];
}

function refreshRadarCacheInBackground(){
let urls=getRefreshableRadarCacheUrls();

if(!urls.length){
return;
}

let runId=++radarState.cacheRefreshRunId;
let nextIndex=0;
let activeCount=0;
let results=[];
let concurrency=6;

function finishIfDone(resolve){
if(nextIndex>=urls.length && activeCount===0){
resolve(results);
}
}

let allDone=new Promise(resolve=>{
function loadNext(){
if(runId!==radarState.cacheRefreshRunId){
resolve([]);
return;
}

let url=urls[nextIndex++];

if(!url){
finishIfDone(resolve);
return;
}

activeCount+=1;
loadRadarImage(url,{refresh:true}).promise
.then(entry=>results.push({url,entry}))
.finally(()=>{
activeCount-=1;
loadNext();
finishIfDone(resolve);
});
}

for(let i=0;i<Math.min(concurrency,urls.length);i++){
loadNext();
}
});

allDone.then(refreshResults=>{
if(runId!==radarState.cacheRefreshRunId || !refreshResults.length){
return;
}

refreshResults.forEach(({url,entry})=>{
let current=radarState.imageCache.get(url);

if(!current || current.status==='loading'){
return;
}

if(entry.status==='loaded' || current.status!=='loaded'){
radarState.imageCache.set(url,createResolvedRadarCacheEntry(url,entry));
}
});

refreshAllRadarFrameLoadStates();

if(!radarState.isPlaying){
refreshRadarPaneImages();
}
});
}

function startRadarCacheRefresh(){
if(radarState.cacheRefreshTimer){
clearInterval(radarState.cacheRefreshTimer);
}

radarState.cacheRefreshTimer=setInterval(refreshRadarCacheInBackground,RADAR_CACHE_REFRESH_INTERVAL_MS);
}

function setRadarPageLoading(pane,isLoading){
pane.classList.toggle('is-loading',!!isLoading);
}

function getRadarPaneElements(){
if(!radarState.paneGrid){
return [];
}

return [...radarState.paneGrid.querySelectorAll('.radar-pane')];
}

function setRadarPaneError(paneElement,message){
let error=paneElement.querySelector('.radar-pane-error');

if(!error){
return;
}

if(message){
error.textContent=message;
error.classList.remove('hidden');
}
else{
error.textContent='';
error.classList.add('hidden');
}
}

function loadActiveRadarFrameImages(paneIndexes){
let frameIndex=radarState.activeIndex;
let frame=radarState.frames[frameIndex];

if(!frame || !radarState.paneGrid){
return;
}

let paneElements=getRadarPaneElements();
let targets=getRadarPaneIndexes(paneIndexes)
.map(paneIndex=>({paneIndex,paneElement:paneElements[paneIndex]}))
.filter(item=>item.paneElement);

targets.forEach(({paneElement,paneIndex})=>{
let url=getRadarFrameUrl(paneIndex,frameIndex);
let img=paneElement.querySelector('.radar-pane-image');
let hasCurrent=!!img?.getAttribute('src');
let cached=radarState.imageCache.get(url);

paneElement.dataset.currentUrl=url;
paneElement.dataset.currentFrameIndex=String(frameIndex);
paneElement.dataset.loadingUrl='';
setRadarPaneError(paneElement,'');
paneElement.classList.toggle('has-current-image',hasCurrent);

if(cached?.status==='loaded'){
applyRadarImageEntry(paneElement,img,url,cached);
setRadarPageLoading(paneElement,false);
refreshRadarFrameLoadState(frameIndex);
return;
}

if(cached?.status==='error' && radarState.isPlaying){
setRadarPageLoading(paneElement,false);
refreshRadarFrameLoadState(frameIndex);
return;
}

setRadarPageLoading(paneElement,!radarState.isPlaying);
paneElement.dataset.loadingUrl=url;
cacheRadarImage(url,{retryError:true}).then(entry=>{
if(!paneElement.isConnected || paneElement.dataset.currentUrl!==url){
return;
}

if(entry.status==='loaded' && img){
applyRadarImageEntry(paneElement,img,url,entry);
}
else{
setRadarPaneError(paneElement,'레이더 이미지를 불러오지 못했습니다.');
}

setRadarPageLoading(paneElement,false);
paneElement.dataset.loadingUrl='';
refreshRadarFrameLoadState(frameIndex);
});
});
}

function getRadarTimelineLabelLeftPercent(index,count){
if(count<=1){
return 50;
}

return ((Number(index)+0.5)/count)*100;
}

function createRadarTimelineLabel(type,index,count,frame){
let label=document.createElement('div');
let isDate=type==='date';
label.className='compare-active-label '+(isDate?'compare-active-time':'compare-active-lead');
label.textContent=isDate ? formatRadarDateLabel(frame) : formatRadarTimeLabel(frame);

if(index===0){
label.classList.add('edge-start');
}

if(index===count-1){
label.classList.add('edge-end');
}

let leftPercent=getRadarTimelineLabelLeftPercent(index,count)+'%';
label.style.left=leftPercent;
label.style.setProperty('--label-left',leftPercent);
return label;
}

function bindRadarTimelinePointer(track){
let dragging=false;

function indexFromEvent(event){
let rect=track.getBoundingClientRect();
let x=Math.max(0,Math.min(event.clientX-rect.left,rect.width));
let count=radarState.frames.length || 1;
return Math.max(0,Math.min(count-1,Math.floor((x/Math.max(1,rect.width))*count)));
}

function apply(event){
setRadarActiveIndex(indexFromEvent(event));
}

track.onpointerdown=event=>{
event.preventDefault();
track.focus?.({preventScroll:true});
dragging=true;
track.setPointerCapture?.(event.pointerId);
apply(event);
};

track.onpointermove=event=>{
if(!dragging){
return;
}

apply(event);
};

track.onpointerup=event=>{
dragging=false;
track.releasePointerCapture?.(event.pointerId);
};

track.onpointercancel=()=>{
dragging=false;
};
}

function bindRadarTimelineHover(segment,list){
segment.onpointerenter=()=>{
segment.classList.add('hover-sync','hover-time-label','hover-lead-label');
list.classList.add('is-hovering');
};
segment.onpointerleave=()=>{
segment.classList.remove('hover-sync','hover-time-label','hover-lead-label');
list.classList.remove('is-hovering');
};
}

function moveRadarSelection(offset){
setRadarActiveIndex(radarState.activeIndex+offset);
}

function handleRadarKeydown(event){
let active=document.activeElement;
let tag=active?.tagName;

if(tag==='INPUT' || tag==='SELECT' || tag==='TEXTAREA'){
return;
}

if(event.key==='ArrowLeft' || event.key==='ArrowUp'){
event.preventDefault();
moveRadarSelection(-1);
return;
}

if(event.key==='ArrowRight' || event.key==='ArrowDown'){
event.preventDefault();
moveRadarSelection(1);
}
}

function renderRadarTimeline(){
let timeline=radarState.timeline;

if(!timeline){
return;
}

timeline.innerHTML='';
timeline.style.setProperty('--forecast-count',String(radarState.frames.length || 1));

let list=document.createElement('div');
list.className='compare-timeline-list single-timeline-list radar-timeline-list';

let row=document.createElement('div');
row.className='compare-timeline-row single-timeline-row radar-timeline-row';

let info=document.createElement('div');
info.className='compare-row-info';
info.innerHTML='<div class="compare-row-model">RADAR</div>';

let track=document.createElement('div');
track.className='compare-track single-forecast-track radar-track';
track.tabIndex=0;
track.setAttribute('role','slider');
track.setAttribute('aria-label','레이더 시각 슬라이더');
track.setAttribute('aria-valuemin','0');
track.setAttribute('aria-valuemax',String(Math.max(0,radarState.frames.length-1)));
track.setAttribute('aria-valuenow',String(radarState.activeIndex));
track.style.gridTemplateColumns=`repeat(${Math.max(1,radarState.frames.length)}, minmax(4px, 1fr))`;

radarState.frames.forEach((frame,index)=>{
let seg=document.createElement('button');
seg.type='button';
let classes=['compare-segment','forecast-segment',`state-${getRadarFrameLoadState(index)}`];
if(index===radarState.activeIndex){
classes.push('active','active-time-label','active-lead-label');
}
if(index===0){
classes.push('edge-start');
}
if(index===radarState.frames.length-1){
classes.push('edge-end');
}
seg.className=classes.join(' ');
seg.dataset.index=String(index);
seg.dataset.time=formatRadarDateLabel(frame);
seg.dataset.lead=formatRadarTimeLabel(frame);
seg.title=`${seg.dataset.time} / ${seg.dataset.lead}`;
seg.onclick=()=>setRadarActiveIndex(index);
bindRadarTimelineHover(seg,list);
track.appendChild(seg);
});

let activeFrame=radarState.frames[radarState.activeIndex];
let count=radarState.frames.length || 1;
if(activeFrame){
track.appendChild(createRadarTimelineLabel('date',radarState.activeIndex,count,activeFrame));
track.appendChild(createRadarTimelineLabel('time',radarState.activeIndex,count,activeFrame));
}

bindRadarTimelinePointer(track);

row.appendChild(info);
row.appendChild(track);
list.appendChild(row);
timeline.appendChild(list);
}

function updateRadarTimelineActiveState(){
let timeline=radarState.timeline;

if(!timeline){
return;
}

let count=radarState.frames.length || 1;
let activeFrame=radarState.frames[radarState.activeIndex];
let track=timeline.querySelector('.radar-track');

timeline.querySelectorAll('.radar-track .compare-segment').forEach(seg=>{
let isActive=Number(seg.dataset.index)===radarState.activeIndex;
seg.classList.toggle('active',isActive);
seg.classList.toggle('active-time-label',isActive);
seg.classList.toggle('active-lead-label',isActive);
});

timeline.querySelectorAll('.radar-track .compare-active-label').forEach(label=>{
label.remove();
});

if(track){
track.setAttribute('aria-valuenow',String(radarState.activeIndex));
}

if(track && activeFrame){
track.appendChild(createRadarTimelineLabel('date',radarState.activeIndex,count,activeFrame));
track.appendChild(createRadarTimelineLabel('time',radarState.activeIndex,count,activeFrame));
}
}

function updateRadarTimeLabel(){
let frame=radarState.frames[radarState.activeIndex];

if(radarState.timeLabel){
radarState.timeLabel.textContent=frame ? formatRadarFrameLabel(frame) : '';
}
}

function refreshRadarPaneImages(){
loadActiveRadarFrameImages();
}

function setRadarActiveIndex(index){
let nextIndex=Math.max(0,Math.min(Number(index)||0,radarState.frames.length-1));

if(nextIndex===radarState.activeIndex){
return;
}

radarState.activeIndex=nextIndex;
updateRadarTimelineActiveState();
updateRadarTimeLabel();
refreshRadarPaneImages();
}

function rebuildRadarTimelineAroundBase({preserveCache=true}={}){
buildRadarFrames();
radarState.activeIndex=Math.max(0,radarState.frames.length-1);

if(preserveCache){
radarState.preloadRunId+=1;
resetRadarFrameLoadStates();
refreshAllRadarFrameLoadStates();
}
else{
resetRadarImageCache();
}

renderRadarTimeline();
updateRadarTimeLabel();
renderRadarPanes();
preloadRadarImages();
}

function syncRadarDateTimeInput(){
if(radarState.dateInput){
radarState.dateInput.value=formatDateTimeDisplay(radarState.baseTime);
}
}

function setRadarBaseTime(date){
radarState.baseTime=roundDateToFiveMinutes(date);
syncRadarDateTimeInput();
rebuildRadarTimelineAroundBase();
}

function shiftRadarBaseTime(minutes){
setRadarBaseTime(new Date(radarState.baseTime.getTime()+minutes*60*1000));
}

function setRadarNow(){
radarState.baseTime=getLatestPublishedRadarTime();
syncRadarDateTimeInput();
rebuildRadarTimelineAroundBase();
}

function stopRadarLoop(){
if(radarState.playTimer){
clearInterval(radarState.playTimer);
radarState.playTimer=null;
}

radarState.isPlaying=false;
updateRadarPlayButton();
}

function startRadarLoop(){
stopRadarLoop();
radarState.isPlaying=true;
updateRadarPlayButton();
requestRadarPlaybackPreload({force:true});
radarState.playTimer=setInterval(()=>{
let next=getNextRadarLoopIndex();

if(next===radarState.activeIndex){
requestRadarPlaybackPreload();
return;
}

setRadarActiveIndex(next);
},700);
}

function toggleRadarLoop(){
if(radarState.isPlaying){
stopRadarLoop();
}
else{
startRadarLoop();
}
}

function updateRadarPlayButton(){
if(radarState.playButton){
radarState.playButton.textContent=radarState.isPlaying?'Ⅱ':'▶';
radarState.playButton.title=radarState.isPlaying?'동화 정지':'동화 시작';
radarState.playButton.classList.toggle('is-playing',radarState.isPlaying);
}
}

function stopRadarAutoRefresh(){
if(radarState.autoRefreshTimer){
clearInterval(radarState.autoRefreshTimer);
radarState.autoRefreshTimer=null;
}

radarState.autoRefreshEnabled=false;
updateRadarAutoRefreshButton();
}

function startRadarAutoRefresh(){
stopRadarAutoRefresh();
radarState.autoRefreshEnabled=true;
radarState.autoRefreshTimer=setInterval(setRadarNow,5*60*1000);
updateRadarAutoRefreshButton();
}

function toggleRadarAutoRefresh(){
if(radarState.autoRefreshEnabled){
stopRadarAutoRefresh();
}
else{
startRadarAutoRefresh();
}
}

function syncRadarAfterResume(){
if(!radarState.root){
return;
}

updateRadarTimelineActiveState();
updateRadarTimeLabel();
refreshRadarPaneImages();
preloadRadarImages();
refreshRadarCacheInBackground();
}

function updateRadarAutoRefreshButton(){
if(!radarState.autoRefreshButton){
return;
}

radarState.autoRefreshButton.textContent=radarState.autoRefreshEnabled?'자동갱신 ON':'자동갱신 OFF';
radarState.autoRefreshButton.title='5분마다 NOW 자동 실행';
radarState.autoRefreshButton.classList.toggle('active',radarState.autoRefreshEnabled);
}

function createSelect(options,value,onchange){
let select=document.createElement('select');

options.forEach(optionData=>{
let option=document.createElement('option');
option.value=String(optionData.value);
option.textContent=optionData.label;
select.appendChild(option);
});

select.value=String(value);
select.onchange=()=>onchange(select.value);
return select;
}

function createRadarInlineField(labelLines,control){
let label=document.createElement('label');
label.className='radar-inline-field';

let span=document.createElement('span');
span.className='radar-inline-label';
span.innerHTML=labelLines.map(line=>`<span>${line}</span>`).join('');

label.appendChild(span);
label.appendChild(control);
return label;
}

function createRadarCheckbox(key,labelText){
let label=document.createElement('label');
label.className='radar-check';

let input=document.createElement('input');
input.type='checkbox';
input.checked=radarState.common[key]==='1';
input.onchange=()=>{
radarState.common[key]=input.checked?'1':'0';
reloadRadarImagesForCurrentSettings();
};

let span=document.createElement('span');
span.textContent=labelText;

label.appendChild(input);
label.appendChild(span);
return label;
}

function createRadarWindControl(){
let control=document.createElement('div');
control.className='radar-wind-control';

let checkLabel=document.createElement('div');
checkLabel.className='radar-check radar-wind-button';
checkLabel.setAttribute('role','button');
checkLabel.setAttribute('aria-expanded',String(radarState.wind.open));
checkLabel.tabIndex=0;
checkLabel.onclick=event=>{
event.stopPropagation();
checkbox.checked=!radarState.wind.enabled;
setRadarWindEnabled(checkbox.checked);
};
checkLabel.onkeydown=event=>{
if(event.key==='Enter' || event.key===' '){
event.preventDefault();
checkLabel.click();
}
};

let checkbox=document.createElement('input');
checkbox.type='checkbox';
checkbox.checked=radarState.wind.enabled;
checkbox.onclick=event=>{
event.stopPropagation();
};
checkbox.onchange=()=>{
setRadarWindEnabled(checkbox.checked);
};

let checkText=document.createElement('span');
checkText.textContent='바람';
let chevron=document.createElement('span');
chevron.className='radar-wind-chevron';
chevron.setAttribute('role','button');
chevron.setAttribute('aria-label','바람 설정');
chevron.tabIndex=0;
chevron.onclick=event=>{
event.stopPropagation();
setPanelOpen(!radarState.wind.open);
};
chevron.onkeydown=event=>{
if(event.key==='Enter' || event.key===' '){
event.preventDefault();
event.stopPropagation();
setPanelOpen(!radarState.wind.open);
}
};
let toggleMain=document.createElement('span');
toggleMain.className='radar-overlay-toggle-main';
toggleMain.appendChild(checkbox);
toggleMain.appendChild(checkText);
checkLabel.appendChild(toggleMain);
checkLabel.appendChild(chevron);


let panel=document.createElement('div');
panel.className='radar-wind-panel'+(radarState.wind.open ? '' : ' hidden');
panel.onclick=event=>event.stopPropagation();
let pointerStartedInsidePanel=false;
let markPointerInsidePanel=()=>{pointerStartedInsidePanel=true;};
panel.addEventListener('pointerdown',markPointerInsidePanel);
panel.addEventListener('mousedown',markPointerInsidePanel);

let pendingWindMode=radarState.wind.mode;
let pendingWindSource=radarState.wind.source;
let pendingWindHeight=radarState.wind.height;
let modeRadios=[];
let sourceSelect=null;
let heightInput=null;

function resetPendingWindSettings(){
pendingWindMode=radarState.wind.mode;
pendingWindSource=radarState.wind.source;
pendingWindHeight=radarState.wind.height;

modeRadios.forEach(radio=>{
radio.checked=radio.value===pendingWindMode;
});

if(sourceSelect){
sourceSelect.value=pendingWindSource;
}

if(heightInput){
heightInput.value=pendingWindHeight;
}
}

function applyPendingWindSettings(){
let selectedMode=modeRadios.find(radio=>radio.checked)?.value || pendingWindMode;
let selectedSource=sourceSelect?.value || pendingWindSource;
let selectedHeight=heightInput?.value || pendingWindHeight;
let nextMode=normalizeRadarWindMode(selectedMode);
let nextSource=normalizeRadarWindSource(selectedSource);
let nextHeight=normalizeRadarWindHeight(selectedHeight);
let changed=(
radarState.wind.mode!==nextMode ||
radarState.wind.source!==nextSource ||
radarState.wind.height!==nextHeight
);

radarState.wind.mode=nextMode;
radarState.wind.source=nextSource;
radarState.wind.height=nextHeight;
pendingWindMode=nextMode;
pendingWindSource=nextSource;
pendingWindHeight=nextHeight;

if(changed && radarState.wind.enabled){
applyRadarWindSettings();
}
}

function positionPanel(){
let rect=checkLabel.getBoundingClientRect();
let width=panel.offsetWidth || 190;
let left=Math.min(Math.max(8,rect.left),window.innerWidth-width-8);
panel.style.left=`${left}px`;
panel.style.top=`${rect.bottom+5}px`;
}

function setPanelOpen(open){
let nextOpen=!!open;
let wasOpen=radarState.wind.open;

if(nextOpen && !radarState.wind.open){
notifyRadarOverlayDropdownOpen('wind');
resetPendingWindSettings();
}

if(!nextOpen && wasOpen){
applyPendingWindSettings();
}

radarState.wind.open=nextOpen;
panel.classList.toggle('hidden',!radarState.wind.open);
checkLabel.setAttribute('aria-expanded',String(radarState.wind.open));
if(radarState.wind.open){
positionPanel();
requestAnimationFrame(positionPanel);
}
}

document.addEventListener('click',()=>{
setPanelOpen(false);
});
document.addEventListener('radarOverlayDropdownOpen',event=>{
if(event.detail?.source!=='wind'){
setPanelOpen(false);
}
});
control.addEventListener('focusout',()=>{
requestAnimationFrame(()=>{
let shouldKeepOpen=control.contains(document.activeElement) || pointerStartedInsidePanel;
pointerStartedInsidePanel=false;

if(radarState.wind.open && !shouldKeepOpen){
setPanelOpen(false);
}
});
});

let modeGroup=document.createElement('div');
modeGroup.className='radar-wind-mode-group';

[
{value:'barb',label:'바람깃'},
{value:'vector',label:'바람벡터'}
].forEach(option=>{
let label=document.createElement('label');
label.className='radar-wind-option';

let radio=document.createElement('input');
radio.type='radio';
radio.name='radarWindMode';
radio.value=option.value;
radio.checked=radarState.wind.mode===option.value;
radio.onchange=()=>{
if(radio.checked){
pendingWindMode=option.value;
}
};
modeRadios.push(radio);

let span=document.createElement('span');
span.textContent=option.label;
label.appendChild(radio);
label.appendChild(span);
modeGroup.appendChild(label);
});

sourceSelect=createSelect(
[
{value:'WISSDOM',label:'WISSDOM'},
{value:'KLAPS',label:'KLAPS'},
{value:'VDAPS',label:'VDAPS'}
],
radarState.wind.source,
value=>{
pendingWindSource=value;
}
);
sourceSelect.className='radar-wind-source-select';

heightInput=document.createElement('input');
heightInput.type='number';
heightInput.className='radar-wind-height-input';
heightInput.value=radarState.wind.height;
heightInput.min='0';
heightInput.step='10';
heightInput.oninput=()=>{pendingWindHeight=heightInput.value;};
heightInput.onchange=()=>{pendingWindHeight=heightInput.value;};
heightInput.onblur=()=>{pendingWindHeight=heightInput.value;};
heightInput.onkeydown=event=>{
if(event.key==='Enter'){
event.currentTarget.blur();
}
};

let heightLabel=document.createElement('label');
heightLabel.className='radar-wind-height-label';
let heightUnit=document.createElement('span');
heightUnit.className='radar-wind-height-unit';
heightUnit.textContent='m';
heightLabel.appendChild(heightInput);
heightLabel.appendChild(heightUnit);

let detailRow=document.createElement('div');
detailRow.className='radar-wind-detail-row';
detailRow.appendChild(sourceSelect);
detailRow.appendChild(heightLabel);

panel.appendChild(modeGroup);
panel.appendChild(detailRow);

control.appendChild(checkLabel);
control.appendChild(panel);
return control;
}

function createRadarStationControl(){
let control=document.createElement('div');
control.className='radar-wind-control radar-station-control';
let pendingDensity=radarState.station.density;
let pendingLabel=radarState.station.label;

let checkLabel=document.createElement('div');
checkLabel.className='radar-check radar-wind-button radar-station-button';
checkLabel.setAttribute('role','button');
checkLabel.setAttribute('aria-expanded',String(radarState.station.open));
checkLabel.tabIndex=0;
checkLabel.onclick=event=>{
event.stopPropagation();
checkbox.checked=!radarState.station.enabled;
setRadarStationEnabled(checkbox.checked);
};
checkLabel.onkeydown=event=>{
if(event.key==='Enter' || event.key===' '){
event.preventDefault();
checkLabel.click();
}
};

let checkbox=document.createElement('input');
checkbox.type='checkbox';
checkbox.checked=radarState.station.enabled;
checkbox.onclick=event=>event.stopPropagation();
checkbox.onchange=()=>setRadarStationEnabled(checkbox.checked);

let checkText=document.createElement('span');
checkText.textContent='지점';

let chevron=document.createElement('span');
chevron.className='radar-wind-chevron';
chevron.setAttribute('role','button');
chevron.setAttribute('aria-label','지점 설정');
chevron.tabIndex=0;
chevron.onclick=event=>{
event.stopPropagation();
setPanelOpen(!radarState.station.open);
};
chevron.onkeydown=event=>{
if(event.key==='Enter' || event.key===' '){
event.preventDefault();
event.stopPropagation();
setPanelOpen(!radarState.station.open);
}
};

let toggleMain=document.createElement('span');
toggleMain.className='radar-overlay-toggle-main';
toggleMain.appendChild(checkbox);
toggleMain.appendChild(checkText);
checkLabel.appendChild(toggleMain);
checkLabel.appendChild(chevron);

let panel=document.createElement('div');
panel.className='radar-wind-panel radar-station-panel'+(radarState.station.open ? '' : ' hidden');
panel.onclick=event=>event.stopPropagation();
let pointerStartedInsidePanel=false;
let markPointerInsidePanel=()=>{pointerStartedInsidePanel=true;};
panel.addEventListener('pointerdown',markPointerInsidePanel);
panel.addEventListener('mousedown',markPointerInsidePanel);

function positionPanel(){
let rect=checkLabel.getBoundingClientRect();
let width=panel.offsetWidth || 210;
let left=Math.min(Math.max(8,rect.left),window.innerWidth-width-8);
panel.style.left=`${left}px`;
panel.style.top=`${rect.bottom+5}px`;
}

function commitPendingSettings(){
let selectedDensity=densityGroup?.querySelector('input[name="radarStationDensity"]:checked')?.value || pendingDensity;
let selectedLabel=labelSelect?.value || pendingLabel;
let nextDensity=normalizeRadarStationDensity(selectedDensity);
let nextLabel=normalizeRadarStationLabel(selectedLabel);
let changed=radarState.station.density!==nextDensity || radarState.station.label!==nextLabel;

radarState.station.density=nextDensity;
radarState.station.label=nextLabel;
pendingDensity=nextDensity;
pendingLabel=nextLabel;

if(changed && radarState.station.enabled){
applyRadarStationSettings();
}
}

function setPanelOpen(open){
let nextOpen=!!open;
let wasOpen=radarState.station.open;

if(nextOpen && !wasOpen){
notifyRadarOverlayDropdownOpen('station');
}

radarState.station.open=nextOpen;

if(!nextOpen && wasOpen){
commitPendingSettings();
}

panel.classList.toggle('hidden',!radarState.station.open);
checkLabel.setAttribute('aria-expanded',String(radarState.station.open));

if(radarState.station.open){
pendingDensity=radarState.station.density;
pendingLabel=radarState.station.label;
syncPendingControls();
positionPanel();
requestAnimationFrame(positionPanel);
}
}

document.addEventListener('click',()=>setPanelOpen(false));
document.addEventListener('radarOverlayDropdownOpen',event=>{
if(event.detail?.source!=='station'){
setPanelOpen(false);
}
});
control.addEventListener('focusout',()=>{
requestAnimationFrame(()=>{
let shouldKeepOpen=control.contains(document.activeElement) || pointerStartedInsidePanel;
pointerStartedInsidePanel=false;

if(radarState.station.open && !shouldKeepOpen){
setPanelOpen(false);
}
});
});

let densityGroup=document.createElement('div');
densityGroup.className='radar-wind-mode-group radar-station-density-group';

[
{value:'sparse',label:'간벌'},
{value:'full',label:'전체'}
].forEach(option=>{
let label=document.createElement('label');
label.className='radar-wind-option';

let radio=document.createElement('input');
radio.type='radio';
radio.name='radarStationDensity';
radio.value=option.value;
radio.checked=pendingDensity===option.value;
radio.onchange=()=>{
if(radio.checked){
pendingDensity=option.value;
}
};

let span=document.createElement('span');
span.textContent=option.label;
label.appendChild(radio);
label.appendChild(span);
densityGroup.appendChild(label);
});

let labelSelect=createSelect(
RADAR_STATION_OPTIONS,
pendingLabel,
value=>{
pendingLabel=value;
}
);
labelSelect.className='radar-wind-source-select radar-station-label-select';

function syncPendingControls(){
densityGroup.querySelectorAll('input[name="radarStationDensity"]').forEach(radio=>{
radio.checked=radio.value===pendingDensity;
});
labelSelect.value=pendingLabel;
}

panel.appendChild(densityGroup);
panel.appendChild(labelSelect);
control.appendChild(checkLabel);
control.appendChild(panel);
return control;
}

function createRadarLightningControl(){
let control=document.createElement('div');
control.className='radar-wind-control radar-lightning-control';
let pendingType=radarState.lightning.type;
let pendingInterval=radarState.lightning.interval;

let checkLabel=document.createElement('div');
checkLabel.className='radar-check radar-wind-button radar-lightning-button';
checkLabel.setAttribute('role','button');
checkLabel.setAttribute('aria-expanded',String(radarState.lightning.open));
checkLabel.tabIndex=0;
checkLabel.onclick=event=>{
event.stopPropagation();
checkbox.checked=!radarState.lightning.enabled;
setRadarLightningEnabled(checkbox.checked);
};
checkLabel.onkeydown=event=>{
if(event.key==='Enter' || event.key===' '){
event.preventDefault();
checkLabel.click();
}
};

let checkbox=document.createElement('input');
checkbox.type='checkbox';
checkbox.checked=radarState.lightning.enabled;
checkbox.onclick=event=>event.stopPropagation();
checkbox.onchange=()=>setRadarLightningEnabled(checkbox.checked);

let checkText=document.createElement('span');
checkText.textContent='낙뢰';

let chevron=document.createElement('span');
chevron.className='radar-wind-chevron';
chevron.setAttribute('role','button');
chevron.setAttribute('aria-label','낙뢰 설정');
chevron.tabIndex=0;
chevron.onclick=event=>{
event.stopPropagation();
setPanelOpen(!radarState.lightning.open);
};
chevron.onkeydown=event=>{
if(event.key==='Enter' || event.key===' '){
event.preventDefault();
event.stopPropagation();
setPanelOpen(!radarState.lightning.open);
}
};

let toggleMain=document.createElement('span');
toggleMain.className='radar-overlay-toggle-main';
toggleMain.appendChild(checkbox);
toggleMain.appendChild(checkText);
checkLabel.appendChild(toggleMain);
checkLabel.appendChild(chevron);

let panel=document.createElement('div');
panel.className='radar-wind-panel radar-lightning-panel'+(radarState.lightning.open ? '' : ' hidden');
panel.onclick=event=>event.stopPropagation();
let pointerStartedInsidePanel=false;
let markPointerInsidePanel=()=>{pointerStartedInsidePanel=true;};
panel.addEventListener('pointerdown',markPointerInsidePanel);
panel.addEventListener('mousedown',markPointerInsidePanel);

function positionPanel(){
let rect=checkLabel.getBoundingClientRect();
let width=panel.offsetWidth || 190;
let left=Math.min(Math.max(8,rect.left),window.innerWidth-width-8);
panel.style.left=`${left}px`;
panel.style.top=`${rect.bottom+5}px`;
}

function commitPendingSettings(){
let selectedType=typeGroup?.querySelector('input[name="radarLightningType"]:checked')?.value || pendingType;
let selectedInterval=intervalInput?.value || pendingInterval;
let nextType=normalizeRadarLightningType(selectedType);
let nextInterval=normalizeRadarLightningInterval(selectedInterval);
let changed=radarState.lightning.type!==nextType || radarState.lightning.interval!==nextInterval;

radarState.lightning.type=nextType;
radarState.lightning.interval=nextInterval;
pendingType=nextType;
pendingInterval=nextInterval;

if(changed && radarState.lightning.enabled){
applyRadarLightningSettings();
}
}

function setPanelOpen(open){
let nextOpen=!!open;
let wasOpen=radarState.lightning.open;

if(nextOpen && !wasOpen){
notifyRadarOverlayDropdownOpen('lightning');
}

radarState.lightning.open=nextOpen;

if(!nextOpen && wasOpen){
commitPendingSettings();
}

panel.classList.toggle('hidden',!radarState.lightning.open);
checkLabel.setAttribute('aria-expanded',String(radarState.lightning.open));

if(radarState.lightning.open){
pendingType=radarState.lightning.type;
pendingInterval=radarState.lightning.interval;
syncPendingControls();
positionPanel();
requestAnimationFrame(positionPanel);
}
}

document.addEventListener('click',()=>setPanelOpen(false));
document.addEventListener('radarOverlayDropdownOpen',event=>{
if(event.detail?.source!=='lightning'){
setPanelOpen(false);
}
});
control.addEventListener('focusout',()=>{
requestAnimationFrame(()=>{
let shouldKeepOpen=control.contains(document.activeElement) || pointerStartedInsidePanel;
pointerStartedInsidePanel=false;

if(radarState.lightning.open && !shouldKeepOpen){
setPanelOpen(false);
}
});
});

let typeGroup=document.createElement('div');
typeGroup.className='radar-wind-mode-group radar-lightning-type-group';

RADAR_LIGHTNING_TYPES.forEach(option=>{
let label=document.createElement('label');
label.className='radar-wind-option';

let radio=document.createElement('input');
radio.type='radio';
radio.name='radarLightningType';
radio.value=option.value;
radio.checked=pendingType===option.value;
radio.onchange=()=>{
if(radio.checked){
pendingType=option.value;
}
};

let span=document.createElement('span');
span.textContent=option.label;
label.appendChild(radio);
label.appendChild(span);
typeGroup.appendChild(label);
});

let intervalInput=document.createElement('input');
intervalInput.type='number';
intervalInput.className='radar-wind-height-input radar-lightning-interval-input';
intervalInput.value=pendingInterval;
intervalInput.min='5';
intervalInput.step='5';
intervalInput.oninput=()=>{
pendingInterval=intervalInput.value;
};
intervalInput.onchange=()=>{
pendingInterval=normalizeRadarLightningInterval(intervalInput.value);
intervalInput.value=pendingInterval;
};
intervalInput.onblur=intervalInput.onchange;
intervalInput.onkeydown=event=>{
if(event.key==='Enter'){
event.currentTarget.blur();
}
};

let intervalLabel=document.createElement('label');
intervalLabel.className='radar-wind-height-label radar-lightning-interval-label';
let intervalUnit=document.createElement('span');
intervalUnit.className='radar-wind-height-unit';
intervalUnit.textContent='분';
intervalLabel.appendChild(intervalInput);
intervalLabel.appendChild(intervalUnit);

function syncPendingControls(){
typeGroup.querySelectorAll('input[name="radarLightningType"]').forEach(radio=>{
radio.checked=radio.value===pendingType;
});
intervalInput.value=pendingInterval;
}

panel.appendChild(typeGroup);
panel.appendChild(intervalLabel);
control.appendChild(checkLabel);
control.appendChild(panel);
return control;
}

function createRadarDatePickerMonth(year,month){
let out=new Date(0,0,1);
out.setFullYear(Number(year) || new Date().getFullYear(),Number(month) || 0,1);
out.setHours(0,0,0,0);
return out;
}

function getRadarDatePickerMaxYear(){
return new Date().getFullYear();
}

function clampRadarDatePickerVisibleMonth(date){
let maxYear=getRadarDatePickerMaxYear();
let year=date.getFullYear();
let month=date.getMonth();

if(year>maxYear){
year=maxYear;
month=11;
}

if(year<1){
year=1;
month=0;
}

return createRadarDatePickerMonth(year,month);
}

function getRadarDatePickerYearRange(centerYear){
let maxYear=getRadarDatePickerMaxYear();
let year=Math.max(1,Math.min(maxYear,Number(centerYear) || maxYear));
return {
start:Math.max(1,year-10),
end:Math.min(maxYear,year+10)
};
}

function createRadarDateTimeControl(dateInput){
let control=document.createElement('div');
control.className='radar-datetime-picker-control';

let timeToggle=document.createElement('button');
timeToggle.type='button';
timeToggle.className='radar-time-picker-toggle';
timeToggle.setAttribute('aria-label','날짜와 시각 선택');
timeToggle.setAttribute('aria-expanded','false');

let panel=document.createElement('div');
panel.className='radar-datetime-picker-panel hidden';
panel.onclick=event=>event.stopPropagation();

let visibleMonth=clampRadarDatePickerVisibleMonth(createRadarDatePickerMonth(radarState.baseTime.getFullYear(),radarState.baseTime.getMonth()));
let pendingDate=null;
let pendingTime=null;

function getCurrentDateParts(){
let normalized=pendingDate || normalizeDateTimeText(dateInput.value,radarState.baseTime).date;
let [year,month,day]=normalized.split('-').map(Number);
return {year,month,day,normalized};
}

function getCurrentTimeParts(){
let normalized=pendingTime || normalizeRadarTimeValue(normalizeDateTimeText(dateInput.value,radarState.baseTime).time);

if(normalized){
return {hour:normalized.hour,minute:normalized.minute};
}

return {
hour:radarState.baseTime.getHours(),
minute:Math.round(radarState.baseTime.getMinutes()/5)*5
};
}

function queueDate(year,month,day){
let selected=new Date(year,month-1,day,radarState.baseTime.getHours(),radarState.baseTime.getMinutes(),0,0);
pendingDate=formatDateInput(selected);
let currentTime=getCurrentTimeParts();
dateInput.value=`${formatDateDisplayInput(selected)} ${pad2(currentTime.hour)}:${pad2(currentTime.minute)}`;
renderPanel();
}

function queueTime(hour,minute){
pendingTime={hour,minute};
let currentDate=pendingDate || getCurrentDateParts().normalized;
dateInput.value=`${formatNormalizedDateDisplay(currentDate)} ${pad2(hour)}:${pad2(minute)}`;
}

function commitPendingDateTime(){
if(!pendingDate && !pendingTime){
return;
}

let currentDateTime=normalizeDateTimeText(dateInput.value,radarState.baseTime);
let nextDate=pendingDate || currentDateTime.date;
let nextTime=pendingTime ? `${pad2(pendingTime.hour)}:${pad2(pendingTime.minute)}` : currentDateTime.time;
pendingDate=null;
pendingTime=null;
let normalizedTime=normalizeRadarTimeValue(nextTime)?.text || formatTimeInput(radarState.baseTime);
dateInput.value=`${formatNormalizedDateDisplay(nextDate)} ${normalizedTime}`;
setRadarBaseTime(parseLocalDateTime(dateInput.value));
}

function renderCalendar(){
visibleMonth=clampRadarDatePickerVisibleMonth(visibleMonth);
let selected=getCurrentDateParts();
let year=visibleMonth.getFullYear();
let month=visibleMonth.getMonth();
let calendar=document.createElement('div');
calendar.className='radar-date-picker-calendar';

let header=document.createElement('div');
header.className='radar-date-picker-header';

let prev=document.createElement('button');
prev.type='button';
prev.className='radar-date-picker-nav';
prev.textContent='‹';
prev.onclick=event=>{
event.stopPropagation();
visibleMonth=clampRadarDatePickerVisibleMonth(createRadarDatePickerMonth(year,month-1));
renderPanel();
};

let title=document.createElement('div');
title.className='radar-date-picker-title';

let yearSelect=document.createElement('select');
yearSelect.className='radar-date-picker-year-select';
let yearRange=getRadarDatePickerYearRange(year);
for(let optionYear=yearRange.start;optionYear<=yearRange.end;optionYear++){
let option=document.createElement('option');
option.value=String(optionYear);
option.textContent=String(optionYear);
yearSelect.appendChild(option);
}
yearSelect.value=String(year);
yearSelect.onchange=event=>{
event.stopPropagation();
visibleMonth=clampRadarDatePickerVisibleMonth(createRadarDatePickerMonth(Number(yearSelect.value),month));
renderPanel();
};

let monthSelect=document.createElement('select');
monthSelect.className='radar-date-picker-month-select';
for(let optionMonth=0;optionMonth<12;optionMonth++){
let option=document.createElement('option');
option.value=String(optionMonth);
option.textContent=`${pad2(optionMonth+1)}월`;
monthSelect.appendChild(option);
}
monthSelect.value=String(month);
monthSelect.onchange=event=>{
event.stopPropagation();
visibleMonth=clampRadarDatePickerVisibleMonth(createRadarDatePickerMonth(year,Number(monthSelect.value)));
renderPanel();
};

title.appendChild(yearSelect);
title.appendChild(monthSelect);

let next=document.createElement('button');
next.type='button';
next.className='radar-date-picker-nav';
next.textContent='›';
next.disabled=year>=getRadarDatePickerMaxYear() && month>=11;
next.onclick=event=>{
event.stopPropagation();
if(next.disabled){
return;
}
visibleMonth=clampRadarDatePickerVisibleMonth(createRadarDatePickerMonth(year,month+1));
renderPanel();
};

header.appendChild(prev);
header.appendChild(title);
header.appendChild(next);
calendar.appendChild(header);

let grid=document.createElement('div');
grid.className='radar-date-picker-grid';

['일','월','화','수','목','금','토'].forEach((label,index)=>{
let weekday=document.createElement('div');
weekday.className='radar-date-picker-weekday'+(index===0 || index===6 ? ' weekend' : '');
weekday.textContent=label;
grid.appendChild(weekday);
});

let firstDay=new Date(year,month,1).getDay();
let daysInMonth=new Date(year,month+1,0).getDate();

for(let i=0;i<firstDay;i++){
let blank=document.createElement('span');
blank.className='radar-date-picker-blank';
grid.appendChild(blank);
}

for(let day=1;day<=daysInMonth;day++){
let dayButton=document.createElement('button');
dayButton.type='button';
dayButton.className='radar-date-picker-day';
dayButton.textContent=String(day);

let dayOfWeek=new Date(year,month,day).getDay();
if(dayOfWeek===0 || dayOfWeek===6){
dayButton.classList.add('weekend');
}

if(selected.year===year && selected.month===month+1 && selected.day===day){
dayButton.classList.add('selected');
}

dayButton.onclick=event=>{
event.stopPropagation();
queueDate(year,month+1,day);
};
grid.appendChild(dayButton);
}

calendar.appendChild(grid);
return calendar;
}

function renderTimePicker(){
let current=getCurrentTimeParts();
let wrap=document.createElement('div');
wrap.className='radar-datetime-time-section';

let label=document.createElement('div');
label.className='radar-datetime-time-label';
label.textContent='시각';

let hourInput=document.createElement('input');
hourInput.type='number';
hourInput.className='radar-time-picker-number radar-time-hour-input';
hourInput.min='0';
hourInput.max='23';
hourInput.step='1';
hourInput.value=pad2(current.hour);

let colon=document.createElement('span');
colon.className='radar-datetime-time-colon';
colon.textContent=':';

let minuteInput=document.createElement('input');
minuteInput.type='number';
minuteInput.className='radar-time-picker-number radar-time-minute-input';
minuteInput.min='0';
minuteInput.max='55';
minuteInput.step='5';
minuteInput.value=pad2(current.minute);

function clampTimeInputs(){
let hour=Math.max(0,Math.min(23,Number.parseInt(hourInput.value,10) || 0));
let minute=Math.max(0,Math.min(55,Number.parseInt(minuteInput.value,10) || 0));
minute=Math.round(minute/5)*5;
hourInput.value=pad2(hour);
minuteInput.value=pad2(minute);
queueTime(hour,minute);
}

hourInput.onchange=clampTimeInputs;
hourInput.onblur=clampTimeInputs;
minuteInput.onchange=clampTimeInputs;
minuteInput.onblur=clampTimeInputs;
[hourInput,minuteInput].forEach(input=>{
input.onkeydown=event=>{
if(event.key==='Enter'){
event.currentTarget.blur();
}
};
});

wrap.appendChild(label);
wrap.appendChild(hourInput);
wrap.appendChild(colon);
wrap.appendChild(minuteInput);
return wrap;
}

function renderPanel(){
panel.innerHTML='';
panel.appendChild(renderCalendar());
panel.appendChild(renderTimePicker());
}

function positionPanel(){
let dateRect=dateInput.getBoundingClientRect();
let controlRect=control.getBoundingClientRect();
let width=Math.round(controlRect.right-dateRect.left);
let left=Math.min(Math.max(8,dateRect.left),window.innerWidth-width-8);
panel.style.left=`${left}px`;
panel.style.top=`${controlRect.bottom+1}px`;
panel.style.width=`${width}px`;
}

function setPanelOpen(open){
let isOpen=!!open;
let wasOpen=!panel.classList.contains('hidden');

if(!isOpen && wasOpen){
commitPendingDateTime();
}

panel.classList.toggle('hidden',!isOpen);
timeToggle.setAttribute('aria-expanded',String(isOpen));

if(isOpen){
let selected=getCurrentDateParts();
visibleMonth=new Date(selected.year,selected.month-1,1);
pendingDate=null;
pendingTime=null;
renderPanel();
positionPanel();
requestAnimationFrame(positionPanel);
}
}

function togglePanel(event){
event.stopPropagation();
setPanelOpen(panel.classList.contains('hidden'));
}

timeToggle.onclick=togglePanel;

timeToggle.onkeydown=event=>{
if(event.key==='Enter' || event.key===' '){
event.preventDefault();
togglePanel(event);
}
};

document.addEventListener('click',()=>setPanelOpen(false));

control.appendChild(timeToggle);
control.appendChild(panel);
return control;
}

function createRadarControlRow(className){
let row=document.createElement('div');
row.className='radar-control-row '+className;
return row;
}

function createRadarModeButton(labelText,{active=false,mapTool=null,onClick=null}={}){
let button=document.createElement('button');
button.type='button';
button.className='radar-mode-button';
button.textContent=labelText;

if(mapTool){
button.dataset.mapTool=mapTool;
}

if(active){
button.classList.add('active');
}

button.onclick=()=>{
if(onClick){
onClick();
return;
}

if(mapTool){
setRadarMapTool(mapTool);
}
};

return button;
}

function createRadarButtonGroup(className,children){
let group=document.createElement('div');
group.className='radar-button-group '+className;
children.forEach(child=>group.appendChild(child));
return group;
}

function createRadarOverlayGroup(){
let group=document.createElement('div');
group.className='radar-overlay-control';

let label=document.createElement('span');
label.className='radar-overlay-label';
label.innerHTML='<span>중첩</span><span>선택</span>';

let checks=createRadarButtonGroup('radar-check-group',[
createRadarWindControl(),
createRadarLightningControl(),
createRadarStationControl(),
createRadarCheckbox('typ','태풍'),
createRadarCheckbox('topo','지형고도'),
createRadarCheckbox('highway','고속도로'),
createRadarCheckbox('lonlat','위경도')
]);

group.appendChild(label);
group.appendChild(checks);
return group;
}

function buildRadarControls(){
let controls=document.createElement('div');
controls.className='radar-controls radar-loop-controls';

let title=document.createElement('div');
title.className='radar-menu-title';
title.innerHTML='<span>레이더</span><span>실황감시</span>';
controls.appendChild(title);

let controlsBody=document.createElement('div');
controlsBody.className='radar-controls-body';
controls.appendChild(controlsBody);

let settingsRow=createRadarControlRow('radar-settings-row');
let playbackRow=createRadarControlRow('radar-playback-row');
controlsBody.appendChild(settingsRow);
controlsBody.appendChild(playbackRow);

let paneCountSelect=createSelect(
[
{value:1,label:'1개창'},
{value:2,label:'2개창'},
{value:3,label:'3개창'},
{value:4,label:'4개창'}
],
radarState.paneCount,
value=>{
radarState.paneCount=Number(value);
reloadRadarImagesForCurrentSettings();
}
);
paneCountSelect.className='radar-pane-count-select';
settingsRow.appendChild(paneCountSelect);

let mapSelect=createSelect(
[
{value:'D3',label:'남한'},
{value:'HR',label:'레이더'},
{value:'HC',label:'레이더(확장)'},
{value:'H1',label:'한반도'},
{value:'H3',label:'동아시아'},
{value:'SE',label:'서울'},
{value:'HL',label:'수도권'}
],
radarState.common.map || 'HR',
value=>{
resetRadarMapView(value);
}
);
mapSelect.className='radar-map-select';
settingsRow.appendChild(mapSelect);

let mapModeGroup=createRadarButtonGroup('radar-map-mode-group',[
createRadarModeButton('전체',{onClick:()=>resetRadarMapView()}),
createRadarModeButton('축소',{mapTool:'zoomOut'}),
createRadarModeButton('배율',{mapTool:'zoomIn'})
]);
radarState.mapModeGroup=mapModeGroup;
settingsRow.appendChild(mapModeGroup);
settingsRow.appendChild(createRadarOverlayGroup());

let nowBtn=document.createElement('button');
nowBtn.type='button';
nowBtn.className='radar-now-button radar-primary-now-button';
nowBtn.textContent='NOW';
nowBtn.onclick=setRadarNow;
playbackRow.appendChild(nowBtn);

let dateInput=document.createElement('input');
dateInput.type='text';
dateInput.className='radar-datetime-input';
dateInput.inputMode='numeric';
dateInput.maxLength=17;
dateInput.placeholder='YYYY.MM.DD. HH:mm';
dateInput.autocomplete='off';
dateInput.spellcheck=false;
dateInput.value=formatDateTimeDisplay(radarState.baseTime);
let commitDateTimeInput=()=>{
let normalizedDateTime=normalizeDateTimeText(dateInput.value,radarState.baseTime);
dateInput.value=normalizedDateTime.display;
setRadarBaseTime(parseLocalDateTime(dateInput.value));
};
dateInput.oninput=()=>{
dateInput.value=dateInput.value.replace(/[^\d.\-/\s:]/g,'').slice(0,17);
};
dateInput.onchange=commitDateTimeInput;
dateInput.onblur=commitDateTimeInput;
dateInput.onkeydown=event=>{
if(event.key==='Enter'){
commitDateTimeInput();
event.currentTarget.blur();
}
};
radarState.dateInput=dateInput;

playbackRow.appendChild(createRadarButtonGroup('radar-datetime-group',[dateInput,createRadarDateTimeControl(dateInput)]));

let shiftControls=document.createElement('div');
shiftControls.className='radar-shift-controls';
RADAR_TIME_SHIFT_OPTIONS.forEach(option=>{
let button=document.createElement('button');
button.type='button';
button.textContent=option.label;
button.onclick=()=>shiftRadarBaseTime(option.minutes);
shiftControls.appendChild(button);
});
playbackRow.appendChild(shiftControls);

playbackRow.appendChild(
createRadarInlineField(
['표출','기간'],
createSelect(RADAR_PERIOD_OPTIONS,radarState.periodMinutes,value=>{
radarState.periodMinutes=Number(value);
rebuildRadarTimelineAroundBase({preserveCache:true});
})
)
);

playbackRow.appendChild(
createRadarInlineField(
['표출','간격'],
createSelect(RADAR_INTERVAL_OPTIONS,radarState.intervalMinutes,value=>{
radarState.intervalMinutes=Number(value);
rebuildRadarTimelineAroundBase({preserveCache:true});
})
)
);

let prevBtn=document.createElement('button');
prevBtn.type='button';
prevBtn.className='radar-now-button radar-playback-button radar-playback-step-button';
prevBtn.textContent='‹';
prevBtn.title='이전 프레임';
prevBtn.onclick=()=>moveRadarSelection(-1);

let playBtn=document.createElement('button');
playBtn.type='button';
playBtn.className='radar-now-button radar-play-button radar-playback-button timeline-play-toggle';
playBtn.textContent='▶';
playBtn.onclick=toggleRadarLoop;
radarState.playButton=playBtn;
updateRadarPlayButton();
let nextBtn=document.createElement('button');
nextBtn.type='button';
nextBtn.className='radar-now-button radar-playback-button radar-playback-step-button';
nextBtn.textContent='›';
nextBtn.title='다음 프레임';
nextBtn.onclick=()=>moveRadarSelection(1);

playbackRow.appendChild(createRadarButtonGroup('radar-playback-controls timeline-playback-controls',[
prevBtn,
playBtn,
nextBtn
]));

let autoRefreshBtn=document.createElement('button');
autoRefreshBtn.type='button';
autoRefreshBtn.className='radar-auto-refresh-button';
autoRefreshBtn.onclick=toggleRadarAutoRefresh;
radarState.autoRefreshButton=autoRefreshBtn;
updateRadarAutoRefreshButton();
playbackRow.appendChild(autoRefreshBtn);

return controls;
}

function createPaneProductControls(pane,index){
normalizeRadarPaneSelection(pane);

let controls=document.createElement('div');
controls.className='radar-pane-controls';

let level1=findRadarLevel1(pane.level1);
let level2=findRadarLevel2(level1.id,pane.level2);

let level1Select=createSelect(
RADAR_PRODUCT_CATALOG.map(item=>({value:item.id,label:item.label})),
level1.id,
value=>{
let nextLevel1=findRadarLevel1(value);
let nextLevel2=getDefaultRadarLevel2(nextLevel1);
let nextLevel3=getDefaultRadarLevel3(nextLevel2);

pane.level1=nextLevel1.id;
pane.level2=nextLevel2.id;
pane.level3=nextLevel3 ? nextLevel3.id : '';

renderRadarPaneAt(index);
preloadRadarImages([index]);
}
);

let level2Select=createSelect(
level1.children.map(item=>({value:item.id,label:item.label})),
level2.id,
value=>{
let nextLevel2=findRadarLevel2(level1.id,value);
let nextLevel3=getDefaultRadarLevel3(nextLevel2);

pane.level2=nextLevel2.id;
pane.level3=nextLevel3 ? nextLevel3.id : '';

renderRadarPaneAt(index);
preloadRadarImages([index]);
}
);

controls.appendChild(level1Select);
controls.appendChild(level2Select);

if(hasRadarLevel3(level2)){
let level3=findRadarLevel3(level1.id,level2.id,pane.level3);

let level3Select=createSelect(
level2.children.map(item=>({value:item.id,label:item.label})),
level3?.id || '',
value=>{
pane.level3=value;
renderRadarPaneAt(index);
preloadRadarImages([index]);
}
);

controls.appendChild(level3Select);
}

return controls;
}

function getRadarPanePreviousSource(index){
let paneElement=getRadarPaneElements()[index];
let img=paneElement?.querySelector('.radar-pane-image');
return img?.getAttribute('src') || '';
}

function createRadarPaneElement(index,previousImageSource){
let pane=radarState.panes[index];
let paneElement=document.createElement('section');
paneElement.className='radar-pane';
paneElement.style.setProperty('--radar-image-width',`${getRadarPaneImageSize(index)+RADAR_IMAGE_WIDTH_MARGIN}px`);
paneElement.style.setProperty('--radar-image-height',`${getRadarPaneImageSize(index)+RADAR_IMAGE_HEIGHT_MARGIN}px`);

let header=document.createElement('div');
header.className='radar-pane-header';
header.appendChild(createPaneProductControls(pane,index));

let viewer=document.createElement('div');
viewer.className='radar-pane-viewer';

let image=document.createElement('img');
image.className='radar-pane-image';
image.alt='레이더 이미지';
image.loading='eager';
image.decoding='sync';
image.onclick=applyRadarMapClick;

if(previousImageSource){
image.src=previousImageSource;
paneElement.classList.add('has-current-image');
}

let loading=document.createElement('div');
loading.className='radar-loading';
loading.innerHTML='<div class="radar-spinner"></div><div>레이더 이미지 로드 중</div>';

let error=document.createElement('div');
error.className='radar-error radar-pane-error hidden';

viewer.appendChild(image);
viewer.appendChild(loading);
viewer.appendChild(error);
paneElement.appendChild(header);
paneElement.appendChild(viewer);
return paneElement;
}

function renderRadarPaneAt(index){
if(!radarState.paneGrid || index<0 || index>=radarState.paneCount){
return;
}

let previousImageSource=getRadarPanePreviousSource(index);
let paneElement=createRadarPaneElement(index,previousImageSource);
let currentPane=getRadarPaneElements()[index];

if(currentPane){
currentPane.replaceWith(paneElement);
}
else{
radarState.paneGrid.appendChild(paneElement);
}

updateRadarPaneSizes();
loadActiveRadarFrameImages([index]);
}

function renderRadarPanes(){
if(!radarState.paneGrid){
return;
}

let previousImageSources=getRadarPaneElements().map(paneElement=>{
let img=paneElement.querySelector('.radar-pane-image');
return img?.getAttribute('src') || '';
});

radarState.paneGrid.innerHTML='';
radarState.paneGrid.style.setProperty('--radar-pane-count',String(radarState.paneCount));
radarState.paneGrid.dataset.paneCount=String(radarState.paneCount);

for(let i=0;i<radarState.paneCount;i++){
radarState.paneGrid.appendChild(createRadarPaneElement(i,previousImageSources[i]));
}

updateRadarPaneSizes();
loadActiveRadarFrameImages();
}

function initRadarAnalysisPage(){
let root=document.getElementById('radarAnalysisApp');

if(!root){
return;
}

radarState.root=root;

if(!radarState.keyboardBound){
document.addEventListener('keydown',handleRadarKeydown);
radarState.keyboardBound=true;
}

if(!radarState.resizeBound){
window.addEventListener('resize',scheduleRadarSizeRefresh);
radarState.resizeBound=true;
}

if(!radarState.resumeBound){
document.addEventListener('visibilitychange',()=>{
if(document.visibilityState==='visible'){
syncRadarAfterResume();
}
});
window.addEventListener('focus',syncRadarAfterResume);
radarState.resumeBound=true;
}

buildRadarFrames();
radarState.activeIndex=Math.max(0,radarState.frames.length-1);

let page=document.createElement('main');
page.className='radar-page';

page.appendChild(buildRadarControls());

let timelineWrap=document.createElement('div');
timelineWrap.className='forecast-bar radar-timeline-bar';

let shell=document.createElement('div');
shell.className='forecast-shell compare-active';

let timeline=document.createElement('div');
timeline.className='forecast-timeline compare-timeline single-timeline radar-timeline';

let timeLabel=document.createElement('div');
timeLabel.className='forecast-label-hidden';

shell.appendChild(timeline);
shell.appendChild(timeLabel);
timelineWrap.appendChild(shell);
page.appendChild(timelineWrap);

let paneGrid=document.createElement('div');
paneGrid.className='radar-pane-grid';
page.appendChild(paneGrid);

root.replaceChildren(page);

radarState.timeline=timeline;
radarState.timeLabel=timeLabel;
radarState.paneGrid=paneGrid;

renderRadarTimeline();
updateRadarTimeLabel();
renderRadarPanes();
preloadRadarImages();
startRadarCacheRefresh();
}

function openRadarAnalysisPage(){
window.open('radar.html','_blank','noopener');
}

function renderRadarAnalysisLauncher(){

let section=document.createElement('div');
section.className='model-section radar-analysis-section';

let button=document.createElement('button');
button.type='button';
button.className='radar-analysis-launcher';
button.title='레이더 분석 페이지 열기';
button.innerHTML='<span class="radar-launcher-icon">↗</span><span class="radar-launcher-text"><span>레이더</span><span>실황감시</span></span>';
button.onclick=openRadarAnalysisPage;

section.appendChild(button);
return section;
}

document.addEventListener('DOMContentLoaded',initRadarAnalysisPage);
