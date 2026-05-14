const ANALYSIS_CATEGORIES=[
  {
    "id": "asia",
    "name": "분석일기도"
  },
  {
    "id": "hkor",
    "name": "분석일기도(한반도)"
  },
  {
    "id": "kas0",
    "name": "분석장 영역 일기도"
  },
  {
    "type": "header",
    "name": "─────────────────"
  },
  {
    "id": "axas",
    "name": "보조분석도"
  },
  {
    "id": "nhem",
    "name": "북반구분석도"
  },
  {
    "type": "header",
    "name": "─────────────────"
  },
  {
    "id": "rain24",
    "name": "24시간강수"
  },
  {
    "type": "header",
    "name": "─────────────────"
  },
  {
    "id": "skewan",
    "name": "분석단열선도"
  },
  {
    "id": "skewob",
    "name": "관측단열선도"
  },
  {
    "id": "skewds",
    "name": "하강단열선도"
  },
  {
    "type": "header",
    "name": "─────────────────"
  },
  {
    "id": "grtopo",
    "name": "지형과바람"
  },
  {
    "type": "header",
    "name": "─────────────────"
  },
  {
    "id": "dust",
    "name": "황사일기도"
  }
];

const HOURLY_CYCLES=[
  0,
  1,
  2,
  3,
  4,
  5,
  6,
  7,
  8,
  9,
  10,
  11,
  12,
  13,
  14,
  15,
  16,
  17,
  18,
  19,
  20,
  21,
  22,
  23
];

const ANALYSIS_PRODUCTS=[
  {
    "category": "asia",
    "id": "sfc3",
    "label": "3시간:지상",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "asia",
    "id": "sfc3_ptrend",
    "label": "3시간:기압변화",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "asia",
    "id": "sfc1",
    "label": "1시간:지상",
    "patternByModel": {
      "kas": "__proxy__"
    },
    "imageCountByModel": {
      "kas": 1
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "asia",
    "id": "sfc1_ptrend",
    "label": "1시간:기압변화",
    "patternByModel": {
      "kas": "__proxy__"
    },
    "imageCountByModel": {
      "kas": 1
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "asia",
    "id": "surf",
    "label": "지상일기도",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__",
      "ecmwf_ra": "__proxy__",
      "kas": "__proxy__"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1,
      "ecmwf_ra": 1,
      "kas": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false,
      "kas": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false,
      "kas": false
    }
  },
  {
    "category": "asia",
    "id": "surf2",
    "label": "지상일기도(2hPa)",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__",
      "kas": "__proxy__"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1,
      "kas": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false,
      "kas": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false,
      "kas": false
    }
  },
  {
    "category": "asia",
    "id": "up92",
    "label": "고층:925hPa",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__",
      "ecmwf_ra": "__proxy__",
      "kas": "__proxy__"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1,
      "ecmwf_ra": 1,
      "kas": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false,
      "kas": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false,
      "kas": false
    }
  },
  {
    "category": "asia",
    "id": "up85",
    "label": "고층:850hPa",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__",
      "ecmwf_ra": "__proxy__",
      "kas": "__proxy__"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1,
      "ecmwf_ra": 1,
      "kas": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false,
      "kas": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false,
      "kas": false
    }
  },
  {
    "category": "asia",
    "id": "up70",
    "label": "고층:700hPa",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__",
      "ecmwf_ra": "__proxy__",
      "kas": "__proxy__"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1,
      "ecmwf_ra": 1,
      "kas": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false,
      "kas": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false,
      "kas": false
    }
  },
  {
    "category": "asia",
    "id": "up50",
    "label": "고층:500hPa",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__",
      "ecmwf_ra": "__proxy__",
      "kas": "__proxy__"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1,
      "ecmwf_ra": 1,
      "kas": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false,
      "kas": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false,
      "kas": false
    }
  },
  {
    "category": "asia",
    "id": "up30",
    "label": "고층:300hPa",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__",
      "ecmwf_ra": "__proxy__",
      "kas": "__proxy__"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1,
      "ecmwf_ra": 1,
      "kas": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false,
      "kas": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false,
      "kas": false
    }
  },
  {
    "category": "asia",
    "id": "up20",
    "label": "고층:200hPa",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__",
      "ecmwf_ra": "__proxy__",
      "kas": "__proxy__"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1,
      "ecmwf_ra": 1,
      "kas": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false,
      "kas": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false,
      "kas": false
    }
  },
  {
    "category": "asia",
    "id": "up10",
    "label": "고층:100hPa",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__",
      "ecmwf_ra": "__proxy__",
      "kas": "__proxy__"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1,
      "ecmwf_ra": 1,
      "kas": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false,
      "kas": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false,
      "kas": false
    }
  },
  {
    "category": "hkor",
    "id": "anlmod",
    "label": "한반도:기압",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__",
      "kas": "__proxy__"
    },
    "cyclesByModel": {
      "kim_anal": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23
      ],
      "um_anal": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23
      ]
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1,
      "kas": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false,
      "kas": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false,
      "kas": false
    }
  },
  {
    "category": "hkor",
    "id": "ptrend",
    "label": "한반도:기압변화",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__"
    },
    "cyclesByModel": {
      "kim_anal": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23
      ],
      "um_anal": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23
      ]
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "hkor",
    "id": "slptmp",
    "label": "한반도:기압/온위",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__",
      "kas": "__proxy__"
    },
    "cyclesByModel": {
      "kim_anal": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23
      ],
      "um_anal": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23
      ]
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1,
      "kas": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false,
      "kas": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false,
      "kas": false
    }
  },
  {
    "category": "hkor",
    "id": "spdmod",
    "label": "한반도:바람벡터",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__"
    },
    "cyclesByModel": {
      "kim_anal": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23
      ],
      "um_anal": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23
      ]
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "hkor",
    "id": "rhumod",
    "label": "한반도:유선/습도",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__",
      "kas": "__proxy__"
    },
    "cyclesByModel": {
      "kim_anal": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23
      ],
      "um_anal": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23
      ]
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1,
      "kas": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false,
      "kas": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false,
      "kas": false
    }
  },
  {
    "category": "hkor",
    "id": "divmod",
    "label": "한반도:수렴/발산",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__"
    },
    "cyclesByModel": {
      "kim_anal": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23
      ],
      "um_anal": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23
      ]
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "kas0",
    "id": "gph500",
    "label": "500 고도,기온,와도",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "id": "gph700",
    "label": "700 고도,상당온위",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "id": "ept850",
    "label": "850 고도,상당온위",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "id": "ept925",
    "label": "925 고도,상당온위",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "id": "ept950",
    "label": "950 고도,상당온위",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "type": "header",
    "label": "──────────────────"
  },
  {
    "category": "kas0",
    "id": "wnd200",
    "label": "200/300 유선,풍속",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "id": "wnd500",
    "label": "500 유선,풍속",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "id": "wnd700",
    "label": "700 유선,풍속",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "id": "wnd850",
    "label": "850 유선,풍속",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "id": "wnd925",
    "label": "925 유선,풍속",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "id": "wnd950",
    "label": "950 유선,풍속",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "type": "header",
    "label": "──────────────────"
  },
  {
    "category": "kas0",
    "id": "ttd500",
    "label": "500 습수(T-Td)",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "id": "ttd700",
    "label": "700 습수(T-Td)",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "id": "anl850",
    "label": "850 습수(T-Td)",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "id": "anl925",
    "label": "925 습수(T-Td)",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "id": "anl950",
    "label": "950 습수(T-Td)",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "id": "anlsfc",
    "label": "지상 습수(T-Td)",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "id": "moflux",
    "label": "850 수분속",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "type": "header",
    "label": "──────────────────"
  },
  {
    "category": "kas0",
    "id": "con850",
    "label": "850 수렴도,등풍속",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "id": "con925",
    "label": "925 수렴도,등풍속",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "type": "header",
    "label": "──────────────────"
  },
  {
    "category": "kas0",
    "id": "dfh500",
    "label": "500 고도변화",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "id": "dft925",
    "label": "925 기온변화",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "kas0",
    "type": "header",
    "label": "──────────────────"
  },
  {
    "category": "kas0",
    "id": "tgc2d",
    "label": "지상바람",
    "patternByModel": {
      "kas": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "imageCountByModel": {
      "kas": 2
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": false
    }
  },
  {
    "category": "axas",
    "id": "axfe",
    "label": "종합장(전구)",
    "patternByModel": {
      "kim_anal": [
        "__proxy__",
        "__proxy__"
      ],
      "um_anal": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "cyclesByModel": {
      "kim_anal": [
        0,
        12
      ],
      "um_anal": [
        0,
        12
      ]
    },
    "imageCountByModel": {
      "kim_anal": 2,
      "um_anal": 2
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "axas",
    "id": "irdf",
    "label": "적외분석장",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "cyclesByModel": {
      "kim_anal": [
        0,
        12
      ],
      "um_anal": [
        0,
        12
      ]
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 2
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "axas",
    "id": "wvdf",
    "label": "수증기분석장",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "cyclesByModel": {
      "kim_anal": [
        0,
        12
      ],
      "um_anal": [
        0,
        12
      ]
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 2
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "axas",
    "id": "axrg",
    "label": "종합장(지역)",
    "patternByModel": {
      "um_anal": [
        "__proxy__",
        "__proxy__"
      ],
      "ecmwf_ra": [
        "__proxy__",
        "__proxy__"
      ]
    },
    "archiveStartByModel": {
      "um_anal": "2002-09-01"
    },
    "archiveEndByModel": {
      "ecmwf_ra": "2002-08-31"
    },
    "cyclesByModel": {
      "um_anal": [
        0,
        12
      ]
    },
    "imageCountByModel": {
      "um_anal": 2,
      "ecmwf_ra": 2
    },
    "usesForecastHourByModel": {
      "um_anal": false,
      "ecmwf_ra": false
    },
    "requiresDetailByModel": {
      "um_anal": false,
      "ecmwf_ra": false
    }
  },
  {
    "category": "nhem",
    "id": "anlmod",
    "label": "500hPa 분석도",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "nhem",
    "id": "difmod",
    "label": "500hPa 분석도",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "nhem",
    "type": "header",
    "label": "──────────────────"
  },
  {
    "category": "nhem",
    "id": "surfce",
    "label": "지상분석과 강수량",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__",
      "ecmwf_ra": "__proxy__"
    },
    "archiveStartByModel": {
      "um_anal": "2010-01-01"
    },
    "archiveEndByModel": {
      "ecmwf_ra": "2009-12-31"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1,
      "ecmwf_ra": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false
    }
  },
  {
    "category": "nhem",
    "id": "gph500",
    "label": "500hPa 와도분석",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__",
      "ecmwf_ra": "__proxy__"
    },
    "archiveStartByModel": {
      "um_anal": "2010-01-01"
    },
    "archiveEndByModel": {
      "ecmwf_ra": "2009-12-31"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1,
      "ecmwf_ra": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false
    }
  },
  {
    "category": "nhem",
    "id": "dfh500",
    "label": "500hPa 고도분석",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__"
    },
    "archiveStartByModel": {
      "um_anal": "2010-01-01"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "nhem",
    "id": "d24h50",
    "label": "500hPa 고도분석증분(1)",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__"
    },
    "archiveStartByModel": {
      "um_anal": "2010-01-01"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "nhem",
    "id": "d12h50",
    "label": "500hPa 고도분석증분(2)",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__"
    },
    "archiveStartByModel": {
      "um_anal": "2010-01-01"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "nhem",
    "id": "dft500",
    "label": "500hPa 기온분석",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__"
    },
    "archiveStartByModel": {
      "um_anal": "2010-01-01"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "nhem",
    "id": "dft850",
    "label": "850hPa 기온분석",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__"
    },
    "archiveStartByModel": {
      "um_anal": "2010-01-01"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "nhem",
    "id": "ept850",
    "label": "850hPa 온위분석",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__"
    },
    "archiveStartByModel": {
      "um_anal": "2010-01-01"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "nhem",
    "id": "mxr850",
    "label": "850hPa 습기분석",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__"
    },
    "archiveStartByModel": {
      "um_anal": "2010-01-01"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "nhem",
    "id": "gph850",
    "label": "하층 바람분석",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__",
      "ecmwf_ra": "__proxy__"
    },
    "archiveStartByModel": {
      "um_anal": "2010-01-01"
    },
    "archiveEndByModel": {
      "ecmwf_ra": "2009-12-31"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1,
      "ecmwf_ra": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false
    }
  },
  {
    "category": "nhem",
    "id": "gph200",
    "label": "상층 바람분석",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__",
      "ecmwf_ra": "__proxy__"
    },
    "archiveStartByModel": {
      "um_anal": "2010-01-01"
    },
    "archiveEndByModel": {
      "ecmwf_ra": "2009-12-31"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1,
      "ecmwf_ra": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false
    }
  },
  {
    "category": "nhem",
    "id": "gph200",
    "label": "상층 바람분석",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__",
      "ecmwf_ra": "__proxy__"
    },
    "archiveStartByModel": {
      "um_anal": "2010-01-01"
    },
    "archiveEndByModel": {
      "ecmwf_ra": "2009-12-31"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1,
      "ecmwf_ra": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false,
      "ecmwf_ra": false
    }
  },
  {
    "category": "rain24",
    "id": "rain24",
    "label": "24시간 강수량",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  },
  {
    "category": "skewan",
    "id": "skewan",
    "label": "분석단열선도",
    "patternByModel": {
      "kas": "__proxy__"
    },
    "imageCountByModel": {
      "kas": 1
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": true
    }
  },
  {
    "category": "skewob",
    "id": "skewob",
    "label": "관측단열선도",
    "patternByModel": {
      "obs_upper": "__proxy__"
    },
    "imageCountByModel": {
      "obs_upper": 1
    },
    "usesForecastHourByModel": {
      "obs_upper": false
    },
    "requiresDetailByModel": {
      "obs_upper": true
    }
  },
  {
    "category": "skewds",
    "id": "skewds",
    "label": "하강단열선도",
    "patternByModel": {
      "obs_upper": "__proxy__"
    },
    "imageCountByModel": {
      "obs_upper": 1
    },
    "usesForecastHourByModel": {
      "obs_upper": false
    },
    "requiresDetailByModel": {
      "obs_upper": true
    }
  },
  {
    "category": "grtopo",
    "id": "grtopo",
    "label": "지형과바람",
    "patternByModel": {
      "kas": "__proxy__"
    },
    "imageCountByModel": {
      "kas": 1
    },
    "usesForecastHourByModel": {
      "kas": false
    },
    "requiresDetailByModel": {
      "kas": true
    }
  },
  {
    "category": "dust",
    "id": "smsand",
    "label": "황사일기도",
    "patternByModel": {
      "kim_anal": "__proxy__",
      "um_anal": "__proxy__"
    },
    "imageCountByModel": {
      "kim_anal": 1,
      "um_anal": 1
    },
    "usesForecastHourByModel": {
      "kim_anal": false,
      "um_anal": false
    },
    "requiresDetailByModel": {
      "kim_anal": false,
      "um_anal": false
    }
  }
];

const ANALYSIS_PRODUCT_CATEGORY_UI_CONFIG={
  "rain24": {
    "hideProductSelect": true
  },
  "skewan": {
    "hideProductSelect": true
  },
  "skewob": {
    "hideProductSelect": true
  },
  "skewds": {
    "hideProductSelect": true
  },
  "grtopo": {
    "hideProductSelect": true
  }
};

const ANALYSIS_CATEGORY_MODEL_RESTRICTIONS={
  "skewob": {
    "allowedModels": [
      "obs_upper"
    ],
    "fallbackModel": "obs_upper"
  },
  "skewds": {
    "allowedModels": [
      "obs_upper"
    ],
    "fallbackModel": "obs_upper"
  }
};

const ANALYSIS_SELECTION_MODEL_RESTRICTIONS={
  "asia:sfc1": {
    "allowedModels": [
      "kas"
    ],
    "fallbackModel": "kas",
    "allowModelSwitch": true
  },
  "asia:sfc1_ptrend": {
    "allowedModels": [
      "kas"
    ],
    "fallbackModel": "kas",
    "allowModelSwitch": true
  }
};

const ANALYSIS_DEFAULT_PRODUCT_BY_CATEGORY={};
