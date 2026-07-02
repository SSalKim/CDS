/* 보조패널 적용 규칙
   - optionSet: aux-data.js의 AUX_OPTION_SETS 키
   - includeByModel: 해당 모델에서 표시할 값만 지정
   - excludeByModel: 해당 모델에서 제외할 값 지정
*/

const AUX_SELECTORS={

stationWide:{
  title:'지점',
  widthClass:'wide',
  optionSet:'kmaStations',
  defaultValue:'47108'
},

upperStation:{
  title:'지점',
  widthClass:'wide',
  optionSet:'upperStations',
  defaultValue:'47102'
},

localArea:{
  title:'상세영역',
  widthClass:'narrow',
  optionSet:'localAreas',
  defaultValue:'s7sl'
},

isentropicLevel:{
  title:'온위면',
  widthClass:'narrow',
  optionSet:'isentropicLevels',
  defaultValue:'350K'
},

prec6h_intensity:{
  title:'6H강수',
  widthClass:'wide',
  optionSet:'prec6h_intensities',
  defaultValue:'no01'
},

prec3h_intensity:{
  title:'3H강수',
  widthClass:'wide',
  optionSet:'prec3h_intensities',
  defaultValue:'no01'
},

prec1h_intensity:{
  title:'1H강수',
  widthClass:'wide',
  optionSet:'prec1h_intensities',
  defaultValue:'no01'
},

snow3h_intensity:{
  title:'3H강설',
  widthClass:'wide',
  optionSet:'snow3h_intensities',
  defaultValue:'no01'
},

snow1h_intensity:{
  title:'1H강설',
  widthClass:'wide',
  optionSet:'snow1h_intensities',
  defaultValue:'no01'
},

visblt_intensity:{
  title:'시정',
  widthClass:'wide',
  optionSet:'visblt_intensities',
  defaultValue:'no01'
},

epsg_criterion:{
  title:'기준값',
  widthClass:'narrow',
  optionSet:'epsg_criterions',
  defaultValue:'no5'
},

lens_criterion:{
  title:'기준값',
  widthClass:'narrow',
  optionSet:'lens_criterions',
  defaultValue:'no01'
},

prob_rain_intensity:{
  title:'6H강수',
  widthClass:'wide',
  optionSet:'prob_rain_intensities',
  defaultValue:'no1'
},

spgt_height:{
  title:'등고선',
  widthClass:'wide',
  optionSet:'spgt_heights',
  defaultValue:'hg01'
},

spgt_height_nhem:{
  title:'등고선',
  widthClass:'wide',
  optionSet:'spgt_heights_nhem',
  defaultValue:'hg01'
},

conf_rain_intensity:{
  title:'일강수',
  widthClass:'wide',
  optionSet:'conf_rain_intensities',
  defaultValue:'no1'
},

sstRegion:{
  title:'지역',
  widthClass:'narrow',
  optionSet:'sstRegions',
  defaultValue:'korea'
},

analysisAsiaOverlay:{
  title:'중첩분석',
  widthClass:'wide',
  optionSet:'analysisAsiaOverlays',
  defaultValue:'base'
},

analysisKoreaOverlay:{
  title:'중첩분석',
  widthClass:'wide',
  optionSet:'analysisKoreaOverlays',
  defaultValue:'base'
},

analysisTyphoonOverlay:{
  title:'중첩분석',
  widthClass:'wide',
  optionSet:'analysisTyphoonOverlays',
  defaultValue:'base'
},


astdLevel:{
  title:'고도',
  widthClass:'narrow',
  optionSet:'astdLevels',
  defaultValue:'700hpa'
},

};

const AUX_USAGE_RULES={

analysis:{

  analysisAsiaOverlay:{selector:'analysisAsiaOverlay'},
  analysisKoreaOverlay:{selector:'analysisKoreaOverlay'},
  analysisTyphoonOverlay:{selector:'analysisTyphoonOverlay'},
  skewan:{
    selector:'stationWide',
    excludeByModel:{
      kas:["47175", "47251"]
    }
  },
  skewob:{
    selector:'upperStation',
    dynamicAvailability:true,
    autoPickFirstAvailable:true,
    loadingMessage:'관측자료 확인 중'
  },
  skewds:{
    selector:'upperStation',
    dynamicAvailability:true,
    autoPickFirstAvailable:true,
    loadingMessage:'관측자료 확인 중'
  },
  grtopo:{
    selector:'localArea'
  },
  "ssta:usst_anal":{
    selector:'sstRegion'
  },
  "ssta:usst_anom":{
    selector:'sstRegion'
  },
  "ssta:gk2a_astd":{
    selector:'astdLevel'
  }
},

forecast:{
  lkor2:{
    selector:'localArea'
  },
  isen:{
    selector:'isentropicLevel'
  },
  skew:{
    selector:'stationWide',
    excludeByModel:{
    "ecmwf": [
        "47098",
        "47099",
        "47203",
        "47551",
        "47102",
        "47090",
        "47095",
        "47100",
        "47106",
        "47114",
        "47121",
        "47142",
        "47130",
        "47137",
        "47138",
        "47139",
        "47279",
        "47283",
        "47115",
        "47096",
        "47153",
        "47255",
        "47161",
        "47162",
        "47192",
        "47284",
        "47140",
        "47172",
        "47251",
        "47245",
        "47247",
        "47701",
        "47158",
        "47168",
        "47169",
        "47170",
        "47174",
        "47175",
        "47262",
        "47266",
        "47268",
        "47710",
        "47239",
        "47232",
        "47235",
        "47128",
        "47127",
        "47135",
        "47605",
        "47185",
        "47188",
        "47189"
    ],
    "kwrf_rdps": [
        "47098",
        "47099",
        "47110",
        "47113",
        "47119",
        "47203",
        "47551",
        "47102",
        "47090",
        "47092",
        "47095",
        "47100",
        "47106",
        "47114",
        "47118",
        "47121",
        "47142",
        "47130",
        "47136",
        "47137",
        "47138",
        "47139",
        "47279",
        "47283",
        "47115",
        "47096",
        "47152",
        "47151",
        "47153",
        "47155",
        "47255",
        "47161",
        "47162",
        "47192",
        "47284",
        "47140",
        "47172",
        "47251",
        "47245",
        "47247",
        "47701",
        "47158",
        "47165",
        "47163",
        "47168",
        "47167",
        "47169",
        "47170",
        "47174",
        "47175",
        "47262",
        "47266",
        "47268",
        "47710",
        "47129",
        "47177",
        "47239",
        "47232",
        "47235",
        "47128",
        "47127",
        "47135",
        "47605",
        "47182",
        "47185",
        "47188",
        "47189"
    ],
    "um_ldps": [
        "47551",
        "47142",
        "47139",
        "47283",
        "47096",
        "47153",
        "47161",
        "47172",
        "47175",
        "47701",
        "47158",
        "47266",
        "47710",
        "47128",
        "47605"
    ],
    "um_rdps": [
        "47551",
        "47118",
        "47142",
        "47139",
        "47283",
        "47096",
        "47153",
        "47161",
        "47701",
        "47158",
        "47174",
        "47175",
        "47266",
        "47710",
        "47239",
        "47605",
        "47172"
    ],
    "kim_gdps": [
        "47175",
        "47251"
    ],
    "um_gdps":[
        "47175",
        "47251"
    ],
}
  },
  city:{
    selector:'stationWide',
    excludeByModel:{
    "kwrf_rdps": [
        "47551",
        "47118",
        "47283",
        "47096",
        "47172",
        "47251",
        "47701",
        "47262",
        "47266",
        "47268",
        "47710",
        "47177",
        "47239",
        "47605"
    ],
    "um_rdps": [
        "47551",
        "47118",
        "47172",
        "47239"
    ],
    "ecmwf": [
        "47172"
    ],
    "um_ldps": [
        "47172"
    ],
    "kim_gdps": [
        "47251"
    ]
}
  }
},

hazard:{
},

ensemble:{
  srf3:{
    selector:'stationWide',
    excludeByModel:{
      kim_epsg:['47175','47251'],
      um_epsg:['47175','47172'],
      ecmwf_eps:['47175','47172']
    },
  },
  mrf6:{
    selector:'stationWide',
    excludeByModel:{
      kim_epsg:['47175','47251'],
      um_epsg:['47175','47172'],
      ecmwf_eps:['47175','47172']
    },
  },
  lrf6:{
    selector:'stationWide',
    excludeByModel:{
      kim_epsg:['47175','47251'],
      ecmwf_eps:['47175','47172']
    },
  },
  trd3:{
    selector:'stationWide',
    excludeByModel:{
      kim_epsg:['47175','47251'],
      um_epsg:['47175','47172'],
      ecmwf_eps:['47175','47172']
    },
  },
  trd6:{
    selector:'stationWide',
    excludeByModel:{
      kim_gdps:['47251'],
      um_gdps:['47172'],
      ecmwf_eps:['47172']
    },
  },
  prob:{
    selector:'prec6h_intensity'
  },
  mp03:{
    selector:'epsg_criterion'
  },
  mp06:{
    selector:'epsg_criterion'
  },
  days:{
    selector:'epsg_criterion'
  },
  mpda:{
    selector:'epsg_criterion'
  },
  prep:{
    selector:'prob_rain_intensity'
  },
  "spgt:spgt":{
        selector:'spgt_height'
  },
  "nhem:spgt":{
        selector:'spgt_height_nhem'
  },
  "cnf1:area":{
    selector:'conf_rain_intensity'
  },
  "cnf2:ar12":{
    selector:'conf_rain_intensity'
  },
  metg:{
    selector:'stationWide',
    excludeByModel:{
      kim_lens:['47172', '47268'],
      um_lens:['47172', '47268']
    },
  },
  rn03:{
    selector:'lens_criterion'
  },
  rn12:{
    selector:'lens_criterion'
  },
  rday:{
    selector:'lens_criterion'
  },
  prn3:{
    selector:'prec3h_intensity'
  },
  prn1:{
    selector:'prec1h_intensity'
  },
  psn3:{
    selector:'snow3h_intensity'
  },
  psn1:{
    selector:'snow1h_intensity'
  },
  pvis:{
    selector:'visblt_intensity'
  },


 }
};


/* expose aux rules for app.js safe lookup */
if(typeof window!=='undefined'){
  window.AUX_SELECTORS=AUX_SELECTORS;
  window.AUX_USAGE_RULES=AUX_USAGE_RULES;
}
