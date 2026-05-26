const MODELS={

kim_gdps:{
name:"GDAPS_KIM",
folder:"KIMG",
archiveStart:"2020-09-28",
cycles:[0,6,12,18],
forecastRules:[
{cycles:[0,12],until:"2025-05-13",max:288},
{cycles:[0,12],max:360},
{cycles:[6,18],max:84}
],
stepSchemeByCycleGroup:{
"0,12":[
{start:0,end:84,step:3},
{start:90,end:96,step:6},
{start:108,end:360,step:12}
],
"6,18":[
{start:0,end:84,step:3}
]
}
},

um_gdps:{
name:"GDAPS_UM",
folder:"GDPS",
archiveStart:"2005-12-02",
archiveEnd:"2026-04-01",
cycles:[0,6,12,18],
cycleAvailability:[
{until:"2011-05-22",cycles:[0,12]},
{from:"2011-05-23",cycles:[0,6,12,18]}
],
forecastRules:[
{until:"2010-05-13",cycles:[0,12],max:240},
{from:"2010-05-14",until:"2013-09-30",cycles:[0,12],max:252},
{from:"2013-10-01",cycles:[0,12],max:288},
{from:"2011-05-23",cycles:[6,18],max:84}
],
stepSchemeByCycleGroup:{
"0,12":[
{start:0,end:84,step:3},
{start:90,end:96,step:6},
{start:108,end:288,step:12}
],
"6,18":[
{start:0,end:84,step:3}
]
}
},

ecmwf:{
name:"ECMWF",
folder:"ECMW",
archiveStart:"2013-01-28",
cycles:[0,12],
forecastRules:[
{cycles:[0,12],max:240}
],
stepSchemeByCycleGroup:{
"0,12":[
{start:0,end:84,step:3},
{start:90,end:96,step:6},
{start:108,end:240,step:12}
],
}
},

ukmo:{
name:"UKUM",
folder:"GDPS",
archiveStart:"2025-11-30",
cycles:[0,12],
forecastRules:[
{cycles:[0,12],max:144}
],
stepSchemeByCycleGroup:{
"0,12":[
{start:0,end:84,step:3},
{start:90,end:96,step:6},
{start:108,end:144,step:12}
],
}
},

kim_rdps:{
name:"RDAPS_KIM",
folder:"KIMR1",
archiveStart:"2022-05-12",
cycles:[0,6,12,18],
forecastRules:[
{from:"2011-05-23",cycles:[6,18],max:72},
{from:"2024-06-27",cycles:[0,12],max:120},
],
stepSchemeByCycleGroup:{
"0,6,12,18":[
{start:0,end:120,step:1}
]
}
},

um_rdps:{
name:"RDAPS_UM",
folder:"RDPS",
archiveStart:"2012-06-01",
archiveEnd:"2019-02-10",
cycles:[0,6,12,18],
forecastRules:[
{until:"2013-09-29",cycles:[0,6,12,18],max:72},
{from:"2013-09-30",cycles:[0,6,12,18],max:87},
],
stepSchemeByCycleGroup:{
"0,6,12,18":[
{start:0,end:87,step:3}
]
}
},

kwrf_rdps:{
name:"RDAPS_WRF",
folder:"KWRF",
archiveStart:"2012-06-01",
archiveEnd:"2015-01-08",
cycles:[0,6,12,18],
forecastRules:[
{cycles:[0,6,12,18],max:72}
],
stepSchemeByCycleGroup:{
"0,6,12,18":[
{start:0,end:72,step:3}
]
}
},

kim_ldps:{
name:"LDAPS_KIM",
folder:"KIML",
archiveStart:"2025-11-14",
cycles:[0,6,12,18],
forecastRules:[
{cycles:[0,6,12,18],max:48}
],
stepSchemeByCycleGroup:{
"0,6,12,18":[
{start:0,end:48,step:1}
]
}
},

um_ldps:{
name:"LDAPS_UM",
folder:"LDPS",
archiveStart:"2012-06-01",
archiveEnd:"2026-03-31",
cycles:[0,6,12,18],
forecastRules:[
{until:"2013-04-28",cycles:[0,6,12,18],max:24},
{from:"2013-04-29",until:"2019-05-27",cycles:[0,6,12,18],max:36},
{from:"2019-05-28",cycles:[0,6,12,18],max:48}
],
stepSchemeByCycleGroup:{
"0,6,12,18":[
{start:0,end:48,step:1}
]
}
},

kim_klfs:{
name:"KLAPS_KIM",
folder:"KLFS",
archiveStart:"2023-02-23",
cycles:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23],
forecastRules:[
{cycles:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23],max:12}
],
stepSchemeByCycleGroup:{
"0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23":[
{start:0,end:12,step:1}
]
}
},

um_klfs:{
name:"KLAPS_UM",
folder:"KLFS",
archiveStart:"2012-06-01",
archiveEnd:"2026-03-31",
cycles:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23],
forecastRules:[
{cycles:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23],max:12}
],
stepSchemeByCycleGroup:{
"0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23":[
{start:0,end:12,step:1}
]
}
},

um_vdps:{
name:"VDAPS_UM",
folder:"VDPS",
archiveStart:"2017-06-20",
archiveEnd:"2021-12-29",
cycles:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23],
forecastRules:[
{cycles:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23],max:12}
],
stepSchemeByCycleGroup:{
"0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23":[
{start:0,end:12,step:1}
]
}
},

kim_epsg:{
name:"EPSG_KIM",
folder:"KIME",
archiveStart:"2021-01-01",
cycles:[0,12],
forecastRules:[
{cycles:[0,12],until:"2025-05-13",max:288},
{cycles:[0,12],max:360},
],
stepSchemeByCycleGroup:{
"0,12":[
{start:0,end:360,step:6},
]
}
},



um_epsg:{
name:"EPSG_UM",
folder:"EPSG",
archiveStart:"2012-06-01",
archiveEnd:"2026-04-01",
cycles:[0,12],
forecastRules:[
{from:"2012-06-01",until:"2013-09-30",cycles:[0,12],max:240},
{from:"2013-10-17",cycles:[0,12],max:288},
],
stepSchemeByCycleGroup:{
"0,12":[
{start:0,end:288,step:6},
]
}
},

kim_lens:{
name:"LENS_KIM",
folder:"KIME",
archiveStart:"2024-04-01",
cycles:[0,12],
forecastRules:[
{cycles:[0,12],max:120}
],
stepSchemeByCycleGroup:{
"0,12":[
{start:0,end:120,step:1},
]
}
},

um_lens:{
name:"LENS_UM",
folder:"EPSG",
archiveStart:"2015-10-28",
cycles:[0,12],
forecastRules:[
{cycles:[0,12],max:72}
],
stepSchemeByCycleGroup:{
"0,12":[
{start:0,end:72,step:1},
]
}
},

ecmwf_eps:{
name:"ECMWF_EPS",
folder:"ECMW",
archiveStart:"2013-04-07",
cycles:[0,12],
forecastRules:[
{cycles:[0,12],max:240}
],
stepSchemeByCycleGroup:{
"0,12":[
{start:0,end:240,step:6},
]
}
},


kim_anal:{
name:"ANAL_KIM",
folder:"KIMN",
archiveStart:"2020-09-28",
cycles:[0,6,12,18],
},

um_anal:{
name:"ANAL_UM",
folder:"ANAL",
archiveStart:"1982-01-01",
archiveEnd:"2026-03-31",
cycles:[0,6,12,18],
cycleAvailability:[
{until:"2011-05-22",cycles:[0,12]},
{from:"2011-05-23",cycles:[0,6,12,18]}
],
},

ecmwf_ra:{
name:"ECMWF_RA",
folder:"ANAL",
archiveStart:"1958-01-01",
archiveEnd:"2011-12-31",
cycles:[0,12],
},

kas:{
name:"KAS",
folder:"ANAL",
archiveStart:"2024-05-11",
cycles:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23],
},

kim_klps:{
name:"KLPS_KIM",
folder:"ANAL",
archiveStart:"2023-02-22",
cycles:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23],
},

um_klps:{
name:"KLPS_UM",
folder:"ANAL",
archiveStart:"2010-03-16",
cycles:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23],
},

obs_upper:{
name:"OBS_UPPER",
folder:"ANAL",
archiveStart:"1957-04-01",
cycles:[0,6,12,18]
},

sat_gk2a:{
name:"SAT_GK2A",
folder:"SAT",
archiveStart:"2022-06-15",
cycles:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
},

usst:{
name:"USST",
folder:"EXTJ",
archiveStart:"2004-02-12",
cycles:[0]
},

edit_chart:{
name:"MANUAL_CHART",
folder:"MAN",
archiveStart:"2004-02-12",
cycles:[0,6,12,18]
},

/* 모델 메타데이터 끝 */



};

function expandSteps(scheme,maxLead){
let out=[];
scheme.forEach(r=>{
let e=Math.min(r.end,maxLead);
for(let h=r.start;h<=e;h+=r.step){
out.push(h);
}
});
return [...new Set(out)];
}

function getCycleScheme(modelId,cycleHour){
let groups=MODELS[modelId]?.stepSchemeByCycleGroup || {};
for(let key in groups){
let members=key.split(',').map(Number);
if(members.includes(cycleHour)){
return groups[key];
}
}

return [];

}

function getForecastHours(modelId,runDate,cycleHour){
let m=MODELS[modelId];
if(!m || !Array.isArray(m.forecastRules)){
return [0];
}
for(let rule of m.forecastRules){
if(!rule.cycles.includes(cycleHour)) continue;
if(rule.from && runDate<new Date(rule.from)) continue;
if(rule.until && runDate>new Date(rule.until)) continue;
return expandSteps(
getCycleScheme(modelId,cycleHour),
rule.max
);
}
return [0];
}

function getAvailableCycles(modelId,date){
let m=MODELS[modelId];
if(!m.cycleAvailability) return m.cycles;
for(let r of m.cycleAvailability){
if(r.from && date<new Date(r.from)) continue;
if(r.until && date>new Date(r.until)) continue;
return r.cycles;
}
return [];
}

function getModelStatus(modelId,date){

let m=MODELS[modelId];

if(m.archiveEnd && date>new Date(m.archiveEnd)){

return {
available:false,
message:
`운영 종료된 모델입니다.\n자료 보유기간: ${m.archiveStart} ~ ${m.archiveEnd}`
};

}

return {
available:true,
message:""
};

}
