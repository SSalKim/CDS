const ENSEMBLE_CATEGORIES=[
{id:"srf3",name:"EPS: EPSgram(단기:5.5일)"},
{id:"mrf6",name:"EPS: EPSgram(중기:12일)"},
{id:"lrf6",name:"EPS: EPSgram(중기:15일)"},
{id:"trd3",name:"EPS: 예측경향(단기:5.5일)"},
{id:"trd6",name:"EPS: 예측경향(중기:12일)"},
{id:"prob",name:"EPS: 예측경향(강수확률분포)"},
{type:"header", name:"─────────────────"},
{id:"mp03",name:"EPS: 강수량(단기 3.5일)"},
{id:"mp06",name:"EPS: 강수량(단기 5.5일)"},
{id:"days",name:"EPS: 강수량(단기예보용)"},
{id:"mpda",name:"EPS: 강수량(중기)"},
{id:"prep",name:"EPS: 강수확률"},
{id:"snwp",name:"EPS: 강설확률"},
{type:"header", name:"─────────────────"},
{id:"efie",name:"EPS: 극값예측지수(EFI)"},
{id:"stdv",name:"EPS: 평균/편차"},
{id:"spgt",name:"EPS: 스파게티"},
{id:"stmp",name:"EPS: Stamp map"},
{id:"nhem",name:"EPS: 북반구일기도"},
{id:"week",name:"EPS: 앙상블-주간예보"},
{id:"cnf1",name:"EPS: 주간강수신뢰도(일)"},
{id:"cnf2",name:"EPS: 주간강수신뢰도(오전/오후)"},
{type:"header", name:"─────────────────"},
{id:"metg",name:"LENS: EPSgram(단기:3일)"},
{id:"rn03",name:"LENS: 강수량(3시간)"},
{id:"rn12",name:"LENS: 강수량(12시간)"},
{id:"rday",name:"LENS: 강수량(단기예보용)"},
{id:"pm03",name:"LENS: 강수량(확률매칭:3시간)"},
{id:"pm01",name:"LENS: 강수량(확률매칭:1시간)"},
{id:"prn3",name:"LENS: 강수확률(3시간)"},
{id:"prn1",name:"LENS: 강수확률(1시간)"},
{id:"psn3",name:"LENS: 강설확률(3시간)"},
{id:"psn1",name:"LENS: 강설확률(1시간)"},
{id:"pvis",name:"LENS: 시정확률(1시간)"},
{id:"fogf",name:"LENS: 시정확률-안개분율"},
{id:"pgst",name:"LENS: 강풍확률-강풍가이던스"},
{id:"mwnd",name:"LENS: 강풍확률-평균(mean)"},
{id:"sprd",name:"LENS: 평균/편차"}
];


const ENSEMBLE_PRODUCTS=[
/* GENS (EPSG) */
{category:"srf3",id:"srf3",label:"EPSgram(단기:5.5일)",
    patternByModel:{
        kim_epsg:"kim_epsg_srf3_{detail}_{run}.png",
        um_epsg:"epsg_srf3_{detail}_{run}.gif",
        ecmwf_eps:"ecmw_epss_{detail}_{run}.gif",
    }
},
{category:"mrf6",id:"mrf6",label:"EPSgram(중기:12일)",
    patternByModel:{
        kim_epsg:"kim_epsg_mrf6_{detail}_{run}.png",
        um_epsg:"epsg_mrf6_{detail}_{run}.gif",
        ecmwf_eps:"ecmw_epsg_{detail}_{run}.gif",
    }
},
{category:"lrf6",id:"lrf6",label:"EPSgram(중기:15일)",
    patternByModel:{
        kim_epsg:"kim_epsg_lrf6_{detail}_{run}.png",
        ecmwf_eps:"ecmw_epsx_{detail}_{run}.gif",
    }
},
{category:"trd3",id:"prcp",label:"강수",
    patternByModel:{
        kim_epsg:"kim_epsg_trnd_srf3_prcp_{detail}_{run}.png",
        um_epsg:"epsg_trnd_srf3_prcp_{detail}_{run}.gif",
        ecmwf_eps:"ecmw_epss_prcp_{detail}_{run}.gif",
    }
},
{category:"trd3",id:"tsfc",label:"기온",
    patternByModel:{
        kim_epsg:"kim_epsg_trnd_srf3_tsfc_{detail}_{run}.png",
        um_epsg:"epsg_trnd_srf3_tsfc_{detail}_{run}.gif",
        ecmwf_eps:"ecmw_epss_tsfc_{detail}_{run}.gif",
    }
},
{category:"trd3",id:"tcld",label:"운량",
    patternByModel:{
        kim_epsg:"kim_epsg_trnd_srf3_tcld_{detail}_{run}.png",
        um_epsg:"epsg_trnd_srf3_tcld_{detail}_{run}.gif",
        ecmwf_eps:"ecmw_epss_tcld_{detail}_{run}.gif",
    }
},
{category:"trd3",id:"wsfc",label:"풍속",
    patternByModel:{
        kim_epsg:"kim_epsg_trnd_srf3_wsfc_{detail}_{run}.png",
        um_epsg:"epsg_trnd_srf3_wsfc_{detail}_{run}.gif",
        ecmwf_eps:"ecmw_epss_wsfc_{detail}_{run}.gif",
    }
},
{category:"trd6",id:"prcp",label:"강수",
    patternByModel:{
        kim_epsg:"kim_epsg_trnd_mrf6_prcp_{detail}_{run}.png",
        um_epsg:"epsg_trnd_mrf6_prcp_{detail}_{run}.gif",
        ecmwf_eps:"ecmw_epsg_prcp_{detail}_{run}.gif",
    }
},
{category:"trd6",id:"tsfc",label:"기온",
    patternByModel:{
        kim_epsg:"kim_epsg_trnd_mrf6_tsfc_{detail}_{run}.png",
        um_epsg:"epsg_trnd_mrf6_tsfc_{detail}_{run}.gif",
        ecmwf_eps:"ecmw_epsg_tsfc_{detail}_{run}.gif",
    }
},
{category:"trd6",id:"tcld",label:"운량",
    patternByModel:{
        kim_epsg:"kim_epsg_trnd_mrf6_tcld_{detail}_{run}.png",
        um_epsg:"epsg_trnd_mrf6_tcld_{detail}_{run}.gif",
        ecmwf_eps:"ecmw_epsg_tcld_{detail}_{run}.gif",
    }
},
{category:"trd6",id:"wsfc",label:"풍속",
    patternByModel:{
        kim_epsg:"kim_epsg_trnd_mrf6_wsfc_{detail}_{run}.png",
        um_epsg:"epsg_trnd_mrf6_wsfc_{detail}_{run}.gif",
        ecmwf_eps:"ecmw_epsg_wsfc_{detail}_{run}.gif",
    }
},
{category:"prob",id:"prob",label:"예측경향(강수확률분포)",
    patternByModel:{
        um_epsg:[
            "epsg_trend_prob_6hprec_{detail}_{run}.gif",
            "epsg_trend_2_prob_6hprec_{detail}_{run}.gif",
        ]
    }
},
{category:"mp03",id:"mp03",label:"강수량(단기 3.5일)",
    patternByModel:{
        kim_epsg:"kim_epsg_mp03_{detail}_{run}.png",
        um_epsg:"epsg_mp03_{detail}_{run}.gif",
        ecmwf_eps:"ecmw_epsg_mp03_{detail}_{run}.gif",
    }
},
{category:"mp06",id:"mp06",label:"강수량(단기 5.5일)",
    patternByModel:{
        kim_epsg:"kim_epsg_mp06_{detail}_{run}.png",
        um_epsg:"epsg_mp06_{detail}_{run}.gif",
        ecmwf_eps:"ecmw_epsg_mp06_{detail}_{run}.gif",
    }
},
{category:"days",id:"days",label:"강수량(단기예보용)",
    patternByModel:{
        kim_epsg:"kim_epsg_rain_days_{detail}_{run}.png",
        um_epsg:"epsg_rain_days_{detail}_{run}.png",
        ecmwf_eps:"ecmw_epsg_rain_days_{detail}_{run}.png",
    }
},
{category:"mpda",id:"mpda",label:"강수량(중기)",
    patternByModel:{
        kim_epsg:"kim_epsg_mpda_{detail}_{run}.png",
        um_epsg:"epsg_mpda_{detail}_{run}.gif",
        ecmwf_eps:"ecmw_epsg_mpda_{detail}_{run}.gif",
    }
},
{category:"prep",id:"prep",label:"강수확률",
    patternByModel:{
        kim_epsg:"kim_epsg_prob_rain_{detail}_s{fh}_{run}.png",
        um_epsg:"epsg_prob_prec_{detail}_s{fh}_{run}.gif"
    }
},
{category:"snwp",id:"snwp",label:"강설확률",
    patternByModel:{
        kim_epsg:"kim_epsg_prob_snow_s{fh}_{run}.png",
        um_epsg:"epsg_prob_snow_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_epsg:[
            {start:15,end:255,step:24},
        ],
        um_epsg:[
            {start:15,end:255,step:24},
        ]
    },
},
{category:"efie",id:"efie",label:"극값예측지수(EFI)",
    patternByModel:{
        um_epsg:"epsg_extn_efi_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        um_epsg:[
            {start:15,end:255,step:24},
        ]
    },
},
{category:"stdv",id:"mslp",label:"동아시아 해면기압",
    patternByModel:{
        kim_epsg:"kim_epsg_stdv_mslp_s{fh}_{run}.png",
        um_epsg:"epsg_stdv_mslp_s{fh}_{run}.gif",
        ecmwf_eps:"ecmw_epsg_sprd_mslp_s{fh}_{run}.gif"
    },
    forecastStepByModel:{
        ecmwf_eps:[
            {start:6,end:240,step:6},
        ]
    }
},
{category:"stdv",id:"h500",label:"500hPa 고도",
    patternByModel:{
        kim_epsg:"kim_epsg_stdv_h500_s{fh}_{run}.png",
        um_epsg:"epsg_stdv_h500_s{fh}_{run}.gif",
        ecmwf_eps:"ecmw_epsg_sprd_h500_s{fh}_{run}.gif"
    },
    forecastStepByModel:{
        ecmwf_eps:[
            {start:6,end:240,step:6},
        ]
    }
},
{category:"stdv",id:"t850",label:"850hPa 기온",
    patternByModel:{
        kim_epsg:"kim_epsg_stdv_t850_s{fh}_{run}.png",
        um_epsg:"epsg_stdv_t850_s{fh}_{run}.gif",
        ecmwf_eps:"ecmw_epsg_sprd_t850_s{fh}_{run}.gif"
    },
    forecastStepByModel:{
        ecmwf_eps:[
            {start:6,end:240,step:6},
        ]
    }
},
{category:"stdv",id:"et85",label:"850hPa 상당온위",
    patternByModel:{
        kim_epsg:"kim_epsg_stdv_et85_s{fh}_{run}.png",
        um_epsg:"epsg_stdv_et85_s{fh}_{run}.gif"
    }
},
{category:"stdv",id:"tpwa",label:"가강수량",
    patternByModel:{
        kim_epsg:"kim_epsg_stdv_tpwa_s{fh}_{run}.png",
        um_epsg:"epsg_stdv_tpwa_s{fh}_{run}.gif"
    }
},
{category:"spgt",id:"spgt",label:"스파게티",
    patternByModel:{
        kim_epsg:"kim_epsg_stdv_spgt_{detail}_s{fh}_{run}.png",
        um_epsg:"epsg_stdv_spgt_{detail}_s{fh}_{run}.gif",
        ecmwf_eps:"ecmw_stdv_spgt_{detail}_s{fh}_{run}.gif"
    },
    forecastStepByModel:{
        ecmwf_eps:[
            {start:6,end:240,step:6},
        ]
    }
},
{category:"stmp",id:"mslp",label:"해면기압, 6시간 누적강수량",
    patternByModel:{
        kim_epsg:"kim_epsg_stamp_mslp_no1_s{fh}_{run}.png",
        um_epsg:"epsg_stamp_mslp_no1_s{fh}_{run}.gif"
    }
},
{category:"stmp",id:"h500",label:"500hPa 고도",
    patternByModel:{
        kim_epsg:"kim_epsg_stamp_h500_no1_s{fh}_{run}.png",
        um_epsg:"epsg_stamp_h500_no1_s{fh}_{run}.gif"
    }
},
{category:"nhem",id:"stdv",label:"500hPa 고도: 평균/편차",
    patternByModel:{
        kim_epsg:"kim_epsg_nhem_spgt_mean_s{fh}_{run}.png",
        um_epsg:"epsg_nhem_spgt_mean_s{fh}_{run}.gif"
    }
},
{category:"nhem",id:"spgt",label:"500hPa 고도: 스파게티/편차",
    patternByModel:{
        kim_epsg:"kim_epsg_nhem_spgt_{detail}_s{fh}_{run}.png",
        um_epsg:"epsg_nhem_spgt_{detail}_s{fh}_{run}.gif"
    }
},
{category:"week",id:"week",label:"앙상블-주간예보",
    patternByModel:{
        um_epsg:"cmpr_week_epsg_{run}.gif"
    },
    folderByModel:{
        um_epsg:"EXTJ"
    },
},
{category:"cnf1",id:"tabl",label:"도시-주간강수신뢰도(일)",
    patternByModel:{
        um_epsg:"epsg_rain_conf_tabl_{run}.gif"
    }
},
{category:"cnf1",id:"area",label:"공간-일일 강수확률",
    patternByModel:{
        um_epsg:"epsg_rain_conf_area_{detail}_{run}.gif"
    }
},
{category:"cnf2",id:"tb12",label:"도시-주간강수신뢰도(오전/오후)",
    patternByModel:{
        um_epsg:"epsg_rain_conf_tb12_{run}.gif"
    }
},
{category:"cnf2",id:"ar12",label:"공간-오전/오후 강수확률",
    patternByModel:{
        um_epsg:"epsg_rain_conf_12hr_{detail}_{run}.gif"
    }
},

/* LENS */

{category:"metg",id:"metg",label:"EPSgram(단기:3일)",
    patternByModel:{
        kim_lens:"kim_lens_metg_{detail}_{run}.png",
        um_lens:"lens_metg_{detail}_{run}.png"
    }
},
{category:"rn03",id:"rn03",label:"강수량(3시간)",
    patternByModel:{
        kim_lens:"kim_lens_dist_prcp_03h_{detail}_{run}.png",
        um_lens:"lens_dist_prcp_03h_{detail}_{run}.png"
    }
},
{category:"rn12",id:"rn12",label:"강수량(12시간)",
    patternByModel:{
        kim_lens:"kim_lens_dist_prcp_12h_{detail}_{run}.png",
        um_lens:"lens_dist_prcp_12h_{detail}_{run}.png"
    }
},
{category:"rday",id:"rday",label:"강수량(단기예보용)",
    patternByModel:{
        kim_lens:"kim_lens_dist_prcp_day_{detail}_{run}.png",
        um_lens:"lens_dist_prcp_day_{detail}_{run}.png"
    }
},
{category:"pm03",id:"pm03",label:"강수량(확률매칭:3시간)",
    patternByModel:{
        kim_lens:"kim_lens_pm_prcp_03h_no01_s{fh}_{run}.png",
        um_lens:"lens_pm_prcp_03h_no01_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_lens:[
            {start:6,end:120,step:3},
        ],
        um_lens:[
            {start:6,end:72,step:3},
        ],
    }
},
{category:"pm01",id:"pm01",label:"강수량(확률매칭:1시간)",
    patternByModel:{
        kim_lens:"kim_lens_pm_prcp_01h_no01_s{fh}_{run}.png",
        um_lens:"lens_pm_prcp_01h_no01_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_lens:[
            {start:4,end:120,step:1},
        ],
        um_lens:[
            {start:4,end:72,step:1},
        ],
    },
    archiveStartByModel:{
        kim_lens:"2023-07-20"
    },
},
{category:"prn3",id:"prn3",label:"강수확률(3시간)",
    patternByModel:{
        kim_lens:"kim_lens_prob_prcp_03h_{detail}_s{fh}_{run}.png",
        um_lens:"lens_prob_prcp_03h_{detail}_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_lens:[
            {start:6,end:120,step:3},
        ],
        um_lens:[
            {start:6,end:72,step:3},
        ],
    }
},
{category:"prn1",id:"prn1",label:"강수확률(1시간)",
    patternByModel:{
        kim_lens:"kim_lens_prob_prcp_01h_{detail}_s{fh}_{run}.png",
        um_lens:"lens_prob_prcp_01h_{detail}_s{fh}_{run}.png"
    },
    archiveStartByModel:{
        kim_lens:"2023-07-20"
    },
    forecastStepByModel:{
        kim_lens:[
            {start:4,end:120,step:1},
        ],
        um_lens:[
            {start:4,end:72,step:1},
        ],
    }
},
{category:"psn3",id:"psn3",label:"강설확률(3시간)",
    patternByModel:{
        kim_lens:"kim_lens_prob_snow_03h_{detail}_s{fh}_{run}.png",
        um_lens:"lens_prob_snow_03h_{detail}_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_lens:[
            {start:6,end:120,step:3},
        ],
        um_lens:[
            {start:6,end:72,step:3},
        ],
    }
},
{category:"psn1",id:"psn1",label:"강설확률(1시간)",
    patternByModel:{
        kim_lens:"kim_lens_prob_snow_01h_{detail}_s{fh}_{run}.png",
        um_lens:"lens_prob_snow_01h_{detail}_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_lens:[
            {start:4,end:120,step:1},
        ],
        um_lens:[
            {start:4,end:72,step:1},
        ],
    }
},
{category:"pvis",id:"pvis",label:"시정확률",
    patternByModel:{
        kim_lens:"kim_lens_prob_visi_01h_{detail}_s{fh}_{run}.png",
        um_lens:"lens_prob_visi_01h_{detail}_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_lens:[
            {start:4,end:120,step:1},
        ],
        um_lens:[
            {start:4,end:72,step:1},
        ],
    }
},
{category:"fogf",id:"fogf",label:"안개분율",
    patternByModel:{
        um_lens:"lens_frac_fog_01h_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        um_lens:[
            {start:4,end:72,step:1},
        ],
    }
},
{category:"pgst",id:"pgst",label:"강풍가이던스",
    patternByModel:{
        kim_lens:"kim_lens_prob_gust_01h_s{fh}_{run}.png",
        um_lens:"lens_prob_gust_01h_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_lens:[
            {start:4,end:120,step:1},
        ],
        um_lens:[
            {start:4,end:72,step:1},
        ],
    }
},
{category:"mwnd",id:"mwnd",label:"평균(mean)",
    patternByModel:{
        kim_lens:"kim_lens_mean_wind_01h_s{fh}_{run}.png",
        um_lens:"lens_mean_wind_01h_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_lens:[
            {start:4,end:120,step:1},
        ],
        um_lens:[
            {start:4,end:72,step:1},
        ],
    }
},
{category:"sprd",id:"temp",label:"기온",
    patternByModel:{
        kim_lens:"kim_lens_stdv_temp_01h_s{fh}_{run}.png",
        um_lens:"lens_stdv_temp_01h_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_lens:[
            {start:4,end:120,step:1},
        ],
        um_lens:[
            {start:4,end:72,step:1},
        ],
    }
},
{category:"sprd",id:"mslp",label:"해면기압",
    patternByModel:{
        kim_lens:"kim_lens_stdv_mslp_01h_s{fh}_{run}.png",
        um_lens:"lens_stdv_mslp_01h_s{fh}_{run}.png"
    },
    forecastStepByModel:{
        kim_lens:[
            {start:3,end:120,step:1},
        ],
        um_lens:[
            {start:3,end:72,step:1},
        ],
    }
},

];


const ENSEMBLE_DEFAULT_PRODUCT_BY_CATEGORY={

srf3:'srf3'

};


const ENSEMBLE_PRODUCT_CATEGORY_UI_CONFIG={
srf3:{hideProductSelect:true},
mrf6:{hideProductSelect:true},
lrf6:{hideProductSelect:true},
prob:{hideProductSelect:true},
mp03:{hideProductSelect:true},
mp06:{hideProductSelect:true},
days:{hideProductSelect:true},
mpda:{hideProductSelect:true},
prep:{hideProductSelect:true},
snwp:{hideProductSelect:true},
efie:{hideProductSelect:true},
spgt:{hideProductSelect:true},
metg:{hideProductSelect:true},
rn03:{hideProductSelect:true},
rn12:{hideProductSelect:true},
rday:{hideProductSelect:true},
pm03:{hideProductSelect:true},
pm01:{hideProductSelect:true},
prn3:{hideProductSelect:true},
prn1:{hideProductSelect:true},
psn3:{hideProductSelect:true},
psn1:{hideProductSelect:true},
pvis:{hideProductSelect:true},
fogf:{hideProductSelect:true},
pgst:{hideProductSelect:true},
mwnd:{hideProductSelect:true}
};


const ENSEMBLE_CATEGORY_MODEL_RESTRICTIONS={

};


const ENSEMBLE_SELECTION_MODEL_RESTRICTIONS={

};


const ENSEMBLE_AUX_SELECTOR_CONFIG={


};