/* 공통 보조패널 원자료 목록
   - 지점/영역/온위면 목록은 여기 한 곳에서만 관리한다.
   - 산출물/모델별 표시 여부는 aux-rules.js에서 관리한다. */

const AUX_OPTION_SETS={

kmaStations:{
  type: "station",
  items:[
    {
      type: "item",
      value: "47108",
      label: "108 서울"
    },
    {
      type: "item",
      value: "47098",
      label: "- 098 동두천"
    },
    {
      type: "item",
      value: "47099",
      label: "- 099 파주"
    },
    {
      type: "item",
      value: "47110",
      label: "- 110 김포공항"
    },
    {
      type: "item",
      value: "47112",
      label: "- 112 인천"
    },
    {
      type: "item",
      value: "47113",
      label: "- 113 인천공항"
    },
    {
      type: "item",
      value: "47119",
      label: "- 119 수원"
    },
    {
      type: "item",
      value: "47203",
      label: "- 203 이천"
    },
    {
      type: "item",
      value: "47551",
      label: "- 551 평택"
    },
    {
      type: "item",
      value: "47102",
      label: "- 102 백령도"
    },
    {
      type: "separator"
    },
    {
      type: "item",
      value: "47104",
      label: "104 북강릉"
    },
    {
      type: "item",
      value: "47090",
      label: "- 090 속초"
    },
    {
      type: "item",
      value: "47092",
      label: "- 092 양양공항"
    },
    {
      type: "item",
      value: "47095",
      label: "- 095 철원"
    },
    {
      type: "item",
      value: "47100",
      label: "- 100 대관령"
    },
    {
      type: "item",
      value: "47101",
      label: "- 101 춘천"
    },
    {
      type: "item",
      value: "47106",
      label: "- 106 동해"
    },
    {
      type: "item",
      value: "47114",
      label: "- 114 원주"
    },
    {
      type: "item",
      value: "47118",
      label: "- 118 원주공항"
    },
    {
      type: "item",
      value: "47121",
      label: "- 121 영월"
    },
    {
      type: "separator"
    },
    {
      type: "item",
      value: "47131",
      label: "131 청주"
    },
    {
      type: "item",
      value: "47128",
      label: "- 128 청주공항"
    },
    {
      type: "item",
      value: "47127",
      label: "- 127 충주"
    },
    {
      type: "item",
      value: "47135",
      label: "- 135 추풍령"
    },
    {
      type: "item",
      value: "47605",
      label: "- 605 영동"
    },
    {
      type: "separator"
    },
    {
      type: "item",
      value: "47133",
      label: "133 대전"
    },
    {
      type: "item",
      value: "47129",
      label: "- 129 서산"
    },
    {
      type: "item",
      value: "47177",
      label: "- 177 홍성"
    },
    {
      type: "item",
      value: "47239",
      label: "- 239 세종"
    },
    {
      type: "item",
      value: "47232",
      label: "- 232 천안"
    },
    {
      type: "item",
      value: "47235",
      label: "- 235 보령"
    },
    {
      type: "separator"
    },
     {
      type: "item",
      value: "47146",
      label: "146 전주"
    },
    {
      type: "item",
      value: "47140",
      label: "- 140 군산"
    },
    {
      type: "item",
      value: "47172",
      label: "- 172 고창"
    },
    {
      type: "item",
      value: "47251",
      label: "- 251 고창군"
    },
    {
      type: "item",
      value: "47245",
      label: "- 245 정읍"
    },
    {
      type: "item",
      value: "47247",
      label: "- 247 남원"
    },
    {
      type: "item",
      value: "47701",
      label: "- 701 무주"
    },
    {
      type: "separator"
    },
    {
      type: "item",
      value: "47156",
      label: "156 광주"
    },
    {
      type: "item",
      value: "47158",
      label: "- 158 광주공항"
    },
    {
      type: "item",
      value: "47165",
      label: "- 165 목포"
    },
    {
      type: "item",
      value: "47163",
      label: "- 163 무안공항"
    },
    {
      type: "item",
      value: "47168",
      label: "- 168 여수"
    },
    {
      type: "item",
      value: "47167",
      label: "- 167 여수공항"
    },
    {
      type: "item",
      value: "47169",
      label: "- 169 흑산도"
    },
    {
      type: "item",
      value: "47170",
      label: "- 170 완도"
    },
    {
      type: "item",
      value: "47174",
      label: "- 174 순천"
    },
    {
      type: "item",
      value: "47175",
      label: "- 175 진도"
    },
    {
      type: "item",
      value: "47268",
      label: "- 268 진도군"
    },
    {
      type: "item",
      value: "47262",
      label: "- 262 나로도"
    },
    {
      type: "item",
      value: "47266",
      label: "- 266 광양"
    },
    {
      type: "item",
      value: "47710",
      label: "- 710 나주"
    },
    {
      type: "separator"
    },
    {
      type: "item",
      value: "47143",
      label: "143 대구"
    },
    {
      type: "item",
      value: "47142",
      label: "- 142 대구공항"
    },
    {
      type: "item",
      value: "47130",
      label: "- 130 울진"
    },
    {
      type: "item",
      value: "47136",
      label: "- 136 안동"
    },
    {
      type: "item",
      value: "47137",
      label: "- 137 상주"
    },
    {
      type: "item",
      value: "47138",
      label: "- 138 포항"
    },
    {
      type: "item",
      value: "47139",
      label: "- 139 포항공항"
    },
    {
      type: "item",
      value: "47279",
      label: "- 279 구미"
    },
    {
      type: "item",
      value: "47283",
      label: "- 283 경주"
    },
    {
      type: "item",
      value: "47115",
      label: "- 115 울릉도"
    },
    {
      type: "item",
      value: "47096",
      label: "- 096 독도"
    },
    {
      type: "separator"
    },
    {
      type: "item",
      value: "47159",
      label: "159 부산"
    },
    {
      type: "item",
      value: "47152",
      label: "- 152 울산"
    },
    {
      type: "item",
      value: "47151",
      label: "- 151 울산공항"
    },
    {
      type: "item",
      value: "47153",
      label: "- 153 김해공항"
    },
    {
      type: "item",
      value: "47155",
      label: "- 155 창원"
    },
    {
      type: "item",
      value: "47255",
      label: "- 255 북창원"
    },
    {
      type: "item",
      value: "47161",
      label: "- 161 사천공항"
    },
    {
      type: "item",
      value: "47162",
      label: "- 162 통영"
    },
    {
      type: "item",
      value: "47192",
      label: "- 192 진주"
    },
    {
      type: "item",
      value: "47284",
      label: "- 284 거창"
    },
    {
      type: "separator"
    },
    {
      type: "item",
      value: "47184",
      label: "184 제주"
    },
    {
      type: "item",
      value: "47182",
      label: "- 182 제주공항"
    },
    {
      type: "item",
      value: "47185",
      label: "- 185 고산"
    },
    {
      type: "item",
      value: "47188",
      label: "- 188 성산"
    },
    {
      type: "item",
      value: "47189",
      label: "- 189 서귀포"
    }
  ]
},

upperStations:{
type: "station",
  items:[ 
    /* 정규 관측 지점 */
    {
      type: "item",
      value: "47102",
      label: "47102 백령도"
    },
    {
      type: "item",
      value: "47104",
      label: "47104 북강릉"
    },
    {
      type: "item",
      value: "47135",
      label: "47135 추풍령"
    },
    {
      type: "item",
      value: "47138",
      label: "47138 포항"
    },
    {
      type: "item",
      value: "47169",
      label: "47169 흑산도"
    },
    {
      type: "item",
      value: "47186",
      label: "47186 태풍센터"
    },
    {
      type: "item",
      value: "47230",
      label: "47230 덕적북리"
    },
    {
      type: "item",
      value: "47269",
      label: "47269 안마도"
    },
    {
      type: "separator"
    },
    {
      type: "item",
      value: "47122",
      label: "47122 오산(공군)"
    },
    {
      type: "item",
      value: "47158",
      label: "47158 광주(공군)"
    },
    {
      type: "separator" /* 관측 종료 지점 */
    },
    {
      type: "item",
      value: "47090",
      label: "47090 속초(종료)"
    },
    {
      type: "item",
      value: "47185",
      label: "47185 고산(종료)"
    },
    {
      type: "separator" /* 기상관측선/차량(모바일) */
    },
    {
      type: "item",
      value: "22003",
      label: "22003 기상1호"
    },
    {
      type: "item",
      value: "47183",
      label: "47183 부산청(차량)"
    },
    {
      type: "item",
      value: "47190",
      label: "47190 광주청(차량)"
    },
    {
      type: "item",
      value: "47191",
      label: "47191 강원청(차량)"
    },
    {
      type: "item",
      value: "47193",
      label: "47193 대구청(차량)"
    },
    {
      type: "item",
      value: "47194",
      label: "47194 수도권청(차량)"
    },
    {
      type: "item",
      value: "47195",
      label: "47195 대전청(차량)"
    },
    {
      type: "item",
      value: "47196",
      label: "47196 전주지청(차량)"
    },
    {
      type: "item",
      value: "47198",
      label: "47198 과학원(MOVE1)"
    },
    {
      type: "item",
      value: "47199",
      label: "47199 과학원(MOVE2)"
    },
    {
      type: "item",
      value: "47200",
      label: "47200 청주지청(차량)"
    },
    {
      type: "item",
      value: "47206",
      label: "47206 제주청(차량)"
    },
    {
      type: "separator" /* 한시적 관측 지점 (집중관측, 연구용 등) */
    },
    {
      type: "item",
      value: "47098",
      label: "47098 동두천",
      hidden:true
    },
    {
      type: "item",
      value: "47112",
      label: "47112 인천",
      hidden:true
    },
    {
      type: "item",
      value: "47113",
      label: "47113 인천공항",
      hidden:true
    },
    {
      type: "item",
      value: "47132",
      label: "47132 안면도",
      hidden:true
    },
    {
      type: "item",
      value: "47201",
      label: "47201 강화",
      hidden:true
    },
    {
      type: "item",
      value: "47258",
      label: "47258 보성군",
      hidden:true
    },
    {
      type: "item",
      value: "47261",
      label: "47261 해남",
      hidden:true
    },
    {
      type: "item",
      value: "47331",
      label: "47331 덕적도",
      hidden:true
    },
    {
      type: "item",
      value: "47500",
      label: "47500 서귀포남원",
      hidden:true
    }
  ]
},



localAreas:{
  type: "area",
  items:[
    {
      type: "item",
      value: "s7sl",
      label: "서울"
    },
    {
      type: "item",
      value: "s1gg",
      label: "수도권청"
    },
    {
      type: "separator"
    },
    {
      type: "item",
      value: "s5gn",
      label: "강원청"
    },
    {
      type: "separator"
    },
    {
      type: "item",
      value: "s0cj",
      label: "청주지청"
    },
    {
      type: "item",
      value: "s4dj",
      label: "대전청"
    },
    {
      type: "separator"
    },
    {
      type: "item",
      value: "s9jj",
      label: "전주지청"
    },
    {
      type: "item",
      value: "s3gj",
      label: "광주청"
    },
    {
      type: "separator"
    },
    {
      type: "item",
      value: "s8dg",
      label: "대구청"
    },
    {
      type: "item",
      value: "s2bs",
      label: "부산청"
    },
    {
      type: "separator"
    },
    {
      type: "item",
      value: "s6jj",
      label: "제주청"
    }
  ]
},

isentropicLevels:{
  type: "level",
  items:[
    {
      type: "item",
      value: "350K",
      label: "350K"
    },
    {
      type: "item",
      value: "345K",
      label: "345K"
    },
    {
      type: "item",
      value: "340K",
      label: "340K"
    },
    {
      type: "item",
      value: "335K",
      label: "335K"
    },
    {
      type: "item",
      value: "330K",
      label: "330K"
    },
    {
      type: "item",
      value: "325K",
      label: "325K"
    },
    {
      type: "item",
      value: "320K",
      label: "320K"
    },
    {
      type: "item",
      value: "315K",
      label: "315K"
    },
    {
      type: "item",
      value: "310K",
      label: "310K"
    },
    {
      type: "item",
      value: "305K",
      label: "305K"
    },
    {
      type: "item",
      value: "300K",
      label: "300K"
    },
    {
      type: "item",
      value: "295K",
      label: "295K"
    },
    {
      type: "item",
      value: "290K",
      label: "290K"
    },
    {
      type: "item",
      value: "285K",
      label: "285K"
    },
    {
      type: "item",
      value: "280K",
      label: "280K"
    },
    {
      type: "item",
      value: "275K",
      label: "275K"
    },
    {
      type: "item",
      value: "270K",
      label: "270K"
    },
    {
      type: "item",
      value: "265K",
      label: "265K"
    },
    {
      type: "item",
      value: "260K",
      label: "260K"
    }
  ]
},

prec6h_intensities:{
  type: "intensity",
  items:[
    {
      type: "item",
      value: "no01",
      label: "1mm 이상"
    },
    {
      type: "item",
      value: "no02",
      label: "5mm 이상"
    },
    {
      type: "item",
      value: "no03",
      label: "10mm 이상"
    },
    {
      type: "item",
      value: "no04",
      label: "25mm 이상"
    }
  ]
},

prec3h_intensities:{
  type: "intensity",
  items:[
    {
      type: "item",
      value: "no06",
      label: "0.5mm 이상"
    },
    {
      type: "item",
      value: "no01",
      label: "1mm 이상"
    },
    {
      type: "item",
      value: "no02",
      label: "5mm 이상"
    },
    {
      type: "item",
      value: "no03",
      label: "10mm 이상"
    },
    {
      type: "item",
      value: "no04",
      label: "25mm 이상"
    },
    {
      type: "item",
      value: "no05",
      label: "50mm 이상"
    },
    {
      type: "item",
      value: "no05",
      label: "50mm 이상"
    },
  ]
},

prec1h_intensities:{
  type: "intensity",
  items:[
    {
      type: "item",
      value: "no06",
      label: "0.5mm 이상"
    },
    {
      type: "item",
      value: "no01",
      label: "1mm 이상"
    },
    {
      type: "item",
      value: "no02",
      label: "5mm 이상"
    },
    {
      type: "item",
      value: "no03",
      label: "10mm 이상"
    },
    {
      type: "item",
      value: "no04",
      label: "25mm 이상"
    },
    {
      type: "item",
      value: "no05",
      label: "50mm 이상"
    }
  ]
},

snow3h_intensities:{
  type: "intensity",
  items:[
    {
      type: "item",
      value: "no01",
      label: "0.1mm 이상"
    },
    {
      type: "item",
      value: "no02",
      label: "0.5mm 이상"
    },
    {
      type: "item",
      value: "no03",
      label: "1mm 이상"
    },
    {
      type: "item",
      value: "no04",
      label: "5mm 이상"
    }
  ]
},

snow1h_intensities:{
  type: "intensity",
  items:[
    {
      type: "item",
      value: "no01",
      label: "0.1mm 이상"
    },
    {
      type: "item",
      value: "no02",
      label: "0.5mm 이상"
    },
    {
      type: "item",
      value: "no03",
      label: "1mm 이상"
    },
    {
      type: "item",
      value: "no04",
      label: "5mm 이상"
    }
  ]
},

visblt_intensities:{
  type: "intensity",
  items:[
    {
      type: "item",
      value: "no01",
      label: "0.1km 미만"
    },
    {
      type: "item",
      value: "no02",
      label: "1.0km 미만"
    }
  ]
},

epsg_criterions:{
  type: "criterion",
  items:[
    {
      type: "item",
      value: "no5",
      label: "CTL"
    },
    {
      type: "item",
      value: "no1",
      label: "MED"
    },
    {
      type: "item",
      value: "no2",
      label: "75%"
    },
    {
      type: "item",
      value: "no3",
      label: "90%"
    },
    {
      type: "item",
      value: "no4",
      label: "MAX"
    }
  ]
},

lens_criterions:{
  type: "criterion",
  items:[
    {
      type: "item",
      value: "no01",
      label: "CTL"
    },
    {
      type: "item",
      value: "no02",
      label: "MED"
    },
    {
      type: "item",
      value: "no03",
      label: "75%"
    },
    {
      type: "item",
      value: "no04",
      label: "90%"
    },
    {
      type: "item",
      value: "no05",
      label: "MAX"
    }
  ]
},

prob_rain_intensities:{
  type: "intensity",
  items:[
    {
      type: "item",
      value: "no1",
      label: "1mm 이상"
    },
    {
      type: "item",
      value: "no2",
      label: "5mm 이상"
    },
    {
      type: "item",
      value: "no3",
      label: "10mm 이상"
    },
    {
      type: "item",
      value: "no4",
      label: "25mm 이상"
    }
  ]
},

spgt_heights:{
  type: "height",
  items:[
    {
      type: "item",
      value: "hg01",
      label: "5340m, 5460m"
    },
    {
      type: "item",
      value: "hg02",
      label: "5400m, 5520m"
    },
    {
      type: "item",
      value: "hg03",
      label: "5460m, 5580m"
    },
    {
      type: "item",
      value: "hg04",
      label: "5520m, 5640m"
    },
    {
      type: "item",
      value: "hg05",
      label: "5580m, 5700m"
    },
    {
      type: "item",
      value: "hg06",
      label: "5640m, 5760m"
    },
    {
      type: "item",
      value: "hg07",
      label: "5700m, 5820m"
    },
    {
      type: "item",
      value: "hg08",
      label: "5760m, 5880m"
    },
  ]
},

spgt_heights_nhem:{
  type: "height",
  items:[
    {
      type: "item",
      value: "hg01",
      label: "5340m, 5580m"
    },
    {
      type: "item",
      value: "hg02",
      label: "5460m, 5700m"
    },
    {
      type: "item",
      value: "hg03",
      label: "5640m, 5880m"
    }
  ]
},

conf_rain_intensities:{
  type: "intensity",
  items:[
    {
      type: "item",
      value: "no1",
      label: "0.1mm 이상"
    },
    {
      type: "item",
      value: "no2",
      label: "0.5mm 이상"
    },
    {
      type: "item",
      value: "no3",
      label: "5.0mm 이상"
    },
    {
      type: "item",
      value: "no4",
      label: "10mm 이상"
    },
    {
      type: "item",
      value: "no5",
      label: "30mm 이상"
    },
    {
      type: "item",
      value: "no6",
      label: "80mm 이상"
    },
    {
      type: "item",
      value: "no7",
      label: "150mm 이상"
    }
  ]
},

sstRegions:{
  type: "region",
  items:[
    {
      type: "item",
      value: "glob",
      label: "전구"
    },
    {
      type: "item",
      value: "rdps",
      label: "아시아"
    },
    {
      type: "item",
      value: "korea",
      label: "한반도"
    }
  ]
},

astdLevels:{
  type: "height",
  items:[
    {
      type: "item",
      value: "700hpa",
      label: "700hPa"
    },
    {
      type: "item",
      value: "850hpa",
      label: "850hPa"
    },
    {
      type: "item",
      value: "925hpa",
      label: "925hPa"
    }
  ]
},

};


/* expose aux data for app.js safe lookup */
if(typeof window!=='undefined'){
  window.AUX_OPTION_SETS=AUX_OPTION_SETS;
}
