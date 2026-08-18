const TYPHOON_MANIFEST_PATH='data/manifest.json';
const TYPHOON_STATUS_PATH='data/status.json';
const TYPHOON_TYP_LIST_CACHE_PREFIX='data/cache/kma_apihub/typ_lst_';
const TYPHOON_TD_LIST_CACHE_PREFIX='data/cache/kma_apihub/td_lst_';
const TYPHOON_TYP_LIST_CACHE_SUFFIX='.json';
const TYPHOON_RAW_REPOSITORY_BASE_URL=normalizeTyphoonBaseUrl(globalThis.CDS_TYPOON_RAW_REPOSITORY_BASE_URL || 'https://raw.githubusercontent.com/SSalKim/CDS/main/');
const TYPHOON_LIVE_DATA_BASE_URL=normalizeTyphoonBaseUrl(globalThis.CDS_TYPOON_LIVE_DATA_BASE_URL || TYPHOON_RAW_REPOSITORY_BASE_URL);
const TYPHOON_ACTIVE_IMAGE_BASE_URL=normalizeTyphoonBaseUrl(globalThis.CDS_TYPOON_ACTIVE_IMAGE_BASE_URL || TYPHOON_RAW_REPOSITORY_BASE_URL);
const TYPHOON_IMPACT_EFF_VALUES=new Set(['1','2','3']);
const TYPHOON_IMPACT_OPTION_BG='#dff5ff';
const TYPHOON_IMPACT_OPTION_COLOR='#0f3d64';
const TYPHOON_IMPACT_OPTION_WEIGHT='700';
const TYPHOON_REFRESH_MS=10*60*1000;
const TYPHOON_SLOT_HOURS=6;
const TYPHOON_CYCLE_WINDOW_START_OFFSET_HOURS=4;
const TYPHOON_CYCLE_WINDOW_END_OFFSET_HOURS=10;
const TYPHOON_PAGE_CACHE_TOKEN=new URLSearchParams(window.location.search).get('fresh') || String(Date.now());
const TYPHOON_IMAGE_PRELOAD_CONCURRENCY=6;
const TYPHOON_IMAGE_CACHE_LIMIT_PER_HORIZON=60;
const TYPHOON_IMAGE_TIMEOUT_MS=20000;
const TYPHOON_FCST_OPTIONS=[
{hours:120,label:'5일예측'},
{hours:240,label:'10일예측'}
];

const TYPHOON_KO_NAME_FALLBACK={
JANGMI:'장미',
HIGOS:'히고스'
};

const TYPHOON_MODEL_LABELS={
KMA:'KMA OFCL',
ECMWF:'ECMWF',
ECMWF_EPS:'ECMWF EPS',
KIM_3h:'KIM',
KIM_6h:'KIM',
KIM_GFDL_6h:'KIM',
KIM_EPS:'KIM EPS',
UM:'UM',
UM_GFDL_6h:'UM',
UM_KEPS:'UM EPS',
UKM:'UKMO',
UKMO_EPS:'UKMO EPS',
GFS:'GFS',
GFS_EPS:'GFS EPS',
CMC:'CMC',
CMC_EPS:'CMC EPS',
NAVGEM:'NAVGEM',
FNMOC_EPS:'NAVGEM EPS',
ICON:'ICON',
ICON_EPS:'ICON EPS',
JGSM:'JGSM',
TEPS:'JGSM EPS',
CTCX:'COAMPS-TC',
COAMPS_EPS:'COAMPS-TC EPS',
AFUM:'GALWEM',
HAFS:'HAFS',
HWRF:'HWRF',
ECMWF_AIFS:'ECMWF AIFS',
ECMWF_AIFS_EPS:'ECMWF AIFS EPS',
IFEC_AI:'KMA AIFS-ECMWF',
IFKM_AI:'KMA AIFS-KIM',
AGFS:'AIGFS',
AIGEFS:'AIGFS EPS',
AICON:'AICON',
FNEC_AI:'FourCastNet-ECMWF',
FNKM_AI:'FourCastNet-KIM',
FNUM_AI:'FourCastNet-UM',
PGEC_AI:'Pangu-Weather-ECMWF',
PGKM_AI:'Pangu-Weather-KIM',
PGUM_AI:'Pangu-Weather-UM',
GCEC_AI:'GraphCast-ECMWF',
GCKM_AI:'GraphCast-KIM',
GCUM_AI:'GraphCast-UM',
GENC:'GenCast',
WNC:'WeatherNext Cyclones',
FNV3:'WeatherNext Cyclones',
HKO_AREC: 'Aurora-ECMWF',
HKO_FXEC: 'FuXi-ECMWF',
HKO_FWEC: 'FengWu-ECMWF',
};

const TYPHOON_MODEL_INFO=[
{name:'ECMWF',description:'유럽중기예보센터(ECMWF) 전구모델'},
{name:'ECMWF EPS',description:'유럽중기예보센터(ECMWF) 앙상블모델 평균'},
{name:'KIM',description:'기상청(KMA) 전구모델'},
{name:'KIM EPS',description:'기상청(KMA) 앙상블모델 평균'},
{name:'UKMO',description:'영국기상청(UKMET) 전구모델'},
{name:'UKMO EPS',description:'영국기상청(UKMET) 앙상블모델 평균'},
{name:'GFS',description:'미해양대기청(NOAA NCEP) 전구모델'},
{name:'GFS EPS',description:'미해양대기청(NOAA NCEP) 앙상블모델 평균'},
{name:'CMC',description:'캐나다기상센터(CMC) 전구모델'},
{name:'CMC EPS',description:'캐나다기상센터(CMC) 앙상블모델 평균'},
{name:'NAVGEM',description:'미해군(FNMOC) 전구모델'},
{name:'NAVGEM EPS',description:'미해군(FNMOC) 앙상블모델 평균'},
{name:'ICON',description:'독일기상청(DWD) 전구모델'},
{name:'ICON EPS',description:'독일기상청(DWD) 앙상블모델 평균'},
{name:'JGSM',description:'일본기상청(JMA) 전구모델'},
{name:'JGSM EPS',description:'일본기상청(JMA) 앙상블모델 평균'},
{name:'COAMPS-TC',description:'미해군연구소(NRL) 태풍모델'},
{name:'COAMPS-TC EPS',description:'미해군연구소(NRL) 앙상블모델 평균'},
{name:'GALWEM',description:'미공군(USAF) 전구모델'},
{name:'HAFS',description:'미해양대기청(NOAA EMC) 태풍모델(신)'},
{name:'HWRF',description:'미해양대기청(NOAA EMC) 태풍모델(구)'},
{name:'ECMWF AIFS',description:'[AI] 유럽중기예보센터(ECMWF) AI 전구모델'},
{name:'ECMWF AIFS EPS',description:'[AI] 유럽중기예보센터(ECMWF) AI 앙상블모델 평균'},
{name:'KMA AIFS-ECMWF',description:'[AI] 기상청 수행 AIFS (ECMWF 초기장)'},
{name:'KMA AIFS-KIM',description:'[AI] 기상청 수행 AIFS (KIM 초기장)'},
{name:'AIGFS',description:'[AI] 미해양대기청(NOAA NCEP) AI 전구모델'},
{name:'AIGFS EPS',description:'[AI] 미해양대기청(NOAA NCEP) AI 앙상블모델 평균'},
{name:'AICON',description:'[AI] 독일기상청(DWD) AI 전구모델'},
{name:'FourCastNet-ECMWF',description:'[AI] 기상청 수행 FourCastNet (ECMWF 초기장)'},
{name:'FourCastNet-KIM',description:'[AI] 기상청 수행 FourCastNet (KIM 초기장)'},
{name:'Pangu-Weather-ECMWF',description:'[AI] 기상청 수행 Pangu-Weather (ECMWF 초기장)'},
{name:'Pangu-Weather-KIM',description:'[AI] 기상청 수행 Pangu-Weather (KIM 초기장)'},
{name:'GraphCast-ECMWF',description:'[AI] 기상청 수행 GraphCast (ECMWF 초기장)'},
{name:'GraphCast-KIM',description:'[AI] 기상청 수행 GraphCast (KIM 초기장)'},
{modelId:'GENC',name:'GenCast',description:'[AI] 구글 딥마인드 앙상블모델(GenCast) 평균'},
{modelId:'WNC',name:'WeatherNext Cyclones',description:'[AI] 구글 딥마인드 앙상블모델(WeatherNext Cyclones) 평균'},
{name:'Aurora-ECMWF',description:'[AI] 홍콩기상청(HKO) 수행 Aurora (ECMWF 초기장)'},
{name:'FuXi-ECMWF',description:'[AI] 홍콩기상청(HKO) 수행 FuXi (ECMWF 초기장)'},
{name:'FengWu-ECMWF',description:'[AI] 홍콩기상청(HKO) 수행 FengWu (ECMWF 초기장)'},
];

// Keep retired models in the catalog so they can be restored without rebuilding their metadata.
const TYPHOON_INACTIVE_MODEL_IDS=new Set(['GENC']);

const TYPHOON_DEFAULT_MODEL_TARGET=TYPHOON_MODEL_INFO.filter(item=>{
let modelKey=item.modelId || item.name;
return !TYPHOON_INACTIVE_MODEL_IDS.has(modelKey);
}).length;

const TYPHOON_MODEL_INFO_GROUP_ENDS=new Set([
'ECMWF EPS',
'KIM EPS',
'UKMO EPS',
'GFS EPS',
'CMC EPS',
'NAVGEM EPS',
'ICON EPS',
'JGSM EPS',
'COAMPS-TC EPS',
'GALWEM',
'HWRF',
'ECMWF AIFS EPS',
'KMA AIFS-KIM',
'AIGFS EPS',
'AICON',
'FourCastNet-KIM',
'Pangu-Weather-KIM',
'GraphCast-KIM',
'WNC',
'Aurora-ECMWF',
'FuXi-ECMWF',
'FengWu-ECMWF'
]);

const TYPHOON_MODEL_INFO_COLORS={
'ECMWF':'#ED2939',
'ECMWF EPS':'#FC6C85',
'KIM':'#FA8128',
'KIM EPS':'#FFB347',
'UKMO':'#FFF200',
'UM EPS':'#B8CE9E',
'UKMO EPS':'#B8CE9E',
'GFS':'#03C04A',
'GFS EPS':'#7DDBA7',
'CMC':'#0CCBF0',
'CMC EPS':'#AAF7F4',
'NAVGEM':'#4470AD',
'NAVGEM EPS':'#99AFD7',
'ICON':'#B85CFFFF',
'ICON EPS':'#E0B3FFFF',
'JGSM':'#997950',
'JGSM EPS':'#654321',
'COAMPS-TC':'#78081C',
'COAMPS-TC EPS':'#A13B4E',
'GALWEM':'#4F746C',
'HAFS':'#9D5E5C',
'HWRF':'#9E9E9E',
'ECMWF AIFS':'#C71585',
'ECMWF AIFS EPS':'#E34FA5',
'KMA AIFS-ECMWF':'#1B2AFA',
'KMA AIFS-KIM':'#DDA520',
'AIGFS':'#E0FF78',
'AIGFS EPS':'#78FF8F',
'AICON':'#C8A3D3FF',
'FourCastNet-ECMWF':'#004B1C',
'FourCastNet-KIM':'#388E3C',
'Pangu-Weather-ECMWF':'#3944BC',
'Pangu-Weather-KIM':'#727EF2',
'Pangu-Weather-UM':'#8EA2FF',
'GraphCast-ECMWF':'#4D248D',
'GraphCast-KIM':'#6C33C6',
'GraphCast-UM':'#B57AD5',
'GenCast':'#9866C7',
'WNC':'#DA70D6',
'FNV3':'#DA70D6',
'WeatherNext Cyclones':'#DA70D6',
'Aurora-ECMWF':'#1E90FF',
'FuXi-ECMWF':'#20B2AA',
'FengWu-ECMWF':'#A6C875'
};


const TYPHOON_MODEL_DETAIL_COLUMNS=[
'표출명칭',
'운영기관',
'모델명',
'도메인',
'구분',
'격자체계 (분해능)',
'연직층수',
'기반',
'참고사항'
];

const TYPHOON_MODEL_DETAIL_ROWS=[
  {
    "표출명칭": "ECMWF",
    "운영기관": "유럽중기예보센터(ECMWF)",
    "모델명": "IFS",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "TCo1279 (~9km)",
    "연직층수": "137층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "ECMWF EPS",
    "운영기관": "유럽중기예보센터(ECMWF)",
    "모델명": "EPS",
    "도메인": "전지구",
    "구분": "앙상블 모델 평균 (M51)",
    "격자체계 (분해능)": "TCo1279 (~9km)",
    "연직층수": "137층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "KIM",
    "운영기관": "기상청(KMA)",
    "모델명": "KIM (GDAPS)",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "NE570NP3 (~8km)",
    "연직층수": "91층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "KIM EPS",
    "운영기관": "기상청(KMA)",
    "모델명": "KIM (GENS)",
    "도메인": "전지구",
    "구분": "앙상블 모델 평균 (M26)",
    "격자체계 (분해능)": "NE192NP3 (~24km)",
    "연직층수": "91층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "UKMO",
    "운영기관": "영국기상청(UKMET)",
    "모델명": "UM",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "N1280 (~10km)",
    "연직층수": "70층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "UKMO EPS",
    "운영기관": "영국기상청(UKMET)",
    "모델명": "UM (MOGREPS-G)",
    "도메인": "전지구",
    "구분": "앙상블 모델 평균 (M25)",
    "격자체계 (분해능)": "N400 (~32km)",
    "연직층수": "70층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "GFS",
    "운영기관": "미해양대기청(NOAA) 국립환경예측센터(NCEP)",
    "모델명": "GFS",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "C768 (~12.5km)",
    "연직층수": "127층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "GFS EPS",
    "운영기관": "미해양대기청(NOAA) 국립환경예측센터(NCEP)",
    "모델명": "GEFS",
    "도메인": "전지구",
    "구분": "앙상블 모델 평균 (M31)",
    "격자체계 (분해능)": "C384 (~25km)",
    "연직층수": "64층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "CMC",
    "운영기관": "캐나다기상센터(CMC)",
    "모델명": "GEM (GDPS)",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "0.135° (~15km)",
    "연직층수": "84층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "CMC EPS",
    "운영기관": "캐나다기상센터(CMC)",
    "모델명": "GEM (GEPS)",
    "도메인": "전지구",
    "구분": "앙상블 모델 평균 (M20)",
    "격자체계 (분해능)": "0.23° (~26km)",
    "연직층수": "84층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "NAVGEM",
    "운영기관": "미해군수치기상해양센터(FNMOC)",
    "모델명": "NAVGEM",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "T681 (~19km)",
    "연직층수": "60층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "NAVGEM EPS",
    "운영기관": "미해군수치기상해양센터(FNMOC)",
    "모델명": "NAVGEM",
    "도메인": "전지구",
    "구분": "앙상블 모델 평균 (M21)",
    "격자체계 (분해능)": "T359 (~35km)",
    "연직층수": "60층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "ICON",
    "운영기관": "독일기상청(DWD)",
    "모델명": "ICON",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "R03B07 (~13km)",
    "연직층수": "120층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "ICON EPS",
    "운영기관": "독일기상청(DWD)",
    "모델명": "ICON EPS",
    "도메인": "전지구",
    "구분": "앙상블 모델 평균 (M40)",
    "격자체계 (분해능)": "R03B06 (~26km)",
    "연직층수": "120층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "JGSM",
    "운영기관": "일본기상청(JMA)",
    "모델명": "GSM",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "TQ959 (~13km)",
    "연직층수": "128층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "JGSM EPS",
    "운영기관": "일본기상청(JMA)",
    "모델명": "GEPS",
    "도메인": "전지구",
    "구분": "앙상블 모델 평균 (M51)",
    "격자체계 (분해능)": "TQ479 (~27km)",
    "연직층수": "128층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "COAMPS-TC",
    "운영기관": "미해군연구소(NRL)",
    "모델명": "COAMPS-TC",
    "도메인": "태풍영역",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "가변형 둥지격차 (4-36km)",
    "연직층수": "40층",
    "기반": "역학코어",
    "참고사항": "COAMPS-TC 실험모델(CTCX), GFS 초기장 활용"
  },
  {
    "표출명칭": "COAMPS-TC EPS",
    "운영기관": "미해군연구소(NRL)",
    "모델명": "COAMPS-TC",
    "도메인": "태풍영역",
    "구분": "앙상블 모델 평균 (M11)",
    "격자체계 (분해능)": "가변형 둥지격차 (4-36km)",
    "연직층수": "40층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "GALWEM",
    "운영기관": "미공군(USAF)",
    "모델명": "UM (GALWEM)",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "N768 (~17km)",
    "연직층수": "70층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "HAFS",
    "운영기관": "미해양대기청(NOAA) 환경모델링센터(EMC)",
    "모델명": "HAFS-A",
    "도메인": "태풍영역",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "가변형 둥지격차 (1.8-5.4km)",
    "연직층수": "81층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "HWRF",
    "운영기관": "미해양대기청(NOAA) 환경모델링센터(EMC)",
    "모델명": "HWRF",
    "도메인": "태풍영역",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "가변형 둥지격차 (1.5-13.5km)",
    "연직층수": "75층",
    "기반": "역학코어",
    "참고사항": ""
  },
  {
    "표출명칭": "ECMWF AIFS",
    "운영기관": "유럽중기예보센터(ECMWF)",
    "모델명": "AIFS-Single",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "0.25° (~28km)",
    "연직층수": "14층",
    "기반": "AI",
    "참고사항": ""
  },
  {
    "표출명칭": "ECMWF AIFS EPS",
    "운영기관": "유럽중기예보센터(ECMWF)",
    "모델명": "AIFS-ENS",
    "도메인": "전지구",
    "구분": "앙상블 모델 평균 (M51)",
    "격자체계 (분해능)": "0.25° (~28km)",
    "연직층수": "14층",
    "기반": "AI",
    "참고사항": ""
  },
  {
    "표출명칭": "KMA AIFS-ECMWF",
    "운영기관": "기상청(KMA)",
    "모델명": "AIFS-Single",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "0.25° (~28km)",
    "연직층수": "13층",
    "기반": "AI",
    "참고사항": "ECMWF AIFS 기상청 국립기상과학원 자체 수행, ECMWF 초기장 활용"
  },
  {
    "표출명칭": "KMA AIFS-KIM",
    "운영기관": "기상청(KMA)",
    "모델명": "AIFS-Single",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "0.25° (~28km)",
    "연직층수": "13층",
    "기반": "AI",
    "참고사항": "ECMWF AIFS 기상청 국립기상과학원 자체 수행, KIM 초기장 활용"
  },
  {
    "표출명칭": "AIGFS",
    "운영기관": "미해양대기청(NOAA) 국립환경예측센터(NCEP)",
    "모델명": "AIGFS",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "0.25° (~28km)",
    "연직층수": "13층",
    "기반": "AI",
    "참고사항": ""
  },
  {
    "표출명칭": "AIGFS EPS",
    "운영기관": "미해양대기청(NOAA) 국립환경예측센터(NCEP)",
    "모델명": "AIGEFS",
    "도메인": "전지구",
    "구분": "앙상블 모델 평균 (M31)",
    "격자체계 (분해능)": "0.25° (~28km)",
    "연직층수": "13층",
    "기반": "AI",
    "참고사항": ""
  },
  {
    "표출명칭": "AICON",
    "운영기관": "독일기상청(DWD)",
    "모델명": "AICON",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "R03B07 (~13km)",
    "연직층수": "13층",
    "기반": "AI",
    "참고사항": ""
  },
  {
    "표출명칭": "FourCastNet-ECMWF",
    "운영기관": "기상청(KMA)",
    "모델명": "FourCastNet",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "0.25° (~28km)",
    "연직층수": "4층",
    "기반": "AI",
    "참고사항": "NVIDIA AI모델 FourCastNet 기상청 국립기상과학원 자체 수행, ECMWF 초기장 활용"
  },
  {
    "표출명칭": "FourCastNet-KIM",
    "운영기관": "기상청(KMA)",
    "모델명": "FourCastNet",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "0.25° (~28km)",
    "연직층수": "4층",
    "기반": "AI",
    "참고사항": "NVIDIA AI모델 FourCastNet 기상청 국립기상과학원 자체 수행, KIM 초기장 활용"
  },
  {
    "표출명칭": "Pangu-Weather-ECMWF",
    "운영기관": "기상청(KMA)",
    "모델명": "Pangu-Weather",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "0.25° (~28km)",
    "연직층수": "14층",
    "기반": "AI",
    "참고사항": "HUAWEI AI모델 Pangu-Weather 기상청 국립기상과학원 자체 수행, ECMWF 초기장 활용"
  },
  {
    "표출명칭": "Pangu-Weather-KIM",
    "운영기관": "기상청(KMA)",
    "모델명": "Pangu-Weather",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "0.25° (~28km)",
    "연직층수": "14층",
    "기반": "AI",
    "참고사항": "HUAWEI AI모델 Pangu-Weather 기상청 국립기상과학원 자체 수행, KIM 초기장 활용"
  },
  {
    "표출명칭": "GraphCast-ECMWF",
    "운영기관": "기상청(KMA)",
    "모델명": "GraphCast",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "0.25° (~28km)",
    "연직층수": "37층",
    "기반": "AI",
    "참고사항": "Google DeepMind AI모델 GraphCast 기상청 국립기상과학원 자체 수행, ECMWF 초기장 활용"
  },
  {
    "표출명칭": "GraphCast-KIM",
    "운영기관": "기상청(KMA)",
    "모델명": "GraphCast",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "0.25° (~28km)",
    "연직층수": "37층",
    "기반": "AI",
    "참고사항": "Google DeepMind AI모델 GraphCast 기상청 국립기상과학원 자체 수행, KIM 초기장 활용"
  },
  {
    "model_id": "GENC",
    "표출명칭": "GenCast",
    "운영기관": "구글 딥마인드(Google DeepMind)",
    "모델명": "GenCast",
    "도메인": "전지구",
    "구분": "앙상블 모델 평균 (M50)",
    "격자체계 (분해능)": "0.25° (~28km)",
    "연직층수": "13층",
    "기반": "AI",
    "참고사항": ""
  },
  {
    "model_id": "WNC",
    "표출명칭": "WeatherNext Cyclones",
    "운영기관": "구글 딥마인드(Google DeepMind)",
    "모델명": "WeatherNext Cyclones (FNV3)",
    "도메인": "전지구",
    "구분": "앙상블 모델 평균 (M50)",
    "격자체계 (분해능)": "0.25° (~28km)",
    "연직층수": "13층",
    "기반": "AI",
    "참고사항": "'26.8.8 현업운영 전환에 따른 내부 ID 변경(FNV3 → WNC), 표출명 WeatherNext Cyclones"
  },
  {
    "표출명칭": "Aurora-ECMWF",
    "운영기관": "홍콩기상청(HKO)",
    "모델명": "Aurora",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "0.25° (~28km)",
    "연직층수": "13층",
    "기반": "AI",
    "참고사항": "Microsoft AI모델 Aurora 홍콩기상청 자체 수행, ECMWF 초기장 활용"
  },
  {
    "표출명칭": "FuXi-ECMWF",
    "운영기관": "홍콩기상청(HKO)",
    "모델명": "FuXi",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "0.25° (~28km)",
    "연직층수": "13층",
    "기반": "AI",
    "참고사항": "중국 푸단 대학교 AI모델 FuXi 홍콩기상청 자체 수행, ECMWF 초기장 활용"
  },
  {
    "표출명칭": "FengWu-ECMWF",
    "운영기관": "홍콩기상청(HKO)",
    "모델명": "FengWu",
    "도메인": "전지구",
    "구분": "결정론적 모델",
    "격자체계 (분해능)": "0.25° (~28km)",
    "연직층수": "13층",
    "기반": "AI",
    "참고사항": "상하이 AI연구소 AI모델 FengWu 홍콩기상청 자체 수행, ECMWF 초기장 활용"
  }
];

const typhoonState={
root:null,
manifest:null,
manifestBaseUrl:'',
driveArchiveImages:new Map(),
driveArchivePathsLoaded:new Set(),
driveArchiveLoadPromises:new Map(),
status:null,
yearIndexes:new Map(),
stormManifestCache:new Map(),
entries:[],
years:[],
storms:[],
slots:[],
selectedYear:'',
selectedStormKey:'',
selectedSlotIndex:0,
selectedFcstHours:240,
timer:null,
keyboardBound:false,
imageCaches:new Map(),
imageLoadStates:new Map(),
imageRequestSeq:0,
initialLoadComplete:false,
modelDetailLastFocus:null,
typImpactByYear:new Map(),
typNowByYear:new Map(),
tdNowByYear:new Map(),
selectionLoadSeq:0,
slotLoadSeq:0
};

function openTyphoonGuidancePage(){
window.open('typhoon.html','_blank','noopener');
}

function reloadTyphoonGuidancePage(){
let url=new URL(window.location.href);
url.searchParams.set('fresh',String(Date.now()));
window.location.replace(url.toString());
}

function renderTyphoonGuidanceLauncher(){
let section=document.createElement('div');
section.className='model-section typhoon-guidance-section';

let button=document.createElement('button');
button.type='button';
button.className='typhoon-guidance-launcher';
button.title='태풍 모델예측 페이지 열기';
button.innerHTML='<span class="typhoon-launcher-icon">↗</span><span class="typhoon-launcher-text"><span>태풍</span><span>모델예측</span><small>(EXP)</small></span>';
button.onclick=openTyphoonGuidancePage;

section.appendChild(button);
return section;
}

function initTyphoonGuidancePage(){
let root=document.getElementById('typhoonGuidanceApp');
if(!root){
return;
}

typhoonState.root=root;
ensureTyphoonModelDetailStyles();
renderTyphoonShell();
loadTyphoonManifest();

if(!typhoonState.timer){
typhoonState.timer=window.setInterval(loadTyphoonManifest,TYPHOON_REFRESH_MS);
}

if(!typhoonState.keyboardBound){
document.addEventListener('keydown',handleTyphoonKeydown);
typhoonState.keyboardBound=true;
}

document.addEventListener('visibilitychange',()=>{
if(document.visibilityState==='visible'){
loadTyphoonManifest();
}
});
}

function renderTyphoonShell(){
let root=typhoonState.root;
if(!root){
return;
}

let page=document.createElement('main');
page.className='typhoon-page';

let header=document.createElement('header');
header.className='typhoon-header';

let titleWrap=document.createElement('button');
titleWrap.type='button';
titleWrap.className='typhoon-title-wrap typhoon-title-button';
titleWrap.title='페이지 새로고침';
titleWrap.onclick=reloadTyphoonGuidancePage;

let title=document.createElement('div');
title.className='typhoon-title';
title.innerHTML='<span>태풍</span><span>모델예측</span>';

titleWrap.appendChild(title);

let controls=document.createElement('div');
controls.className='typhoon-select-controls';

let yearSelect=document.createElement('select');
yearSelect.className='typhoon-year-select';
yearSelect.dataset.role='yearSelect';
yearSelect.onchange=event=>handleTyphoonYearChange(event.target.value);

let stormSelect=document.createElement('select');
stormSelect.className='typhoon-storm-select';
stormSelect.dataset.role='stormSelect';
stormSelect.onchange=event=>handleTyphoonStormChange(event.target.value);

controls.appendChild(yearSelect);
controls.appendChild(stormSelect);
controls.appendChild(createTyphoonFcstSelector());

header.appendChild(titleWrap);
header.appendChild(controls);

let timeBar=document.createElement('div');
timeBar.className='forecast-bar typhoon-time-bar';

let shell=document.createElement('div');
shell.className='forecast-shell compare-active typhoon-time-shell';

let slider=document.createElement('input');
slider.type='range';
slider.min='0';
slider.max='0';
slider.step='1';
slider.value='0';
slider.className='native-forecast-slider typhoon-time-slider';
slider.dataset.role='timeSlider';
slider.oninput=event=>{
setTyphoonSlotIndex(Number(event.target.value));
};

let timeline=document.createElement('div');
timeline.className='forecast-timeline compare-timeline single-timeline typhoon-timeline';
timeline.dataset.role='timeline';

let timeLabel=document.createElement('div');
timeLabel.className='forecast-label-hidden';
timeLabel.dataset.role='timeLabel';

shell.appendChild(slider);
shell.appendChild(timeline);
shell.appendChild(timeLabel);
timeBar.appendChild(shell);

let viewer=document.createElement('div');
viewer.className='typhoon-viewer';

let viewerStage=document.createElement('div');
viewerStage.className='typhoon-viewer-stage';
viewerStage.dataset.role='viewer';

let viewerLoading=document.createElement('div');
viewerLoading.className='loading typhoon-viewer-loading hidden';
viewerLoading.dataset.role='viewerLoading';
viewerLoading.setAttribute('role','status');
viewerLoading.setAttribute('aria-live','polite');
viewerLoading.setAttribute('aria-hidden','true');
viewerLoading.innerHTML='<div class="spinner"></div><div class="loading-text">이미지 로딩 중</div>';

viewer.appendChild(viewerStage);
viewer.appendChild(viewerLoading);

let content=document.createElement('div');
content.className='typhoon-content';
content.appendChild(viewer);
content.appendChild(createTyphoonModelInfoPanel());

page.appendChild(header);
page.appendChild(timeBar);
page.appendChild(content);

root.replaceChildren(page);
}

function createTyphoonModelInfoPanel(){
let panel=document.createElement('aside');
panel.className='typhoon-model-info-panel';
panel.setAttribute('aria-label','태풍 모델 설명');

let list=document.createElement('div');
list.className='typhoon-model-info-list';

TYPHOON_MODEL_INFO.forEach(item=>{
let modelKey=item.modelId || item.name;
if(TYPHOON_INACTIVE_MODEL_IDS.has(modelKey)){
return;
}
let row=document.createElement('div');
row.className='typhoon-model-info-row';
row.dataset.modelId=modelKey;
if(TYPHOON_MODEL_INFO_GROUP_ENDS.has(modelKey)){
row.classList.add('is-group-end');
}
row.style.setProperty('--typhoon-model-color',TYPHOON_MODEL_INFO_COLORS[modelKey] || '#1d4ed8');

let name=document.createElement('div');
name.className='typhoon-model-info-name';
name.textContent=item.name;

let description=document.createElement('div');
description.className='typhoon-model-info-description';
description.textContent=item.description;

row.appendChild(name);
row.appendChild(description);
list.appendChild(row);
});

let actions=document.createElement('div');
actions.className='typhoon-model-info-actions';

let updatedAt=document.createElement('div');
updatedAt.className='typhoon-updated-time';
updatedAt.dataset.role='subtitle';
updatedAt.textContent='';

let detailButton=document.createElement('button');
detailButton.type='button';
detailButton.className='typhoon-model-detail-button';
detailButton.title='모델 상세 설명 열기';
detailButton.innerHTML='<span class="typhoon-model-detail-button-icon">▦</span><span>상세보기</span>';
detailButton.onclick=()=>openTyphoonModelDetailModal(detailButton);

actions.appendChild(updatedAt);
actions.appendChild(detailButton);
panel.appendChild(list);
panel.appendChild(actions);
return panel;
}

function ensureTyphoonModelDetailStyles(){
if(document.getElementById('typhoonModelDetailStyles')){
return;
}
let style=document.createElement('style');
style.id='typhoonModelDetailStyles';
style.textContent=`
.typhoon-storm-select option.typhoon-impact-storm-option{
background:#dff5ff;
color:#0f3d64;
font-weight:700;
}
.typhoon-storm-select option.typhoon-active-storm-option{
background:#F9E5FF;
color:#5d2b66;
font-weight:700;
}
.typhoon-model-info-panel{
position:relative;
display:flex;
flex-direction:column;
min-height:0;
}
.typhoon-model-info-list{
min-height:0;
}
.typhoon-model-info-actions{
display:flex;
align-items:center;
justify-content:space-between;
gap:12px;
padding:10px 10px 12px;
margin-top:auto;
border-top:1px solid rgba(15,23,42,.08);
background:linear-gradient(180deg,rgba(255,255,255,.72),rgba(248,250,252,.96));
position:sticky;
bottom:0;
z-index:2;
}
.typhoon-model-info-actions .typhoon-updated-time{
flex:1 1 auto;
min-width:0;
margin-right:auto;
display:flex;
flex-direction:column;
align-items:flex-start;
justify-content:center;
text-align:left;
font-size:12px;
font-weight:750;
letter-spacing:-.02em;
line-height:1.35;
color:#64748b;
white-space:normal;
overflow:visible;
}
.typhoon-updated-time .typhoon-updated-time-line,
.typhoon-updated-time .typhoon-update-schedule{
width:100%;
text-align:left;
}
.typhoon-updated-time .typhoon-update-schedule{
margin-top:2px;
font-size:11px;
font-weight:500;
color:#7c8798;
}
.typhoon-fcst-option{
transition:background .15s ease,border-color .15s ease,box-shadow .15s ease,filter .15s ease,color .15s ease;
}
.typhoon-fcst-option:has(input:checked),
.typhoon-fcst-option.is-active{
background:linear-gradient(135deg,rgba(37,99,235,.95),rgba(14,165,233,.88)) !important;
border-color:rgba(37,99,235,.32) !important;
color:#fff !important;
box-shadow:0 8px 18px rgba(37,99,235,.20), inset 0 1px 0 rgba(255,255,255,.22) !important;
}
.typhoon-fcst-option:has(input:checked) span,
.typhoon-fcst-option.is-active span{
color:#fff !important;
}
.typhoon-fcst-option:has(input:checked):hover,
.typhoon-fcst-option.is-active:hover{
filter:saturate(1.06) brightness(1.03);
}
.typhoon-model-detail-button{
appearance:none;
border:1px solid rgba(37,99,235,.22);
background:linear-gradient(135deg,rgba(37,99,235,.95),rgba(14,165,233,.88));
color:#fff;
border-radius:999px;
padding:8px 13px;
font-family:inherit;
font-size:12px;
font-weight:800;
letter-spacing:-.01em;
line-height:1;
display:inline-flex;
align-items:center;
gap:6px;
box-shadow:0 8px 18px rgba(37,99,235,.22), inset 0 1px 0 rgba(255,255,255,.22);
cursor:pointer;
flex:0 0 auto;
transition:box-shadow .15s ease,filter .15s ease,background .15s ease;
}
.typhoon-model-detail-button:hover{
box-shadow:0 8px 18px rgba(37,99,235,.22), inset 0 1px 0 rgba(255,255,255,.26);
filter:saturate(1.06) brightness(1.03);
}
.typhoon-model-detail-button:active{
box-shadow:0 6px 14px rgba(37,99,235,.2), inset 0 1px 0 rgba(255,255,255,.2);
filter:brightness(.98);
}
.typhoon-model-detail-button:focus-visible{
outline:3px solid rgba(56,189,248,.45);
outline-offset:2px;
}
.typhoon-model-detail-button-icon{
font-size:13px;
line-height:1;
}
.typhoon-model-detail-overlay{
position:fixed;
inset:0;
z-index:10000;
display:flex;
align-items:center;
justify-content:center;
padding:28px;
background:rgba(15,23,42,.34);
backdrop-filter:blur(8px) saturate(1.05);
-webkit-backdrop-filter:blur(8px) saturate(1.05);
animation:typhoonDetailOverlayIn .16s ease-out;
}
.typhoon-model-detail-dialog{
width:min(1680px,calc(100vw - 28px));
max-height:min(860px,calc(100vh - 28px));
background:linear-gradient(180deg,#ffffff,#f8fafc);
border:1px solid rgba(148,163,184,.34);
border-radius:22px;
box-shadow:0 26px 70px rgba(2,6,23,.34),0 2px 10px rgba(15,23,42,.10);
display:flex;
flex-direction:column;
overflow:hidden;
animation:typhoonDetailDialogIn .18s cubic-bezier(.2,.8,.2,1);
}
.typhoon-model-detail-header{
display:flex;
align-items:flex-start;
justify-content:space-between;
gap:18px;
padding:22px 24px 18px;
background:linear-gradient(135deg,#0f172a,#1e3a8a 55%,#0369a1);
color:#fff;
}
.typhoon-model-detail-title-wrap{
display:flex;
flex-direction:column;
gap:7px;
min-width:0;
}
.typhoon-model-detail-title{
margin:0;
font-size:23px;
font-weight:850;
letter-spacing:-.035em;
line-height:1.12;
}
.typhoon-model-detail-subtitle{
margin:0;
font-size:13px;
font-weight:600;
color:rgba(219,234,254,.88);
line-height:1.45;
}
.typhoon-model-detail-close{
appearance:none;
border:1px solid rgba(255,255,255,.22);
background:rgba(255,255,255,.12);
color:#fff;
width:36px;
height:36px;
border-radius:12px;
font-size:24px;
line-height:1;
display:flex;
align-items:center;
justify-content:center;
cursor:pointer;
transition:background .15s ease;
flex:0 0 auto;
}
.typhoon-model-detail-close:hover{
background:rgba(255,255,255,.22);
}
.typhoon-model-detail-body{
padding:16px 18px 18px;
min-height:0;
display:flex;
flex-direction:column;
gap:12px;
}
.typhoon-model-detail-summary{
display:flex;
flex-wrap:wrap;
gap:8px;
font-size:12px;
font-weight:800;
color:#334155;
}
.typhoon-model-detail-chip{
border:1px solid rgba(148,163,184,.32);
background:#fff;
border-radius:999px;
padding:6px 10px;
box-shadow:0 2px 8px rgba(15,23,42,.04);
}
.typhoon-model-detail-table-wrap{
min-height:0;
overflow-y:auto;
overflow-x:auto;
overscroll-behavior:contain;
-webkit-overflow-scrolling:touch;
border:1px solid rgba(148,163,184,.28);
border-radius:16px;
background:#fff;
box-shadow:0 8px 24px rgba(15,23,42,.06);
}
.typhoon-model-detail-table{
width:100%;
min-width:1080px;
border-collapse:separate;
border-spacing:0;
font-size:11.7px;
color:#1e293b;
table-layout:auto;
}
.typhoon-model-detail-table thead th{
position:sticky;
top:0;
z-index:1;
background:#eaf2ff;
color:#0f172a;
font-weight:850;
text-align:left;
white-space:nowrap;
padding:10px 8px;
border-bottom:1px solid rgba(148,163,184,.42);
box-shadow:0 1px 0 rgba(255,255,255,.7) inset;
}
.typhoon-model-detail-table tbody td{
padding:9px 8px;
vertical-align:top;
border-bottom:1px solid rgba(226,232,240,.9);
line-height:1.34;
white-space:nowrap;
}
.typhoon-model-detail-table tbody tr:nth-child(even) td{
background:#f8fafc;
}
.typhoon-model-detail-table tbody tr:hover td{
background:#eef6ff;
}
.typhoon-model-detail-table tbody tr:last-child td{
border-bottom:0;
}
.typhoon-model-detail-name{
font-weight:900;
white-space:nowrap;
color:var(--typhoon-model-detail-color,#0f172a);
}
.typhoon-model-detail-basis{
display:inline-flex;
align-items:center;
justify-content:center;
border-radius:999px;
padding:3px 8px;
font-weight:850;
font-size:11.5px;
white-space:nowrap;
}
.typhoon-model-detail-basis.is-ai{
background:#f5e8ff;
color:#7e22ce;
}
.typhoon-model-detail-basis.is-dynamical{
background:#e0f2fe;
color:#075985;
}
.typhoon-model-detail-note{
color:#475569;
}
@keyframes typhoonDetailOverlayIn{
from{opacity:0;}
to{opacity:1;}
}
@keyframes typhoonDetailDialogIn{
from{opacity:0;transform:translateY(10px) scale(.985);}
to{opacity:1;transform:translateY(0) scale(1);}
}
@media (max-width: 1280px){
.typhoon-model-detail-table{font-size:11.5px;}
.typhoon-model-detail-note{min-width:0;}
}
@media (max-width: 900px){
.typhoon-model-detail-overlay{padding:14px;align-items:stretch;}
.typhoon-model-detail-dialog{width:100%;max-height:calc(100vh - 28px);border-radius:18px;}
.typhoon-model-detail-header{padding:18px 18px 15px;}
.typhoon-model-detail-title{font-size:20px;}
.typhoon-model-detail-body{padding:14px;}
.typhoon-model-detail-table{font-size:11.5px;min-width:1040px;}
}
`;
document.head.appendChild(style);
}

function openTyphoonModelDetailModal(triggerElement=null){
ensureTyphoonModelDetailStyles();
closeTyphoonModelDetailModal({restoreFocus:false});
typhoonState.modelDetailLastFocus=triggerElement || document.activeElement;

let overlay=document.createElement('div');
overlay.className='typhoon-model-detail-overlay';
overlay.dataset.role='modelDetailOverlay';
overlay.setAttribute('aria-hidden','false');

let dialog=document.createElement('section');
dialog.className='typhoon-model-detail-dialog';
dialog.setAttribute('role','dialog');
dialog.setAttribute('aria-modal','true');
dialog.setAttribute('aria-labelledby','typhoonModelDetailTitle');
dialog.tabIndex=-1;

let header=document.createElement('div');
header.className='typhoon-model-detail-header';

let titleWrap=document.createElement('div');
titleWrap.className='typhoon-model-detail-title-wrap';

let title=document.createElement('h2');
title.id='typhoonModelDetailTitle';
title.className='typhoon-model-detail-title';
title.textContent='모델 상세정보';

let subtitle=document.createElement('p');
subtitle.className='typhoon-model-detail-subtitle';
subtitle.textContent='2026년 6월 기준 표출 모델';

titleWrap.appendChild(title);
titleWrap.appendChild(subtitle);

let closeButton=document.createElement('button');
closeButton.type='button';
closeButton.className='typhoon-model-detail-close';
closeButton.setAttribute('aria-label','모델 상세 설명 닫기');
closeButton.innerHTML='×';
closeButton.onclick=()=>closeTyphoonModelDetailModal();

header.appendChild(titleWrap);
header.appendChild(closeButton);

let body=document.createElement('div');
body.className='typhoon-model-detail-body';
body.appendChild(createTyphoonModelDetailSummary());
body.appendChild(createTyphoonModelDetailTable());

dialog.appendChild(header);
dialog.appendChild(body);
overlay.appendChild(dialog);
overlay.addEventListener('click',event=>{
if(event.target===overlay){
closeTyphoonModelDetailModal();
}
});

document.body.appendChild(overlay);
dialog.focus({preventScroll:true});
}

function closeTyphoonModelDetailModal({restoreFocus=true}={}){
let overlay=document.querySelector('[data-role="modelDetailOverlay"]');
if(overlay){
overlay.remove();
}
if(restoreFocus && typhoonState.modelDetailLastFocus && typeof typhoonState.modelDetailLastFocus.focus==='function'){
typhoonState.modelDetailLastFocus.focus({preventScroll:true});
}
typhoonState.modelDetailLastFocus=null;
}

function createTyphoonModelDetailSummary(){
let summary=document.createElement('div');
summary.className='typhoon-model-detail-summary';
let activeRows=TYPHOON_MODEL_DETAIL_ROWS.filter(row=>{
let modelKey=row.model_id || row['표출명칭'] || '';
return !TYPHOON_INACTIVE_MODEL_IDS.has(modelKey);
});
let total=activeRows.length;
let aiCount=activeRows.filter(row=>String(row['기반'] || '').toUpperCase()==='AI').length;
let dynamicalCount=total-aiCount;
[
`전체 ${total}개 모델`,
`역학코어 기반 ${dynamicalCount}개 모델`,
`AI 기반 ${aiCount}개 모델`
].forEach(text=>{
let chip=document.createElement('span');
chip.className='typhoon-model-detail-chip';
chip.textContent=text;
summary.appendChild(chip);
});
return summary;
}

function createTyphoonModelDetailTable(){
let wrap=document.createElement('div');
wrap.className='typhoon-model-detail-table-wrap';

let table=document.createElement('table');
table.className='typhoon-model-detail-table';

let thead=document.createElement('thead');
let headRow=document.createElement('tr');
TYPHOON_MODEL_DETAIL_COLUMNS.forEach(column=>{
let th=document.createElement('th');
th.scope='col';
th.textContent=column;
headRow.appendChild(th);
});
thead.appendChild(headRow);

let tbody=document.createElement('tbody');
TYPHOON_MODEL_DETAIL_ROWS.forEach(row=>{
let modelKey=row.model_id || row['표출명칭'] || '';
if(TYPHOON_INACTIVE_MODEL_IDS.has(modelKey)){
return;
}
let tr=document.createElement('tr');
TYPHOON_MODEL_DETAIL_COLUMNS.forEach(column=>{
let td=document.createElement('td');
let value=row[column] || '';
if(column==='표출명칭'){
td.className='typhoon-model-detail-name';
td.style.setProperty('--typhoon-model-detail-color',TYPHOON_MODEL_INFO_COLORS[row.model_id || value] || '#0f172a');
td.textContent=value;
}
else if(column==='기반'){
let chip=document.createElement('span');
let isAi=String(value).toUpperCase()==='AI';
chip.className='typhoon-model-detail-basis '+(isAi?'is-ai':'is-dynamical');
chip.textContent=value || '-';
td.appendChild(chip);
}
else if(column==='참고사항'){
td.className='typhoon-model-detail-note';
td.textContent=value || '-';
}
else{
td.textContent=value || '-';
}
tr.appendChild(td);
});
tbody.appendChild(tr);
});

table.appendChild(thead);
table.appendChild(tbody);
wrap.appendChild(table);
return wrap;
}

function createTyphoonFcstSelector(){
let group=document.createElement('div');
group.className='typhoon-fcst-toggle';
group.setAttribute('role','radiogroup');
group.setAttribute('aria-label','예측기간');

TYPHOON_FCST_OPTIONS.forEach(option=>{
let label=document.createElement('label');
let isActiveOption=typhoonState.selectedFcstHours===option.hours;
label.className='typhoon-fcst-option'+(isActiveOption?' is-active':'');

let input=document.createElement('input');
input.type='radio';
input.name='typhoonFcstHours';
input.value=String(option.hours);
input.dataset.role='fcstOption';
input.checked=isActiveOption;
input.onchange=async()=>{
let requestId=++typhoonState.selectionLoadSeq;
let currentDataTime=getSelectedTyphoonDataTime();
typhoonState.selectedFcstHours=option.hours;
selectDefaultSlotForStorm(currentDataTime);
renderTyphoonSelects();
renderTyphoonTimeline();
setTyphoonViewerLoading(true);
try{
await preloadTyphoonStormImages(typhoonState.selectedStormKey,option.hours,{
isCancelled:()=>requestId!==typhoonState.selectionLoadSeq,
onPriorityLoaded:()=>renderPriorityTyphoonSelection(requestId)
});
if(requestId!==typhoonState.selectionLoadSeq){
return;
}
await renderTyphoonManifest();
}
finally{
if(requestId===typhoonState.selectionLoadSeq){
setTyphoonViewerLoading(false);
}
}
};

let text=document.createElement('span');
text.textContent=option.label;

label.appendChild(input);
label.appendChild(text);
group.appendChild(label);
});

return group;
}

async function renderPriorityTyphoonSelection(requestId){
if(requestId!==typhoonState.selectionLoadSeq){
return;
}
await renderTyphoonSelectedRun();
if(requestId===typhoonState.selectionLoadSeq){
setTyphoonViewerLoading(false);
}
}

async function loadTyphoonManifest(){
let root=typhoonState.root;
if(!root){
return;
}

let showInitialLoading=!typhoonState.initialLoadComplete;
root.classList.add('typhoon-loading-state');
if(showInitialLoading){
setTyphoonViewerLoading(true);
}

try{
let previousYear=typhoonState.selectedYear;
let previousStormKey=typhoonState.selectedStormKey;
let previousDataTime=getSelectedTyphoonDataTime();
let hasPreviousStormSelection=Boolean(previousStormKey);
let manifest=null;
let status=null;
let manifestError=null;
let manifestResult=null;

try{
manifestResult=await fetchTyphoonJsonWithFallback(TYPHOON_MANIFEST_PATH);
manifest=manifestResult.payload;
}
catch(error){
manifestError=error;
}

try{
let statusResult=await fetchTyphoonJsonWithFallback(
TYPHOON_STATUS_PATH,
typhoonDataBaseUrls(manifestResult?.baseUrl)
);
status=statusResult.payload;
}
catch(error){
status=null;
}

if(!manifest && !status){
throw manifestError || new Error('HTTP 404');
}

typhoonState.manifest=manifest;
typhoonState.manifestBaseUrl=manifestResult?.baseUrl || '';
typhoonState.status=status;
typhoonState.stormManifestCache=new Map();
let latestManifestYear=typhoonManifestYears()[0] || '';
if(latestManifestYear){
typhoonState.yearIndexes.delete(latestManifestYear);
typhoonState.typImpactByYear.delete(latestManifestYear);
typhoonState.typNowByYear.delete(latestManifestYear);
typhoonState.tdNowByYear.delete(latestManifestYear);
}
typhoonState.driveArchiveImages=new Map();
typhoonState.driveArchivePathsLoaded=new Set();
typhoonState.driveArchiveLoadPromises=new Map();
rebuildTyphoonEntries();
syncTyphoonSelection({
preferredYear:previousYear,
preferredStormKey:previousStormKey,
preferredDataTime:previousDataTime,
selectDefaultStorm:true
});
renderTyphoonSelects();
await preloadTyphoonDropdownData();
if(!hasPreviousStormSelection){
typhoonState.selectedStormKey='';
}
syncTyphoonSelection({
preferredYear:previousYear,
preferredStormKey:previousStormKey,
preferredDataTime:previousDataTime,
selectDefaultStorm:true
});
await ensureSelectedTyphoonStormManifest();
rebuildTyphoonEntries();
syncTyphoonSelection({preferredYear:previousYear,preferredStormKey:previousStormKey,preferredDataTime:previousDataTime});
renderTyphoonSelects();
renderTyphoonTimeline();
let requestId=typhoonState.selectionLoadSeq;
await preloadTyphoonStormImages(typhoonState.selectedStormKey,typhoonState.selectedFcstHours,{
isCancelled:()=>requestId!==typhoonState.selectionLoadSeq,
onPriorityLoaded:()=>renderPriorityTyphoonSelection(requestId)
});
if(requestId!==typhoonState.selectionLoadSeq){
return;
}
await renderTyphoonManifest();
}
catch(error){
typhoonState.manifest=null;
typhoonState.manifestBaseUrl='';
typhoonState.status=null;
typhoonState.entries=[];
typhoonState.yearIndexes=new Map();
typhoonState.stormManifestCache=new Map();
typhoonState.typImpactByYear=new Map();
typhoonState.typNowByYear=new Map();
typhoonState.tdNowByYear=new Map();
typhoonState.driveArchiveImages=new Map();
typhoonState.driveArchivePathsLoaded=new Set();
typhoonState.driveArchiveLoadPromises=new Map();
syncTyphoonSelection();
renderTyphoonEmpty(`자료 없음 (${error.message})`);
}
finally{
root.classList.remove('typhoon-loading-state');
typhoonState.initialLoadComplete=true;
if(showInitialLoading){
setTyphoonViewerLoading(false);
}
}
}

async function handleTyphoonYearChange(year){
let root=typhoonState.root;
let requestId=++typhoonState.selectionLoadSeq;
typhoonState.selectedYear=String(year || '');
typhoonState.selectedSlotIndex=0;
root?.classList.add('typhoon-loading-state');
setTyphoonViewerLoading(true);
rebuildTyphoonEntries();
syncTyphoonSelection({preferredYear:typhoonState.selectedYear,selectDefaultStorm:true});
renderTyphoonSelects();
try{
await ensureTyphoonYearIndex(typhoonState.selectedYear);
if(!typhoonState.typImpactByYear.has(typhoonState.selectedYear) || !typhoonState.typNowByYear.has(typhoonState.selectedYear) || !typhoonState.tdNowByYear.has(typhoonState.selectedYear)){
await loadTyphoonImpactMapsForYears([typhoonState.selectedYear]);
}
rebuildTyphoonEntries();
syncTyphoonSelection({preferredYear:typhoonState.selectedYear,selectDefaultStorm:true});
if(requestId!==typhoonState.selectionLoadSeq){
return;
}
pruneTyphoonImageCache();
renderTyphoonSelects();
await loadTyphoonStormSelection(typhoonState.selectedStormKey,requestId);
}
finally{
root?.classList.remove('typhoon-loading-state');
if(requestId===typhoonState.selectionLoadSeq){
setTyphoonViewerLoading(false);
}
}
}

async function loadTyphoonStormSelection(stormKey,requestId,preferredDataTime=''){
typhoonState.selectedStormKey=String(stormKey || '');
typhoonState.selectedSlotIndex=0;
await ensureSelectedTyphoonStormManifest();
if(requestId!==typhoonState.selectionLoadSeq){
return false;
}
rebuildTyphoonEntries();
selectDefaultSlotForStorm(preferredDataTime);
renderTyphoonSelects();
renderTyphoonTimeline();
await preloadTyphoonStormImages(typhoonState.selectedStormKey,typhoonState.selectedFcstHours,{
isCancelled:()=>requestId!==typhoonState.selectionLoadSeq,
onPriorityLoaded:()=>renderPriorityTyphoonSelection(requestId)
});
if(requestId!==typhoonState.selectionLoadSeq){
return false;
}
pruneTyphoonImageCache();
await renderTyphoonManifest();
return true;
}

async function handleTyphoonStormChange(stormKey){
let root=typhoonState.root;
let requestId=++typhoonState.selectionLoadSeq;
let preferredDataTime=getSelectedTyphoonDataTime();
root?.classList.add('typhoon-loading-state');
setTyphoonViewerLoading(true);
try{
await loadTyphoonStormSelection(stormKey,requestId,preferredDataTime);
}
finally{
root?.classList.remove('typhoon-loading-state');
if(requestId===typhoonState.selectionLoadSeq){
setTyphoonViewerLoading(false);
}
}
}

function rebuildTyphoonEntries(){
let loadedInventory=[];
typhoonState.stormManifestCache.forEach(payload=>{
if(Array.isArray(payload?.inventory)){
loadedInventory.push(...payload.inventory);
}
});
let rootRuns=Array.isArray(typhoonState.manifest?.runs) ? typhoonState.manifest.runs : [];
let rootInventory=Array.isArray(typhoonState.manifest?.inventory) ? typhoonState.manifest.inventory : [];
typhoonState.entries=normalizeTyphoonEntries({
...typhoonState.manifest,
inventory:[],
runs:[...rootInventory,...rootRuns,...loadedInventory]
},typhoonState.status);
}

function typhoonManifestYears(){
let years=new Set();
let indexes=Array.isArray(typhoonState.manifest?.manifest_indexes) ? typhoonState.manifest.manifest_indexes : [];
indexes.forEach(item=>{
let year=String(item?.year || '').trim();
if(year){
years.add(year);
}
});
typhoonState.entries.forEach(entry=>{
if(entry.year){
years.add(entry.year);
}
});
return [...years].sort((a,b)=>b.localeCompare(a));
}

async function ensureTyphoonYearIndex(year){
let key=String(year || '').trim();
if(!key || typhoonState.yearIndexes.has(key)){
return typhoonState.yearIndexes.get(key) || null;
}

let indexes=Array.isArray(typhoonState.manifest?.manifest_indexes) ? typhoonState.manifest.manifest_indexes : [];
let item=indexes.find(index=>String(index?.year || '').trim()===key);
let path=String(item?.path || '').trim();
if(!path){
typhoonState.yearIndexes.set(key,null);
return null;
}
try{
let payload=await fetchTyphoonJson(path,typhoonState.manifestBaseUrl);
typhoonState.yearIndexes.set(key,payload);
return payload;
}
catch(error){
console.warn(`?쒗뭾 year index 濡쒕뱶 ?ㅽ뙣: ${path}`,error);
typhoonState.yearIndexes.set(key,null);
return null;
}
}

async function preloadTyphoonDropdownData(){
let years=typhoonManifestYears();
await Promise.all([
Promise.all(years.map(year=>ensureTyphoonYearIndex(year))),
loadTyphoonImpactMapsForYears(years)
]);
}

function typhoonYearSummaryEntries(year){
let key=String(year || '').trim();
let indexPayload=typhoonState.yearIndexes.get(key);
let systems=Array.isArray(indexPayload?.systems) ? indexPayload.systems : [];
if(!systems.length){
return [];
}
let entries=systems
.map((system,index)=>summaryEntryFromYearSystem(system,index))
.filter(Boolean);
return dedupeLinkedTyphoonEntries(linkTdEntriesToTyphoons(entries))
.sort((a,b)=>a.sortKey.localeCompare(b.sortKey));
}

function summaryEntryFromYearSystem(system,index=0){
let year=String(system?.year || '').trim();
let stage=normalizeTyphoonStage(system?.stage || 'TYP');
let typNumber=Number(system?.typ_number || 0);
let typName=normalizeTyphoonName(system?.typ_name || 'NONAME');
let typNameKo=system?.typ_name_ko || koreanTyphoonName(typName);
let dataTime=String(system?.latest_data_time || '').trim();
if(!year || !typNumber || !dataTime){
return null;
}
return applyTyphoonSortKey({
index,
entry:system,
metadata:{},
job:system,
windowInfo:{},
imagePath:'',
dataTime,
generatedAt:'',
fcstHours:typhoonState.selectedFcstHours || 120,
year,
stage,
typNumber,
tdNumber:system?.linked_td_number || null,
linkedTypNumber:system?.linked_typ_number || null,
typNameKo,
typName,
stormKey:[year,stage,typNumber,typName].join('|'),
manifestPath:String(system?.manifest_path || '').trim(),
summaryOnly:true
});
}

async function ensureSelectedTyphoonStormManifest(){
let paths=manifestPathsForStormKey(typhoonState.selectedYear,typhoonState.selectedStormKey);
let missing=paths.filter(path=>path && !typhoonState.stormManifestCache.has(path));
if(!missing.length){
return;
}
await Promise.all(missing.map(async path=>{
try{
let payload=await fetchTyphoonJson(path,typhoonState.manifestBaseUrl);
typhoonState.stormManifestCache.set(path,payload);
}
catch(error){
console.warn(`?쒗뭾 storm manifest 濡쒕뱶 ?ㅽ뙣: ${path}`,error);
}
}));
}

function typhoonStormKeyInfo(stormKey){
let parts=String(stormKey || '').split('|');
return {
year:String(parts[0] || ''),
stage:normalizeTyphoonStage(parts[1] || ''),
typNumber:Number(parts[2] || 0),
typName:parts.slice(3).join('|')
};
}

function entryMatchesSelectedStormManifest(entry,selected,yearText,selectedKey){
if(!entry?.manifestPath || String(entry.year || '')!==yearText){
return false;
}
if(entry.stormKey===selectedKey){
return true;
}
let linkedTypNumber=Number(entry.linkedTypNumber || entry.linked_typ_number || 0);
if(selected.stage!=='TD' && entry.stage==='TD' && linkedTypNumber===selected.typNumber){
return true;
}
return false;
}

function manifestPathsForStormKey(year,stormKey){
let paths=new Set();
let yearText=String(year || '').trim();
let selectedKey=String(stormKey || '');
let selected=typhoonStormKeyInfo(selectedKey);

typhoonYearSummaryEntries(year).forEach(entry=>{
if(entry.stormKey===selectedKey && entry.manifestPath){
paths.add(entry.manifestPath);
return;
}
if(entryMatchesSelectedStormManifest(entry,selected,yearText,selectedKey)){
paths.add(entry.manifestPath);
}
});
if(!paths.size){
typhoonState.entries.forEach(entry=>{
if(entry.year===yearText && entry.stormKey===selectedKey && entry.manifestPath){
paths.add(entry.manifestPath);
return;
}
if(entryMatchesSelectedStormManifest(entry,selected,yearText,selectedKey)){
paths.add(entry.manifestPath);
}
});
}
return [...paths];
}

async function fetchTyphoonJsonBatch(paths,concurrency=8,baseUrl=''){
let results=[];
let index=0;
let workers=Array.from({length:Math.max(1,Math.min(concurrency,paths.length || 1))},async ()=>{
while(index<paths.length){
let current=index++;
try{
results[current]=await fetchTyphoonJson(paths[current],baseUrl);
}
catch(error){
console.warn(`태풍 manifest 로드 실패: ${paths[current]}`,error);
results[current]=null;
}
}
});
await Promise.all(workers);
return results.filter(Boolean);
}

async function fetchTyphoonJson(path,baseUrl=''){
let url=typhoonBuildUrl(path,baseUrl);
let response=await fetch(`${url}${url.includes('?') ? '&' : '?'}fresh=${Date.now()}`,{cache:'no-store'});
if(!response.ok){
throw new Error(`HTTP ${response.status}`);
}
return response.json();
}

async function fetchTyphoonJsonWithFallback(path,baseUrls=typhoonDataBaseUrls()){
let lastError=null;
for(let baseUrl of baseUrls){
try{
return {
payload:await fetchTyphoonJson(path,baseUrl),
baseUrl
};
}
catch(error){
lastError=error;
}
}
throw lastError || new Error('HTTP 404');
}

function typhoonSystemRootFromAssetPath(value){
let path=normalizeTyphoonAssetPath(value);
let parts=path.split('/').filter(Boolean);
if(parts.length>=3 && parts[0]==='data' && /^\d{4}$/.test(parts[1])){
return parts.slice(0,3).join('/');
}
return '';
}

function typhoonDriveArchivePathForRun(run){
let explicit=String(run?.metadata?.drive_archive_path || run?.driveArchivePath || '').trim();
if(explicit){
return normalizeTyphoonAssetPath(explicit);
}
let systemRoot=typhoonSystemRootFromAssetPath(run?.imagePath || run?.metadata?.image_path || '');
return systemRoot ? `${systemRoot}/drive_archive.json` : '';
}

async function loadTyphoonDriveArchiveImages(path,baseUrl=''){
if(!path){
return new Map();
}
try{
let result=await fetchTyphoonJsonWithFallback(
path,
typhoonDataBaseUrls(baseUrl)
);
return normalizeTyphoonDriveArchiveImages(result.payload);
}
catch(error){
return new Map();
}
}

async function ensureTyphoonDriveArchiveImagesForPath(path){
let archivePath=normalizeTyphoonAssetPath(path);
if(!archivePath || typhoonState.driveArchivePathsLoaded.has(archivePath)){
return typhoonState.driveArchiveImages;
}
if(!typhoonState.driveArchiveLoadPromises.has(archivePath)){
let promise=loadTyphoonDriveArchiveImages(archivePath,typhoonState.manifestBaseUrl)
.then(images=>{
images.forEach((url,imagePath)=>{
typhoonState.driveArchiveImages.set(imagePath,url);
});
typhoonState.driveArchivePathsLoaded.add(archivePath);
return typhoonState.driveArchiveImages;
})
.catch(error=>{
console.warn('?쒗뭾 Drive archive manifest 濡쒕뱶 ?ㅽ뙣',error);
typhoonState.driveArchivePathsLoaded.add(archivePath);
return typhoonState.driveArchiveImages;
})
.finally(()=>{
typhoonState.driveArchiveLoadPromises.delete(archivePath);
});
typhoonState.driveArchiveLoadPromises.set(archivePath,promise);
}
return typhoonState.driveArchiveLoadPromises.get(archivePath);
}

async function ensureTyphoonDriveArchiveImagesForRun(run){
if(!run?.imagePath || typhoonState.driveArchiveImages.has(run.imagePath)){
return;
}
await ensureTyphoonDriveArchiveImagesForPath(typhoonDriveArchivePathForRun(run));
}

function normalizeTyphoonDriveArchiveImages(payload){
let images=payload?.images || payload?.entries || {};
let archiveMap=new Map();

if(Array.isArray(images)){
images.forEach(item=>{
let path=normalizeTyphoonAssetPath(item?.image_path || item?.imagePath || item?.path || '');
let url=normalizeTyphoonDriveArchiveUrl(
item?.url || item?.drive_url || item?.driveUrl || item?.thumbnail_url || '',
item?.file_id || item?.fileId || ''
);
if(path && url){
archiveMap.set(path,url);
}
});
return archiveMap;
}

if(images && typeof images==='object'){
Object.entries(images).forEach(([path,value])=>{
let normalizedPath=normalizeTyphoonAssetPath(path);
let fileId=typeof value==='string' ? '' : String(value?.file_id || value?.fileId || '').trim();
let url=typeof value==='string'
?normalizeTyphoonDriveArchiveUrl(value)
:normalizeTyphoonDriveArchiveUrl(value?.url || value?.drive_url || value?.driveUrl || value?.thumbnail_url || '',fileId);
if(normalizedPath && url){
archiveMap.set(normalizedPath,url);
}
});
}

return archiveMap;
}

function normalizeTyphoonDriveArchiveUrl(value,fileId=''){
let url=String(value || '').trim();
let id=String(fileId || '').trim();
if(!id && url){
try{
let parsed=new URL(url,window.location.href);
let host=parsed.hostname.toLowerCase();
if(host==='drive.google.com' || host==='drive.usercontent.google.com'){
id=parsed.searchParams.get('id') || '';
}
}
catch(error){
id='';
}
}
if(id && /^https:\/\/drive\.google\.com\/uc\?/i.test(url)){
return typhoonDriveUserContentUrl(id);
}
if(!url && id){
return typhoonDriveUserContentUrl(id);
}
return url;
}

function typhoonDriveUserContentUrl(fileId){
let id=String(fileId || '').trim();
return id ? `https://drive.usercontent.google.com/download?id=${encodeURIComponent(id)}&export=view&authuser=0` : '';
}

function normalizeTyphoonEntries(manifest,status){
let source=Array.isArray(manifest?.inventory) && manifest.inventory.length ? manifest.inventory : manifest?.runs;
let runs=Array.isArray(source) ? source : [];
let statusRuns=normalizeStatusRuns(status);

let seen=new Set();
let normalized=[...runs,...statusRuns]
.map((entry,index)=>{
let metadata=entry?.result?.metadata || {};
let job=entry?.job || {};
let windowInfo=entry?.window || {};
let imagePath=normalizeTyphoonAssetPath(metadata.image_path || '');
let dataTime=metadata.data_time || job.data_time || windowInfo.data_time || '';
let generatedAt=metadata.generated_at_utc || manifest.updated_at_utc || '';
let fcstHours=Number(metadata.fcst_hours || job.fcst_hours || parseTyphoonFcstHoursFromPath(imagePath) || 120);
let year=String(metadata.storm_year || job.year || dataTime.slice(0,4) || '');
let rawStage=normalizeTyphoonStage(metadata.storm_stage || job.stage || 'TYP');
let rawTypNumber=Number(metadata.typ_number || job.typ_number || 0);
let linkedTypNumber=metadata.linked_typ_number || job.linked_typ_number || null;
let rawTypName=normalizeTyphoonName(metadata.typ_name || job.typ_name || 'NONAME');
let rawTypNameKo=metadata.typ_name_ko || job.typ_name_ko || koreanTyphoonName(rawTypName);
let hasCanonicalIdentity=Boolean(
metadata.canonical_storm_stage || metadata.canonical_typ_number || metadata.canonical_typ_name ||
job.canonical_storm_stage || job.canonical_typ_number || job.canonical_typ_name
);
let stage=hasCanonicalIdentity
?normalizeTyphoonStage(metadata.canonical_storm_stage || job.canonical_storm_stage || rawStage)
:rawStage;
let typNumber=Number(
hasCanonicalIdentity
?(metadata.canonical_typ_number || job.canonical_typ_number || rawTypNumber)
:rawTypNumber
);
let typName=normalizeTyphoonName(
hasCanonicalIdentity
?(metadata.canonical_typ_name || job.canonical_typ_name || rawTypName || 'NONAME')
:(rawTypName || 'NONAME')
);
let typNameKo=hasCanonicalIdentity
?(metadata.canonical_typ_name_ko || job.canonical_typ_name_ko || rawTypNameKo || koreanTyphoonName(typName))
:(rawTypNameKo || koreanTyphoonName(typName));
let tdNumber=rawStage==='TD'
?rawTypNumber
:(metadata.linked_td_number || job.linked_td_number || job.td_number || null);
let stormKey=[year,stage,typNumber,typName].join('|');
return applyTyphoonSortKey({
index,
entry,
metadata,
job,
windowInfo,
imagePath,
dataTime,
generatedAt,
fcstHours,
year,
stage,
originalStage:rawStage!==stage ? rawStage : undefined,
typNumber,
tdNumber,
linkedTypNumber,
typNameKo,
typName,
stormKey
});
})
.filter(run=>run.year && run.dataTime && run.imagePath && !run.metadata?.no_output)
.filter(run=>{
let key=`${run.year}|${run.stage}|${run.typNumber}|${run.dataTime}|${run.fcstHours}|${run.imagePath}`;
if(seen.has(key)){
return false;
}
seen.add(key);
return true;
});

return dedupeLinkedTyphoonEntries(linkTdEntriesToTyphoons(normalized))
.sort((a,b)=>a.sortKey.localeCompare(b.sortKey));
}

function applyTyphoonSortKey(run){
run.sortKey=`${run.year}${String(run.typNumber).padStart(2,'0')}${run.dataTime}${String(run.fcstHours).padStart(3,'0')}${run.generatedAt}`.padEnd(37,'0');
return run;
}

function normalizeTyphoonStage(stage){
let text=String(stage || 'TYP').trim().toUpperCase();
if(text.startsWith('TD')){
return 'TD';
}
if(text.startsWith('TYP')){
return 'TYP';
}
return text || 'TYP';
}

function linkTdEntriesToTyphoons(entries){
let tdLinks=new Map();
let typLinks=new Map();

function keepEarliest(map,key,entry){
let existing=map.get(key);
if(!existing || String(entry.dataTime || '')<String(existing.dataTime || '')){
map.set(key,entry);
}
}

entries.forEach(entry=>{
if(entry.stage==='TD'){
return;
}
if(entry.tdNumber){
keepEarliest(tdLinks,`${entry.year}|${Number(entry.tdNumber)}`,entry);
}
if(entry.typNumber){
keepEarliest(typLinks,`${entry.year}|${Number(entry.typNumber)}`,entry);
}
});

if(!tdLinks.size && !typLinks.size){
return entries;
}

return entries.map(entry=>{
if(entry.stage!=='TD'){
return entry;
}
let linked=tdLinks.get(`${entry.year}|${entry.typNumber}`);
if(!linked && entry.linkedTypNumber){
linked=typLinks.get(`${entry.year}|${Number(entry.linkedTypNumber)}`);
}
if(!linked){
return entry;
}

let firstNamedTyp=typLinks.get(`${entry.year}|${Number(linked.typNumber)}`) || linked;
linked=firstNamedTyp;

return applyTyphoonSortKey({
...entry,
originalStage:'TD',
stage:linked.stage,
typNumber:linked.typNumber,
typName:linked.typName,
typNameKo:linked.typNameKo,
tdNumber:entry.typNumber,
linkedTypNumber:entry.linkedTypNumber,
stormKey:linked.stormKey
});
});
}

function dedupeLinkedTyphoonEntries(entries){
let byKey=new Map();
entries.forEach(entry=>{
let key=`${entry.year}|${entry.stormKey}|${entry.dataTime}|${entry.fcstHours}`;
let existing=byKey.get(key);
if(!existing){
byKey.set(key,entry);
return;
}
if(existing.originalStage==='TD' && entry.originalStage!=='TD'){
byKey.set(key,entry);
return;
}
if(String(entry.generatedAt || '')>String(existing.generatedAt || '')){
byKey.set(key,entry);
}
});
return [...byKey.values()];
}

function normalizeStatusRuns(status){
let cycles=status?.cycles || {};
let entries=[];
Object.keys(cycles).forEach(dataTime=>{
let storms=cycles[dataTime] || {};
Object.keys(storms).forEach(stormKey=>{
let record=storms[stormKey] || {};
let metadata=record.metadata || {};
if(!metadata.data_time){
metadata={...metadata,data_time:dataTime};
}
let typName=normalizeTyphoonName(metadata.typ_name || 'NONAME');
entries.push({
job:{
storm_key:stormKey,
stage:normalizeTyphoonStage(metadata.storm_stage || 'TYP'),
year:Number(metadata.storm_year || String(dataTime).slice(0,4)),
data_time:dataTime,
td_number:null,
linked_td_number:metadata.linked_td_number || null,
linked_typ_number:metadata.linked_typ_number || null,
typ_number:metadata.typ_number || 0,
typ_name:typName,
typ_name_ko:metadata.typ_name_ko || koreanTyphoonName(typName),
canonical_storm_stage:metadata.canonical_storm_stage || '',
canonical_typ_number:metadata.canonical_typ_number || null,
canonical_typ_name:metadata.canonical_typ_name || '',
canonical_typ_name_ko:metadata.canonical_typ_name_ko || '',
typ_en:typName,
atcf_id:metadata.atcf_id || '',
fcst_hours:metadata.fcst_hours || parseTyphoonFcstHoursFromPath(metadata.image_path || '') || 120,
skip_atcf:!!metadata.skip_atcf
},
window:{data_time:dataTime},
result:{status:record.last_status || 'status',metadata}
});
});
});
return entries;
}

function syncTyphoonSelection({preferredYear='',preferredStormKey='',preferredDataTime='',selectDefaultStorm=true}={}){
typhoonState.years=typhoonManifestYears();

let preferredYearText=String(preferredYear || '');
if(preferredYearText && typhoonState.years.includes(preferredYearText)){
typhoonState.selectedYear=preferredYearText;
}
else if(!typhoonState.years.includes(typhoonState.selectedYear)){
typhoonState.selectedYear=typhoonState.years[0] || '';
}

typhoonState.storms=buildTyphoonStormsForYear(typhoonState.selectedYear);

let preferredStormText=String(preferredStormKey || '');
if(preferredStormText && typhoonState.storms.some(storm=>storm.key===preferredStormText)){
typhoonState.selectedStormKey=preferredStormText;
}
else if(!typhoonState.storms.some(storm=>storm.key===typhoonState.selectedStormKey)){
if(selectDefaultStorm){
selectDefaultStormForYear();
}
else{
typhoonState.selectedStormKey='';
typhoonState.selectedSlotIndex=0;
}
}

typhoonState.slots=buildTyphoonSlotsForStorm(typhoonState.selectedStormKey);

let preferredSlotIndex=preferredDataTime
?typhoonState.slots.findIndex(slot=>slot.dataTime===preferredDataTime && slot.entry)
:-1;
if(preferredSlotIndex>=0){
typhoonState.selectedSlotIndex=preferredSlotIndex;
}
// Initial summary entries and the full storm manifest can have different slot counts.
else if(!preferredDataTime || typhoonState.selectedSlotIndex<0 || typhoonState.selectedSlotIndex>=typhoonState.slots.length || !typhoonState.slots[typhoonState.selectedSlotIndex]?.entry){
selectDefaultSlotForStorm();
}
}


async function loadTyphoonImpactMapsForYears(years){
let uniqueYears=[...new Set((years || []).map(year=>String(year || '').trim()).filter(Boolean))]
.filter(year=>!typhoonState.typImpactByYear.has(year) || !typhoonState.typNowByYear.has(year) || !typhoonState.tdNowByYear.has(year));
let nextImpactMap=new Map(typhoonState.typImpactByYear);
let nextNowMap=new Map(typhoonState.typNowByYear);
let nextTdNowMap=new Map(typhoonState.tdNowByYear);
await Promise.all(uniqueYears.map(async year=>{
let maps=await fetchTyphoonListMapsForYear(year);
nextImpactMap.set(year,maps.impact);
nextNowMap.set(year,maps.now);
nextTdNowMap.set(year,maps.tdNow);
}));
typhoonState.typImpactByYear=nextImpactMap;
typhoonState.typNowByYear=nextNowMap;
typhoonState.tdNowByYear=nextTdNowMap;
}

async function fetchTyphoonListMapsForYear(year){
let path=`${TYPHOON_TYP_LIST_CACHE_PREFIX}${year}${TYPHOON_TYP_LIST_CACHE_SUFFIX}`;
let tdPath=`${TYPHOON_TD_LIST_CACHE_PREFIX}${year}${TYPHOON_TYP_LIST_CACHE_SUFFIX}`;
let impact=new Map();
let now=new Map();
let tdNow=new Map();
try{
let payload=await fetchTyphoonJson(path,typhoonState.manifestBaseUrl);
let rows=Array.isArray(payload?.rows) ? payload.rows : [];
rows.forEach(row=>{
let seq=Number(row?.SEQ);
let eff=normalizeTyphoonImpactEff(row?.EFF);
let status=normalizeTyphoonNowStatus(row?.NOW);
if(!Number.isFinite(seq) || seq<=0){
return;
}
if(eff){
impact.set(String(seq),eff);
}
if(status){
now.set(String(seq),{
status,
startTime:String(row?.TM_ST || '').trim(),
endTime:String(row?.TM_ED || '').trim()
});
}
});
}
catch(error){
}
try{
let tdPayload=await fetchTyphoonJson(tdPath,typhoonState.manifestBaseUrl);
let tdRows=Array.isArray(tdPayload?.rows) ? tdPayload.rows : [];
tdRows.forEach(row=>{
let td=Number(row?.TD);
if(!Number.isFinite(td) || td<=0){
return;
}
tdNow.set(String(td),{
status:'1',
startTime:String(row?.TM_ST || '').trim(),
endTime:String(row?.TM_ED || '').trim()
});
});
}
catch(error){
}
return {impact,now,tdNow};
}

function normalizeTyphoonImpactEff(value){
let text=String(value ?? '').trim();
return ['1','2','3','4'].includes(text) ? text : '';
}

function normalizeTyphoonNowStatus(value){
let text=String(value ?? '').trim();
return ['1','2'].includes(text) ? text : '';
}

function typhoonImpactEffLabel(eff){
if(eff==='1') return '상륙';
if(eff==='2') return '직접영향';
if(eff==='3') return '간접영향';
if(eff==='4') return '영향 없음';
return '';
}

function preferredTyphoonImpactEff(current,next){
let currentEff=normalizeTyphoonImpactEff(current);
let nextEff=normalizeTyphoonImpactEff(next);
if(!currentEff) return nextEff;
if(!nextEff) return currentEff;
return Number(nextEff)<Number(currentEff) ? nextEff : currentEff;
}

function typhoonImpactEffectForEntry(entry){
let metadata=entry?.metadata || {};
let job=entry?.job || {};
let rawStage=normalizeTyphoonStage(entry?.originalStage || entry?.stage || metadata.storm_stage || job.stage || '');
if(rawStage==='TD'){
return '';
}
let explicit=normalizeTyphoonImpactEff(
metadata.typ_eff ?? metadata.kma_eff ?? metadata.impact_eff ??
job.typ_eff ?? job.kma_eff ?? job.impact_eff ?? ''
);
if(explicit){
return explicit;
}
let year=String(entry?.year || metadata.storm_year || job.year || '').trim();
let typNumber=Number(entry?.typNumber || metadata.linked_typ_number || metadata.typ_number || job.linked_typ_number || job.typ_number || 0);
if(!year || !Number.isFinite(typNumber) || typNumber<=0){
return '';
}
let yearMap=typhoonState.typImpactByYear instanceof Map ? typhoonState.typImpactByYear.get(year) : null;
return yearMap instanceof Map ? (yearMap.get(String(typNumber)) || '') : '';
}

function typhoonNowStatusForEntry(entry){
return typhoonNowStatusFromRecord(typhoonNowRecordForEntry(entry));
}

function typhoonNowRecordForEntry(entry){
let metadata=entry?.metadata || {};
let job=entry?.job || {};
let rawStage=normalizeTyphoonStage(entry?.originalStage || entry?.stage || metadata.storm_stage || job.stage || '');
let year=String(entry?.year || metadata.storm_year || job.year || '').trim();
if(rawStage==='TD'){
let tdNumber=Number(entry?.tdNumber || metadata.td_number || job.td_number || metadata.data_typ_number || metadata.typ_number || job.typ_number || entry?.typNumber || 0);
if(!year || !Number.isFinite(tdNumber) || tdNumber<=0){
return null;
}
let tdYearMap=typhoonState.tdNowByYear instanceof Map ? typhoonState.tdNowByYear.get(year) : null;
return tdYearMap instanceof Map ? (tdYearMap.get(String(tdNumber)) || null) : null;
}
let typNumber=Number(entry?.typNumber || metadata.canonical_typ_number || metadata.typ_number || job.canonical_typ_number || job.typ_number || 0);
if(!year || !Number.isFinite(typNumber) || typNumber<=0){
return null;
}
let yearMap=typhoonState.typNowByYear instanceof Map ? typhoonState.typNowByYear.get(year) : null;
return yearMap instanceof Map ? (yearMap.get(String(typNumber)) || null) : null;
}

function typhoonNowStatusFromRecord(record){
if(!record){
return '';
}
if(typeof record==='string'){
return normalizeTyphoonNowStatus(record);
}
return normalizeTyphoonNowStatus(record.status);
}

function isActiveTyphoonNowRecord(record){
let status=typhoonNowStatusFromRecord(record);
if(status!=='1' || isEndedTyphoonNowRecord(record)){
return false;
}
if(record && typeof record==='object'){
let startTime=String(record.startTime || '').trim();
if(startTime){
let startDate=parseTyphoonUtcDate(startTime);
if(startDate && startDate.getTime()>Date.now()){
return false;
}
}
}
return true;
}

function isEndedTyphoonNowRecord(record){
if(!record || typeof record!=='object'){
return false;
}
let endTime=String(record.endTime || '').trim();
if(!endTime){
return false;
}
let endDate=parseTyphoonUtcDate(endTime);
return Boolean(endDate && endDate.getTime()<Date.now());
}

function isKoreaImpactTyphoonEntry(entry){
return TYPHOON_IMPACT_EFF_VALUES.has(typhoonImpactEffectForEntry(entry));
}

function compareTyphoonStormRecency(a,b){
return (
String(b.sortTime || '').localeCompare(String(a.sortTime || '')) ||
String(b.latest || '').localeCompare(String(a.latest || '')) ||
Number(b.typNumber || 0)-Number(a.typNumber || 0) ||
a.label.localeCompare(b.label)
);
}

function compareTyphoonStormOrder(a,b){
let activeOrder=Number(Boolean(b.active))-Number(Boolean(a.active));
if(activeOrder){
return activeOrder;
}
if(a.active && b.active){
return compareTyphoonStormRecency(a,b);
}

let aIsTyp=a.stage!=='TD';
let bIsTyp=b.stage!=='TD';
if(aIsTyp!==bIsTyp){
return compareTyphoonStormRecency(a,b);
}
if(aIsTyp){
return (
Number(b.typNumber || 0)-Number(a.typNumber || 0) ||
compareTyphoonStormRecency(a,b)
);
}
return compareTyphoonStormRecency(a,b);
}

function buildTyphoonStormsForYear(year){
let byKey=new Map();
let activeWindowTimes=typhoonActiveWindowDataTimes();
let summaryEntries=typhoonYearSummaryEntries(year);
let sourceEntries=summaryEntries.length ? summaryEntries : typhoonState.entries.filter(entry=>entry.year===year);
sourceEntries
.filter(entry=>entry.year===year)
.forEach(entry=>{
let isNamedTypEntry=entry.stage!=='TD' && entry.originalStage!=='TD';
let impactEff=typhoonImpactEffectForEntry(entry);
let entryLabel=stormDropdownLabel(entry);
let entryLabelHasKo=Boolean(String(entry.typNameKo || '').trim());
if(!byKey.has(entry.stormKey)){
byKey.set(entry.stormKey,{
key:entry.stormKey,
typNumber:entry.typNumber,
stage:entry.stage,
label:entryLabel,
labelHasKo:entryLabelHasKo,
first:entry.dataTime,
latest:entry.dataTime,
typFirst:isNamedTypEntry ? entry.dataTime : '',
active:isActiveTyphoonStormEntry(entry,activeWindowTimes),
impactEff,
impact:TYPHOON_IMPACT_EFF_VALUES.has(impactEff),
manifestPaths:new Set()
});
}
let storm=byKey.get(entry.stormKey);
if(entryLabelHasKo && !storm.labelHasKo){
storm.label=entryLabel;
storm.labelHasKo=true;
}
if(entry.manifestPath){
storm.manifestPaths.add(entry.manifestPath);
}
if(entry.stage!=='TD'){
storm.stage=entry.stage;
}
if(isNamedTypEntry && (!storm.typFirst || entry.dataTime<storm.typFirst)){
storm.typFirst=entry.dataTime;
}
if(entry.dataTime<storm.first){
storm.first=entry.dataTime;
}
if(entry.dataTime>storm.latest){
storm.latest=entry.dataTime;
}
if(isActiveTyphoonStormEntry(entry,activeWindowTimes)){
storm.active=true;
}
storm.impactEff=preferredTyphoonImpactEff(storm.impactEff,impactEff);
if(TYPHOON_IMPACT_EFF_VALUES.has(storm.impactEff)){
storm.impact=true;
}
});
typhoonState.entries
.filter(entry=>entry.year===year)
.forEach(entry=>{
let storm=byKey.get(entry.stormKey);
if(storm && isActiveTyphoonStormEntry(entry,activeWindowTimes)){
storm.active=true;
}
});
return [...byKey.values()]
.map(storm=>({
...storm,
manifestPaths:[...storm.manifestPaths],
sortTime:(storm.stage==='TD' ? storm.first : (storm.typFirst || storm.first)) || storm.first
}))
.sort(compareTyphoonStormOrder);
}

function typhoonActiveWindowDataTimes(){
let windows=Array.isArray(typhoonState.manifest?.active_windows) ? typhoonState.manifest.active_windows : [];
let times=new Set();
windows.forEach(window=>{
let dataTime=String(window?.data_time || '').trim();
if(dataTime){
times.add(dataTime);
times.add(dataTime.slice(0,10));
}
});
return times;
}

function isActiveTyphoonStormEntry(entry,activeWindowTimes=typhoonActiveWindowDataTimes()){
let nowRecord=typhoonNowRecordForEntry(entry);
let nowStatus=typhoonNowStatusFromRecord(nowRecord);
if(nowStatus){
return isActiveTyphoonNowRecord(nowRecord);
}
let dataTime=String(entry?.dataTime || '');
return Boolean(dataTime && (activeWindowTimes.has(dataTime) || activeWindowTimes.has(dataTime.slice(0,10))));
}

function isActiveTyphoonStormRun(run,activeWindowTimes=typhoonActiveWindowDataTimes()){
let stormKey=String(run?.stormKey || '');
if(!stormKey){
return isActiveTyphoonStormEntry(run,activeWindowTimes);
}
return isActiveTyphoonStorm(stormKey,activeWindowTimes);
}

function isActiveTyphoonStorm(stormKey,activeWindowTimes=typhoonActiveWindowDataTimes()){
let normalizedStormKey=String(stormKey || '');
if(!normalizedStormKey){
return false;
}
let storms=Array.isArray(typhoonState.storms) ? typhoonState.storms : [];
if(storms.some(storm=>storm.key===normalizedStormKey && storm.active)){
return true;
}
let entries=Array.isArray(typhoonState.entries) ? typhoonState.entries : [];
return entries.some(entry=>entry.stormKey===normalizedStormKey && isActiveTyphoonStormEntry(entry,activeWindowTimes));
}

function selectDefaultStormForYear(){
let storms=buildTyphoonStormsForYear(typhoonState.selectedYear);
typhoonState.storms=storms;
typhoonState.selectedStormKey=storms.length ? storms[0].key : '';
selectDefaultSlotForStorm();
}

function selectDefaultSlotForStorm(preferredDataTime=''){
typhoonState.slots=buildTyphoonSlotsForStorm(typhoonState.selectedStormKey);
let firstAvailable=-1;
let firstTypAvailable=-1;
let latestAvailable=-1;
typhoonState.slots.forEach((slot,index)=>{
if(slot.entry){
if(firstAvailable<0){
firstAvailable=index;
}
if(firstTypAvailable<0 && slot.entry.stage!=='TD' && slot.entry.originalStage!=='TD'){
firstTypAvailable=index;
}
latestAvailable=index;
}
});
let preferredIndex=preferredDataTime ? typhoonState.slots.findIndex(slot=>slot.dataTime===preferredDataTime && slot.entry) : -1;
let endedDefaultIndex=firstTypAvailable>=0 ? firstTypAvailable : firstAvailable;
let defaultIndex=isActiveTyphoonStorm(typhoonState.selectedStormKey) ? latestAvailable : endedDefaultIndex;
typhoonState.selectedSlotIndex=Math.max(0,preferredIndex>=0 ? preferredIndex : defaultIndex);
}

function getSelectedTyphoonSlot(){
return typhoonState.slots[typhoonState.selectedSlotIndex] || null;
}

function getSelectedTyphoonRun(){
return getSelectedTyphoonSlot()?.entry || null;
}

function getSelectedTyphoonDataTime(){
return getSelectedTyphoonSlot()?.dataTime || '';
}

async function setTyphoonSlotIndex(index){
let maxIndex=Math.max(0,typhoonState.slots.length-1);
let nextIndex=Math.max(0,Math.min(Number(index)||0,maxIndex));
typhoonState.selectedSlotIndex=nextIndex;
renderTyphoonTimeline();
let run=getSelectedTyphoonRun();
let requestId=++typhoonState.slotLoadSeq;
let showLoading=!!run && getTyphoonRunLoadState(run)!=='available';
setTyphoonViewerLoading(showLoading);
try{
await renderTyphoonSelectedRun();
}
finally{
if(requestId===typhoonState.slotLoadSeq){
setTyphoonViewerLoading(false);
}
}
}

function moveTyphoonSelection(offset){
setTyphoonSlotIndex(typhoonState.selectedSlotIndex+offset);
}

function buildTyphoonSlotsForStorm(stormKey){
let entries=typhoonState.entries
.filter(entry=>entry.stormKey===stormKey)
.filter(entry=>entry.fcstHours===typhoonState.selectedFcstHours)
.sort((a,b)=>a.dataTime.localeCompare(b.dataTime));

if(!entries.length){
return [];
}

let byTime=new Map(entries.map(entry=>[entry.dataTime,entry]));
let start=parseTyphoonUtcDate(entries[0].dataTime);
let end=parseTyphoonUtcDate(entries[entries.length-1].dataTime);
if(!start || !end){
return entries.map(entry=>({dataTime:entry.dataTime,entry}));
}

let slots=[];
for(let cursor=new Date(start.getTime());cursor<=end;cursor.setUTCHours(cursor.getUTCHours()+TYPHOON_SLOT_HOURS)){
let dataTime=formatTyphoonStamp(cursor);
slots.push({dataTime,entry:byTime.get(dataTime) || null});
}
return slots;
}

async function renderTyphoonManifest(){
updateTyphoonSubtitle();
renderTyphoonSelects();
renderTyphoonTimeline();

if(!typhoonState.entries.length){
renderTyphoonEmpty('표출 가능한 자료 없음');
return;
}

await renderTyphoonSelectedRun();
}

function renderTyphoonSelects(){
let yearSelect=typhoonState.root?.querySelector('[data-role="yearSelect"]');
let stormSelect=typhoonState.root?.querySelector('[data-role="stormSelect"]');
if(!yearSelect || !stormSelect){
return;
}

yearSelect.innerHTML='';
typhoonState.years.forEach(year=>{
let option=document.createElement('option');
option.value=year;
option.textContent=year;
yearSelect.appendChild(option);
});
yearSelect.value=typhoonState.selectedYear;

stormSelect.innerHTML='';
typhoonState.storms.forEach(storm=>{
let option=document.createElement('option');
option.value=storm.key;
option.textContent=storm.label;
let optionClasses=[];
let allowImpactHighlight=storm.stage!=='TD';
if(allowImpactHighlight && storm.impact){
optionClasses.push('typhoon-impact-storm-option');
option.style.backgroundColor=TYPHOON_IMPACT_OPTION_BG;
option.style.color=TYPHOON_IMPACT_OPTION_COLOR;
option.style.fontWeight=TYPHOON_IMPACT_OPTION_WEIGHT;
option.title=`한반도 영향: ${typhoonImpactEffLabel(storm.impactEff)}`;
}
if(storm.active){
optionClasses.push('typhoon-active-storm-option');
option.style.backgroundColor='#F9E5FF';
option.style.color='#5d2b66';
option.style.fontWeight='800';
option.title=storm.impact ? `진행중 · 한반도 영향: ${typhoonImpactEffLabel(storm.impactEff)}` : '진행중';
}
option.className=optionClasses.join(' ');
stormSelect.appendChild(option);
});
stormSelect.value=typhoonState.selectedStormKey;

yearSelect.disabled=!typhoonState.years.length;
stormSelect.disabled=!typhoonState.storms.length;

typhoonState.root?.querySelectorAll('[data-role="fcstOption"]').forEach(input=>{
let checked=Number(input.value)===typhoonState.selectedFcstHours;
input.checked=checked;
let label=input.closest('.typhoon-fcst-option');
if(label){
label.classList.toggle('is-active',checked);
}
});
}

function updateTyphoonSubtitle(run=getSelectedTyphoonRun()){
let subtitle=typhoonState.root?.querySelector('[data-role="subtitle"]');
if(!subtitle){
return;
}
let updated=formatTyphoonKst(run?.generatedAt || run?.metadata?.generated_at_utc || '');
subtitle.replaceChildren();

let updatedLine=document.createElement('div');
updatedLine.className='typhoon-updated-time-line';
updatedLine.textContent=updated && updated!=='-'
?`최근 업데이트 : ${updated}`
:'최근 업데이트 : -';

let scheduleLine=document.createElement('div');
scheduleLine.className='typhoon-update-schedule';
scheduleLine.textContent=formatTyphoonCycleSchedule(run);

subtitle.appendChild(updatedLine);
subtitle.appendChild(scheduleLine);
}

function renderTyphoonTimeline(){
let timeline=typhoonState.root?.querySelector('[data-role="timeline"]');
let slider=typhoonState.root?.querySelector('[data-role="timeSlider"]');
let label=typhoonState.root?.querySelector('[data-role="timeLabel"]');
if(!timeline || !slider || !label){
return;
}

let slots=typhoonState.slots;
timeline.innerHTML='';
timeline.style.setProperty('--forecast-count',String(slots.length || 1));
slider.min='0';
slider.max=String(Math.max(0,slots.length-1));
slider.value=String(Math.min(typhoonState.selectedSlotIndex,Math.max(0,slots.length-1)));
slider.disabled=slots.length<=1;

let list=document.createElement('div');
list.className='compare-timeline-list single-timeline-list typhoon-timeline-list';

let row=document.createElement('div');
row.className='compare-timeline-row single-timeline-row typhoon-timeline-row';

let info=document.createElement('div');
info.className='compare-row-info';
info.innerHTML='<div class="compare-row-model">VTG</div>';

let track=document.createElement('div');
track.className='compare-track single-forecast-track typhoon-track';
track.tabIndex=0;
track.setAttribute('role','slider');
track.setAttribute('aria-label','태풍 모델예측 시각 슬라이더');
track.setAttribute('aria-valuemin','0');
track.setAttribute('aria-valuemax',String(Math.max(0,slots.length-1)));
track.setAttribute('aria-valuenow',String(typhoonState.selectedSlotIndex));
track.style.gridTemplateColumns=`repeat(${Math.max(1,slots.length)}, minmax(4px, 1fr))`;

slots.forEach((slot,index)=>{
let segment=document.createElement('button');
segment.type='button';
let loadState=slot.entry ? getTyphoonRunLoadState(slot.entry) : 'missing';
let classes=['compare-segment','forecast-segment',`state-${loadState}`];
if(index===typhoonState.selectedSlotIndex){
classes.push('active','active-time-label','active-lead-label');
}
if(index===0){
classes.push('edge-start');
}
if(index===slots.length-1){
classes.push('edge-end');
}
segment.className=classes.join(' ');
segment.dataset.index=String(index);
segment.dataset.time=formatTyphoonDateLabel(slot.dataTime);
segment.dataset.lead=formatTyphoonHourLabel(slot.dataTime);
segment.title=slot.entry ? formatTyphoonTime(slot.dataTime) : `${formatTyphoonTime(slot.dataTime)} 자료 없음`;
segment.onclick=()=>{
setTyphoonSlotIndex(index);
};
bindTyphoonTimelineHover(segment,list);
track.appendChild(segment);
});

let selected=slots[typhoonState.selectedSlotIndex];
if(selected){
track.appendChild(createTyphoonTimelineLabel('date',typhoonState.selectedSlotIndex,slots.length,selected.dataTime));
track.appendChild(createTyphoonTimelineLabel('hour',typhoonState.selectedSlotIndex,slots.length,selected.dataTime));
}

bindTyphoonTimelinePointer(track);

row.appendChild(info);
row.appendChild(track);
list.appendChild(row);
timeline.appendChild(list);

label.textContent=selected ? formatTyphoonTime(selected.dataTime) : '';
}

function bindTyphoonTimelineHover(segment,list){
segment.onpointerenter=()=>{
segment.classList.add('hover-sync','hover-time-label','hover-lead-label');
list.classList.add('is-hovering');
};
segment.onpointerleave=()=>{
segment.classList.remove('hover-sync','hover-time-label','hover-lead-label');
list.classList.remove('is-hovering');
};
}

function bindTyphoonTimelinePointer(track){
let dragging=false;
let dragRect=null;
let dragCount=1;
let activePointerId=null;

function indexFromClientX(clientX){
let rect=dragRect || track.getBoundingClientRect();
let x=Math.max(0,Math.min(clientX-rect.left,rect.width));
let count=dragCount || typhoonState.slots.length || 1;
return Math.max(0,Math.min(count-1,Math.floor((x/Math.max(1,rect.width))*count)));
}

function applyClientX(clientX){
setTyphoonSlotIndex(indexFromClientX(clientX));
}

function beginDrag(event){
if(event.button!==undefined && event.button!==0){
return false;
}
event.preventDefault();
track.focus?.({preventScroll:true});
dragRect=track.getBoundingClientRect();
dragCount=typhoonState.slots.length || 1;
dragging=true;
applyClientX(event.clientX);
return true;
}

function endPointerDrag(){
dragging=false;
dragRect=null;
dragCount=1;
activePointerId=null;
window.removeEventListener('pointermove',handleWindowPointerMove);
window.removeEventListener('pointerup',handleWindowPointerUp);
window.removeEventListener('pointercancel',handleWindowPointerUp);
}

function handleWindowPointerMove(event){
if(!dragging || (activePointerId!==null && event.pointerId!==activePointerId)){
return;
}
event.preventDefault();
applyClientX(event.clientX);
}

function handleWindowPointerUp(event){
if(activePointerId!==null && event.pointerId!==activePointerId){
return;
}
endPointerDrag();
}

track.onpointerdown=event=>{
if(!beginDrag(event)){
return;
}
activePointerId=event.pointerId;
window.addEventListener('pointermove',handleWindowPointerMove);
window.addEventListener('pointerup',handleWindowPointerUp);
window.addEventListener('pointercancel',handleWindowPointerUp);
};

track.onmousedown=event=>{
if(window.PointerEvent || dragging || !beginDrag(event)){
return;
}

let handleMove=moveEvent=>applyClientX(moveEvent.clientX);
let handleUp=()=>{
dragging=false;
dragRect=null;
dragCount=1;
window.removeEventListener('mousemove',handleMove);
window.removeEventListener('mouseup',handleUp);
};

window.addEventListener('mousemove',handleMove);
window.addEventListener('mouseup',handleUp);
};
}

function handleTyphoonKeydown(event){
let modalOverlay=document.querySelector('[data-role="modelDetailOverlay"]');
if(modalOverlay){
if(event.key==='Escape'){
event.preventDefault();
closeTyphoonModelDetailModal();
}
return;
}

let active=document.activeElement;
let tag=active?.tagName;

if(tag==='INPUT' || tag==='SELECT' || tag==='TEXTAREA'){
return;
}

if(event.key==='ArrowLeft' || event.key==='ArrowUp'){
event.preventDefault();
moveTyphoonSelection(-1);
return;
}

if(event.key==='ArrowRight' || event.key==='ArrowDown'){
event.preventDefault();
moveTyphoonSelection(1);
}
}

async function renderTyphoonSelectedRun(){
let selected=getSelectedTyphoonSlot();
if(!selected){
updateTyphoonSubtitle(null);
renderTyphoonEmpty('표출 가능한 자료 없음');
return;
}

if(!selected.entry){
updateTyphoonSubtitle(null);
renderTyphoonMissingSlot(selected.dataTime);
return;
}

await renderTyphoonRun(selected.entry);
}

function getTyphoonImageUrl(run){

if(!run?.imagePath){
return '';
}

let version=run.generatedAt || run.metadata?.generated_at_utc || typhoonState.manifest?.updated_at_utc || '';
let archiveUrl=shouldUseRawTyphoonImage(run) ? '' : typhoonState.driveArchiveImages.get(run.imagePath);
if(archiveUrl){
let fileId=typhoonDriveFileIdFromUrl(archiveUrl);
return getTyphoonDriveImageUrls(fileId,archiveUrl)[0] || archiveUrl;
}
let imagePath=shouldUseRawTyphoonImage(run)
?typhoonBuildUrl(run.imagePath,TYPHOON_ACTIVE_IMAGE_BASE_URL)
:typhoonBuildUrl(run.imagePath,TYPHOON_LIVE_DATA_BASE_URL);
return cacheBustedTyphoonPath(imagePath,version);

}

function getTyphoonImageUrls(run){
let primary=getTyphoonImageUrl(run);
let urls=primary ? [primary] : [];
if(!run?.imagePath){
return urls;
}

let version=run.generatedAt || run.metadata?.generated_at_utc || typhoonState.manifest?.updated_at_utc || '';
if(shouldUseRawTyphoonImage(run)){
[
typhoonBuildUrl(run.imagePath,TYPHOON_LIVE_DATA_BASE_URL)
].forEach(path=>{
let url=cacheBustedTyphoonPath(path,version);
if(url){
urls.push(url);
}
});
}

let archiveUrl=typhoonState.driveArchiveImages.get(run.imagePath);
let fileId=typhoonDriveFileIdFromUrl(archiveUrl);
if(fileId){
urls.push(...getTyphoonDriveImageUrls(fileId,archiveUrl));
}
else if(archiveUrl){
urls.push(archiveUrl);
}
return [...new Set(urls.filter(Boolean))];
}

function getTyphoonDriveImageUrls(fileId,archiveUrl=''){
let id=String(fileId || '').trim();
let urls=[];
if(id){
urls.push(typhoonDriveThumbnailUrl(id));
urls.push(typhoonDriveGoogleusercontentUrl(id));
}
if(archiveUrl){
urls.push(archiveUrl);
}
return [...new Set(urls.filter(Boolean))];
}

function typhoonDriveFileIdFromUrl(value){
let url=String(value || '').trim();
if(!url){
return '';
}
try{
let parsed=new URL(url,window.location.href);
let id=parsed.searchParams.get('id') || '';
if(id){
return id;
}
let match=parsed.pathname.match(/\/d\/([^/]+)/);
return match ? decodeURIComponent(match[1]) : '';
}
catch(error){
return '';
}
}

function typhoonDriveGoogleusercontentUrl(fileId){
let id=String(fileId || '').trim();
return id ? `https://lh3.googleusercontent.com/d/${encodeURIComponent(id)}` : '';
}

function typhoonDriveThumbnailUrl(fileId){
let id=String(fileId || '').trim();
return id ? `https://drive.google.com/thumbnail?id=${encodeURIComponent(id)}&sz=w2400` : '';
}

function shouldUseRawTyphoonImage(run){
return Boolean(TYPHOON_ACTIVE_IMAGE_BASE_URL && isActiveTyphoonStormRun(run));
}

function getTyphoonAnalyticsSource(url){
return window.CDSAnalytics?.sourceFromUrl
?window.CDSAnalytics.sourceFromUrl(url || '')
:'unknown';
}

function getTyphoonAnalyticsParams(run,{url='',urls=[]}={}){
let stormStatus=shouldUseRawTyphoonImage(run) ? 'active' : 'ended';
let fcstHours=Number(run?.fcstHours || 0);
let forecastRange=fcstHours===120 ? '5일예측' : (fcstHours===240 ? '10일예측' : `${fcstHours}시간예측`);
let archiveUrl=run?.imagePath ? typhoonState.driveArchiveImages.get(run.imagePath) : '';
let archiveSource=stormStatus==='active'
?'github_raw'
:(archiveUrl ? getTyphoonAnalyticsSource(archiveUrl) : 'github_raw');
let stormKey=run?.stormKey || [
run?.year || '',
run?.stage || '',
run?.typNumber || '',
run?.typName || ''
].join('|');

return {
analytics_key:['vtg',stormKey,run?.dataTime || '',run?.fcstHours || ''].filter(Boolean).join('|'),
storm_key:stormKey,
storm_year:String(run?.year || ''),
storm_stage:run?.stage || '',
storm_origin_stage:run?.originalStage || run?.stage || '',
storm_number:Number(run?.typNumber || 0),
storm_name:run?.typName || '',
storm_label:stormDropdownLabel(run),
storm_status:stormStatus,
fcst_hours:fcstHours,
forecast_days:fcstHours ? fcstHours/24 : 0,
forecast_range:forecastRange,
data_time:run?.dataTime || '',
image_source:getTyphoonAnalyticsSource(url || urls?.[0] || ''),
archive_source:archiveSource,
view_context:'vtg'
};
}

function trackTyphoonImageView(run,result){
if(!window.CDSAnalytics?.trackTyphoonView){
return;
}

window.CDSAnalytics.trackTyphoonView(
getTyphoonAnalyticsParams(run,{url:result?.url || ''})
);
}

function trackTyphoonImageFailure(run,result,urls){
if(!window.CDSAnalytics?.trackTyphoonImageFailure){
return;
}

let attemptedSources=[...new Set((urls || []).map(getTyphoonAnalyticsSource).filter(Boolean))];
window.CDSAnalytics.trackTyphoonImageFailure({
...getTyphoonAnalyticsParams(run,{url:result?.url || '',urls}),
attempt_count:Array.isArray(urls) ? urls.length : 0,
attempted_sources:attemptedSources,
last_source:getTyphoonAnalyticsSource(result?.url || urls?.[urls.length-1] || '')
});
}

function configureTyphoonImageElement(image,url){

image.className='typhoon-guidance-image';
image.alt='태풍 모델예측 이미지';
image.decoding='async';
image.loading='eager';
image.dataset.cacheUrl=url;
return image;

}

function typhoonCacheHorizon(value){
return Number(value)===240 ? 240 : 120;
}

function getTyphoonImageCache(fcstHours){
let horizon=typhoonCacheHorizon(fcstHours);
if(!typhoonState.imageCaches.has(horizon)){
typhoonState.imageCaches.set(horizon,new Map());
}
return typhoonState.imageCaches.get(horizon);
}

function getTyphoonRunCacheKey(run){
if(!run){
return '';
}
return [
typhoonCacheHorizon(run.fcstHours),
run.stormKey || '',
run.dataTime || '',
run.imagePath || '',
run.generatedAt || run.metadata?.generated_at_utc || ''
].join('|');
}

function getTyphoonRunLoadState(run){
if(!run?.imagePath){
return 'missing';
}
return typhoonState.imageLoadStates.get(getTyphoonRunCacheKey(run)) || 'loading';
}

function setTyphoonRunLoadState(run,state){
let key=getTyphoonRunCacheKey(run);
if(!key){
return;
}
typhoonState.imageLoadStates.set(key,state);
updateTyphoonTimelineRunState(run,state);
}

function updateTyphoonTimelineRunState(run,state=getTyphoonRunLoadState(run)){
let key=getTyphoonRunCacheKey(run);
let index=typhoonState.slots.findIndex(slot=>slot.entry && getTyphoonRunCacheKey(slot.entry)===key);
if(index<0){
return;
}
let segment=typhoonState.root?.querySelector(`[data-role="timeline"] .forecast-segment[data-index="${index}"]`);
if(!segment){
return;
}
segment.classList.remove('state-loading','state-available','state-missing');
segment.classList.add(`state-${state}`);
}

function getTyphoonActiveImageUrls(fcstHours){
let horizon=typhoonCacheHorizon(fcstHours);

return new Set(
typhoonState.entries
.filter(run=>typhoonCacheHorizon(run.fcstHours)===horizon)
.flatMap(run=>getTyphoonImageUrls(run))
.filter(Boolean)
);

}

function getSelectedTyphoonImageUrls(fcstHours){
let stormKey=typhoonState.selectedStormKey;
let horizon=typhoonCacheHorizon(fcstHours);
return new Set(
typhoonState.entries
.filter(run=>run.stormKey===stormKey && typhoonCacheHorizon(run.fcstHours)===horizon)
.flatMap(run=>getTyphoonImageUrls(run))
.filter(Boolean)
);
}

function pruneTyphoonImageCache(){

for(let [horizon,cache] of typhoonState.imageCaches){
let activeUrls=getTyphoonActiveImageUrls(horizon);
let protectedUrls=getSelectedTyphoonImageUrls(horizon);
for(let url of cache.keys()){
if(!activeUrls.has(url)){
cache.delete(url);
}
}

while(cache.size>TYPHOON_IMAGE_CACHE_LIMIT_PER_HORIZON){
let removable=[...cache.keys()].find(url=>!protectedUrls.has(url));
if(!removable){
break;
}
cache.delete(removable);
}
}

}

async function loadTyphoonCachedImage(run){

let urls=getTyphoonImageUrls(run);
let horizon=typhoonCacheHorizon(run.fcstHours);

if(!urls.length){
setTyphoonRunLoadState(run,'missing');
return Promise.resolve({ok:false,url:'',image:null});
}

setTyphoonRunLoadState(run,'loading');
let lastResult={ok:false,url:urls[0] || '',image:null};
for(let url of urls){
let result=await loadTyphoonCachedImageUrl(url,horizon);
if(result?.ok){
setTyphoonRunLoadState(run,'available');
return result;
}
lastResult=result || lastResult;
}
setTyphoonRunLoadState(run,'missing');
return lastResult;

}

function loadTyphoonCachedImageUrl(url,fcstHours){

let cache=getTyphoonImageCache(fcstHours);
let cached=cache.get(url);
if(cached){
return cached.promise;
}

let promise=new Promise(resolve=>{
let done=false;
let image=configureTyphoonImageElement(new Image(),url);

let timer=setTimeout(()=>{
if(done){return;}
done=true;
resolve({ok:false,url,image:null});
},TYPHOON_IMAGE_TIMEOUT_MS);

image.onload=async()=>{
if(done){return;}

try{
if(typeof image.decode==='function'){
await image.decode();
}
}
catch(e){}

if(done){return;}
done=true;
clearTimeout(timer);
resolve({ok:true,url,image});
};

image.onerror=()=>{
if(done){return;}
done=true;
clearTimeout(timer);
resolve({ok:false,url,image:null});
};

image.src=url;
});

cache.set(url,{url,promise});

promise.then(result=>{
if(!result?.ok){
cache.delete(url);
}
});

pruneTyphoonImageCache();
return promise;

}

async function preloadTyphoonStormImages(stormKey,fcstHours,{
isCancelled=()=>false,
onPriorityLoaded=null
}={}){
let runs=[];
let seen=new Set();
let horizon=typhoonCacheHorizon(fcstHours);
typhoonState.entries.forEach(run=>{
if(run.stormKey!==stormKey || !run.imagePath || typhoonCacheHorizon(run.fcstHours)!==horizon){
return;
}
let key=`${run.imagePath}|${run.generatedAt || run.metadata?.generated_at_utc || ''}`;
if(seen.has(key)){
return;
}
seen.add(key);
runs.push(run);
});
let total=runs.length;
let loaded=0;
let priorityRun=getSelectedTyphoonRun();
let priorityKey=getTyphoonRunCacheKey(priorityRun);
let priorityIndex=priorityKey ? runs.findIndex(run=>getTyphoonRunCacheKey(run)===priorityKey) : -1;

if(priorityIndex>=0){
priorityRun=runs.splice(priorityIndex,1)[0];
await ensureTyphoonDriveArchiveImagesForRun(priorityRun);
if(isCancelled()){
return {total,loaded,cancelled:true};
}
let result=await loadTyphoonCachedImage(priorityRun);
if(result?.ok){
loaded++;
}
if(isCancelled()){
return {total,loaded,cancelled:true};
}
if(typeof onPriorityLoaded==='function'){
await onPriorityLoaded(priorityRun,result);
}
if(isCancelled()){
return {total,loaded,cancelled:true};
}
}

let archivePaths=[...new Set(runs.map(typhoonDriveArchivePathForRun).filter(Boolean))];
await Promise.all(archivePaths.map(path=>ensureTyphoonDriveArchiveImagesForPath(path)));
if(isCancelled()){
return {total,loaded,cancelled:true};
}

let nextIndex=0;
let worker=async()=>{
while(nextIndex<runs.length && !isCancelled()){
let index=nextIndex++;
let result=await loadTyphoonCachedImage(runs[index]);
if(result?.ok){
loaded++;
}
}
};
let workerCount=Math.min(TYPHOON_IMAGE_PRELOAD_CONCURRENCY,runs.length);
await Promise.all(Array.from({length:workerCount},worker));
pruneTyphoonImageCache();
return {total,loaded,cancelled:isCancelled()};
}

function createTyphoonStatusPanel(message,{hidden=false}={}){

let panel=document.createElement('div');
panel.className='typhoon-status-panel'+(hidden?' hidden':'');
panel.textContent=message;
return panel;

}

function setTyphoonViewerLoading(isLoading,message='이미지 로딩 중'){
let viewer=typhoonState.root?.querySelector('.typhoon-viewer');
let loading=typhoonState.root?.querySelector('[data-role="viewerLoading"]');
viewer?.classList.toggle('is-loading',!!isLoading);
if(!loading){
return;
}
loading.classList.toggle('hidden',!isLoading);
loading.setAttribute('aria-hidden',isLoading?'false':'true');
let text=loading.querySelector('.loading-text');
if(text){
text.textContent=message;
}
}

function waitForTyphoonImagePaint(){
return new Promise(resolve=>{
let done=false;
let finish=()=>{
if(done){return;}
done=true;
clearTimeout(timer);
resolve();
};
let timer=setTimeout(finish,250);
window.requestAnimationFrame(()=>{
window.requestAnimationFrame(finish);
});
});
}

async function renderTyphoonRun(run){
let viewer=typhoonState.root?.querySelector('[data-role="viewer"]');
if(!viewer){
return;
}

updateTyphoonSubtitle(run);

let requestId=++typhoonState.imageRequestSeq;

if(!run.imagePath){
renderTyphoonMissingSlot(run.dataTime);
return;
}

await ensureTyphoonDriveArchiveImagesForRun(run);

if(requestId!==typhoonState.imageRequestSeq){
return;
}

let urls=getTyphoonImageUrls(run);
let url=urls[0] || '';
let currentImage=viewer.querySelector('.typhoon-guidance-image');

if(currentImage?.dataset.cacheUrl && urls.includes(currentImage.dataset.cacheUrl) && currentImage.complete){
setTyphoonRunLoadState(run,'available');
await waitForTyphoonImagePaint();
trackTyphoonImageView(run,{url:currentImage.dataset.cacheUrl});
return;
}

if(!currentImage){
viewer.replaceChildren(createTyphoonStatusPanel(''));
}

let result=await loadTyphoonCachedImage(run);

if(requestId!==typhoonState.imageRequestSeq){
return;
}

if(!(result.ok && result.image)){
trackTyphoonImageFailure(run,result,urls);
}

if(result.ok && result.image){
let error=createTyphoonStatusPanel('이미지 로드 실패',{hidden:true});
viewer.replaceChildren(result.image,error);
await waitForTyphoonImagePaint();
trackTyphoonImageView(run,result);
return;
}

viewer.replaceChildren(createTyphoonStatusPanel('이미지 로드 실패'));
return;
}

function renderTyphoonMissingSlot(dataTime){
typhoonState.imageRequestSeq++;
setTyphoonViewerLoading(false);
let viewer=typhoonState.root?.querySelector('[data-role="viewer"]');
if(viewer){
viewer.innerHTML=`<div class="typhoon-status-panel">${escapeHtml(formatTyphoonTime(dataTime))} 자료 없음</div>`;
}
}

function renderTyphoonEmpty(message){
typhoonState.imageRequestSeq++;
setTyphoonViewerLoading(false);
let viewer=typhoonState.root?.querySelector('[data-role="viewer"]');
let timeline=typhoonState.root?.querySelector('[data-role="timeline"]');
if(timeline){
timeline.innerHTML='';
}
if(viewer){
viewer.innerHTML=`<div class="typhoon-status-panel">${escapeHtml(message)}</div>`;
}
updateTyphoonSubtitle();
renderTyphoonSelects();
}

function displayModelLabels(metadata){
let labels=Array.isArray(metadata.model_labels) ? metadata.model_labels : [];
if(labels.length){
return labels;
}
let models=Array.isArray(metadata.models) ? metadata.models : [];
let seen=new Set();
let result=[];
models.forEach(model=>{
let label=TYPHOON_MODEL_LABELS[model] || model;
if(!seen.has(label)){
seen.add(label);
result.push(label);
}
});
return result;
}

function stormDropdownLabel(entry){
if(entry.stage==='TD'){
return `제${entry.typNumber}호 TD`;
}
let name=entry.typNameKo || koreanTyphoonName(entry.typName) || entry.typName;
return `제${entry.typNumber}호 태풍 ${name}`.trim();
}

function normalizeTyphoonName(name){
let text=String(name || '').trim();
return text;
}

function koreanTyphoonName(name){
return TYPHOON_KO_NAME_FALLBACK[String(name || '').trim().toUpperCase()] || '';
}

function cycleStormLabel(run){
let year=String(run.year || run.dataTime.slice(0,4)).slice(-2);
let cycloneId=run.typNumber ? `${year}${String(run.typNumber).padStart(2,'0')}` : '';
return `${cycloneId} ${run.typName}`.trim();
}

function modelCountLabel(run){
let metadata=run.metadata || {};
let count=metadata.model_count;
let target=metadata.target_model_count || TYPHOON_DEFAULT_MODEL_TARGET;
if(count===undefined || count===null || count===''){
return `0/${target}`;
}
return `${count}/${target}`;
}

function normalizeTyphoonBaseUrl(value){
let text=String(value || '').trim();
return text ? text.replace(/\/+$/,'/') : '';
}

function isAbsoluteTyphoonUrl(value){
return /^https?:\/\//i.test(String(value || ''));
}

function typhoonBuildUrl(path,baseUrl=''){
let text=String(path || '').trim();
if(!text || isAbsoluteTyphoonUrl(text)){
return text;
}
let normalizedPath=text.replace(/\\/g,'/').replace(/^\/+/,'');
let normalizedBase=normalizeTyphoonBaseUrl(baseUrl);
return normalizedBase ? `${normalizedBase}${normalizedPath}` : normalizedPath;
}

function typhoonDataBaseUrls(preferredBaseUrl=''){
let urls=[];
[preferredBaseUrl,TYPHOON_LIVE_DATA_BASE_URL,''].forEach(baseUrl=>{
let normalizedBase=normalizeTyphoonBaseUrl(baseUrl);
if(!urls.includes(normalizedBase)){
urls.push(normalizedBase);
}
});
return urls;
}

function normalizeTyphoonAssetPath(value){
let path=String(value || '').replace(/\\/g,'/');
if(!path){
return '';
}
if(isAbsoluteTyphoonUrl(path)){
return path;
}
for(let marker of ['data/','VTG_IMG/']){
let markerIndex=path.indexOf(marker);
if(markerIndex>=0){
return path.slice(markerIndex);
}
}
return path.replace(/^\/+/,'');
}

function parseTyphoonFcstHoursFromPath(value){
let match=String(value || '').match(/_(\d{2,3})h\.png(?:$|\?)/i);
return match ? Number(match[1]) : 0;
}

function cacheBustedTyphoonPath(path,version){
if(!path){
return '';
}
let separator=path.includes('?') ? '&' : '?';
let cacheKey=[version,TYPHOON_PAGE_CACHE_TOKEN].filter(Boolean).join('-') || Date.now();
return `${path}${separator}fresh=${encodeURIComponent(cacheKey)}`;
}

function formatCycleCompact(value){
if(!value || value.length<10){
return '-';
}
return `${value.slice(4,6)}-${value.slice(6,8)} ${value.slice(8,10)}UTC`;
}

function formatTyphoonDateLabel(value){
if(!value || value.length<8){
return '-';
}
return `${value.slice(4,6)}.${value.slice(6,8)}`;
}

function formatTyphoonHourLabel(value){
if(!value || value.length<10){
return '-';
}
return `${value.slice(8,10)}UTC`;
}

function getTyphoonTimelineLabelLeftPercent(index,count){
if(count<=1){
return 50;
}
return ((Number(index)+0.5)/count)*100;
}

function createTyphoonTimelineLabel(type,index,count,dataTime){
let label=document.createElement('div');
let isDate=type==='date';
label.className='compare-active-label '+(isDate?'compare-active-time':'compare-active-lead');
label.textContent=isDate ? formatTyphoonDateLabel(dataTime) : formatTyphoonHourLabel(dataTime);
if(index===0){
label.classList.add('edge-start');
}
if(index===count-1){
label.classList.add('edge-end');
}
let leftPercent=getTyphoonTimelineLabelLeftPercent(index,count)+'%';
label.style.left=leftPercent;
label.style.setProperty('--label-left',leftPercent);
return label;
}

function formatTyphoonTime(value){
if(!value || value.length<10){
return '';
}
return `${value.slice(0,4)}-${value.slice(4,6)}-${value.slice(6,8)} ${value.slice(8,10)}UTC`;
}

function formatTyphoonKst(value){
let date=parseTyphoonUtcDate(value);
if(!date){
return '-';
}
date.setUTCHours(date.getUTCHours()+9);
return `${date.getUTCFullYear()}-${pad2(date.getUTCMonth()+1)}-${pad2(date.getUTCDate())} ${pad2(date.getUTCHours())}:${pad2(date.getUTCMinutes())} KST`;
}

function addTyphoonUtcHours(date,hours){
return new Date(date.getTime()+Number(hours || 0)*60*60*1000);
}

function formatTyphoonKstWindowTime(date){
let kst=addTyphoonUtcHours(date,9);
return `${pad2(kst.getUTCHours())}KST`;
}

function formatTyphoonCycleSchedule(run=getSelectedTyphoonRun()){
let dataTime=String(run?.dataTime || getSelectedTyphoonDataTime() || '').trim();
let cycle=parseTyphoonUtcDate(dataTime);
if(!cycle){
return '00/06/12/18UTC cycle window';
}
let cycleHour=pad2(cycle.getUTCHours());
let start=addTyphoonUtcHours(cycle,TYPHOON_CYCLE_WINDOW_START_OFFSET_HOURS);
let end=addTyphoonUtcHours(cycle,TYPHOON_CYCLE_WINDOW_END_OFFSET_HOURS);
return `${cycleHour}UTC 기준 ${formatTyphoonKstWindowTime(start)} 시작 / ${formatTyphoonKstWindowTime(end)} 완료`;
}

function parseTyphoonUtcDate(value){
let raw=String(value || '').trim();
if(!raw){
return null;
}
if(!/^\d{10,14}$/.test(raw)){
let date=new Date(raw);
return Number.isNaN(date.getTime()) ? null : date;
}
let year=Number(raw.slice(0,4));
let month=Number(raw.slice(4,6))-1;
let day=Number(raw.slice(6,8));
let hour=Number(raw.slice(8,10));
let minute=Number(raw.slice(10,12) || 0);
if([year,month,day,hour,minute].some(Number.isNaN)){
return null;
}
return new Date(Date.UTC(year,month,day,hour,minute));
}

function formatTyphoonStamp(date){
return `${date.getUTCFullYear()}${pad2(date.getUTCMonth()+1)}${pad2(date.getUTCDate())}${pad2(date.getUTCHours())}${pad2(date.getUTCMinutes())}`;
}

function pad2(value){
return String(value).padStart(2,'0');
}

function escapeHtml(value){
return String(value ?? '').replace(/[&<>"']/g,character=>({
'&':'&amp;',
'<':'&lt;',
'>':'&gt;',
'"':'&quot;',
"'":'&#39;'
}[character]));
}

document.addEventListener('DOMContentLoaded',initTyphoonGuidancePage);
