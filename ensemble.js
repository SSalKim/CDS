const ENSEMBLE_CATEGORIES=[
  {
    "id": "srf3",
    "name": "EPS: EPSgram(단기:5.5일)"
  },
  {
    "id": "mrf6",
    "name": "EPS: EPSgram(중기:12일)"
  },
  {
    "id": "lrf6",
    "name": "EPS: EPSgram(중기:15일)"
  },
  {
    "id": "trd3",
    "name": "EPS: 예측경향(단기:5.5일)"
  },
  {
    "id": "trd6",
    "name": "EPS: 예측경향(중기:12일)"
  },
  {
    "id": "prob",
    "name": "EPS: 예측경향(강수확률분포)"
  },
  {
    "type": "header",
    "name": "─────────────────"
  },
  {
    "id": "mp03",
    "name": "EPS: 강수량(단기 3.5일)"
  },
  {
    "id": "mp06",
    "name": "EPS: 강수량(단기 5.5일)"
  },
  {
    "id": "days",
    "name": "EPS: 강수량(단기예보용)"
  },
  {
    "id": "mpda",
    "name": "EPS: 강수량(중기)"
  },
  {
    "id": "prep",
    "name": "EPS: 강수확률"
  },
  {
    "id": "snwp",
    "name": "EPS: 강설확률"
  },
  {
    "type": "header",
    "name": "─────────────────"
  },
  {
    "id": "efie",
    "name": "EPS: 극값예측지수(EFI)"
  },
  {
    "id": "stdv",
    "name": "EPS: 평균/편차"
  },
  {
    "id": "spgt",
    "name": "EPS: 스파게티"
  },
  {
    "id": "stmp",
    "name": "EPS: Stamp map"
  },
  {
    "id": "nhem",
    "name": "EPS: 북반구일기도"
  },
  {
    "id": "week",
    "name": "EPS: 앙상블-주간예보"
  },
  {
    "id": "cnf1",
    "name": "EPS: 주간강수신뢰도(일)"
  },
  {
    "id": "cnf2",
    "name": "EPS: 주간강수신뢰도(오전/오후)"
  },
  {
    "type": "header",
    "name": "─────────────────"
  },
  {
    "id": "metg",
    "name": "LENS: EPSgram(단기:3일)"
  },
  {
    "id": "rn03",
    "name": "LENS: 강수량(3시간)"
  },
  {
    "id": "rn12",
    "name": "LENS: 강수량(12시간)"
  },
  {
    "id": "rday",
    "name": "LENS: 강수량(단기예보용)"
  },
  {
    "id": "pm03",
    "name": "LENS: 강수량(확률매칭:3시간)"
  },
  {
    "id": "pm01",
    "name": "LENS: 강수량(확률매칭:1시간)"
  },
  {
    "id": "prn3",
    "name": "LENS: 강수확률(3시간)"
  },
  {
    "id": "prn1",
    "name": "LENS: 강수확률(1시간)"
  },
  {
    "id": "psn3",
    "name": "LENS: 강설확률(3시간)"
  },
  {
    "id": "psn1",
    "name": "LENS: 강설확률(1시간)"
  },
  {
    "id": "pvis",
    "name": "LENS: 시정확률(1시간)"
  },
  {
    "id": "fogf",
    "name": "LENS: 시정확률-fog fraction"
  },
  {
    "id": "pgst",
    "name": "LENS: 강풍확률-강풍가이던스"
  },
  {
    "id": "mwnd",
    "name": "LENS: 강풍확률-평균(mean)"
  },
  {
    "id": "sprd",
    "name": "LENS: 평균/편차"
  }
];

const ENSEMBLE_PRODUCTS=[
  {
    "category": "srf3",
    "id": "srf3",
    "label": "EPSgram(단기:5.5일)",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": false,
      "um_epsg": false,
      "ecmwf_eps": false
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    }
  },
  {
    "category": "mrf6",
    "id": "mrf6",
    "label": "EPSgram(중기:12일)",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": false,
      "um_epsg": false,
      "ecmwf_eps": false
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    }
  },
  {
    "category": "lrf6",
    "id": "lrf6",
    "label": "EPSgram(중기:15일)",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": false,
      "ecmwf_eps": false
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "ecmwf_eps": true
    }
  },
  {
    "category": "trd3",
    "id": "prcp",
    "label": "강수",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": false,
      "um_epsg": false,
      "ecmwf_eps": false
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    }
  },
  {
    "category": "trd3",
    "id": "tsfc",
    "label": "기온",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": false,
      "um_epsg": false,
      "ecmwf_eps": false
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    }
  },
  {
    "category": "trd3",
    "id": "tcld",
    "label": "운량",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": false,
      "um_epsg": false,
      "ecmwf_eps": false
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    }
  },
  {
    "category": "trd3",
    "id": "wsfc",
    "label": "풍속",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": false,
      "um_epsg": false,
      "ecmwf_eps": false
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    }
  },
  {
    "category": "trd6",
    "id": "prcp",
    "label": "강수",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": false,
      "um_epsg": false,
      "ecmwf_eps": false
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    }
  },
  {
    "category": "trd6",
    "id": "tsfc",
    "label": "기온",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": false,
      "um_epsg": false,
      "ecmwf_eps": false
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    }
  },
  {
    "category": "trd6",
    "id": "tcld",
    "label": "운량",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": false,
      "um_epsg": false,
      "ecmwf_eps": false
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    }
  },
  {
    "category": "trd6",
    "id": "wsfc",
    "label": "풍속",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": false,
      "um_epsg": false,
      "ecmwf_eps": false
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    }
  },
  {
    "category": "prob",
    "id": "prob",
    "label": "예측경향(강수확률분포)",
    "patternByModel": {
      "um_epsg": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "um_epsg": 2
    },
    "usesForecastHourByModel": {
      "um_epsg": false
    },
    "requiresDetailByModel": {
      "um_epsg": true
    }
  },
  {
    "category": "mp03",
    "id": "mp03",
    "label": "강수량(단기 3.5일)",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": false,
      "um_epsg": false,
      "ecmwf_eps": false
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    }
  },
  {
    "category": "mp06",
    "id": "mp06",
    "label": "강수량(단기 5.5일)",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": false,
      "um_epsg": false,
      "ecmwf_eps": false
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    }
  },
  {
    "category": "days",
    "id": "days",
    "label": "강수량(단기예보용)",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": false,
      "um_epsg": false,
      "ecmwf_eps": false
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    }
  },
  {
    "category": "mpda",
    "id": "mpda",
    "label": "강수량(중기)",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": false,
      "um_epsg": false,
      "ecmwf_eps": false
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    }
  },
  {
    "category": "prep",
    "id": "prep",
    "label": "강수확률",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": true,
      "um_epsg": true
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "um_epsg": true
    }
  },
  {
    "category": "snwp",
    "id": "snwp",
    "label": "강설확률",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_epsg": [
        {
          "start": 15,
          "end": 255,
          "step": 24
        }
      ],
      "um_epsg": [
        {
          "start": 15,
          "end": 255,
          "step": 24
        }
      ]
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": true,
      "um_epsg": true
    },
    "requiresDetailByModel": {
      "kim_epsg": false,
      "um_epsg": false
    }
  },
  {
    "category": "efie",
    "id": "efie",
    "label": "극값예측지수(EFI)",
    "patternByModel": {
      "um_epsg": "__proxy__"
    },
    "forecastStepByModel": {
      "um_epsg": [
        {
          "start": 15,
          "end": 255,
          "step": 24
        }
      ]
    },
    "imageCountByModel": {
      "um_epsg": 1
    },
    "usesForecastHourByModel": {
      "um_epsg": true
    },
    "requiresDetailByModel": {
      "um_epsg": false
    }
  },
  {
    "category": "stdv",
    "id": "mslp",
    "label": "동아시아 해면기압",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "forecastStepByModel": {
      "ecmwf_eps": [
        {
          "start": 6,
          "end": 240,
          "step": 6
        }
      ]
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    },
    "requiresDetailByModel": {
      "kim_epsg": false,
      "um_epsg": false,
      "ecmwf_eps": false
    }
  },
  {
    "category": "stdv",
    "id": "h500",
    "label": "500hPa 고도",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "forecastStepByModel": {
      "ecmwf_eps": [
        {
          "start": 6,
          "end": 240,
          "step": 6
        }
      ]
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    },
    "requiresDetailByModel": {
      "kim_epsg": false,
      "um_epsg": false,
      "ecmwf_eps": false
    }
  },
  {
    "category": "stdv",
    "id": "t850",
    "label": "850hPa 기온",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "forecastStepByModel": {
      "ecmwf_eps": [
        {
          "start": 6,
          "end": 240,
          "step": 6
        }
      ]
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    },
    "requiresDetailByModel": {
      "kim_epsg": false,
      "um_epsg": false,
      "ecmwf_eps": false
    }
  },
  {
    "category": "stdv",
    "id": "et85",
    "label": "850hPa 상당온위",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": true,
      "um_epsg": true
    },
    "requiresDetailByModel": {
      "kim_epsg": false,
      "um_epsg": false
    }
  },
  {
    "category": "stdv",
    "id": "tpwa",
    "label": "가강수량",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": true,
      "um_epsg": true
    },
    "requiresDetailByModel": {
      "kim_epsg": false,
      "um_epsg": false
    }
  },
  {
    "category": "spgt",
    "id": "spgt",
    "label": "스파게티",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__",
      "ecmwf_eps": "__proxy__"
    },
    "forecastStepByModel": {
      "ecmwf_eps": [
        {
          "start": 6,
          "end": 240,
          "step": 6
        }
      ]
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1,
      "ecmwf_eps": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "um_epsg": true,
      "ecmwf_eps": true
    }
  },
  {
    "category": "stmp",
    "id": "mslp",
    "label": "해면기압, 6시간 누적강수량",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": true,
      "um_epsg": true
    },
    "requiresDetailByModel": {
      "kim_epsg": false,
      "um_epsg": false
    }
  },
  {
    "category": "stmp",
    "id": "h500",
    "label": "500hPa 고도",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": true,
      "um_epsg": true
    },
    "requiresDetailByModel": {
      "kim_epsg": false,
      "um_epsg": false
    }
  },
  {
    "category": "nhem",
    "id": "stdv",
    "label": "500hPa 고도: 평균/편차",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": true,
      "um_epsg": true
    },
    "requiresDetailByModel": {
      "kim_epsg": false,
      "um_epsg": false
    }
  },
  {
    "category": "nhem",
    "id": "spgt",
    "label": "500hPa 고도: 스파게티/편차",
    "patternByModel": {
      "kim_epsg": "__proxy__",
      "um_epsg": "__proxy__"
    },
    "imageCountByModel": {
      "kim_epsg": 1,
      "um_epsg": 1
    },
    "usesForecastHourByModel": {
      "kim_epsg": true,
      "um_epsg": true
    },
    "requiresDetailByModel": {
      "kim_epsg": true,
      "um_epsg": true
    }
  },
  {
    "category": "week",
    "id": "week",
    "label": "앙상블-주간예보",
    "patternByModel": {
      "um_epsg": "__proxy__"
    },
    "imageCountByModel": {
      "um_epsg": 1
    },
    "usesForecastHourByModel": {
      "um_epsg": false
    },
    "requiresDetailByModel": {
      "um_epsg": false
    }
  },
  {
    "category": "cnf1",
    "id": "tabl",
    "label": "도시-주간강수신뢰도(일)",
    "patternByModel": {
      "um_epsg": "__proxy__"
    },
    "imageCountByModel": {
      "um_epsg": 1
    },
    "usesForecastHourByModel": {
      "um_epsg": false
    },
    "requiresDetailByModel": {
      "um_epsg": false
    }
  },
  {
    "category": "cnf1",
    "id": "area",
    "label": "공간-일일 강수확률",
    "patternByModel": {
      "um_epsg": "__proxy__"
    },
    "imageCountByModel": {
      "um_epsg": 1
    },
    "usesForecastHourByModel": {
      "um_epsg": false
    },
    "requiresDetailByModel": {
      "um_epsg": true
    }
  },
  {
    "category": "cnf2",
    "id": "tb12",
    "label": "도시-주간강수신뢰도(오전/오후)",
    "patternByModel": {
      "um_epsg": "__proxy__"
    },
    "imageCountByModel": {
      "um_epsg": 1
    },
    "usesForecastHourByModel": {
      "um_epsg": false
    },
    "requiresDetailByModel": {
      "um_epsg": false
    }
  },
  {
    "category": "cnf2",
    "id": "ar12",
    "label": "공간-오전/오후 강수확률",
    "patternByModel": {
      "um_epsg": "__proxy__"
    },
    "imageCountByModel": {
      "um_epsg": 1
    },
    "usesForecastHourByModel": {
      "um_epsg": false
    },
    "requiresDetailByModel": {
      "um_epsg": true
    }
  },
  {
    "category": "metg",
    "id": "metg",
    "label": "EPSgram(단기:3일)",
    "patternByModel": {
      "kim_lens": "__proxy__",
      "um_lens": "__proxy__"
    },
    "imageCountByModel": {
      "kim_lens": 1,
      "um_lens": 1
    },
    "usesForecastHourByModel": {
      "kim_lens": false,
      "um_lens": false
    },
    "requiresDetailByModel": {
      "kim_lens": true,
      "um_lens": true
    }
  },
  {
    "category": "rn03",
    "id": "rn03",
    "label": "강수량(3시간)",
    "patternByModel": {
      "kim_lens": "__proxy__",
      "um_lens": "__proxy__"
    },
    "imageCountByModel": {
      "kim_lens": 1,
      "um_lens": 1
    },
    "usesForecastHourByModel": {
      "kim_lens": false,
      "um_lens": false
    },
    "requiresDetailByModel": {
      "kim_lens": true,
      "um_lens": true
    }
  },
  {
    "category": "rn12",
    "id": "rn12",
    "label": "강수량(12시간)",
    "patternByModel": {
      "kim_lens": "__proxy__",
      "um_lens": "__proxy__"
    },
    "imageCountByModel": {
      "kim_lens": 1,
      "um_lens": 1
    },
    "usesForecastHourByModel": {
      "kim_lens": false,
      "um_lens": false
    },
    "requiresDetailByModel": {
      "kim_lens": true,
      "um_lens": true
    }
  },
  {
    "category": "rday",
    "id": "rday",
    "label": "강수량(단기예보용)",
    "patternByModel": {
      "kim_lens": "__proxy__",
      "um_lens": "__proxy__"
    },
    "imageCountByModel": {
      "kim_lens": 1,
      "um_lens": 1
    },
    "usesForecastHourByModel": {
      "kim_lens": false,
      "um_lens": false
    },
    "requiresDetailByModel": {
      "kim_lens": true,
      "um_lens": true
    }
  },
  {
    "category": "pm03",
    "id": "pm03",
    "label": "강수량(확률매칭:3시간)",
    "patternByModel": {
      "kim_lens": "__proxy__",
      "um_lens": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_lens": [
        {
          "start": 6,
          "end": 120,
          "step": 3
        }
      ],
      "um_lens": [
        {
          "start": 6,
          "end": 72,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_lens": 1,
      "um_lens": 1
    },
    "usesForecastHourByModel": {
      "kim_lens": true,
      "um_lens": true
    },
    "requiresDetailByModel": {
      "kim_lens": false,
      "um_lens": false
    }
  },
  {
    "category": "pm01",
    "id": "pm01",
    "label": "강수량(확률매칭:1시간)",
    "patternByModel": {
      "kim_lens": "__proxy__",
      "um_lens": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_lens": [
        {
          "start": 4,
          "end": 120,
          "step": 1
        }
      ],
      "um_lens": [
        {
          "start": 4,
          "end": 72,
          "step": 1
        }
      ]
    },
    "archiveStartByModel": {
      "kim_lens": "2023-07-20"
    },
    "imageCountByModel": {
      "kim_lens": 1,
      "um_lens": 1
    },
    "usesForecastHourByModel": {
      "kim_lens": true,
      "um_lens": true
    },
    "requiresDetailByModel": {
      "kim_lens": false,
      "um_lens": false
    }
  },
  {
    "category": "prn3",
    "id": "prn3",
    "label": "강수확률(3시간)",
    "patternByModel": {
      "kim_lens": "__proxy__",
      "um_lens": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_lens": [
        {
          "start": 6,
          "end": 120,
          "step": 3
        }
      ],
      "um_lens": [
        {
          "start": 6,
          "end": 72,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_lens": 1,
      "um_lens": 1
    },
    "usesForecastHourByModel": {
      "kim_lens": true,
      "um_lens": true
    },
    "requiresDetailByModel": {
      "kim_lens": true,
      "um_lens": true
    }
  },
  {
    "category": "prn1",
    "id": "prn1",
    "label": "강수확률(1시간)",
    "patternByModel": {
      "kim_lens": "__proxy__",
      "um_lens": "__proxy__"
    },
    "archiveStartByModel": {
      "kim_lens": "2023-07-20"
    },
    "forecastStepByModel": {
      "kim_lens": [
        {
          "start": 4,
          "end": 120,
          "step": 1
        }
      ],
      "um_lens": [
        {
          "start": 4,
          "end": 72,
          "step": 1
        }
      ]
    },
    "imageCountByModel": {
      "kim_lens": 1,
      "um_lens": 1
    },
    "usesForecastHourByModel": {
      "kim_lens": true,
      "um_lens": true
    },
    "requiresDetailByModel": {
      "kim_lens": true,
      "um_lens": true
    }
  },
  {
    "category": "psn3",
    "id": "psn3",
    "label": "강설확률(3시간)",
    "patternByModel": {
      "kim_lens": "__proxy__",
      "um_lens": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_lens": [
        {
          "start": 6,
          "end": 120,
          "step": 3
        }
      ],
      "um_lens": [
        {
          "start": 6,
          "end": 72,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_lens": 1,
      "um_lens": 1
    },
    "usesForecastHourByModel": {
      "kim_lens": true,
      "um_lens": true
    },
    "requiresDetailByModel": {
      "kim_lens": true,
      "um_lens": true
    }
  },
  {
    "category": "psn1",
    "id": "psn1",
    "label": "강설확률(1시간)",
    "patternByModel": {
      "kim_lens": "__proxy__",
      "um_lens": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_lens": [
        {
          "start": 4,
          "end": 120,
          "step": 1
        }
      ],
      "um_lens": [
        {
          "start": 4,
          "end": 72,
          "step": 1
        }
      ]
    },
    "imageCountByModel": {
      "kim_lens": 1,
      "um_lens": 1
    },
    "usesForecastHourByModel": {
      "kim_lens": true,
      "um_lens": true
    },
    "requiresDetailByModel": {
      "kim_lens": true,
      "um_lens": true
    }
  },
  {
    "category": "pvis",
    "id": "pvis",
    "label": "시정확률",
    "patternByModel": {
      "kim_lens": "__proxy__",
      "um_lens": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_lens": [
        {
          "start": 4,
          "end": 120,
          "step": 1
        }
      ],
      "um_lens": [
        {
          "start": 4,
          "end": 72,
          "step": 1
        }
      ]
    },
    "imageCountByModel": {
      "kim_lens": 1,
      "um_lens": 1
    },
    "usesForecastHourByModel": {
      "kim_lens": true,
      "um_lens": true
    },
    "requiresDetailByModel": {
      "kim_lens": true,
      "um_lens": true
    }
  },
  {
    "category": "fogf",
    "id": "fogf",
    "label": "fog fraction",
    "patternByModel": {
      "um_lens": "__proxy__"
    },
    "forecastStepByModel": {
      "um_lens": [
        {
          "start": 4,
          "end": 72,
          "step": 1
        }
      ]
    },
    "imageCountByModel": {
      "um_lens": 1
    },
    "usesForecastHourByModel": {
      "um_lens": true
    },
    "requiresDetailByModel": {
      "um_lens": false
    }
  },
  {
    "category": "pgst",
    "id": "pgst",
    "label": "강풍가이던스",
    "patternByModel": {
      "kim_lens": "__proxy__",
      "um_lens": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_lens": [
        {
          "start": 4,
          "end": 120,
          "step": 1
        }
      ],
      "um_lens": [
        {
          "start": 4,
          "end": 72,
          "step": 1
        }
      ]
    },
    "imageCountByModel": {
      "kim_lens": 1,
      "um_lens": 1
    },
    "usesForecastHourByModel": {
      "kim_lens": true,
      "um_lens": true
    },
    "requiresDetailByModel": {
      "kim_lens": false,
      "um_lens": false
    }
  },
  {
    "category": "mwnd",
    "id": "mwnd",
    "label": "평균(mean)",
    "patternByModel": {
      "kim_lens": "__proxy__",
      "um_lens": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_lens": [
        {
          "start": 4,
          "end": 120,
          "step": 1
        }
      ],
      "um_lens": [
        {
          "start": 4,
          "end": 72,
          "step": 1
        }
      ]
    },
    "imageCountByModel": {
      "kim_lens": 1,
      "um_lens": 1
    },
    "usesForecastHourByModel": {
      "kim_lens": true,
      "um_lens": true
    },
    "requiresDetailByModel": {
      "kim_lens": false,
      "um_lens": false
    }
  },
  {
    "category": "sprd",
    "id": "temp",
    "label": "기온",
    "patternByModel": {
      "kim_lens": "__proxy__",
      "um_lens": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_lens": [
        {
          "start": 4,
          "end": 120,
          "step": 1
        }
      ],
      "um_lens": [
        {
          "start": 4,
          "end": 72,
          "step": 1
        }
      ]
    },
    "imageCountByModel": {
      "kim_lens": 1,
      "um_lens": 1
    },
    "usesForecastHourByModel": {
      "kim_lens": true,
      "um_lens": true
    },
    "requiresDetailByModel": {
      "kim_lens": false,
      "um_lens": false
    }
  },
  {
    "category": "sprd",
    "id": "mslp",
    "label": "해면기압",
    "patternByModel": {
      "kim_lens": "__proxy__",
      "um_lens": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_lens": [
        {
          "start": 3,
          "end": 120,
          "step": 1
        }
      ],
      "um_lens": [
        {
          "start": 3,
          "end": 72,
          "step": 1
        }
      ]
    },
    "imageCountByModel": {
      "kim_lens": 1,
      "um_lens": 1
    },
    "usesForecastHourByModel": {
      "kim_lens": true,
      "um_lens": true
    },
    "requiresDetailByModel": {
      "kim_lens": false,
      "um_lens": false
    }
  }
];
