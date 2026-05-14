const PRODUCT_CATEGORIES=[
  {
    "id": "asia",
    "name": "기본예상도"
  },
  {
    "id": "hkor",
    "name": "기본예상도(한반도)"
  },
  {
    "id": "lkor1",
    "name": "국지모델(한반도)"
  },
  {
    "id": "lkor2",
    "name": "국지모델(상세영역)"
  },
  {
    "id": "nhem",
    "name": "북반구예상"
  },
  {
    "id": "radm",
    "name": "구름모의영상"
  },
  {
    "id": "isen",
    "name": "등온위면분석"
  },
  {
    "id": "wtem1",
    "name": "상세-바람기온"
  },
  {
    "id": "wtem2",
    "name": "상세바람-기온(확장영역)"
  },
  {
    "type": "header",
    "name": "─────────────────"
  },
  {
    "id": "skew",
    "name": "예상단열선도"
  },
  {
    "id": "city",
    "name": "연직시계열"
  }
];

const PRODUCTS=[
  {
    "category": "asia",
    "type": "header",
    "label": "──── 고도/기온 ────"
  },
  {
    "category": "asia",
    "id": "gph200",
    "label": "200/300 고도,기온,풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "gph500",
    "label": "500 고도,기온,풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "gph700",
    "label": "700 고도,상당온위",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "ept850",
    "label": "850 고도,상당온위",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "ept925",
    "label": "925 고도,상당온위",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "thk500",
    "label": "1000-500 층후",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "thk700",
    "label": "1000-700 층후",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "thk850",
    "label": "1000-850 층후",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "type": "header",
    "label": "──── 유선/풍속 ────"
  },
  {
    "category": "asia",
    "id": "wnd200",
    "label": "200/300 유선,풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "wnd500",
    "label": "500 유선,풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "wnd700",
    "label": "700 유선,풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "wnd850",
    "label": "850 유선,풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "wnd925",
    "label": "925 유선,풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "type": "header",
    "label": "────── 강수 ──────"
  },
  {
    "category": "asia",
    "id": "surfce",
    "label": "해면기압, 누적강수량",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "acrain",
    "label": "총누적강수량",
    "patternByModel": {
      "um_gdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "um_gdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "um_gdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "um_gdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "rain3h",
    "label": "3시간 누적강수량",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "rain6h",
    "label": "6시간 누적강수량",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "rain12",
    "label": "12시간 누적강수량",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    }
  },
  {
    "category": "asia",
    "id": "rainth",
    "label": "총누적강수량(3시간간격)",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "raint6",
    "label": "총누적강수량(6시간간격)",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "rndays",
    "label": "총누적강수량(단기예보용)",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    }
  },
  {
    "category": "asia",
    "id": "snw950",
    "label": "눈혼합비",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false
    }
  },
  {
    "category": "asia",
    "id": "acsnow",
    "label": "강설량",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "acptot",
    "label": "강수량",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "anltpw",
    "label": "가강수량, MSLP",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "type": "header",
    "label": "──── 습수/수분속 ────"
  },
  {
    "category": "asia",
    "id": "ttd700",
    "label": "700 습수(T-Td)",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "anl850",
    "label": "850 습수(T-Td)",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "anl925",
    "label": "925 습수(T-Td)",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "anlsfc",
    "label": "지상 습수(T-Td)",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "fxko78",
    "label": "700-850 습수도",
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
      "kim_gdps": false,
      "um_gdps": false,
      "kim_rdps": false
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "kim_rdps": false
    }
  },
  {
    "category": "asia",
    "id": "moflux",
    "label": "850 수분속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "type": "header",
    "label": "──── 발산/수렴 ────"
  },
  {
    "category": "asia",
    "id": "div200",
    "label": "200/300 발산장,등풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "con850",
    "label": "850 수렴도,등풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "type": "header",
    "label": "────── 전선 ──────"
  },
  {
    "category": "asia",
    "id": "frg700",
    "label": "700 전선강도,고도,기온",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "frg850",
    "label": "850 전선강도,고도,기온",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "frg925",
    "label": "925 전선강도,고도,기온",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "type": "header",
    "label": "─── 역학적 강제력 ───"
  },
  {
    "category": "asia",
    "id": "dfmslp",
    "label": "지상 기압변화",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "advort",
    "label": "500 와도이류",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "dfh500",
    "label": "500 고도변화",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "vel700",
    "label": "700 상승속도",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "dft850",
    "label": "850 기온변화",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "gph850",
    "label": "850 혼합비",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "adthck",
    "label": "1000-700 층후이류",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "type": "header",
    "label": "────── 기타 ──────"
  },
  {
    "category": "asia",
    "id": "tgc2d",
    "label": "지상바람",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "archiveStartByModel": {
      "um_ldps": "2018-01-18"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "asia",
    "id": "fxfe",
    "label": "종합보조예상",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "um_rdps": true,
      "kwrf_rdps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "um_rdps": false,
      "kwrf_rdps": false
    }
  },
  {
    "category": "hkor",
    "type": "header",
    "label": "──── 고도/기온 ────"
  },
  {
    "category": "hkor",
    "id": "gph200",
    "label": "200/300 고도,기온,풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "gph500",
    "label": "500 고도,기온,풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "gph700",
    "label": "700 고도,상당온위",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "ept850",
    "label": "850 고도,상당온위",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "ept925",
    "label": "925 고도,상당온위",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "thk500",
    "label": "1000-500 층후",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "thk700",
    "label": "1000-700 층후",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "thk850",
    "label": "1000-850 층후",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "type": "header",
    "label": "──── 유선/풍속 ────"
  },
  {
    "category": "hkor",
    "id": "wnd200",
    "label": "200/300 유선,풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "wnd500",
    "label": "500 유선,풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "wnd700",
    "label": "700 유선,풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "wnd850",
    "label": "850 유선,풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "wnd925",
    "label": "925 유선,풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "type": "header",
    "label": "────── 강수 ──────"
  },
  {
    "category": "hkor",
    "id": "acrain",
    "label": "총누적강수량",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "acptot",
    "label": "시간별 누적강수량",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "ukmo": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "ukmo": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "ukmo": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "ukmo": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "prcp3h",
    "label": "3시간 누적강수량",
    "forecastStepByModel": {
      "kim_rdps": [
        {
          "start": 0,
          "end": 120,
          "step": 3
        }
      ],
      "kim_ldps": [
        {
          "start": 0,
          "end": 48,
          "step": 3
        }
      ]
    },
    "patternByModel": {
      "kim_rdps": "__proxy__",
      "kim_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_rdps": 1,
      "kim_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_rdps": true,
      "kim_ldps": true
    },
    "requiresDetailByModel": {
      "kim_rdps": false,
      "kim_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "snw950",
    "label": "눈혼합비",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "tmerge",
    "label": "신적설(수상당량비 적용)",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "anltpw",
    "label": "가강수량, MSLP",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "type": "header",
    "label": "──── 습수/수분속 ────"
  },
  {
    "category": "hkor",
    "id": "ttd700",
    "label": "700 습수(T-Td)",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "anl850",
    "label": "850 습수(T-Td)",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "anl925",
    "label": "925 습수(T-Td)",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "anlsfc",
    "label": "지상 습수(T-Td)",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "moflux",
    "label": "850 수분속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "type": "header",
    "label": "──── 발산/수렴 ────"
  },
  {
    "category": "hkor",
    "id": "div200",
    "label": "200/300 발산장,등풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "con850",
    "label": "850 수렴도,등풍속",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "type": "header",
    "label": "────── 전선 ──────"
  },
  {
    "category": "hkor",
    "id": "frg700",
    "label": "700 전선강도,고도,기온",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "frg850",
    "label": "850 전선강도,고도,기온",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "frg925",
    "label": "925 전선강도,고도,기온",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "type": "header",
    "label": "─── 역학적 강제력 ───"
  },
  {
    "category": "hkor",
    "id": "dfmslp",
    "label": "지상 기압변화",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "advort",
    "label": "500 와도이류",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "dfh500",
    "label": "500 고도변화",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "vel700",
    "label": "700 상승속도",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "dft850",
    "label": "850 기온변화",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "gph850",
    "label": "850 혼합비",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "adthck",
    "label": "1000-700 층후이류",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "type": "header",
    "label": "────── 기타 ──────"
  },
  {
    "category": "hkor",
    "id": "wndgst",
    "label": "강풍가이던스",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "hkor",
    "id": "tdif",
    "label": "상하층 기온차 분석",
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
    "category": "hkor",
    "id": "guid",
    "label": "대류불안정 종합분석",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "um_rdps": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_rdps": [
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
    "category": "klfs_vdps",
    "id": "gph200",
    "label": "200 고도,기온,풍속",
    "patternByModel": {
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "gph300",
    "label": "300 고도,기온,풍속",
    "patternByModel": {
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "gph500",
    "label": "500 고도,기온,와도",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "gph700",
    "label": "700 고도,기온,상당온위",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "gph850",
    "label": "850 고도,기온,비습,바람",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "gph925",
    "label": "925 고도,기온,비습,바람",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "thk700",
    "label": "1000-700 층후, 850 상당온위",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "type": "header",
    "label": "──────────────────"
  },
  {
    "category": "klfs_vdps",
    "id": "wnd200",
    "label": "200 유선,풍속",
    "patternByModel": {
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "wnd500",
    "label": "500 유선,풍속",
    "patternByModel": {
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "wnd850",
    "label": "850 유선,풍속",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "type": "header",
    "label": "──────────────────"
  },
  {
    "category": "klfs_vdps",
    "id": "surfce",
    "label": "해면기압, 누적강수량",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "acrain",
    "label": "총누적강수량",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "prcptp",
    "label": "강수유형",
    "patternByModel": {
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "lowdbz",
    "label": "레이더 반사도",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "type": "header",
    "label": "──────────────────"
  },
  {
    "category": "klfs_vdps",
    "id": "ttd700",
    "label": "700 습수(T-Td)",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "anl850",
    "label": "850 습수(T-Td)",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "anl925",
    "label": "925 습수(T-Td)",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "anlsfc",
    "label": "지상 습수(T-Td)",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "moflux",
    "label": "850 수분속",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "div200",
    "label": "200 발산",
    "patternByModel": {
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "con850",
    "label": "850 수렴,풍속",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "con925",
    "label": "925 수렴,풍속",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "type": "header",
    "label": "──────────────────"
  },
  {
    "category": "klfs_vdps",
    "id": "vel700",
    "label": "700 상승속도",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "type": "header",
    "label": "──────────────────"
  },
  {
    "category": "klfs_vdps",
    "id": "tmpwnd",
    "label": "10m 바람, 2m 기온",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "sfcshm",
    "label": "지상비습",
    "patternByModel": {
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "visblt",
    "label": "지상시정",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "type": "header",
    "label": "──────────────────"
  },
  {
    "category": "klfs_vdps",
    "id": "kindex",
    "label": "K-Index",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "sindex",
    "label": "쇼월터 index",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "lindex",
    "label": "Lifted index",
    "patternByModel": {
      "kim_klfs": "__proxy__",
      "um_klfs": "__proxy__",
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_klfs": 1,
      "um_klfs": 1,
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "kim_klfs": true,
      "um_klfs": true,
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "kim_klfs": false,
      "um_klfs": false,
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "type": "header",
    "label": "──────────────────"
  },
  {
    "category": "klfs_vdps",
    "id": "hghcld",
    "label": "상층운량",
    "patternByModel": {
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "midcld",
    "label": "중층운량",
    "patternByModel": {
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "um_vdps": false
    }
  },
  {
    "category": "klfs_vdps",
    "id": "lowcld",
    "label": "하층운량",
    "patternByModel": {
      "um_vdps": "__proxy__"
    },
    "imageCountByModel": {
      "um_vdps": 1
    },
    "usesForecastHourByModel": {
      "um_vdps": true
    },
    "requiresDetailByModel": {
      "um_vdps": false
    }
  },
  {
    "category": "lkor1",
    "id": "tgcwnd",
    "label": "지상기온",
    "patternByModel": {
      "kim_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "lkor1",
    "id": "grtopo",
    "label": "지형과바람",
    "patternByModel": {
      "kim_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "lkor1",
    "id": "olwrad",
    "label": "장파복사량",
    "patternByModel": {
      "kim_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "lkor1",
    "id": "cldvlo",
    "label": "최하층운량",
    "patternByModel": {
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "um_ldps": false
    }
  },
  {
    "category": "lkor1",
    "id": "bltype",
    "label": "경계층타입",
    "patternByModel": {
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "um_ldps": false
    }
  },
  {
    "category": "lkor1",
    "id": "surfce",
    "label": "해면기압,누적강수량",
    "patternByModel": {
      "kim_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    }
  },
  {
    "category": "lkor1",
    "id": "acrain",
    "label": "총누적강수량",
    "patternByModel": {
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "um_ldps": false
    }
  },
  {
    "category": "lkor2",
    "id": "surfce",
    "label": "시간강수량",
    "patternByModel": {
      "kim_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    }
  },
  {
    "category": "lkor2",
    "id": "acrain",
    "label": "누적강수량",
    "patternByModel": {
      "kim_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    }
  },
  {
    "category": "lkor2",
    "id": "tgcwnd",
    "label": "지상기온",
    "patternByModel": {
      "kim_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    }
  },
  {
    "category": "lkor2",
    "id": "grtopo",
    "label": "지형과바람",
    "patternByModel": {
      "kim_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    }
  },
  {
    "category": "lkor2",
    "id": "vrtwnd",
    "label": "최하층연직속도",
    "patternByModel": {
      "kim_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    }
  },
  {
    "category": "lkor2",
    "id": "rmir",
    "label": "구름모의영상",
    "patternByModel": {
      "kim_rdps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_rdps": [
        {
          "start": 1,
          "end": 48,
          "step": 1
        }
      ]
    },
    "imageCountByModel": {
      "kim_rdps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_rdps": true,
      "um_ldps": true
    }
  },
  {
    "category": "lkor2",
    "id": "gstwnd",
    "label": "강풍(산불지원)",
    "patternByModel": {
      "kim_rdps": "__proxy__",
      "kim_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_rdps": 1,
      "kim_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_rdps": true,
      "kim_ldps": true
    },
    "requiresDetailByModel": {
      "kim_rdps": true,
      "kim_ldps": true
    }
  },
  {
    "category": "nhem",
    "id": "surfce",
    "label": "해면기압,강수량",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    }
  },
  {
    "category": "nhem",
    "id": "gph500",
    "label": "500hPa 고도,기온",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    }
  },
  {
    "category": "nhem",
    "id": "dfh500",
    "label": "500hPa 고도변화,기온",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    }
  },
  {
    "category": "nhem",
    "id": "dft500",
    "label": "500hPa 고도,기온변화",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    }
  },
  {
    "category": "nhem",
    "id": "dft850",
    "label": "850hPa 고도,기온변화",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    }
  },
  {
    "category": "nhem",
    "id": "ept850",
    "label": "850hPa 고도,상당온위",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    }
  },
  {
    "category": "nhem",
    "id": "mxr850",
    "label": "850hPa 고도,혼합비",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    }
  },
  {
    "category": "nhem",
    "id": "gph850",
    "label": "하층바람",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    }
  },
  {
    "category": "nhem",
    "id": "gph200",
    "label": "상층바람",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    }
  },
  {
    "category": "radm",
    "id": "olwrad",
    "label": "지구장파 복사량",
    "patternByModel": {
      "kim_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "um_gdps": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 2,
      "um_gdps": 2
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false
    }
  },
  {
    "category": "radm",
    "id": "rmir",
    "label": "적외채널:천리안2A",
    "patternByModel": {
      "kim_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "um_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "kim_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "um_ldps": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_gdps": [
        {
          "start": 0,
          "end": 12,
          "step": 1
        },
        {
          "start": 15,
          "end": 144,
          "step": 3
        }
      ],
      "um_gdps": [
        {
          "start": 0,
          "end": 12,
          "step": 1
        },
        {
          "start": 15,
          "end": 144,
          "step": 3
        }
      ],
      "kim_rdps": [
        {
          "start": 1,
          "end": 48,
          "step": 1
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 2,
      "um_gdps": 2,
      "kim_rdps": 2,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "kim_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "kim_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "radm",
    "id": "rmwv",
    "label": "수증기채널:천리안2A",
    "patternByModel": {
      "kim_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "um_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "kim_rdps": [
        "__proxy__",
        "__proxy__"
      ],
      "um_ldps": "__proxy__"
    },
    "forecastStepByModel": {
      "kim_gdps": [
        {
          "start": 0,
          "end": 12,
          "step": 1
        },
        {
          "start": 15,
          "end": 144,
          "step": 3
        }
      ],
      "um_gdps": [
        {
          "start": 0,
          "end": 12,
          "step": 1
        },
        {
          "start": 15,
          "end": 144,
          "step": 3
        }
      ],
      "kim_rdps": [
        {
          "start": 1,
          "end": 48,
          "step": 1
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 2,
      "um_gdps": 2,
      "kim_rdps": 2,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "kim_rdps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "kim_rdps": false,
      "um_ldps": false
    }
  },
  {
    "category": "isen",
    "id": "isen",
    "label": "등온위면분석",
    "patternByModel": {
      "kim_gdps": [
        "__proxy__",
        "__proxy__"
      ],
      "um_gdps": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 2,
      "um_gdps": 2
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": true,
      "um_gdps": true
    }
  },
  {
    "category": "wtem1",
    "id": "wsfc",
    "label": "WTEM: 지상",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "um_ldps": "__proxy__",
      "kim_ldps": "__proxy__"
    },
    "forecastStepByModel": {
      "um_ldps": [
        {
          "start": 0,
          "end": 48,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "um_ldps": 1,
      "kim_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "um_ldps": true,
      "kim_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "um_ldps": false,
      "kim_ldps": false
    }
  },
  {
    "category": "wtem1",
    "id": "wt00",
    "label": "WTEM: 1000hPa",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "um_ldps": "__proxy__",
      "kim_ldps": "__proxy__"
    },
    "forecastStepByModel": {
      "um_ldps": [
        {
          "start": 0,
          "end": 48,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "um_ldps": 1,
      "kim_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "um_ldps": true,
      "kim_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "um_ldps": false,
      "kim_ldps": false
    }
  },
  {
    "category": "wtem1",
    "id": "wt92",
    "label": "WTEM: 925hPa",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "um_ldps": "__proxy__",
      "kim_ldps": "__proxy__"
    },
    "forecastStepByModel": {
      "um_ldps": [
        {
          "start": 0,
          "end": 48,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "um_ldps": 1,
      "kim_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "um_ldps": true,
      "kim_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "um_ldps": false,
      "kim_ldps": false
    }
  },
  {
    "category": "wtem1",
    "id": "wt85",
    "label": "WTEM: 850hPa",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "um_ldps": "__proxy__",
      "kim_ldps": "__proxy__"
    },
    "forecastStepByModel": {
      "um_ldps": [
        {
          "start": 0,
          "end": 48,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "um_ldps": 1,
      "kim_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "um_ldps": true,
      "kim_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "um_ldps": false,
      "kim_ldps": false
    }
  },
  {
    "category": "wtem1",
    "id": "wt70",
    "label": "WTEM: 700hPa",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "um_ldps": "__proxy__",
      "kim_ldps": "__proxy__"
    },
    "forecastStepByModel": {
      "um_ldps": [
        {
          "start": 0,
          "end": 48,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "um_ldps": 1,
      "kim_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "um_ldps": true,
      "kim_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "um_ldps": false,
      "kim_ldps": false
    }
  },
  {
    "category": "wtem1",
    "id": "wt50",
    "label": "WTEM: 500hPa",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "um_ldps": "__proxy__",
      "kim_ldps": "__proxy__"
    },
    "forecastStepByModel": {
      "um_ldps": [
        {
          "start": 0,
          "end": 48,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "um_ldps": 1,
      "kim_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "um_ldps": true,
      "kim_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "um_ldps": false,
      "kim_ldps": false
    }
  },
  {
    "category": "wtem1",
    "id": "wt30",
    "label": "WTEM: 300hPa",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "um_ldps": "__proxy__",
      "kim_ldps": "__proxy__"
    },
    "forecastStepByModel": {
      "um_ldps": [
        {
          "start": 0,
          "end": 48,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "um_ldps": 1,
      "kim_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "um_ldps": true,
      "kim_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "um_ldps": false,
      "kim_ldps": false
    }
  },
  {
    "category": "wtem1",
    "id": "wt20",
    "label": "WTEM: 200hPa",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "um_ldps": "__proxy__",
      "kim_ldps": "__proxy__"
    },
    "forecastStepByModel": {
      "um_ldps": [
        {
          "start": 0,
          "end": 48,
          "step": 3
        }
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "um_ldps": 1,
      "kim_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "um_ldps": true,
      "kim_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "um_ldps": false,
      "kim_ldps": false
    }
  },
  {
    "category": "wtem2",
    "id": "wsfc",
    "label": "WTEM-지상",
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
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 2,
      "um_gdps": 2,
      "ecmwf": 2
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    }
  },
  {
    "category": "wtem2",
    "id": "wt92",
    "label": "WTEM-925hPa",
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
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 2,
      "um_gdps": 2,
      "ecmwf": 2
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    }
  },
  {
    "category": "wtem2",
    "id": "wt85",
    "label": "WTEM-850hPa",
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
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 2,
      "um_gdps": 2,
      "ecmwf": 2
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    }
  },
  {
    "category": "wtem2",
    "id": "wt70",
    "label": "WTEM-700hPa",
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
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 2,
      "um_gdps": 2,
      "ecmwf": 2
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    }
  },
  {
    "category": "wtem2",
    "id": "wt50",
    "label": "WTEM-500hPa",
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
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 2,
      "um_gdps": 2,
      "ecmwf": 2
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    }
  },
  {
    "category": "wtem2",
    "id": "wt20",
    "label": "WTEM-200~300hPa",
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
      ]
    },
    "imageCountByModel": {
      "kim_gdps": 2,
      "um_gdps": 2,
      "ecmwf": 2
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true
    },
    "requiresDetailByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    }
  },
  {
    "category": "skew",
    "id": "skew",
    "label": "예상단열선도",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    },
    "requiresDetailByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    }
  },
  {
    "category": "city",
    "id": "shrt",
    "label": "단기",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__",
      "kim_rdps": "__proxy__",
      "um_rdps": "__proxy__",
      "kwrf_rdps": "__proxy__",
      "kim_ldps": "__proxy__",
      "um_ldps": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1,
      "kim_rdps": 1,
      "um_rdps": 1,
      "kwrf_rdps": 1,
      "kim_ldps": 1,
      "um_ldps": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false,
      "kim_rdps": false,
      "um_rdps": false,
      "kwrf_rdps": false,
      "kim_ldps": false,
      "um_ldps": false
    },
    "requiresDetailByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true,
      "kim_rdps": true,
      "um_rdps": true,
      "kwrf_rdps": true,
      "kim_ldps": true,
      "um_ldps": true
    }
  },
  {
    "category": "city",
    "id": "long",
    "label": "중기",
    "patternByModel": {
      "kim_gdps": "__proxy__",
      "um_gdps": "__proxy__",
      "ecmwf": "__proxy__"
    },
    "imageCountByModel": {
      "kim_gdps": 1,
      "um_gdps": 1,
      "ecmwf": 1
    },
    "usesForecastHourByModel": {
      "kim_gdps": false,
      "um_gdps": false,
      "ecmwf": false
    },
    "requiresDetailByModel": {
      "kim_gdps": true,
      "um_gdps": true,
      "ecmwf": true
    }
  }
];
