const MODELS={
  "kim_gdps": {
    "name": "GDAPS_KIM",
    "archiveStart": "2021-01-01",
    "cycles": [
      0,
      6,
      12,
      18
    ],
    "forecastRules": [
      {
        "cycles": [
          0,
          12
        ],
        "until": "2025-05-13",
        "max": 288
      },
      {
        "cycles": [
          0,
          12
        ],
        "max": 360
      },
      {
        "cycles": [
          6,
          18
        ],
        "max": 84
      }
    ],
    "stepSchemeByCycleGroup": {
      "0,12": [
        {
          "start": 0,
          "end": 84,
          "step": 3
        },
        {
          "start": 90,
          "end": 96,
          "step": 6
        },
        {
          "start": 108,
          "end": 360,
          "step": 12
        }
      ],
      "6,18": [
        {
          "start": 0,
          "end": 84,
          "step": 3
        }
      ]
    }
  },
  "um_gdps": {
    "name": "GDAPS_UM",
    "archiveStart": "2005-12-02",
    "archiveEnd": "2026-04-01",
    "cycles": [
      0,
      6,
      12,
      18
    ],
    "cycleAvailability": [
      {
        "until": "2011-05-22",
        "cycles": [
          0,
          12
        ]
      },
      {
        "from": "2011-05-23",
        "cycles": [
          0,
          6,
          12,
          18
        ]
      }
    ],
    "forecastRules": [
      {
        "until": "2010-05-13",
        "cycles": [
          0,
          12
        ],
        "max": 240
      },
      {
        "from": "2010-05-14",
        "until": "2013-09-30",
        "cycles": [
          0,
          12
        ],
        "max": 252
      },
      {
        "from": "2013-10-01",
        "cycles": [
          0,
          12
        ],
        "max": 288
      },
      {
        "from": "2011-05-23",
        "cycles": [
          6,
          18
        ],
        "max": 84
      }
    ],
    "stepSchemeByCycleGroup": {
      "0,12": [
        {
          "start": 0,
          "end": 84,
          "step": 3
        },
        {
          "start": 90,
          "end": 96,
          "step": 6
        },
        {
          "start": 108,
          "end": 288,
          "step": 12
        }
      ],
      "6,18": [
        {
          "start": 0,
          "end": 84,
          "step": 3
        }
      ]
    }
  },
  "ecmwf": {
    "name": "ECMWF",
    "archiveStart": "2013-01-28",
    "cycles": [
      0,
      12
    ],
    "forecastRules": [
      {
        "cycles": [
          0,
          12
        ],
        "max": 240
      }
    ],
    "stepSchemeByCycleGroup": {
      "0,12": [
        {
          "start": 0,
          "end": 84,
          "step": 3
        },
        {
          "start": 90,
          "end": 96,
          "step": 6
        },
        {
          "start": 108,
          "end": 240,
          "step": 12
        }
      ]
    }
  },
  "ukmo": {
    "name": "UKUM",
    "archiveStart": "2025-11-30",
    "cycles": [
      0,
      12
    ],
    "forecastRules": [
      {
        "cycles": [
          0,
          12
        ],
        "max": 144
      }
    ],
    "stepSchemeByCycleGroup": {
      "0,12": [
        {
          "start": 0,
          "end": 84,
          "step": 3
        },
        {
          "start": 90,
          "end": 96,
          "step": 6
        },
        {
          "start": 108,
          "end": 144,
          "step": 12
        }
      ]
    }
  },
  "kim_rdps": {
    "name": "RDAPS_KIM",
    "archiveStart": "2022-05-12",
    "cycles": [
      0,
      6,
      12,
      18
    ],
    "forecastRules": [
      {
        "from": "2011-05-23",
        "cycles": [
          6,
          18
        ],
        "max": 72
      },
      {
        "from": "2024-06-27",
        "cycles": [
          0,
          12
        ],
        "max": 120
      }
    ],
    "stepSchemeByCycleGroup": {
      "0,6,12,18": [
        {
          "start": 0,
          "end": 120,
          "step": 1
        }
      ]
    }
  },
  "um_rdps": {
    "name": "RDAPS_UM",
    "archiveStart": "2012-06-01",
    "archiveEnd": "2019-02-10",
    "cycles": [
      0,
      6,
      12,
      18
    ],
    "forecastRules": [
      {
        "cycles": [
          0,
          6,
          12,
          18
        ],
        "max": 87
      }
    ],
    "stepSchemeByCycleGroup": {
      "0,6,12,18": [
        {
          "start": 0,
          "end": 87,
          "step": 3
        }
      ]
    }
  },
  "kwrf_rdps": {
    "name": "RDAPS_WRF",
    "archiveStart": "2012-06-01",
    "archiveEnd": "2015-01-08",
    "cycles": [
      0,
      6,
      12,
      18
    ],
    "forecastRules": [
      {
        "cycles": [
          0,
          6,
          12,
          18
        ],
        "max": 72
      }
    ],
    "stepSchemeByCycleGroup": {
      "0,6,12,18": [
        {
          "start": 0,
          "end": 72,
          "step": 3
        }
      ]
    }
  },
  "kim_ldps": {
    "name": "LDAPS_KIM",
    "archiveStart": "2025-11-14",
    "cycles": [
      0,
      6,
      12,
      18
    ],
    "forecastRules": [
      {
        "cycles": [
          0,
          6,
          12,
          18
        ],
        "max": 48
      }
    ],
    "stepSchemeByCycleGroup": {
      "0,6,12,18": [
        {
          "start": 0,
          "end": 48,
          "step": 1
        }
      ]
    }
  },
  "um_ldps": {
    "name": "LDAPS_UM",
    "archiveStart": "2012-06-01",
    "archiveEnd": "2026-03-31",
    "cycles": [
      0,
      6,
      12,
      18
    ],
    "forecastRules": [
      {
        "until": "2013-04-28",
        "cycles": [
          0,
          6,
          12,
          18
        ],
        "max": 24
      },
      {
        "from": "2013-04-29",
        "until": "2019-05-27",
        "cycles": [
          0,
          6,
          12,
          18
        ],
        "max": 36
      },
      {
        "from": "2019-05-28",
        "cycles": [
          0,
          6,
          12,
          18
        ],
        "max": 48
      }
    ],
    "stepSchemeByCycleGroup": {
      "0,6,12,18": [
        {
          "start": 0,
          "end": 48,
          "step": 1
        }
      ]
    }
  },
  "kim_klfs": {
    "name": "KLAPS_KIM",
    "archiveStart": "2023-02-23",
    "cycles": [
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
    "forecastRules": [
      {
        "cycles": [
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
        "max": 12
      }
    ],
    "stepSchemeByCycleGroup": {
      "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23": [
        {
          "start": 0,
          "end": 12,
          "step": 1
        }
      ]
    }
  },
  "um_klfs": {
    "name": "KLAPS_UM",
    "archiveStart": "2012-06-01",
    "archiveEnd": "2026-03-31",
    "cycles": [
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
    "forecastRules": [
      {
        "cycles": [
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
        "max": 12
      }
    ],
    "stepSchemeByCycleGroup": {
      "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23": [
        {
          "start": 0,
          "end": 12,
          "step": 1
        }
      ]
    }
  },
  "um_vdps": {
    "name": "VDAPS_UM",
    "archiveStart": "2017-06-20",
    "archiveEnd": "2021-12-29",
    "cycles": [
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
    "forecastRules": [
      {
        "cycles": [
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
        "max": 12
      }
    ],
    "stepSchemeByCycleGroup": {
      "0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23": [
        {
          "start": 0,
          "end": 12,
          "step": 1
        }
      ]
    }
  },
  "kim_epsg": {
    "name": "EPSG_KIM",
    "archiveStart": "2021-01-01",
    "cycles": [
      0,
      12
    ],
    "forecastRules": [
      {
        "cycles": [
          0,
          12
        ],
        "until": "2025-05-13",
        "max": 288
      },
      {
        "cycles": [
          0,
          12
        ],
        "max": 360
      }
    ],
    "stepSchemeByCycleGroup": {
      "0,12": [
        {
          "start": 0,
          "end": 360,
          "step": 6
        }
      ]
    }
  },
  "um_epsg": {
    "name": "EPSG_UM",
    "archiveStart": "2012-06-01",
    "archiveEnd": "2026-04-01",
    "cycles": [
      0,
      12
    ],
    "forecastRules": [
      {
        "from": "2012-06-01",
        "until": "2013-09-30",
        "cycles": [
          0,
          12
        ],
        "max": 240
      },
      {
        "from": "2013-10-17",
        "cycles": [
          0,
          12
        ],
        "max": 288
      }
    ],
    "stepSchemeByCycleGroup": {
      "0,12": [
        {
          "start": 0,
          "end": 288,
          "step": 6
        }
      ]
    }
  },
  "kim_lens": {
    "name": "LENS_KIM",
    "archiveStart": "2024-04-01",
    "cycles": [
      0,
      12
    ],
    "forecastRules": [
      {
        "cycles": [
          0,
          12
        ],
        "max": 120
      }
    ],
    "stepSchemeByCycleGroup": {
      "0,12": [
        {
          "start": 0,
          "end": 120,
          "step": 1
        }
      ]
    }
  },
  "um_lens": {
    "name": "LENS_UM",
    "archiveStart": "2015-10-28",
    "cycles": [
      0,
      12
    ],
    "forecastRules": [
      {
        "cycles": [
          0,
          12
        ],
        "max": 72
      }
    ],
    "stepSchemeByCycleGroup": {
      "0,12": [
        {
          "start": 0,
          "end": 72,
          "step": 1
        }
      ]
    }
  },
  "ecmwf_eps": {
    "name": "ECMWF_EPS",
    "archiveStart": "2013-04-07",
    "cycles": [
      0,
      12
    ],
    "forecastRules": [
      {
        "cycles": [
          0,
          12
        ],
        "max": 240
      }
    ],
    "stepSchemeByCycleGroup": {
      "0,12": [
        {
          "start": 0,
          "end": 240,
          "step": 6
        }
      ]
    }
  },
  "kim_anal": {
    "name": "ANAL_KIM",
    "archiveStart": "2020-09-28",
    "cycles": [
      0,
      6,
      12,
      18
    ]
  },
  "um_anal": {
    "name": "ANAL_UM",
    "archiveStart": "1982-01-01",
    "archiveEnd": "2026-03-31",
    "cycles": [
      0,
      6,
      12,
      18
    ],
    "cycleAvailability": [
      {
        "until": "2011-05-22",
        "cycles": [
          0,
          12
        ]
      },
      {
        "from": "2011-05-23",
        "cycles": [
          0,
          6,
          12,
          18
        ]
      }
    ]
  },
  "ecmwf_ra": {
    "name": "ECMWF_RA",
    "archiveStart": "1958-01-01",
    "archiveEnd": "2011-12-31",
    "cycles": [
      0,
      12
    ]
  },
  "kas": {
    "name": "KAS",
    "archiveStart": "2024-05-11",
    "cycles": [
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
      23,
      24
    ]
  },
  "kim_klps": {
    "name": "KLPS_KIM",
    "archiveStart": "2023-02-22",
    "cycles": [
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
      23,
      24
    ]
  },
  "um_klps": {
    "name": "KLPS_UM",
    "archiveStart": "2010-03-16",
    "cycles": [
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
      23,
      24
    ]
  },
  "obs_upper": {
    "name": "OBS_UPPER",
    "archiveStart": "1957-04-01",
    "cycles": [
      0,
      6,
      12,
      18
    ]
  },
  "edit_chart": {
    "name": "MANUAL_CHART",
    "archiveStart": "2004-02-12",
    "cycles": [
      0,
      6,
      12,
      18
    ]
  }
};


function expandSteps(scheme,maxLead){
let out=[];
if(!Array.isArray(scheme)) return [0];
scheme.forEach(r=>{
let e=Math.min(r.end,maxLead);
for(let h=r.start;h<=e;h+=r.step){
out.push(h);
}
});
return [...new Set(out)].sort((a,b)=>a-b);
}

function getCycleScheme(modelId,cycleHour){
let groups=MODELS[modelId]?.stepSchemeByCycleGroup || {};
for(let key in groups){
let members=key.split(',').map(Number);
if(members.includes(cycleHour)){
return groups[key];
}
}
return [];
}

function getForecastHours(modelId,runDate,cycleHour){
let m=MODELS[modelId];
if(!m || !Array.isArray(m.forecastRules)){
return [0];
}
for(let rule of m.forecastRules){
if(!rule.cycles.includes(cycleHour)) continue;
if(rule.from && runDate<new Date(rule.from)) continue;
if(rule.until && runDate>new Date(rule.until)) continue;
return expandSteps(getCycleScheme(modelId,cycleHour),rule.max);
}
return [0];
}

function getAvailableCycles(modelId,date){
let m=MODELS[modelId];
if(!m) return [];
if(!m.cycleAvailability) return m.cycles || [];
for(let r of m.cycleAvailability){
if(r.from && date<new Date(r.from)) continue;
if(r.until && date>new Date(r.until)) continue;
return r.cycles;
}
return m.cycles || [];
}

function getModelStatus(modelId,date){
let m=MODELS[modelId];
if(!m){ return {available:false,message:`${modelId} 모델 메타데이터가 없습니다.`}; }
if(m.archiveStart && date<new Date(m.archiveStart)){
return {available:false,message:`자료 보유기간 이전입니다.\n자료 보유기간: ${m.archiveStart} ~ ${m.archiveEnd || '현재'}`};
}
if(m.archiveEnd && date>new Date(m.archiveEnd)){
return {available:false,message:`운영 종료된 모델입니다.\n자료 보유기간: ${m.archiveStart || '미상'} ~ ${m.archiveEnd}`};
}
return {available:true,message:""};
}
