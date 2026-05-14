const HAZARD_CATEGORIES=[
  {
    "id": "stbl",
    "name": "안정도(대류)"
  },
  {
    "id": "lgtn",
    "name": "낙뢰"
  },
  {
    "id": "fogv",
    "name": "안개"
  },
  {
    "id": "airq",
    "name": "대기안정도"
  }
];

const HAZARD_PRODUCTS=[
  {
    "category": "stbl",
    "id": "kindex",
    "label": "K Index",
    "patternByModel": {
      "kim_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "um_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "ecmwf": [
        "__proxy__",
        "__proxy__"
      ],
      "kim_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "um_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "kwrf_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "kim_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 2,
      "um_gdps": 2,
      "ecmwf": 2,
      "kim_rdps": 2,
      "um_rdps": 2,
      "kwrf_rdps": 2,
      "kim_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false
    }
  },
  {
    "category": "stbl",
    "id": "lindex",
    "label": "Lifted Index",
    "patternByModel": {
      "kim_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "um_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "ecmwf": [
        "__proxy__",
        "__proxy__"
      ],
      "kim_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "um_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "kwrf_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "kim_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 2,
      "um_gdps": 2,
      "ecmwf": 2,
      "kim_rdps": 2,
      "um_rdps": 2,
      "kwrf_rdps": 2,
      "kim_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false
    }
  },
  {
    "category": "stbl",
    "id": "sindex",
    "label": "쇼월터 Index",
    "patternByModel": {
      "kim_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "um_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "ecmwf": [
        "__proxy__",
        "__proxy__"
      ],
      "kim_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "um_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "kwrf_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "kim_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 2,
      "um_gdps": 2,
      "ecmwf": 2,
      "kim_rdps": 2,
      "um_rdps": 2,
      "kwrf_rdps": 2,
      "kim_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false
    }
  },
  {
    "category": "stbl",
    "id": "totidx",
    "label": "토탈 total 지수",
    "patternByModel": {
      "kim_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "um_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "ecmwf": [
        "__proxy__",
        "__proxy__"
      ],
      "kim_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "um_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "kwrf_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "kim_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 2,
      "um_gdps": 2,
      "ecmwf": 2,
      "kim_rdps": 2,
      "um_rdps": 2,
      "kwrf_rdps": 2,
      "kim_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false
    }
  },
  {
    "category": "stbl",
    "id": "gdiidx",
    "label": "GDI 지수",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "kim_rdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "kim_rdps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "kim_rdps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "kim_rdps": false
    }
  },
  {
    "category": "stbl",
    "id": "sbcape",
    "label": "지상기반 CAPE",
    "patternByModel": {
      "kim_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "um_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "ecmwf": [
        "__proxy__",
        "__proxy__"
      ],
      "kim_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "kim_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 2,
      "um_gdps": 2,
      "ecmwf": 2,
      "kim_rdps": 2,
      "kim_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "kim_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "kim_ldps": false
    }
  },
  {
    "category": "stbl",
    "id": "srh03k",
    "label": "SRH",
    "patternByModel": {
      "kim_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "um_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "ecmwf": [
        "__proxy__",
        "__proxy__"
      ],
      "kim_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "um_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "kwrf_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "kim_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 2,
      "um_gdps": 2,
      "ecmwf": 2,
      "kim_rdps": 2,
      "um_rdps": 2,
      "kwrf_rdps": 2,
      "kim_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false
    }
  },
  {
    "category": "stbl",
    "id": "frcvel",
    "label": "지면마찰속도",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "um_rdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "um_rdps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "um_rdps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "um_rdps": false
    }
  },
  {
    "category": "lgtn",
    "id": "lght",
    "label": "낙뢰가이던스",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "um_rdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "um_rdps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "um_rdps": false
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "um_rdps": false
    }
  },
  {
    "category": "lgtn",
    "id": "lgtidx",
    "label": "구름물리:낙뢰가이던스",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "um_rdps": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_gdps": [
        {
          "start": 0,
          "end": 84,
          "step": 3
        }
      ],
      "um_gdps": [
        {
          "start": 0,
          "end": 84,
          "step": 3
        }
      ],
      "ecmwf": [
        {
          "start": 0,
          "end": 84,
          "step": 3
        }
      ],
      "um_rdps": [
        {
          "start": 0,
          "end": 84,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "um_rdps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "um_rdps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "um_rdps": false
    }
  },
  {
    "category": "fogv",
    "id": "fxko4s",
    "label": "습도 예상도",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "fogv",
    "id": "visnew",
    "label": "구름변수:안개가이던스",
    "patternByModel": {
      "um_gdps": "__proxy__",
      "kim_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "um_gdps": 1,
      "kim_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "um_gdps": true,
      "kim_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "um_gdps": false,
      "kim_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "airq",
    "id": "airstb",
    "label": "안정도",
    "patternByModel": {
      "kim_gdps": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_gdps": [
        {
          "start": 0,
          "end": 144,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false
    }
  },
  {
    "category": "airq",
    "id": "wndsfc",
    "label": "지표면 풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_gdps": [
        {
          "start": 0,
          "end": 144,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false
    }
  },
  {
    "category": "airq",
    "id": "wnd850",
    "label": "850hPa 풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_gdps": [
        {
          "start": 0,
          "end": 144,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false
    }
  },
  {
    "category": "airq",
    "id": "pblhgt",
    "label": "PBL 고도",
    "patternByModel": {
      "kim_gdps": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_gdps": [
        {
          "start": 0,
          "end": 144,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false
    }
  },
  {
    "category": "airq",
    "id": "acptot",
    "label": "3시간 누적강수",
    "patternByModel": {
      "kim_gdps": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_gdps": [
        {
          "start": 0,
          "end": 144,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false
    }
  },
  {
    "category": "airq",
    "id": "ventlt",
    "label": "환기지수",
    "patternByModel": {
      "kim_gdps": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_gdps": [
        {
          "start": 0,
          "end": 144,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false
    }
  },
  {
    "category": "airq",
    "id": "invlay",
    "label": "역전층유무",
    "patternByModel": {
      "kim_gdps": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_gdps": [
        {
          "start": 0,
          "end": 144,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false
    }
  }
];
