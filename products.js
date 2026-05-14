/* 예보장 */

const PRODUCT_CATEGORIES=[
{id:"asia", name:"기본예상도"},
{id:"hkor", name:"기본예상도(한반도)"},
{id:"lkor1", name:"국지모델(한반도)"},
{id:"lkor2", name:"국지모델(상세영역)"},
{id:"nhem", name:"북반구예상"},
{id:"radm", name:"구름모의영상"},
{id:"isen", name:"등온위면분석"},
{id:"wtem1", name:"상세-바람기온"},
{id:"wtem2", name:"상세바람-기온(확장영역)"},
{type:"header", name:"─────────────────"},
{id:"skew", name:"예상단열선도"},
{id:"city", name:"연직시계열"}
];

const PRODUCTS=[

/* 기본예상도 */
{category:"asia", type:"header", label:"──── 고도/기온 ────"},
{category:"asia", id:"gph200", label:"200/300 고도,기온,풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_gph200_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_gph200_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_gph200_s{fh}_{run}.gif",
        ukmo: "ukum_erly_asia_gph200_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_asia_gph200_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_gph200_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_gph200_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_gph200_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"gph500", label:"500 고도,기온,풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_gph500_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_gph500_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_gph500_s{fh}_{run}.gif",
        ukmo: "ukum_erly_asia_gph500_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_asia_gph500_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_gph500_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_gph500_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_gph500_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"gph700", label:"700 고도,상당온위",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_gph700_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_gph700_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_gph700_s{fh}_{run}.gif",
        ukmo: "ukum_erly_asia_gph700_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_asia_gph700_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_gph700_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_gph700_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_gph700_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"ept850", label:"850 고도,상당온위",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_ept850_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_ept850_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_ept850_s{fh}_{run}.gif",
        ukmo: "ukum_erly_asia_ept850_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_asia_ept850_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_ept850_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_ept850_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_ept850_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"ept925", label:"925 고도,상당온위",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_ept925_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_ept925_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_ept925_s{fh}_{run}.gif",
        ukmo: "ukum_erly_asia_ept925_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_asia_ept925_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_ept925_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_ept925_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_ept925_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"thk500", label:"1000-500 층후",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_thk500_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_thk500_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_thk500_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_thk500_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_thk500_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_thk500_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_thk500_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"thk700", label:"1000-700 층후",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_thk700_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_thk700_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_thk700_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_thk700_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_thk700_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_thk700_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_thk700_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"thk850", label:"1000-850 층후",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_thk850_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_thk850_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_thk850_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_thk850_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_thk850_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_thk850_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_thk850_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", type:"header", label:"──── 유선/풍속 ────"},
{category:"asia", id:"wnd200", label:"200/300 유선,풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_wnd200_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_wnd200_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_wnd200_s{fh}_{run}.gif",
        ukmo: "ukum_erly_asia_wnd200_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_asia_wnd200_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_wnd200_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_wnd200_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_wnd200_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"wnd500", label:"500 유선,풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_wnd500_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_wnd500_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_wnd500_s{fh}_{run}.gif",
        ukmo: "ukum_erly_asia_wnd500_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_asia_wnd500_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_wnd500_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_wnd500_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_wnd500_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"wnd700", label:"700 유선,풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_wnd700_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_wnd700_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_wnd700_s{fh}_{run}.gif",
        ukmo: "ukum_erly_asia_wnd700_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_asia_wnd700_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_wnd700_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_wnd700_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_wnd700_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"wnd850", label:"850 유선,풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_wnd850_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_wnd850_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_wnd850_s{fh}_{run}.gif",
        ukmo: "ukum_erly_asia_wnd850_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_asia_wnd850_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_wnd850_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_wnd850_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_wnd850_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"wnd925", label:"925 유선,풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_wnd925_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_wnd925_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_wnd925_s{fh}_{run}.gif",
        ukmo: "ukum_erly_asia_wnd925_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_asia_wnd925_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_wnd925_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_wnd925_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_wnd925_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", type:"header", label:"────── 강수 ──────"},
{category:"asia", id:"surfce", label:"해면기압, 누적강수량",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_surfce_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_surfce_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_surfce_s{fh}_{run}.gif",
        ukmo: "ukum_erly_asia_surfce_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_asia_surfce_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_surfce_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_surfce_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_surfce_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"acrain", label:"총누적강수량",
    patternByModel:{
        um_gdps: "gdps_erly_asia_surfce_ft06_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_acrain_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"rain3h", label:"3시간 누적강수량",
    patternByModel:{
        kim_gdps: "kim_gdps_lc40_fxko4r1_{run}.png",
        um_gdps: "gdps_lc40_fxko4r1_{run}.gif",
        ecmwf: "ecmw_lc20_rain3h_{run}.gif",
        ukmo: "ukum_lc40_fxko4r1_{run}.png",
        kim_rdps: "kim_rdps_fxko4r1_{run}.png",
        um_rdps: "rdps_lc30_fxko4r1_pa4_{run}.gif",
        kwrf_rdps: "kwrf_lc10_fxko4r1_pa4_{run}.gif",
        um_ldps: "ldps_lc06_rain3h_{run}.gif"
    }
},
{category:"asia", id:"rain6h", label:"6시간 누적강수량",
    patternByModel:{
        kim_gdps: "kim_gdps_lc40_rain6h_{run}.png",
        um_gdps: "gdps_lc40_rain6h_{run}.gif",
        ecmwf: "ecmw_lc20_rain6h_{run}.gif",
        kim_rdps: "kim_rdps_rain6h_{run}.png",
        um_rdps: "rdps_lc30_rain6h_{run}.gif",
        kwrf_rdps: "kwrf_lc10_rain6h_{run}.gif",
        um_ldps: "ldps_lc06_rain6h_{run}.gif"
    }
},
{category:"asia", id:"rain12", label:"12시간 누적강수량",
    patternByModel:{
        kim_gdps: "kim_gdps_lc40_rain12_{run}.png",
        um_gdps: "gdps_lc40_rain12_{run}.gif",
        ecmwf: "ecmw_lc20_rain12_{run}.gif"
    }
},
{category:"asia", id:"rainth", label:"총누적강수량(3시간간격)",
    patternByModel:{
        kim_gdps: "kim_gdps_lc40_rainth_{run}.png",
        um_gdps: "gdps_lc40_rainth_{run}.gif",
        ecmwf: "ecmw_lc20_rainth_{run}.gif",
        kim_rdps: "kim_rdps_rainth_{run}.png",
        um_rdps: "rdps_lc30_rainth_{run}.gif",
        kwrf_rdps: "kwrf_lc10_rainth_{run}.gif",
        um_ldps: "ldps_lc06_rainth_{run}.gif"
    }
},
{category:"asia", id:"raint6", label:"총누적강수량(6시간간격)",
    patternByModel:{
        kim_gdps: "kim_gdps_lc40_raint6_{run}.png",
        um_gdps: "gdps_lc40_raint6_{run}.gif",
        ecmwf: "ecmw_lc20_raint6_{run}.gif",
        um_rdps: "rdps_lc30_raint6_{run}.gif",
        kwrf_rdps: "kwrf_lc10_raint6_{run}.gif",
        um_ldps: "ldps_lc06_raint6_{run}.gif"
    }
},
{category:"asia", id:"rndays", label:"총누적강수량(단기예보용)",
    patternByModel:{
        kim_gdps: "kim_gdps_rain_days_{run}.png",
        um_gdps: "gdps_rain_days_{run}.png",
        ecmwf: "ecmw_rain_days_{run}.png"
    }
},
{category:"asia", id:"snw950", label:"눈혼합비",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_snw950_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_snw950_ft06_pa4_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_snw950_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_snw950_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_snw950_ft03_pa4_s{fh}_{run}.gif"
    }
},
{category:"asia", id:"acsnow", label:"강설량",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_acsnow_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_acsnow_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_acsnow_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_acsnow_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_acsnow_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_acsnow_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_acsnow_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"acptot", label:"강수량",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_acptot_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_acptot_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_acptot_s{fh}_{run}.gif",
        ukmo: "ukum_erly_asia_acptot_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_asia_acptot_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_acptot_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_acptot_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_acptot_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"anltpw", label:"가강수량, MSLP",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_anltpw_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_anltpw_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_anltpw_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_anltpw_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_anltpw_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_anltpw_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_anltpw_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", type:"header", label:"──── 습수/수분속 ────"},
{category:"asia", id:"ttd700", label:"700 습수(T-Td)",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_ttd700_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_ttd700_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_ttd700_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_ttd700_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_ttd700_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_ttd700_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_ttd700_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"anl850", label:"850 습수(T-Td)",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_anl850_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_anl850_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_anl850_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_anl850_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_anl850_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_anl850_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_anl850_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"anl925", label:"925 습수(T-Td)",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_anl925_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_anl925_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_anl925_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_anl925_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_anl925_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_anl925_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_anl925_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"anlsfc", label:"지상 습수(T-Td)",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_anlsfc_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_anlsfc_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_anlsfc_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_anlsfc_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_anlsfc_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_anlsfc_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_anlsfc_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"fxko78", label:"700-850 습수도",
    patternByModel:{
        kim_gdps: "kim_gdps_lc20_fxko78_{run}.png",
        um_gdps: "gdps_lc20_fxko78_{run}.gif",
        kim_rdps: "kim_rdps_fxko78_{run}.png"
    }
},
{category:"asia", id:"moflux", label:"850 수분속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_moflux_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_moflux_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_moflux_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_moflux_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_moflux_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_moflux_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_moflux_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", type:"header", label:"──── 발산/수렴 ────"},
{category:"asia", id:"div200", label:"200/300 발산장,등풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_div200_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_div200_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_div200_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_div200_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_div200_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_div200_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_div200_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"con850", label:"850 수렴도,등풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_con850_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_con850_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_con850_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_con850_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_con850_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_con850_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_con850_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", type:"header", label:"────── 전선 ──────"},
{category:"asia", id:"frg700", label:"700 전선강도,고도,기온",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_frg700_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_frg700_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_frg700_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_frg700_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_frg700_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_frg700_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_frg700_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"frg850", label:"850 전선강도,고도,기온",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_frg850_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_frg850_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_frg850_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_frg850_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_frg850_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_frg850_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_frg850_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"frg925", label:"925 전선강도,고도,기온",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_frg925_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_frg925_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_frg925_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_frg925_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_frg925_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_frg925_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_frg925_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", type:"header", label:"─── 역학적 강제력 ───"},
{category:"asia", id:"dfmslp", label:"지상 기압변화",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_dfmslp_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_dfmslp_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_dfmslp_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_dfmslp_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_dfmslp_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_dfmslp_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"advort", label:"500 와도이류",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_advort_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_advort_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_advort_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_advort_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_advort_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_advort_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_advort_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"dfh500", label:"500 고도변화",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_dfh500_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_dfh500_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_dfh500_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_dfh500_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_dfh500_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_dfh500_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_dfh500_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"vel700", label:"700 상승속도",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_vel700_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_vel700_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_vel700_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_vel700_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_vel700_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_vel700_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_vel700_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"dft850", label:"850 기온변화",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_dft850_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_dft850_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_dft850_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_dft850_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_dft850_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_dft850_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_dft850_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"gph850", label:"850 혼합비",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_gph850_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_gph850_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_gph850_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_gph850_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_gph850_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_gph850_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_gph850_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"adthck", label:"1000-700 층후이류",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_adthck_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_adthck_ft06_pa4_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc40_asia_adthck_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_adthck_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_adthck_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_adthck_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_adthck_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", type:"header", label:"────── 기타 ──────"},
{category:"asia", id:"tgc2d", label:"지상바람",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_tgc2d_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_tgc2d_ft06_pa4_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_asia_tgc2d_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_asia_tgc2d_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_tgc2d_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_asia_tgc2d_s{fh}_{run}.gif"
    },
    archiveStartByModel:{
        um_ldps:"2018-01-18"
    },
},
{category:"asia", id:"fxfe", label:"종합보조예상",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_asia_fxfe_ft06_pa4_s{fh}_{run}.png",
        um_gdps: "gdps_erly_asia_fxfe_ft06_pa4_s{fh}_{run}.gif",
        um_rdps: "rdps_lc30_asia_fxfe_ft03_pa4_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_asia_fxfe_ft03_pa4_s{fh}_{run}.gif"
    }
},

/* 기본예상도(한반도) */
{category:"hkor", type:"header", label:"──── 고도/기온 ────"},
{category:"hkor", id:"gph200", label:"200/300 고도,기온,풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_gph200_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_gph200_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_gph200_s{fh}_{run}.gif",
        ukmo: "ukum_erly_hkor_gph200_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_hkor_gph200_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_gph200_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_gph200_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_gph200_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_gph200_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"gph500", label:"500 고도,기온,풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_gph500_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_gph500_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_gph500_s{fh}_{run}.gif",
        ukmo: "ukum_erly_hkor_gph500_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_hkor_gph500_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_gph500_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_gph500_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_gph500_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_gph500_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"gph700", label:"700 고도,상당온위",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_gph700_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_gph700_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_gph700_s{fh}_{run}.gif",
        ukmo: "ukum_erly_hkor_gph700_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_hkor_gph700_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_gph700_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_gph700_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_gph700_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_gph700_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"ept850", label:"850 고도,상당온위",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_ept850_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_ept850_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_ept850_s{fh}_{run}.gif",
        ukmo: "ukum_erly_hkor_ept850_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_hkor_ept850_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_ept850_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_ept850_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_ept850_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_ept850_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"ept925", label:"925 고도,상당온위",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_ept925_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_ept925_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_ept925_s{fh}_{run}.gif",
        ukmo: "ukum_erly_hkor_ept925_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_hkor_ept925_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_ept925_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_ept925_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_ept925_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_ept925_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"thk500", label:"1000-500 층후",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_thk500_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_thk500_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_thk500_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_thk500_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_thk500_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_thk500_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_thk500_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_thk500_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"thk700", label:"1000-700 층후",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_thk700_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_thk700_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_thk700_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_thk700_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_thk700_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_thk700_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_thk700_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_thk700_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"thk850", label:"1000-850 층후",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_thk850_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_thk850_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_thk850_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_thk850_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_thk850_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_thk850_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_thk850_s{fh}_{run}.gif"
    }
},
{category:"hkor", type:"header", label:"──── 유선/풍속 ────"},
{category:"hkor", id:"wnd200", label:"200/300 유선,풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_wnd200_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_wnd200_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_wnd200_s{fh}_{run}.gif",
        ukmo: "ukum_erly_hkor_wnd200_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_hkor_wnd200_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_wnd200_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_wnd200_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_wnd200_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_wnd200_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"wnd500", label:"500 유선,풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_wnd500_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_wnd500_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_wnd500_s{fh}_{run}.gif",
        ukmo: "ukum_erly_hkor_wnd500_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_hkor_wnd500_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_wnd500_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_wnd500_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_wnd500_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_wnd500_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"wnd700", label:"700 유선,풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_wnd700_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_wnd700_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_wnd700_s{fh}_{run}.gif",
        ukmo: "ukum_erly_hkor_wnd700_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_hkor_wnd700_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_wnd700_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_wnd700_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_wnd700_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_wnd700_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"wnd850", label:"850 유선,풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_wnd850_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_wnd850_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_wnd850_s{fh}_{run}.gif",
        ukmo: "ukum_erly_hkor_wnd850_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_hkor_wnd850_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_wnd850_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_wnd850_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_wnd850_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_wnd850_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"wnd925", label:"925 유선,풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_wnd925_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_wnd925_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_wnd925_s{fh}_{run}.gif",
        ukmo: "ukum_erly_hkor_wnd925_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_hkor_wnd925_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_wnd925_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_wnd925_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_wnd925_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_wnd925_s{fh}_{run}.gif"
    }
},
{category:"hkor", type:"header", label:"────── 강수 ──────"},
{category:"hkor", id:"acrain", label:"총누적강수량",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_acrain_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_acrain_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_acrain_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_acrain_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_acrain_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_acrain_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_acrain_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_acrain_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"acptot", label:"시간별 누적강수량",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_acptot_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_acptot_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_acptot_s{fh}_{run}.gif",
        ukmo: "ukum_erly_hkor_acptot_s{fh}_{run}.png",
        kim_rdps: "kim_rdps_erly_hkor_acptot_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_acptot_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_surfce_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_acptot_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_acptot_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"prcp3h", label:"3시간 누적강수량",
    forecastStepByModel:{
        kim_rdps:[
            {start:0,end:120,step:3}
        ],
        kim_ldps:[
            {start:0,end:48,step:3}
        ]
    },
    patternByModel:{
        kim_rdps: "kim_rdps_erly_hkor_prcp3h_s{fh}_{run}.png",
        kim_ldps: "kim_ldps_erly_hkor_prcp3h_s{fh}_{run}.png",
    }
},
{category:"hkor", id:"snw950", label:"눈혼합비",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_snw950_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_snw950_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_snw950_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_snw950_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_snw950_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_snw950_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"tmerge", label:"신적설(수상당량비 적용)",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_merg_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_merg_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_tmerge_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_merg_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_merg_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_merg_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_merg_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"anltpw", label:"가강수량, MSLP",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_anltpw_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_anltpw_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_anltpw_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_anltpw_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_anltpw_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_anltpw_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_anltpw_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_anltpw_s{fh}_{run}.gif"
    }
},
{category:"hkor", type:"header", label:"──── 습수/수분속 ────"},
{category:"hkor", id:"ttd700", label:"700 습수(T-Td)",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_ttd700_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_ttd700_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_ttd700_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_ttd700_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_ttd700_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_ttd700_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_ttd700_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_ttd700_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"anl850", label:"850 습수(T-Td)",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_anl850_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_anl850_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_anl850_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_anl850_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_anl850_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_anl850_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_anl850_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_anl850_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"anl925", label:"925 습수(T-Td)",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_anl925_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_anl925_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_anl925_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_anl925_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_anl925_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_anl925_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_anl925_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_anl925_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"anlsfc", label:"지상 습수(T-Td)",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_anlsfc_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_anlsfc_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_anlsfc_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_anlsfc_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_anlsfc_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_anlsfc_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_anlsfc_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_anlsfc_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"moflux", label:"850 수분속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_moflux_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_moflux_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_moflux_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_moflux_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_moflux_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_moflux_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_moflux_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_moflux_s{fh}_{run}.gif"
    }
},
{category:"hkor", type:"header", label:"──── 발산/수렴 ────"},
{category:"hkor", id:"div200", label:"200/300 발산장,등풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_div200_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_div200_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_div200_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_div200_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_div200_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_div200_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_div200_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_div200_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"con850", label:"850 수렴도,등풍속",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_con850_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_con850_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_con850_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_con850_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_con850_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_con850_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_con850_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_con850_s{fh}_{run}.gif"
    }
},
{category:"hkor", type:"header", label:"────── 전선 ──────"},
{category:"hkor", id:"frg700", label:"700 전선강도,고도,기온",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_frg700_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_frg700_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_frg700_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_frg700_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_frg700_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_frg700_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_frg700_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_frg700_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"frg850", label:"850 전선강도,고도,기온",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_frg850_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_frg850_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_frg850_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_frg850_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_frg850_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_frg850_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_frg850_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_frg850_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"frg925", label:"925 전선강도,고도,기온",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_frg925_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_frg925_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_frg925_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_frg925_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_frg925_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_frg925_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_frg925_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_frg925_s{fh}_{run}.gif"
    }
},
{category:"hkor", type:"header", label:"─── 역학적 강제력 ───"},
{category:"hkor", id:"dfmslp", label:"지상 기압변화",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_dfmslp_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_dfmslp_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_dfmslp_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_dfmslp_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_dfmslp_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_dfmslp_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_dfmslp_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"advort", label:"500 와도이류",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_advort_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_advort_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_advort_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_advort_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_advort_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_advort_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_advort_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_advort_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"dfh500", label:"500 고도변화",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_dfh500_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_dfh500_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_dfh500_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_dfh500_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_dfh500_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_dfh500_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_dfh500_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_dfh500_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"vel700", label:"700 상승속도",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_vel700_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_vel700_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_vel700_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_vel700_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_vel700_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_vel700_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_vel700_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_vel700_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"dft850", label:"850 기온변화",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_dft850_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_dft850_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_dft850_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_dft850_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_dft850_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_dft850_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_dft850_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_dft850_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"gph850", label:"850 혼합비",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_gph850_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_gph850_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_gph850_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_gph500_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_gph850_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_gph850_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_gph850_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_gph850_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"adthck", label:"1000-700 층후이류",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_adthck_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_adthck_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_adthck_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_adthck_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_adthck_s{fh}_{run}.gif",
        kwrf_rdps: "kwrf_lc10_hkor_adthck_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_adthck_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_adthck_s{fh}_{run}.gif"
    }
},
{category:"hkor", type:"header", label:"────── 기타 ──────"},
{category:"hkor", id:"wndgst", label:"강풍가이던스",
    patternByModel:{
        kim_gdps: "kim_gdps_erly_hkor_wndgst_s{fh}_{run}.png",
        um_gdps: "gdps_erly_hkor_wndgst_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_hkor_wndgst_s{fh}_{run}.gif",
        kim_rdps: "kim_rdps_erly_hkor_wndgst_s{fh}_{run}.png",
        um_rdps: "rdps_lc10_hkor_wndgst_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_erly_hkor_wndgst_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_wndgst_s{fh}_{run}.gif"
    }
},
{category:"hkor", id:"tdif", label:"상하층 기온차 분석",
    patternByModel:{
        kim_gdps: "kim_gdps_hkor_tdif_s{fh}_{run}.png",
        um_gdps: "gdps_hkor_tdif_s{fh}_{run}.png",
        um_rdps: "rdps_hkor_diff_s{fh}_{run}.png"
    }
},
{category:"hkor", id:"guid", label:"대류불안정 종합분석",
    patternByModel:{
        kim_gdps: "kim_gdps_hkor_guid_s{fh}_{run}.png",
        um_gdps: "gdps_hkor_guid_s{fh}_{run}.png",
        ecmwf: "ecmw_hkor_guid_s{fh}_{run}.png",
        um_rdps: "rdps_hkor_guid_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_rdps:[
            {start:0,end:84,step:3}
        ],
        um_gdps:[
            {start:0,end:84,step:3}
        ],
        ecmwf:[
            {start:0,end:84,step:3}
        ],
    },
},

/* 초단기 전용 */
{category:"klfs_vdps", id:"gph200", label:"200 고도,기온,풍속",
    patternByModel:{
        um_vdps: "vdps_rg15_gph200_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"gph300", label:"300 고도,기온,풍속",
    patternByModel:{
        um_vdps: "vdps_rg15_gph300_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"gph500", label:"500 고도,기온,와도",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_gph500_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_gph500_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_gph500_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"gph700", label:"700 고도,기온,상당온위",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_gph700_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_gph700_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_gph700_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"gph850", label:"850 고도,기온,비습,바람",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_gph850_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_gph850_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_mix850_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"gph925", label:"925 고도,기온,비습,바람",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_gph925_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_gph925_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_mix925_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"thk700", label:"1000-700 층후, 850 상당온위",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_thk700_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_thk700_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_thickn_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", type:"header", label:"──────────────────"},
{category:"klfs_vdps", id:"wnd200", label:"200 유선,풍속",
    patternByModel:{
        um_vdps: "vdps_rg15_wnd200_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"wnd500", label:"500 유선,풍속",
    patternByModel:{
        um_vdps: "vdps_rg15_wnd500_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"wnd850", label:"850 유선,풍속",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_wnd850_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_wnd850_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_wnd850_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", type:"header", label:"──────────────────"},
{category:"klfs_vdps", id:"surfce", label:"해면기압, 누적강수량",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_surfce_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_surfce_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_surfce_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"acrain", label:"총누적강수량",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_acrain_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_acrain_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_acrain_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"prcptp", label:"강수유형",
    patternByModel:{
        um_vdps: "vdps_rg15_prcptp_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"lowdbz", label:"레이더 반사도",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_lowdbz_ft01_pa4_s{fh}_{run}.png",
        um_klfs: "klfs_lc05_korea_lowdbz_ft01_pa4_s{fh}_{run}.png",
        um_vdps: "vdps_rg15_dpsimu_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", type:"header", label:"──────────────────"},
{category:"klfs_vdps", id:"ttd700", label:"700 습수(T-Td)",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_ttd700_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_ttd700_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_ttd700_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"anl850", label:"850 습수(T-Td)",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_anl850_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_anl850_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_ttd850_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"anl925", label:"925 습수(T-Td)",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_anl925_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_anl925_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_ttd925_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"anlsfc", label:"지상 습수(T-Td)",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_anlsfc_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_anlsfc_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_ttdsfc_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"moflux", label:"850 수분속",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_moflux_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_moflux_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_moistx_s{fh}_{run}.png"
    }
},

{category:"klfs_vdps", id:"div200", label:"200 발산",
    patternByModel:{
        um_vdps: "vdps_rg15_div200_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"con850", label:"850 수렴,풍속",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_con850_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_con850_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_con850_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"con925", label:"925 수렴,풍속",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_con925_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_con925_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_con925_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", type:"header", label:"──────────────────"},
{category:"klfs_vdps", id:"vel700", label:"700 상승속도",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_vel700_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_vel700_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_tempvv_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", type:"header", label:"──────────────────"},
{category:"klfs_vdps", id:"tmpwnd", label:"10m 바람, 2m 기온",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_tmpwnd_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_tmpwnd_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_sfctmp_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"sfcshm", label:"지상비습",
    patternByModel:{
        um_vdps: "vdps_rg15_sfcshm_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"visblt", label:"지상시정",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_visblt_ft01_pa4_s{fh}_{run}.png",
        um_klfs: "klfs_lc05_korea_visblt_ft01_pa4_s{fh}_{run}.png",
        um_vdps: "vdps_rg15_visblt_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", type:"header", label:"──────────────────"},
{category:"klfs_vdps", id:"kindex", label:"K-Index",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_kindex_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_kindex_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_kindex_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"sindex", label:"쇼월터 index",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_sindex_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_sindex_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_sindex_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"lindex", label:"Lifted index",
    patternByModel:{
        kim_klfs: "kim_klfs_lc05_korea_lindex_ft01_pa4_s{fh}_{run}.gif",
        um_klfs: "klfs_lc05_korea_lindex_ft01_pa4_s{fh}_{run}.gif",
        um_vdps: "vdps_rg15_lindex_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", type:"header", label:"──────────────────"},
{category:"klfs_vdps", id:"hghcld", label:"상층운량",
    patternByModel:{
        um_vdps: "vdps_rg15_hghcld_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"midcld", label:"중층운량",
    patternByModel:{
        um_vdps: "vdps_rg15_midcld_s{fh}_{run}.png"
    }
},
{category:"klfs_vdps", id:"lowcld", label:"하층운량",
    patternByModel:{
        um_vdps: "vdps_rg15_lowcld_s{fh}_{run}.png"
    }
},

/* 국지모델(한반도) */
{category:"lkor1", id:"tgcwnd", label:"지상기온",
    patternByModel:{
        kim_rdps: "kim_rdps_hkor_tgcwnd_s{fh}_{run}.png",
        kim_ldps: "kim_ldps_hkor_tgcwnd_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_tgcwnd_s{fh}_{run}.gif"
    }
},
{category:"lkor1", id:"grtopo", label:"지형과바람",
    patternByModel:{
        kim_rdps: "kim_rdps_hkor_grtopo_s{fh}_{run}.png",
        kim_ldps: "kim_ldps_hkor_grtopo_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_grtopo_s{fh}_{run}.gif"
    }
},
{category:"lkor1", id:"olwrad", label:"장파복사량",
    patternByModel:{
        kim_rdps: "kim_rdps_hkor_olwrad_s{fh}_{run}.png",
        kim_ldps: "kim_ldps_hkor_olwrad_s{fh}_{run}.png",
        um_ldps: "ldps_lc06_olwrad_s{fh}_{run}.gif"
    }
},
{category:"lkor1", id:"cldvlo", label:"최하층운량",
    patternByModel:{
        um_ldps: "ldps_lc06_cldvlo_s{fh}_{run}.gif"
    }
},
{category:"lkor1", id:"bltype", label:"경계층타입",
    patternByModel:{
        um_ldps: "ldps_lc06_bltype_s{fh}_{run}.gif"
    }
},
{category:"lkor1", id:"surfce", label:"해면기압,누적강수량",
    patternByModel:{
        kim_rdps: "kim_rdps_hkor_surfce_s{fh}_{run}.png",
        kim_ldps: "kim_ldps_hkor_surfce_s{fh}_{run}.png",
        um_ldps: "ldps_l1p5_surfce_s{fh}_{run}.gif"
    }
},
{category:"lkor1", id:"acrain", label:"총누적강수량",
    patternByModel:{
        um_ldps: "ldps_l1p5_acrain_s{fh}_{run}.gif"
    }
},

/* 국지모델(상세영역) */
{category:"lkor2", id:"surfce", label:"시간강수량",
    patternByModel:{
        kim_rdps: "kim_rdps_{detail}_surfce_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_{detail}_surfce_s{fh}_{run}.gif",
        um_ldps: "ldps_l1p5_{detail}_surfce_s{fh}_{run}.gif"
    },
    folderByModel:{
        kim_rdps:"KIMR2"
    },
},
{category:"lkor2", id:"acrain", label:"누적강수량",
    patternByModel:{
        kim_rdps: "kim_rdps_{detail}_acrain_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_{detail}_acrain_s{fh}_{run}.gif",
        um_ldps: "ldps_l1p5_{detail}_acrain_s{fh}_{run}.gif"
    },
    folderByModel:{
        kim_rdps:"KIMR2"
    },
},
{category:"lkor2", id:"tgcwnd", label:"지상기온",
    patternByModel:{
        kim_rdps: "kim_rdps_{detail}_tgcwnd_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_{detail}_tgcwnd_s{fh}_{run}.gif",
        um_ldps: "ldps_l1p5_{detail}_tgcwnd_s{fh}_{run}.gif"
    },
    folderByModel:{
        kim_rdps:"KIMR2"
    },
},
{category:"lkor2", id:"grtopo", label:"지형과바람",
    patternByModel:{
        kim_rdps: "kim_rdps_{detail}_grtopo_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_{detail}_grtopo_s{fh}_{run}.gif",
        um_ldps: "ldps_l1p5_{detail}_grtopo_s{fh}_{run}.gif"
    },
    folderByModel:{
        kim_rdps:"KIMR2"
    },
},
{category:"lkor2", id:"vrtwnd", label:"최하층연직속도",
    patternByModel:{
        kim_rdps: "kim_rdps_{detail}_vrtwnd_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_{detail}_vrtwnd_s{fh}_{run}.gif",
        um_ldps: "ldps_l1p5_{detail}_vrtwnd_s{fh}_{run}.gif"
    },
    folderByModel:{
        kim_rdps:"KIMR2"
    },
},
{category:"lkor2", id:"rmir", label:"구름모의영상",
    patternByModel:{
        kim_rdps: "kim_radm_rdps_l1p5_{detail}_gk2a_rmir_s{fh}_{run}.gif",
        um_ldps: "ldps_l1p5_{detail}_gk2a_rmir_s{fh}_{run}.gif"
    },
    forecastStepByModel:{
        kim_rdps:[
            {start:1,end:48,step:1}
        ]
    },
    folderByModel:{
        kim_rdps:"KIMA"
    },
},
{category:"lkor2", id:"gstwnd", label:"강풍(산불지원)",
    patternByModel:{
        kim_rdps: "kim_rdps_{detail}_gstwnd_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_{detail}_gstwnd_s{fh}_{run}.gif"
    },
    folderByModel:{
        kim_rdps:"KIMR2"
    },
},


/* 북반구예상 */
{category:"nhem", id:"surfce", label:"해면기압,강수량",
    patternByModel:{
        kim_gdps: "kim_nhem_ps60_surfce_s{fh}_{run}.png",
        um_gdps: "nhem_ps60_surfce_s{fh}_{run}.gif",
        ecmwf: "ecmw_nhem_ps60_surfce_s{fh}_{run}.gif"
    }
},
{category:"nhem", id:"gph500", label:"500hPa 고도,기온",
    patternByModel:{
        kim_gdps: "kim_nhem_ps60_gph500_s{fh}_{run}.png",
        um_gdps: "nhem_ps60_gph500_s{fh}_{run}.gif",
        ecmwf: "ecmw_nhem_ps60_gph500_s{fh}_{run}.gif"
    }
},
{category:"nhem", id:"dfh500", label:"500hPa 고도변화,기온",
    patternByModel:{
        kim_gdps: "kim_nhem_ps60_dfh500_s{fh}_{run}.png",
        um_gdps: "nhem_ps60_dfh500_s{fh}_{run}.gif",
        ecmwf: "ecmw_nhem_ps60_dfh500_s{fh}_{run}.gif"
    }
},
{category:"nhem", id:"dft500", label:"500hPa 고도,기온변화",
    patternByModel:{
        kim_gdps: "kim_nhem_ps60_dft500_s{fh}_{run}.png",
        um_gdps: "nhem_ps60_dft500_s{fh}_{run}.gif",
        ecmwf: "ecmw_nhem_ps60_dft500_s{fh}_{run}.gif"
    }
},
{category:"nhem", id:"dft850", label:"850hPa 고도,기온변화",
    patternByModel:{
        kim_gdps: "kim_nhem_ps60_dft850_s{fh}_{run}.png",
        um_gdps: "nhem_ps60_dft850_s{fh}_{run}.gif",
        ecmwf: "ecmw_nhem_ps60_dft850_s{fh}_{run}.gif"
    }
},
{category:"nhem", id:"ept850", label:"850hPa 고도,상당온위",
    patternByModel:{
        kim_gdps: "kim_nhem_ps60_ept850_s{fh}_{run}.png",
        um_gdps: "nhem_ps60_ept850_s{fh}_{run}.gif",
        ecmwf: "ecmw_nhem_ps60_ept850_s{fh}_{run}.gif"
    }
},
{category:"nhem", id:"mxr850", label:"850hPa 고도,혼합비",
    patternByModel:{
        kim_gdps: "kim_nhem_ps60_mxr850_s{fh}_{run}.png",
        um_gdps: "nhem_ps60_mxr850_s{fh}_{run}.gif",
        ecmwf: "ecmw_nhem_ps60_mxr850_s{fh}_{run}.gif"
    }
},
{category:"nhem", id:"gph850", label:"하층바람",
    patternByModel:{
        kim_gdps: "kim_nhem_ps60_gph850_s{fh}_{run}.png",
        um_gdps: "nhem_ps60_gph850_s{fh}_{run}.gif",
        ecmwf: "ecmw_nhem_ps60_gph850_s{fh}_{run}.gif"
    }
},
{category:"nhem", id:"gph200", label:"상층바람",
    patternByModel:{
        kim_gdps: "kim_nhem_ps60_gph200_s{fh}_{run}.png",
        um_gdps: "nhem_ps60_gph200_s{fh}_{run}.gif",
        ecmwf: "ecmw_nhem_ps60_gph200_s{fh}_{run}.gif"
    }
},


/* 구름모의영상 */
{category:"radm", id:"olwrad", label:"지구장파 복사량",
    patternByModel:{
        kim_gdps:[
            "kim_gdps_erly_asia_olwrad_ft06_pa4_s{fh}_{run}.png",
            "kim_gdps_erly_hkor_olwrad_s{fh}_{run}.png"
        ],
        um_gdps:[
            "gdps_erly_asia_olwrad_ft06_pa4_s{fh}_{run}.gif",
            "gdps_erly_hkor_olwrad_s{fh}_{run}.gif"
        ]
    }
},
{category:"radm", id:"rmir", label:"적외채널:천리안2A",
    patternByModel:{
        kim_gdps:[
            "kim_radm_gdps_asia_gk2a_lc05_rmir_s{fh}_{run}.png",
            "kim_radm_gdps_kor_gk2a_lc05_rmir_s{fh}_{run}.png"
        ],
        um_gdps:[
            "radm_gdps_asia_gk2a_lc05_rmir_s{fh}_{run}.gif",
            "radm_gdps_kor_gk2a_lc05_rmir_s{fh}_{run}.gif"
        ],
        kim_rdps:[
            "kim_radm_rdps_asia_gk2a_lc05_rmir_s{fh}_{run}.png",
            "kim_radm_rdps_gk2a_lc15_rmir_s{fh}_{run}.png"
        ],
        um_ldps:"radm_ldps_gk2a_lc15_rmir_s{fh}_{run}.png"
    },
    folderByModel:{
        kim_gdps:"KIMA",
        um_gdps:"APPM",
        kim_rdps:"KIMA",
        um_ldps:"APPM"
    },
    forecastStepByModel:{
        kim_gdps:[
            {start:0,end:12,step:1},
            {start:15,end:144,step:3}
        ],
        um_gdps:[
            {start:0,end:12,step:1},
            {start:15,end:144,step:3}
        ],
        kim_rdps:[
            {start:1,end:48,step:1}
        ]
    },
},
{category:"radm", id:"rmwv", label:"수증기채널:천리안2A",
    patternByModel:{
        kim_gdps:[
            "kim_radm_gdps_asia_gk2a_lc05_rmwv_s{fh}_{run}.png",
            "kim_radm_gdps_kor_gk2a_lc05_rmwv_s{fh}_{run}.png"
        ],
        um_gdps:[
            "radm_gdps_asia_gk2a_lc05_rmwv_s{fh}_{run}.gif",
            "radm_gdps_kor_gk2a_lc05_rmwv_s{fh}_{run}.gif"
        ],
        kim_rdps:[
            "kim_radm_rdps_asia_gk2a_lc05_rmwv_s{fh}_{run}.png",
            "kim_radm_rdps_gk2a_lc15_rmwv_s{fh}_{run}.png"
        ],
        um_ldps:"radm_ldps_gk2a_lc15_rmwv_s{fh}_{run}.png"
    },
    folderByModel:{
        kim_gdps:"KIMA",
        um_gdps:"APPM",
        kim_rdps:"KIMA",
        um_ldps:"APPM"
    },
    forecastStepByModel:{
        kim_gdps:[
            {start:0,end:12,step:1},
            {start:15,end:144,step:3}
        ],
        um_gdps:[
            {start:0,end:12,step:1},
            {start:15,end:144,step:3}
        ],
        kim_rdps:[
            {start:1,end:48,step:1}
        ]
    },
},

/* 등온위면분석 */
{category:"isen", id:"isen", label:"등온위면분석",
    patternByModel:{
        kim_gdps:[
            "kim_gdps_erly_isen_{detail}_s{fh}_{run}.gif",
            "kim_gdps_korea_isen_{detail}_s{fh}_{run}.gif"
        ],
        um_gdps:[
            "gdps_erly_isen_{detail}_s{fh}_{run}.gif",
            "gdps_korea_isen_{detail}_s{fh}_{run}.gif"
        ]
    }
},

/* 상세:바람기온 */
{category:"wtem1", id:"wsfc", label:"WTEM: 지상",
    patternByModel:{
        kim_gdps:"kim_gdps_lc40_wtem_wsfc_s{fh}_{run}.png",
        um_gdps:"gdps_lc40_wtem_wsfc_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_wtem_wsfc_s{fh}_{run}.gif",
        kim_rdps:"kim_rdps_hkor_wsfc_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_wtem_wsfc_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_hkor_wtsfc_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_hkor_wsfc_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        um_ldps:[
            {start:0,end:48,step:3},
        ]
    },
},
{category:"wtem1", id:"wt00", label:"WTEM: 1000hPa",
    patternByModel:{
        kim_gdps:"kim_gdps_lc40_wtem_wt00_s{fh}_{run}.png",
        um_gdps:"gdps_lc40_wtem_wt00_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_wtem_wt00_s{fh}_{run}.gif",
        kim_rdps:"kim_rdps_hkor_wt00_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_wtem_wt00_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_hkor_wt000_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_hkor_wt00_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        um_ldps:[
            {start:0,end:48,step:3},
        ]
    },
},
{category:"wtem1", id:"wt92", label:"WTEM: 925hPa",
    patternByModel:{
        kim_gdps:"kim_gdps_lc40_wtem_wt92_s{fh}_{run}.png",
        um_gdps:"gdps_lc40_wtem_wt92_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_wtem_wt92_s{fh}_{run}.gif",
        kim_rdps:"kim_rdps_hkor_wt92_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_wtem_wt92_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_hkor_wt925_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_hkor_wt92_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        um_ldps:[
            {start:0,end:48,step:3},
        ]
    },
},
{category:"wtem1", id:"wt85", label:"WTEM: 850hPa",
    patternByModel:{
        kim_gdps:"kim_gdps_lc40_wtem_wt85_s{fh}_{run}.png",
        um_gdps:"gdps_lc40_wtem_wt85_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_wtem_wt85_s{fh}_{run}.gif",
        kim_rdps:"kim_rdps_hkor_wt85_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_wtem_wt85_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_hkor_wt850_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_hkor_wt85_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        um_ldps:[
            {start:0,end:48,step:3},
        ]
    },
},    
{category:"wtem1", id:"wt70", label:"WTEM: 700hPa",
    patternByModel:{
        kim_gdps:"kim_gdps_lc40_wtem_wt70_s{fh}_{run}.png",
        um_gdps:"gdps_lc40_wtem_wt70_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_wtem_wt70_s{fh}_{run}.gif",
        kim_rdps:"kim_rdps_hkor_wt70_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_wtem_wt70_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_hkor_wt700_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_hkor_wt70_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        um_ldps:[
            {start:0,end:48,step:3},
        ]
    },
},
{category:"wtem1", id:"wt50", label:"WTEM: 500hPa",
    patternByModel:{
        kim_gdps:"kim_gdps_lc40_wtem_wt50_s{fh}_{run}.png",
        um_gdps:"gdps_lc40_wtem_wt50_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_wtem_wt50_s{fh}_{run}.gif",
        kim_rdps:"kim_rdps_hkor_wt50_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_wtem_wt50_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_hkor_wt500_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_hkor_wt50_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        um_ldps:[
            {start:0,end:48,step:3},
        ]
    },
},
{category:"wtem1", id:"wt30", label:"WTEM: 300hPa",
    patternByModel:{
        kim_gdps:"kim_gdps_lc40_wtem_wt30_s{fh}_{run}.png",
        um_gdps:"gdps_lc40_wtem_wt30_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_wtem_wt30_s{fh}_{run}.gif",
        kim_rdps:"kim_rdps_hkor_wt30_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_wtem_wt30_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_hkor_wt300_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_hkor_wt30_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        um_ldps:[
            {start:0,end:48,step:3},
        ]
    },
},
{category:"wtem1", id:"wt20", label:"WTEM: 200hPa",
    patternByModel:{
        kim_gdps:"kim_gdps_lc40_wtem_wt20_s{fh}_{run}.png",
        um_gdps:"gdps_lc40_wtem_wt20_s{fh}_{run}.gif",
        ecmwf: "ecmw_lc20_wtem_wt20_s{fh}_{run}.gif",
        kim_rdps:"kim_rdps_hkor_wt20_s{fh}_{run}.png",
        um_rdps: "rdps_lc30_wtem_wt20_ft03_pa4_s{fh}_{run}.gif",
        um_ldps: "ldps_hkor_wt200_s{fh}_{run}.gif",
        kim_ldps: "kim_ldps_hkor_wt20_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        um_ldps:[
            {start:0,end:48,step:3},
        ]
    },
},

/* 상세:바람기온(확장영역) */

{category:"wtem2", id:"wsfc", label:"WTEM-지상",
    patternByModel:{
        kim_gdps:[
            "kim_gdps_lc20_xkor_wtmsfc_s{fh}_{run}.png",
            "kim_gdps_lc20_xkor_strsfc_s{fh}_{run}.png"
        ],
        um_gdps:[
            "gdps_lc20_xkor_wtmsfc_s{fh}_{run}.gif",
            "gdps_lc20_xkor_strsfc_s{fh}_{run}.gif"
        ],
        ecmwf:[
            "ecmw_lc20_xkor_wtmsfc_s{fh}_{run}.gif",
            "ecmw_lc20_xkor_strsfc_s{fh}_{run}.gif"
        ],
    },
},
{category:"wtem2", id:"wt92", label:"WTEM-925hPa",
    patternByModel:{
        kim_gdps:[
            "kim_gdps_lc20_xkor_wtm925_s{fh}_{run}.png",
            "kim_gdps_lc20_xkor_str925_s{fh}_{run}.png"
        ],
        um_gdps:[
            "gdps_lc20_xkor_wtm925_s{fh}_{run}.gif",
            "gdps_lc20_xkor_str925_s{fh}_{run}.gif"
        ],
        ecmwf:[
            "ecmw_lc20_xkor_wtm925_s{fh}_{run}.gif",
            "ecmw_lc20_xkor_str925_s{fh}_{run}.gif"
        ],
    },
},
{category:"wtem2", id:"wt85", label:"WTEM-850hPa",
    patternByModel:{
        kim_gdps:[
            "kim_gdps_lc20_xkor_wtm850_s{fh}_{run}.png",
            "kim_gdps_lc20_xkor_str850_s{fh}_{run}.png"
        ],
        um_gdps:[
            "gdps_lc20_xkor_wtm850_s{fh}_{run}.gif",
            "gdps_lc20_xkor_str850_s{fh}_{run}.gif"
        ],
        ecmwf:[
            "ecmw_lc20_xkor_wtm850_s{fh}_{run}.gif",
            "ecmw_lc20_xkor_str850_s{fh}_{run}.gif"
        ],
    },
},
{category:"wtem2", id:"wt70", label:"WTEM-700hPa",
    patternByModel:{
        kim_gdps:[
            "kim_gdps_lc20_xkor_wtm700_s{fh}_{run}.png",
            "kim_gdps_lc20_xkor_str700_s{fh}_{run}.png"
        ],
        um_gdps:[
            "gdps_lc20_xkor_wtm700_s{fh}_{run}.gif",
            "gdps_lc20_xkor_str700_s{fh}_{run}.gif"
        ],
        ecmwf:[
            "ecmw_lc20_xkor_wtm700_s{fh}_{run}.gif",
            "ecmw_lc20_xkor_str700_s{fh}_{run}.gif"
        ],
    },
},
{category:"wtem2", id:"wt50", label:"WTEM-500hPa",
    patternByModel:{
        kim_gdps:[
            "kim_gdps_lc20_xkor_wtm500_s{fh}_{run}.png",
            "kim_gdps_lc20_xkor_str500_s{fh}_{run}.png"
        ],
        um_gdps:[
            "gdps_lc20_xkor_wtm500_s{fh}_{run}.gif",
            "gdps_lc20_xkor_str500_s{fh}_{run}.gif"
        ],
        ecmwf:[
            "ecmw_lc20_xkor_wtm500_s{fh}_{run}.gif",
            "ecmw_lc20_xkor_str500_s{fh}_{run}.gif"
        ],
    },
},
{category:"wtem2", id:"wt20", label:"WTEM-200~300hPa",
    patternByModel:{
        kim_gdps:[
            "kim_gdps_lc20_xkor_wtm200_s{fh}_{run}.png",
            "kim_gdps_lc20_xkor_str200_s{fh}_{run}.png"
        ],
        um_gdps:[
            "gdps_lc20_xkor_wtm200_s{fh}_{run}.gif",
            "gdps_lc20_xkor_str200_s{fh}_{run}.gif"
        ],
        ecmwf:[
            "ecmw_lc20_xkor_wtm200_s{fh}_{run}.gif",
            "ecmw_lc20_xkor_str200_s{fh}_{run}.gif"
        ],
    },
},

/* 예상단열선도 */
{category:"skew", id:"skew", label:"예상단열선도",
    patternByModel:{
        kim_gdps:"kim_gdps_skew_{detail}_s{fh}_{run}.png",
        um_gdps:"gdps_skew_{detail}_s{fh}_{run}.gif",
        ecmwf:"ecmw_skew_{detail}_s{fh}_{run}.gif",
        kim_rdps:"kim_rdps_skew_{detail}_s{fh}_{run}.png",
        um_rdps:"rdps_skew_{detail}_s{fh}_{run}.gif",
        kwrf_rdps:"kwrf_skew_{detail}_s{fh}_{run}.gif",
        kim_ldps:"kim_ldps_skew_{detail}_s{fh}_{run}.png",
        um_ldps:"ldps_skew_{detail}_s{fh}_{run}.gif"
    },
    folderByModel:{
        kim_rdps:"KIMR3"
    },
},

/* 연직시계열 */
{category:"city", id:"shrt", label:"단기",
    patternByModel:{
        kim_gdps:"kim_gdps_erly_city_{detail}_t072_{run}.png",
        um_gdps:"gdps_erly_city_{detail}_t072_{run}.gif",
        ecmwf:"ecmw_city_{detail}_t072_{run}.gif",
        kim_rdps:"kim_rdps_erly_city_{detail}_t072_{run}.png",
        um_rdps:"rdps_lc30_city_{detail}_pa4_{run}.gif",
        kwrf_rdps:"kwrf_lc10_city_{detail}_pa4_{run}.gif",
        kim_ldps:"kim_ldps_erly_city_{detail}_t048_{run}.png",
        um_ldps:"ldps_l1p5_city_{detail}_{run}.gif"
    }
},
{category:"city", id:"long", label:"중기",
    patternByModel:{
        kim_gdps:"kim_gdps_erly_city_{detail}_pa4_{run}.png",
        um_gdps:"gdps_erly_city_{detail}_pa4_{run}.gif",
        ecmwf:"ecmw_city_{detail}_t240_{run}.gif"
    }
},


];