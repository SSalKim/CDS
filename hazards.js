const HAZARD_CATEGORIES=[

{id:"stbl",name:"안정도(대류)"},
{id:"lgtn",name:"낙뢰"},
{id:"fogv",name:"안개"},
{id:"airq",name:"대기안정도"},

];


const HAZARD_PRODUCTS=[

/* 안정도(대류) */
{category:"stbl",id:"kindex",label:"K Index",
    patternByModel:{
        kim_gdps:[
        "kim_gdps_erly_asia_kindex_ft06_pa4_s{fh}_{run}.png",
        "kim_gdps_erly_hkor_kindex_s{fh}_{run}.png"
        ],
        um_gdps:[
        "gdps_erly_asia_kindex_ft06_pa4_s{fh}_{run}.gif",
        "gdps_erly_hkor_kindex_s{fh}_{run}.gif"
        ],
        ecmwf:[
        "ecmw_lc40_asia_kindex_s{fh}_{run}.gif",
        "ecmw_lc20_hkor_kindex_s{fh}_{run}.gif"
        ],
        kim_rdps:[
        "kim_rdps_erly_asia_kindex_s{fh}_{run}.png",
        "kim_rdps_erly_hkor_kindex_s{fh}_{run}.png"
        ],
        um_rdps:[
        "rdps_lc30_asia_kindex_ft03_pa4_s{fh}_{run}.gif",
        "rdps_lc10_hkor_kindex_s{fh}_{run}.gif"
        ],
        kwrf_rdps:[
        "kwrf_lc30_asia_kindex_ft03_pa4_s{fh}_{run}.gif",
        "kwrf_lc10_hkor_kindex_s{fh}_{run}.gif"
        ],
        kim_ldps:[
        "kim_ldps_erly_hkor_kindex_s{fh}_{run}.png"
        ]
    }  
},
{category:"stbl",id:"lindex",label:"Lifted Index",
    patternByModel:{
        kim_gdps:[
        "kim_gdps_erly_asia_lindex_ft06_pa4_s{fh}_{run}.png",
        "kim_gdps_erly_hkor_lindex_s{fh}_{run}.png"
        ],
        um_gdps:[
        "gdps_erly_asia_lindex_ft06_pa4_s{fh}_{run}.gif",
        "gdps_erly_hkor_lindex_s{fh}_{run}.gif"
        ],
        ecmwf:[
        "ecmw_lc40_asia_lindex_s{fh}_{run}.gif",
        "ecmw_lc20_hkor_lindex_s{fh}_{run}.gif"
        ],
        kim_rdps:[
        "kim_rdps_erly_asia_lindex_s{fh}_{run}.png",
        "kim_rdps_erly_hkor_lindex_s{fh}_{run}.png"
        ],
        um_rdps:[
        "rdps_lc30_asia_lindex_ft03_pa4_s{fh}_{run}.gif",
        "rdps_lc10_hkor_lindex_s{fh}_{run}.gif"
        ],
        kwrf_rdps:[
        "kwrf_lc30_asia_lindex_ft03_pa4_s{fh}_{run}.gif",
        "kwrf_lc10_hkor_lindex_s{fh}_{run}.gif"
        ],
        kim_ldps:[
        "kim_ldps_erly_hkor_lindex_s{fh}_{run}.png"
        ]
    }  
},
{category:"stbl",id:"sindex",label:"쇼월터 Index",
    patternByModel:{
        kim_gdps:[
        "kim_gdps_erly_asia_sindex_ft06_pa4_s{fh}_{run}.png",
        "kim_gdps_erly_hkor_sindex_s{fh}_{run}.png"
        ],
        um_gdps:[
        "gdps_erly_asia_sindex_ft06_pa4_s{fh}_{run}.gif",
        "gdps_erly_hkor_sindex_s{fh}_{run}.gif"
        ],
        ecmwf:[
        "ecmw_lc40_asia_sindex_s{fh}_{run}.gif",
        "ecmw_lc20_hkor_sindex_s{fh}_{run}.gif"
        ],
        kim_rdps:[
        "kim_rdps_erly_asia_sindex_s{fh}_{run}.png",
        "kim_rdps_erly_hkor_sindex_s{fh}_{run}.png"
        ],
        um_rdps:[
        "rdps_lc30_asia_sindex_ft03_pa4_s{fh}_{run}.gif",
        "rdps_lc10_hkor_sindex_s{fh}_{run}.gif"
        ],
        kwrf_rdps:[
        "kwrf_lc30_asia_sindex_ft03_pa4_s{fh}_{run}.gif",
        "kwrf_lc10_hkor_sindex_s{fh}_{run}.gif"
        ],
        kim_ldps:[
        "kim_ldps_erly_hkor_sindex_s{fh}_{run}.png"
        ]
    }  
},
{category:"stbl",id:"totidx",label:"토탈 total 지수",
    patternByModel:{
        kim_gdps:[
        "kim_gdps_erly_asia_totidx_ft06_pa4_s{fh}_{run}.png",
        "kim_gdps_erly_hkor_totidx_s{fh}_{run}.png"
        ],
        um_gdps:[
        "gdps_erly_asia_totidx_ft06_pa4_s{fh}_{run}.gif",
        "gdps_erly_hkor_totidx_s{fh}_{run}.gif"
        ],
        ecmwf:[
        "ecmw_lc40_asia_totidx_s{fh}_{run}.gif",
        "ecmw_lc20_hkor_totidx_s{fh}_{run}.gif"
        ],
        kim_rdps:[
        "kim_rdps_erly_asia_totidx_s{fh}_{run}.png",
        "kim_rdps_erly_hkor_totidx_s{fh}_{run}.png"
        ],
        um_rdps:[
        "rdps_lc30_asia_totidx_ft03_pa4_s{fh}_{run}.gif",
        "rdps_lc10_hkor_totidx_s{fh}_{run}.gif"
        ],
        kwrf_rdps:[
        "kwrf_lc30_asia_totidx_ft03_pa4_s{fh}_{run}.gif",
        "kwrf_lc10_hkor_totidx_s{fh}_{run}.gif"
        ],
        kim_ldps:[
        "kim_ldps_erly_hkor_totidx_s{fh}_{run}.png"
        ]
    }  
},
{category:"stbl",id:"gdiidx",label:"GDI 지수",
    patternByModel:{
        kim_gdps:"kim_gdps_erly_asia_gdiidx_ft03_pa4_s{fh}_{run}.png",
        um_gdps:"gdps_erly_asia_gdiidx_ft03_pa4_s{fh}_{run}.gif",
        kim_rdps:"kim_rdps_erly_asia_gdiidx_s{fh}_{run}.png"
    }  
},
{category:"stbl",id:"sbcape",label:"지상기반 CAPE",
    patternByModel:{
        kim_gdps:[
        "kim_gdps_erly_asia_sbcape_ft06_pa4_s{fh}_{run}.png",
        "kim_gdps_erly_hkor_sbcape_s{fh}_{run}.png"
        ],
        um_gdps:[
        "gdps_erly_asia_sbcape_ft06_pa4_s{fh}_{run}.gif",
        "gdps_erly_hkor_sbcape_s{fh}_{run}.gif"
        ],
        ecmwf:[
        "ecmw_lc40_asia_sbcape_s{fh}_{run}.gif",
        "ecmw_lc20_hkor_sbcape_s{fh}_{run}.gif"
        ],
        kim_rdps:[
        "kim_rdps_erly_asia_sbcape_s{fh}_{run}.png",
        "kim_rdps_erly_hkor_sbcape_s{fh}_{run}.png"
        ],
        kim_ldps:[
        "kim_ldps_erly_hkor_sbcape_s{fh}_{run}.png"
        ]
    }  
},
{category:"stbl",id:"srh03k",label:"SRH",
    patternByModel:{
        kim_gdps:[
        "kim_gdps_erly_asia_srh03k_ft06_pa4_s{fh}_{run}.png",
        "kim_gdps_erly_hkor_srh03k_s{fh}_{run}.png"
        ],
        um_gdps:[
        "gdps_erly_asia_srh03k_ft06_pa4_s{fh}_{run}.gif",
        "gdps_erly_hkor_srh03k_s{fh}_{run}.gif"
        ],
        ecmwf:[
        "ecmw_lc40_asia_srh03k_s{fh}_{run}.gif",
        "ecmw_lc20_hkor_srh03k_s{fh}_{run}.gif"
        ],
        kim_rdps:[
        "kim_rdps_erly_asia_srh03k_s{fh}_{run}.png",
        "kim_rdps_erly_hkor_srh03k_s{fh}_{run}.png"
        ],
        um_rdps:[
        "rdps_lc30_asia_srh03k_ft03_pa4_s{fh}_{run}.gif",
        "rdps_lc10_hkor_srh03k_s{fh}_{run}.gif"
        ],
        kwrf_rdps:[
        "kwrf_lc30_asia_srh03k_ft03_pa4_s{fh}_{run}.gif",
        "kwrf_lc10_hkor_srh03k_s{fh}_{run}.gif"
        ],
        kim_ldps:[
        "kim_ldps_erly_hkor_srh03k_s{fh}_{run}.png"
        ]
    }  
},
{category:"stbl",id:"frcvel",label:"지면마찰속도",
    patternByModel:{
        kim_gdps:"kim_gdps_erly_asia_frcvel_ft06_pa4_s{fh}_{run}.png",
        um_gdps:"gdps_erly_asia_frcvel_ft06_pa4_s{fh}_{run}.gif",
        um_rdps:"rdps_lc30_asia_frcvel_ft03_pa4_s{fh}_{run}.gif"
    }  
},

/* 낙뢰 */
{category:"lgtn",id:"lght",label:"낙뢰가이던스",
    patternByModel:{
        kim_gdps:"kim_gdps_lc20_lght_{run}.gif",
        um_gdps:"gdps_lc20_lght_{run}.gif",
        um_rdps: "rdps_lc30_lght_pa4_{run}.gif"
    }  
},
{category:"lgtn",id:"lgtidx",label:"구름물리:낙뢰가이던스",
    patternByModel:{
        kim_gdps:"kim_gdps_lc30_asia_lgtidx_ft03_pa4_s{fh}_{run}.png",
        um_gdps:"gdps_lc30_asia_lgtidx_ft03_pa4_s{fh}_{run}.gif",
        ecmwf:"ecmw_asia_lgtidx_ft03_pa4_s{fh}_{run}.gif",
        um_rdps:"rdps_lc30_asia_lgtidx_ft03_pa4_s{fh}_{run}.gif"
    },
    forecastStepByModel:{
        kim_gdps:[
            {start:0,end:84,step:3}
        ],
        um_gdps:[
            {start:0,end:84,step:3}
        ],
        ecmwf:[
            {start:0,end:84,step:3}
        ],
        um_rdps:[
            {start:0,end:84,step:3}
        ],
    }

},

/* 안개 */
{category:"fogv",id:"fxko4s",label:"습도 예상도",
    patternByModel:{
        kim_gdps:"kim_gdps_lc20_fxkorh_{run}.png",
        um_gdps:"gdps_lc20_fxkorh_{run}.gif",
        kim_rdps:"kim_rdps_fxkorh_{run}.png",
        um_rdps:"rdps_lc30_fxko4s1_pa4_{run}.gif",
        kwrf_rdps:"kwrf_lc10_fxko4s1_pa4_{run}.gif",
        kim_ldps:"kim_ldps_fxkorh_{run}.png",
        um_ldps:"ldps_l1p5_fxko4s1_{run}.gif"
    }  
},
{category:"fogv",id:"fogvis",label:"시정",
    patternByModel:{
        kim_rdps:"kim_rdps_fogvis_s{fh}_{run}.png",
        kim_ldps:"kim_ldps_fogvis_s{fh}_{run}.png",
        um_gdps:"gdps_ufog_lc20_fogvis_s{fh}_{run}.gif",
        um_ldps:"ldps_l1p5_ufog_fogvis_h{fh}_{run}.gif"
    },
    archiveStartByModel:{
        kim_rdps:"2026-03-30",
        kim_ldps:"2026-03-30"
    },
    folderByModel:{
        kim_rdps:"KIMR2",
    },
},
{category:"fogv",id:"fogvis",label:"안개분율",
    patternByModel:{
        kim_rdps:"kim_rdps_fogfrc_s{fh}_{run}.png",
        kim_ldps:"kim_ldps_fogfrc_s{fh}_{run}.png",
        um_gdps:"gdps_ufog_lc20_fogfrc_s{fh}_{run}.gif",
        um_ldps:"ldps_l1p5_ufog_fogfrc_h{fh}_{run}.gif"
    },
    archiveStartByModel:{
        kim_rdps:"2026-03-30",
        kim_ldps:"2026-03-30"
    },
    folderByModel:{
        kim_rdps:"KIMR2",
    },
},
{category:"fogv",id:"visnew",label:"구름변수:안개가이던스",
    patternByModel:{
        um_gdps:"gdps_hkor_visnew_s{fh}_{run}.gif",
        kim_rdps:"kim_rdps_erly_hkor_visnew_s{fh}_{run}.png",
        kim_ldps:"kim_ldps_erly_hkor_visnew_s{fh}_{run}.png",
        um_ldps:"ldps_l1p5_visnew_s{fh}_{run}.gif"
    }
},

/* 대기안정도 */
{category:"airq",id:"airstb",label:"안정도",
    patternByModel:{
        kim_gdps:"kim_gdps_airq_hkor_airstb_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_gdps:[
            {start:0,end:144,step:3}
        ]
    }
},
{category:"airq",id:"wndsfc",label:"지표면 풍속",
    patternByModel:{
        kim_gdps:"kim_gdps_airq_hkor_wndsfc_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_gdps:[
            {start:0,end:144,step:3}
        ]
    }
},
{category:"airq",id:"wnd850",label:"850hPa 풍속",
    patternByModel:{
        kim_gdps:"kim_gdps_airq_hkor_wnd850_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_gdps:[
            {start:0,end:144,step:3}
        ]
    }
},
{category:"airq",id:"pblhgt",label:"PBL 고도",
    patternByModel:{
        kim_gdps:"kim_gdps_airq_hkor_pblhgt_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_gdps:[
            {start:0,end:144,step:3}
        ]
    }
},
{category:"airq",id:"acptot",label:"3시간 누적강수",
    patternByModel:{
        kim_gdps:"kim_gdps_airq_hkor_acptot_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_gdps:[
            {start:0,end:144,step:3}
        ]
    }
},
{category:"airq",id:"ventlt",label:"환기지수",
    patternByModel:{
        kim_gdps:"kim_gdps_airq_hkor_ventlt_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_gdps:[
            {start:0,end:144,step:3}
        ]
    }
},
{category:"airq",id:"invlay",label:"역전층유무",
    patternByModel:{
        kim_gdps:"kim_gdps_airq_hkor_invlay_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_gdps:[
            {start:0,end:144,step:3}
        ]
    }
}
];


/*
위험기상 1차 드롭다운별 2차 드롭다운 기본값
*/
const HAZARD_DEFAULT_PRODUCT_BY_CATEGORY={



};


/*
위험기상 2차 드롭다운 숨김 규칙
필요할 때만 사용한다.
예:
const HAZARD_PRODUCT_CATEGORY_UI_CONFIG={
typhoon:{hideProductSelect:true}
};
*/
const HAZARD_PRODUCT_CATEGORY_UI_CONFIG={

};


/*
위험기상 category별 모델 제한
비워두면 모든 모델 버튼이 기존대로 사용 가능하다.
*/
const HAZARD_CATEGORY_MODEL_RESTRICTIONS={


stbl:{
allowedModels:["kim_gdps","um_gdps","ecmwf","kim_rdps","um_rdps","kwrf_rdps","kim_ldps"],
fallbackModel:"kim_gdps"
},

lgtn:{
allowedModels:["kim_gdps","um_gdps","ecmwf","um_rdps"],
fallbackModel:"kim_gdps"
},

fogv:{
allowedModels:["kim_gdps","um_gdps","ecmwf","kim_rdps","um_rdps","kwrf_rdps","kim_ldps","um_ldps"],
fallbackModel:"kim_gdps"
},

airq:{
allowedModels:["kim_gdps"],
fallbackModel:"kim_gdps"
},

};


/*
위험기상 1차+2차 조합별 모델 제한
형식: "category:productId"
*/
const HAZARD_SELECTION_MODEL_RESTRICTIONS={

/*
예시:
"typhoon:typhoon_track":{
allowedModels:["kim_gdps","ecmwf"],
fallbackModel:"kim_gdps"
}
*/

};


/*
위험기상 보조 패널 설정
pattern에 {detail}을 쓰는 산출물이 생기면 여기에 연결한다.
*/
const HAZARD_AUX_SELECTOR_CONFIG={

/*
예시:
risk_region:{
title:"지역",
defaultValue:"kr",
items:[
{type:"item",value:"kr",label:"전국"},
{type:"item",value:"capital",label:"수도권"},
{type:"separator"},
{type:"item",value:"gangwon",label:"강원"}
]
}
*/

};
