const ANALYSIS_CATEGORIES=[

{id:"asia",name:"분석일기도"},
{id:"hkor",name:"분석일기도(한반도)"},
{id:"typh",name:"분석일기도(태풍영역)"},
{id:"kas0",name:"분석장 영역 일기도"},
{type:"header", name:"─────────────────"},
{id:"axas",name:"보조분석도"},
{id:"nhem",name:"북반구분석도"},
{type:"header", name:"─────────────────"},
{id:"rain24",name:"24시간강수"},
{type:"header", name:"─────────────────"},
{id:"skewan",name:"분석단열선도"},
{id:"skewob",name:"관측단열선도"},
{id:"skewds",name:"하강단열선도"},
{type:"header", name:"─────────────────"},
{id:"grtopo",name:"지형과바람"},
{type:"header", name:"─────────────────"},
{id:"dust",name:"황사일기도"},

];

const HOURLY_CYCLES=[
0,1,2,3,4,5,6,7,8,9,10,11,
12,13,14,15,16,17,18,19,20,21,22,23
];

const THREE_HOUR_CYCLES=[0,3,6,9,12,15,18,21];
const TWELVE_HOUR_CYCLES=[0,12];

const ANALYSIS_PRODUCTS=[

{category:"asia",id:"sfc3",label:"3시간:지상",
    cycles:THREE_HOUR_CYCLES,
    patternByModel:{
        kim_anal:"kim_sfc3_anlden_pb4_{run}.gif",
        um_anal:"sfc3_anlden_pb4_{run}.gif"
    }
},
{category:"asia",id:"sfc3_ptrend",label:"3시간:기압변화",
    cycles:THREE_HOUR_CYCLES,
    patternByModel:{
        kim_anal:"kim_sfc3_ptrend_pb4_{run}.gif",
        um_anal:"sfc3_ptrend_pb4_{run}.gif"
    }
},
{category:"asia",id:"sfc1",label:"1시간:지상",
    patternByModel:{
        kas:"kas0_sfc3_anlden_pb4_{run}.gif",
    }
},
{category:"asia",id:"sfc1_ptrend",label:"1시간:기압변화",
    patternByModel:{
        kas:"kas0_sfc3_ptrend_pb4_{run}.gif",
    }
},
{category:"asia",id:"surf",label:"지상일기도",
    patternByModel:{
        kim_anal:"kim_surf_anlmod_pb4_{run}.gif",
        um_anal:"surf_anlmod_pb4_{run}.gif",
        ecmwf_ra:"surf_anlmod_pb4_{run}.png",
        kas:"kas0_surf_anlmod_pb4_{run}.gif",
    }
},
{category:"asia",id:"surf2",label:"지상일기도(2hPa)",
    patternByModel:{
        kim_anal:"kim_surf_anlmo2_pb4_{run}.gif",
        um_anal:"surf_anlmo2_pb4_{run}.gif",
        kas:"kas0_surf_anlmo2_pb4_{run}.gif",
    }
},
{category:"asia",id:"up92",label:"고층:925hPa",
    patternByModel:{
        kim_anal:"kim_up92_anlmod_pb4_{run}.gif",
        um_anal:"up92_anlmod_pb4_{run}.gif",
        ecmwf_ra:"up92_anlmod_pb4_{run}.png",
        kas:"kas0_up92_anlmod_pb4_{run}.gif",
    }
},
{category:"asia",id:"up85",label:"고층:850hPa",
    patternByModel:{
        kim_anal:"kim_up85_anlmod_pb4_{run}.gif",
        um_anal:"up85_anlmod_pb4_{run}.gif",
        ecmwf_ra:"up85_anlmod_pb4_{run}.png",
        kas:"kas0_up85_anlmod_pb4_{run}.gif",
    }
},
{category:"asia",id:"up70",label:"고층:700hPa",
    patternByModel:{
        kim_anal:"kim_up70_anlmod_pb4_{run}.gif",
        um_anal:"up70_anlmod_pb4_{run}.gif",
        ecmwf_ra:"up70_anlmod_pb4_{run}.png",
        kas:"kas0_up70_anlmod_pb4_{run}.gif",
    }
},
{category:"asia",id:"up50",label:"고층:500hPa",
    patternByModel:{
        kim_anal:"kim_up50_anlmod_pb4_{run}.gif",
        um_anal:"up50_anlmod_pb4_{run}.gif",
        ecmwf_ra:"up50_anlmod_pb4_{run}.png",
        kas:"kas0_up50_anlmod_pb4_{run}.gif",
    }
},
{category:"asia",id:"up30",label:"고층:300hPa",
    patternByModel:{
        kim_anal:"kim_up30_anlmod_pb4_{run}.gif",
        um_anal:"up30_anlmod_pb4_{run}.gif",
        ecmwf_ra:"up30_anlmod_pb4_{run}.png",
        kas:"kas0_up30_anlmod_pb4_{run}.gif",
    }
},
{category:"asia",id:"up20",label:"고층:200hPa",
    patternByModel:{
        kim_anal:"kim_up20_anlmod_pb4_{run}.gif",
        um_anal:"up20_anlmod_pb4_{run}.gif",
        ecmwf_ra:"up20_anlmod_pb4_{run}.png",
        kas:"kas0_up20_anlmod_pb4_{run}.gif",
    }
},
{category:"asia",id:"up10",label:"고층:100hPa",
    patternByModel:{
        kim_anal:"kim_up10_anlmod_pb4_{run}.gif",
        um_anal:"up10_anlmod_pb4_{run}.gif",
        ecmwf_ra:"up10_anlmod_pb4_{run}.png",
        kas:"kas0_up10_anlmod_pb4_{run}.gif",
    }
},

/* 분석일기도(한반도) */

{category:"hkor",id:"anlmod",label:"한반도:기압",
    patternByModel:{
        kim_anal:"kim_kor1_anlmod_pb4_{run}.gif",
        um_anal:"kor1_anlmod_pb4_{run}.gif",
        kas:"kas0_kor1_anlmod_pb4_{run}.gif",
    },
    cyclesByModel:{
        kim_anal:HOURLY_CYCLES,
        um_anal:HOURLY_CYCLES,
    }
},
{category:"hkor",id:"ptrend",label:"한반도:기압변화",
    patternByModel:{
        kim_anal:"kim_kor1_ptrend_pb4_{run}.gif",
        um_anal:"kor1_ptrend_pb4_{run}.gif",
    },
    cyclesByModel:{
        kim_anal:HOURLY_CYCLES,
        um_anal:HOURLY_CYCLES,
    }
},
{category:"hkor",id:"slptmp",label:"한반도:기압/온위",
    patternByModel:{
        kim_anal:"kim_kor1_slptmp_pb4_{run}.gif",
        um_anal:"kor1_slptmp_pb4_{run}.gif",
        kas:"kas0_kor1_slptmp_pb4_{run}.gif",
    },
    cyclesByModel:{
        kim_anal:HOURLY_CYCLES,
        um_anal:HOURLY_CYCLES,
    }
},
{category:"hkor",id:"spdmod",label:"한반도:바람벡터",
    patternByModel:{
        kim_anal:"kim_kor1_spdmod_pb4_{run}.gif",
        um_anal:"kor1_spdmod_pb4_{run}.gif",
    },
    cyclesByModel:{
        kim_anal:HOURLY_CYCLES,
        um_anal:HOURLY_CYCLES,
    }
},
{category:"hkor",id:"rhumod",label:"한반도:유선/습도",
    patternByModel:{
        kim_anal:"kim_kor1_rhumod_pb4_{run}.gif",
        um_anal:"kor1_rhumod_pb4_{run}.gif",
        kas:"kas0_kor1_rhumod_pb4_{run}.gif",
    },
    cyclesByModel:{
        kim_anal:HOURLY_CYCLES,
        um_anal:HOURLY_CYCLES,
    }
},
{category:"hkor",id:"divmod",label:"한반도:수렴/발산",
    patternByModel:{
        kim_anal:"kim_kor1_divmod_pb4_{run}.gif",
        um_anal:"kor1_divmod_pb4_{run}.gif"
    },
    cyclesByModel:{
        kim_anal:HOURLY_CYCLES,
        um_anal:HOURLY_CYCLES,
    }
},

/* 분석일기도(태풍영역) */

{category:"typh",id:"sfc3",label:"3시간:지상",
    cycles:THREE_HOUR_CYCLES,
    patternByModel:{
        kim_anal:"kim_sfc3_anlden_typh_pb4_{run}.gif",
        um_anal:"sfc3_anlden_typh_pb4_{run}.gif"
    }
},
{category:"typh",id:"sfc3_ptrend",label:"3시간:기압변화",
    cycles:THREE_HOUR_CYCLES,
    patternByModel:{
        kim_anal:"kim_sfc3_ptrend_typh_pb4_{run}.gif",
        um_anal:"sfc3_ptrend_typh_pb4_{run}.gif"
    }
},
{category:"typh",id:"surf",label:"지상일기도",
    patternByModel:{
        kim_anal:"kim_surf_anlmod_typh_pb4_{run}.gif",
        um_anal:"surf_anlmod_typh_pb4_{run}.gif"
    }
},
{category:"typh",id:"up92",label:"고층:925hPa",
    patternByModel:{
        kim_anal:"kim_up92_anlmod_typh_pb4_{run}.gif",
        um_anal:"up92_anlmod_typh_pb4_{run}.gif",
    }
},
{category:"typh",id:"up85",label:"고층:850hPa",
    patternByModel:{
        kim_anal:"kim_up85_anlmod_typh_pb4_{run}.gif",
        um_anal:"up85_anlmod_typh_pb4_{run}.gif",
    }
},
{category:"typh",id:"up70",label:"고층:700hPa",
    patternByModel:{
        kim_anal:"kim_up70_anlmod_typh_pb4_{run}.gif",
        um_anal:"up70_anlmod_typh_pb4_{run}.gif",
    }
},
{category:"typh",id:"up50",label:"고층:500hPa",
    patternByModel:{
        kim_anal:"kim_up50_anlmod_typh_pb4_{run}.gif",
        um_anal:"up50_anlmod_typh_pb4_{run}.gif",
    }
},
{category:"typh",id:"up30",label:"고층:300hPa",
    patternByModel:{
        kim_anal:"kim_up30_anlmod_typh_pb4_{run}.gif",
        um_anal:"up30_anlmod_typh_pb4_{run}.gif",
    }
},
{category:"typh",id:"up20",label:"고층:200hPa",
    patternByModel:{
        kim_anal:"kim_up20_anlmod_typh_pb4_{run}.gif",
        um_anal:"up20_anlmod_typh_pb4_{run}.gif",
    }
},
{category:"typh",id:"up10",label:"고층:100hPa",
    patternByModel:{
        kim_anal:"kim_up10_anlmod_typh_pb4_{run}.gif",
        um_anal:"up10_anlmod_typh_pb4_{run}.gif",
    }
},
{category:"typh", type:"header", label:"──────────────────"},
{category:"typh",id:"200div",label:"중첩분석: 200hPa 발산",
    patternByModel:{
        kim_anal:"kim_typh_anal_200div_pb4_{run}.gif",
        um_anal:"typh_anal_200div_pb4_{run}.gif",
    },
    folderByModel:{
        um_anal:"TYPH",
    }
},
{category:"typh",id:"200sln",label:"중첩분석: 200hPa 유선",
    patternByModel:{
        kim_anal:"kim_typh_anal_200sln_pb4_{run}.gif",
        um_anal:"typh_anal_200sln_pb4_{run}.gif",
    },
    folderByModel:{
        um_anal:"TYPH",
    }
},
{category:"typh",id:"200wnd",label:"중첩분석: 200hPa 바람",
    patternByModel:{
        kim_anal:"kim_typh_anal_200wnd_pb4_{run}.gif",
        um_anal:"typh_anal_200wnd_pb4_{run}.gif",
    },
    folderByModel:{
        um_anal:"TYPH",
    }
},
{category:"typh",id:"500vor",label:"중첩분석: 500hPa 와도",
    patternByModel:{
        kim_anal:"kim_typh_anal_500vor_pb4_{run}.gif",
        um_anal:"typh_anal_500vor_pb4_{run}.gif",
    },
    folderByModel:{
        um_anal:"TYPH",
    }
},
{category:"typh",id:"500sln",label:"중첩분석: 500hPa 유선",
    patternByModel:{
        kim_anal:"kim_typh_anal_500sln_pb4_{run}.gif",
        um_anal:"typh_anal_500sln_pb4_{run}.gif",
    },
    folderByModel:{
        um_anal:"TYPH",
    }
},
{category:"typh",id:"850con",label:"중첩분석: 850hPa 수렴",
    patternByModel:{
        kim_anal:"kim_typh_anal_850con_pb4_{run}.gif",
        um_anal:"typh_anal_850con_pb4_{run}.gif",
    },
    folderByModel:{
        um_anal:"TYPH",
    }
},
{category:"typh",id:"850sln",label:"중첩분석: 850hPa 유선",
    patternByModel:{
        kim_anal:"kim_typh_anal_850sln_pb4_{run}.gif",
        um_anal:"typh_anal_850sln_pb4_{run}.gif",
    },
    folderByModel:{
        um_anal:"TYPH",
    }
},
{category:"typh",id:"850wnd",label:"중첩분석: 850hPa 바람",
    patternByModel:{
        kim_anal:"kim_typh_anal_850wnd_pb4_{run}.gif",
        um_anal:"typh_anal_850wnd_pb4_{run}.gif",
    },
    folderByModel:{
        um_anal:"TYPH",
    }
},
{category:"typh",id:"850vor",label:"중첩분석: 850hPa 와도",
    patternByModel:{
        kim_anal:"kim_typh_anal_850vor_pb4_{run}.gif",
        um_anal:"typh_anal_850vor_pb4_{run}.gif",
    },
    folderByModel:{
        um_anal:"TYPH",
    }
},
{category:"typh",id:"10msln",label:"중첩분석: 10m 유선",
    patternByModel:{
        kim_anal:"kim_typh_anal_10msln_pb4_{run}.gif",
        um_anal:"typh_anal_10msln_pb4_{run}.gif",
    },
    folderByModel:{
        um_anal:"TYPH",
    }
},
{category:"typh",id:"wndshr",label:"중첩분석: 200-850 바람시어",
    patternByModel:{
        kim_anal:"kim_typh_anal_wndshr_pb4_{run}.gif",
        um_anal:"typh_anal_wndshr_pb4_{run}.gif",
    },
    folderByModel:{
        um_anal:"TYPH",
    }
},
{category:"typh",id:"wndsh2",label:"중첩분석: 200-850 바람시어(2)",
    patternByModel:{
        kim_anal:"kim_typh_anal_wndsh2_pb4_{run}.gif",
        um_anal:"typh_anal_wndsh2_pb4_{run}.gif",
    },
    folderByModel:{
        um_anal:"TYPH",
    }
},
{category:"typh",id:"prs200",label:"중첩분석: 해면기압-200 등고선",
    patternByModel:{
        kim_anal:"kim_typh_anal_prs200_pb4_{run}.gif",
        um_anal:"typh_anal_prs200_pb4_{run}.gif",
    },
    folderByModel:{
        um_anal:"TYPH",
    }
},


/* 분석장 영역 일기도(KAS) */
{category:"kas0",id:"gph500",label:"500 고도,기온,와도",
    patternByModel:{
        kas:[
            "kas0_asia_gph500_{run}.png",
            "kas0_hkor_gph500_{run}.png",
        ]
    }
},
{category:"kas0",id:"gph700",label:"700 고도,상당온위",
    patternByModel:{
        kas:[
            "kas0_asia_gph700_{run}.png",
            "kas0_hkor_gph700_{run}.png",
        ]
    }
},
{category:"kas0",id:"ept850",label:"850 고도,상당온위",
    patternByModel:{
        kas:[
            "kas0_asia_ept850_{run}.png",
            "kas0_hkor_ept850_{run}.png",
        ]
    }
},
{category:"kas0",id:"ept925",label:"925 고도,상당온위",
    patternByModel:{
        kas:[
            "kas0_asia_ept925_{run}.png",
            "kas0_hkor_ept925_{run}.png",
        ]
    }
},
{category:"kas0",id:"ept950",label:"950 고도,상당온위",
    patternByModel:{
        kas:[
            "kas0_asia_ept950_{run}.png",
            "kas0_hkor_ept950_{run}.png",
        ]
    }
},
{category:"kas0", type:"header", label:"──────────────────"},
{category:"kas0",id:"wnd200",label:"200/300 유선,풍속",
    patternByModel:{
        kas:[
            "kas0_asia_wnd200_{run}.png",
            "kas0_hkor_wnd200_{run}.png",
        ]
    }
},
{category:"kas0",id:"wnd500",label:"500 유선,풍속",
    patternByModel:{
        kas:[
            "kas0_asia_wnd500_{run}.png",
            "kas0_hkor_wnd500_{run}.png",
        ]
    }
},
{category:"kas0",id:"wnd700",label:"700 유선,풍속",
    patternByModel:{
        kas:[
            "kas0_asia_wnd700_{run}.png",
            "kas0_hkor_wnd700_{run}.png",
        ]
    }
},
{category:"kas0",id:"wnd850",label:"850 유선,풍속",
    patternByModel:{
        kas:[
            "kas0_asia_wnd850_{run}.png",
            "kas0_hkor_wnd850_{run}.png",
        ]
    }
},
{category:"kas0",id:"wnd925",label:"925 유선,풍속",
    patternByModel:{
        kas:[
            "kas0_asia_wnd925_{run}.png",
            "kas0_hkor_wnd925_{run}.png",
        ]
    }
},
{category:"kas0",id:"wnd950",label:"950 유선,풍속",
    patternByModel:{
        kas:[
            "kas0_asia_wnd950_{run}.png",
            "kas0_hkor_wnd950_{run}.png",
        ]
    }
},
{category:"kas0", type:"header", label:"──────────────────"},
{category:"kas0",id:"ttd500",label:"500 습수(T-Td)",
    patternByModel:{
        kas:[
            "kas0_asia_ttd500_{run}.png",
            "kas0_hkor_ttd500_{run}.png",
        ]
    }
},
{category:"kas0",id:"ttd700",label:"700 습수(T-Td)",
    patternByModel:{
        kas:[
            "kas0_asia_ttd700_{run}.png",
            "kas0_hkor_ttd700_{run}.png",
        ]
    }
},
{category:"kas0",id:"anl850",label:"850 습수(T-Td)",
    patternByModel:{
        kas:[
            "kas0_asia_anl850_{run}.png",
            "kas0_hkor_anl850_{run}.png",
        ]
    }
},
{category:"kas0",id:"anl925",label:"925 습수(T-Td)",
    patternByModel:{
        kas:[
            "kas0_asia_anl925_{run}.png",
            "kas0_hkor_anl925_{run}.png",
        ]
    }
},
{category:"kas0",id:"anl950",label:"950 습수(T-Td)",
    patternByModel:{
        kas:[
            "kas0_asia_anl950_{run}.png",
            "kas0_hkor_anl950_{run}.png",
        ]
    }
},
{category:"kas0",id:"anlsfc",label:"지상 습수(T-Td)",
    patternByModel:{
        kas:[
            "kas0_asia_anlsfc_{run}.png",
            "kas0_hkor_anlsfc_{run}.png",
        ]
    }
},
{category:"kas0",id:"moflux",label:"850 수분속",
    patternByModel:{
        kas:[
            "kas0_asia_moflux_{run}.png",
            "kas0_hkor_moflux_{run}.png",
        ]
    }
},
{category:"kas0", type:"header", label:"──────────────────"},
{category:"kas0",id:"con850",label:"850 수렴도,등풍속",
    patternByModel:{
        kas:[
            "kas0_asia_con850_{run}.png",
            "kas0_hkor_con850_{run}.png",
        ]
    }
},
{category:"kas0",id:"con925",label:"925 수렴도,등풍속",
    patternByModel:{
        kas:[
            "kas0_asia_con925_{run}.png",
            "kas0_hkor_con925_{run}.png",
        ]
    }
},
{category:"kas0", type:"header", label:"──────────────────"},
{category:"kas0",id:"dfh500",label:"500 고도변화",
    patternByModel:{
        kas:[
            "kas0_asia_dfh500_{run}.png",
            "kas0_hkor_dfh500_{run}.png",
        ]
    }
},
{category:"kas0",id:"dft925",label:"925 기온변화",
    patternByModel:{
        kas:[
            "kas0_asia_dft925_{run}.png",
            "kas0_hkor_dft925_{run}.png",
        ]
    }
},
{category:"kas0", type:"header", label:"──────────────────"},
{category:"kas0",id:"tgc2d",label:"지상바람",
    patternByModel:{
        kas:[
            "kas0_asia_tgc2d_{run}.png",
            "kas0_hkor_tgc2d_{run}.png",
        ]
    }
},

/* 보조분석도 */
{category:"axas",id:"axfe",label:"종합장(전구)",
    patternByModel:{
        kim_anal:[
            "kim_gdps_anal_axfe03_pb4_{run}.gif",
            "kim_gdps_anal_axfe04_pb4_{run}.gif",
        ],
        um_anal:[
            "gdps_anal_axfe03_pb4_{run}.gif",
            "gdps_anal_axfe04_pb4_{run}.gif",
        ],
    },
    folderByModel:{
        kim_anal:"KIMG",
        um_anal:"GDPS",
    },
    cyclesByModel:{
        kim_anal:[0,12],
        um_anal:[0,12]
    }
},
{category:"axas",id:"irdf",label:"적외분석장",
    patternByModel:{
        kim_anal:[
            "kim_radm_gdps_gk2a_diff_rmir_{run}.png"
        ],
        um_anal:[
            "radm_gdps_gk2a_diff_rmir_{run}.png",
            "radm_sfc3_diff_rmir_{run}.png"
        ]
    },
    folderByModel:{
        kim_anal:"KIMA",
        um_anal:"APPM",
    },
    cyclesByModel:{
        kim_anal:[0,12],
        um_anal:[0,12]
    }
},
{category:"axas",id:"wvdf",label:"수증기분석장",
    patternByModel:{
        kim_anal:[
            "kim_radm_gdps_gk2a_diff_rmwv_{run}.png"
        ],
        um_anal:[
            "radm_gdps_gk2a_diff_rmwv_{run}.png",
            "radm_sfc3_diff_rmwv_{run}.png"
        ],
    },
    folderByModel:{
        kim_anal:"KIMA",
        um_anal:"APPM",
    },
    cyclesByModel:{
        kim_anal:[0,12],
        um_anal:[0,12]
    }
},
{category:"axas",id:"axrg",label:"종합장(지역)",
    patternByModel:{
        um_anal:[
            "r3oi_lc30_anal_axfe03_pb4_{run}.gif",
            "r3oi_lc30_anal_axfe04_pb4_{run}.gif",
        ],
        ecmwf_ra:[
            "r3oi_lc30_anal_axfe03_pb4_{run}.gif",
            "r3oi_lc30_anal_axfe04_pb4_{run}.gif",
        ],
    },
    folderByModel:{
        ecmwf_ra:"ANAL",
    },
    archiveStartByModel:{
        um_anal:"2002-09-01",
    },
    archiveEndByModel:{
        ecmwf_ra:"2002-08-31"
    },
    cyclesByModel:{
        um_anal:[0,12]
    }
},

/* 북반구분석도 */
{category:"nhem",id:"anlmod",label:"500hPa 분석도",
    patternByModel:{
        kim_anal:"kim_n500_anlmod_pb4_{run}.gif",
        um_anal:"n500_anlmod_pb4_{run}.gif"
    }
},
{category:"nhem",id:"difmod",label:"500hPa 편차도",
    patternByModel:{
        kim_anal:"kim_n500_difmod_pb4_{run}.gif",
        um_anal:"n500_difmod_pb4_{run}.gif"
    }
},
{category:"nhem", type:"header", label:"──────────────────"},
{category:"nhem",id:"surfce",label:"지상분석과 강수량",
    patternByModel:{
        kim_anal:"kim_nhem_ps60_surfce_pb4_{run}.gif",
        um_anal:"nhem_ps60_surfce_pb4_{run}.gif",
        ecmwf_ra:"nhem_ps60_surfce_pa4_{run}.gif"  
    },
    folderByModel:{
        ecmwf_ra:"ANAL",
    },
    archiveStartByModel:{
        um_anal:"2010-01-01",
    },
    archiveEndByModel:{
        ecmwf_ra:"2009-12-31"
    }
},
{category:"nhem",id:"gph500",label:"500hPa 와도분석",
    patternByModel:{
        kim_anal:"kim_nhem_ps60_gph500_pb4_{run}.gif",
        um_anal:"nhem_ps60_gph500_pb4_{run}.gif",
        ecmwf_ra:"nhem_ps60_gph500_pa4_{run}.gif"  
    },
    folderByModel:{
        ecmwf_ra:"ANAL",
    },
    archiveStartByModel:{
        um_anal:"2010-01-01",
    },
    archiveEndByModel:{
        ecmwf_ra:"2009-12-31"
    }
},
{category:"nhem",id:"dfh500",label:"500hPa 고도분석",
    patternByModel:{
        kim_anal:"kim_nhem_ps60_dfh500_pb4_{run}.gif",
        um_anal:"nhem_ps60_dfh500_pb4_{run}.gif",
    },
    archiveStartByModel:{
        um_anal:"2010-01-01",
    }
},
{category:"nhem",id:"d24h50",label:"500hPa 고도분석증분(1)",
    patternByModel:{
        kim_anal:"kim_nhem_ps60_d24h50_pb4_{run}.gif",
        um_anal:"nhem_ps60_d24h50_pb4_{run}.gif"
    },
    archiveStartByModel:{
        um_anal:"2010-01-01",
    }
},
{category:"nhem",id:"d12h50",label:"500hPa 고도분석증분(2)",
    patternByModel:{
        kim_anal:"kim_nhem_ps60_d12h50_pb4_{run}.gif",
        um_anal:"nhem_ps60_d12h50_pb4_{run}.gif"
    },
    archiveStartByModel:{
        um_anal:"2010-01-01",
    }
},
{category:"nhem",id:"dft500",label:"500hPa 기온분석",
    patternByModel:{
        kim_anal:"kim_nhem_ps60_dft500_pb4_{run}.gif",
        um_anal:"nhem_ps60_dft500_pb4_{run}.gif"
    },
    archiveStartByModel:{
        um_anal:"2010-01-01",
    }
},
{category:"nhem",id:"dft850",label:"850hPa 기온분석",
    patternByModel:{
        kim_anal:"kim_nhem_ps60_dft850_pb4_{run}.gif",
        um_anal:"nhem_ps60_dft850_pb4_{run}.gif"
    },
    archiveStartByModel:{
        um_anal:"2010-01-01",
    }
},
{category:"nhem",id:"ept850",label:"850hPa 온위분석",
    patternByModel:{
        kim_anal:"kim_nhem_ps60_ept850_pb4_{run}.gif",
        um_anal:"nhem_ps60_ept850_pb4_{run}.gif"
    },
    archiveStartByModel:{
        um_anal:"2010-01-01",
    }
},
{category:"nhem",id:"mxr850",label:"850hPa 습기분석",
    patternByModel:{
        kim_anal:"kim_nhem_ps60_mxr850_pb4_{run}.gif",
        um_anal:"nhem_ps60_mxr850_pb4_{run}.gif"
    },
    archiveStartByModel:{
        um_anal:"2010-01-01",
    }
},
{category:"nhem",id:"gph850",label:"하층 바람분석",
    patternByModel:{
        kim_anal:"kim_nhem_ps60_gph850_pb4_{run}.gif",
        um_anal:"nhem_ps60_gph850_pb4_{run}.gif",
        ecmwf_ra:"nhem_ps60_gph850_pa4_{run}.gif"  
    },
    folderByModel:{
        ecmwf_ra:"ANAL",
    },
    archiveStartByModel:{
        um_anal:"2010-01-01",
    },
    archiveEndByModel:{
        ecmwf_ra:"2009-12-31"
    }
},
{category:"nhem",id:"gph200",label:"상층 바람분석",
    patternByModel:{
        kim_anal:"kim_nhem_ps60_gph200_pb4_{run}.gif",
        um_anal:"nhem_ps60_gph200_pb4_{run}.gif",
        ecmwf_ra:"nhem_ps60_gph200_pa4_{run}.gif"  
    },
    folderByModel:{
        ecmwf_ra:"ANAL",
    },
    archiveStartByModel:{
        um_anal:"2010-01-01",
    },
    archiveEndByModel:{
        ecmwf_ra:"2009-12-31"
    }
},
{category:"nhem",id:"gph850",label:"하층 바람분석",
    patternByModel:{
        kim_anal:"kim_nhem_ps60_gph850_pb4_{run}.gif",
        um_anal:"nhem_ps60_gph850_pb4_{run}.gif",
        ecmwf_ra:"nhem_ps60_gph850_pa4_{run}.gif"  
    },
    folderByModel:{
        ecmwf_ra:"ANAL",
    },
    archiveStartByModel:{
        um_anal:"2010-01-01",
    },
    archiveEndByModel:{
        ecmwf_ra:"2009-12-31"
    }
},


/* 24시간 강수량 */
{category:"rain24",id:"rain24",label:"24시간 강수량",
    cycles:TWELVE_HOUR_CYCLES,
    patternByModel:{
        kim_anal:[
            "kim_sfc3_rain24_pb4_{run}.gif"
        ],
        um_anal:[
            "sfc3_rain24_pb4_{run}.gif"
        ],
    }
},

/* 분석단열선도 */
{category:"skewan",id:"skewan",label:"분석단열선도",
    patternByModel:{
        kas:"kas0_skew_{detail}_{run}.png"
    }
},

/* 관측단열선도 */
{category:"skewob",id:"skewob",label:"관측단열선도",
    patternByModel:{
        obs_upper:"skew_{detail}_pb4_{run}.gif"
    }
},
{category:"skewds",id:"skewds",label:"하강단열선도",
    patternByModel:{
        obs_upper:"skew_desc_{detail}_pb4_{run}.gif"
    }
},

/* 지형과바람 */
{category:"grtopo",id:"grtopo",label:"지형과바람",
    patternByModel:{
        kas:"kas0_{detail}_grtopo_{run}.svg"
    }
},

{category:"dust",id:"smsand",label:"황사일기도",
    patternByModel:{
        kim_anal:[
            "kim_sfc3_smsand_pb4_{run}.gif"
        ],
        um_anal:[
            "sfc3_smsand_pb4_{run}.gif"
        ],
    }
},


];


const ANALYSIS_DEFAULT_PRODUCT_BY_CATEGORY={

};


const ANALYSIS_PRODUCT_CATEGORY_UI_CONFIG={
rain24:{hideProductSelect:true},
skewan:{hideProductSelect:true},
skewob:{hideProductSelect:true},
skewds:{hideProductSelect:true},
grtopo:{hideProductSelect:true},
};


const ANALYSIS_CATEGORY_MODEL_RESTRICTIONS={

skewob:{
allowedModels:["obs_upper"],
fallbackModel:"obs_upper"
},
skewds:{
allowedModels:["obs_upper"],
fallbackModel:"obs_upper"
}

};


const ANALYSIS_SELECTION_MODEL_RESTRICTIONS={

"asia:sfc1":{
allowedModels:["kas"],
fallbackModel:"kas",
allowModelSwitch:true
},

"asia:sfc1_ptrend":{
allowedModels:["kas"],
fallbackModel:"kas",
allowModelSwitch:true
}

};
