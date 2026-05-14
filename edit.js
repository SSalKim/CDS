const EDIT_CATEGORIES=[
  {
    "id": "surf",
    "name": "지상12"
  },
  {
    "id": "ghmd_s24",
    "name": "지상24H예상"
  },
  {
    "type": "header",
    "name": "─────────────────"
  },
  {
    "id": "sfc3",
    "name": "지상03"
  },
  {
    "id": "up92",
    "name": "925hPa"
  },
  {
    "id": "up85",
    "name": "850hPa"
  },
  {
    "id": "up70",
    "name": "700hPa"
  },
  {
    "id": "up50",
    "name": "500hPa"
  },
  {
    "id": "up30",
    "name": "300hPa"
  },
  {
    "id": "up20",
    "name": "200hPa"
  },
  {
    "id": "up10",
    "name": "100hPa"
  }
];

const EDIT_PRODUCTS=[
  {
    "category": "surf",
    "id": "surf",
    "label": "지상12",
    "patternByModel": {
      "edit_chart": "__proxy__"
    },
    "imageCountByModel": {
      "edit_chart": 1
    },
    "usesForecastHourByModel": {
      "edit_chart": false
    },
    "requiresDetailByModel": {
      "edit_chart": false
    }
  },
  {
    "category": "ghmd_s24",
    "id": "ghmd_s24",
    "label": "지상24H예상",
    "patternByModel": {
      "edit_chart": "__proxy__"
    },
    "imageCountByModel": {
      "edit_chart": 1
    },
    "usesForecastHourByModel": {
      "edit_chart": false
    },
    "requiresDetailByModel": {
      "edit_chart": false
    }
  },
  {
    "category": "sfc3",
    "id": "sfc3",
    "label": "지상03",
    "patternByModel": {
      "edit_chart": "__proxy__"
    },
    "imageCountByModel": {
      "edit_chart": 1
    },
    "usesForecastHourByModel": {
      "edit_chart": false
    },
    "requiresDetailByModel": {
      "edit_chart": false
    }
  },
  {
    "category": "up92",
    "id": "up92",
    "label": "925hPa",
    "patternByModel": {
      "edit_chart": "__proxy__"
    },
    "imageCountByModel": {
      "edit_chart": 1
    },
    "usesForecastHourByModel": {
      "edit_chart": false
    },
    "requiresDetailByModel": {
      "edit_chart": false
    }
  },
  {
    "category": "up85",
    "id": "up85",
    "label": "850hPa",
    "patternByModel": {
      "edit_chart": "__proxy__"
    },
    "imageCountByModel": {
      "edit_chart": 1
    },
    "usesForecastHourByModel": {
      "edit_chart": false
    },
    "requiresDetailByModel": {
      "edit_chart": false
    }
  },
  {
    "category": "up70",
    "id": "up70",
    "label": "700hPa",
    "patternByModel": {
      "edit_chart": "__proxy__"
    },
    "imageCountByModel": {
      "edit_chart": 1
    },
    "usesForecastHourByModel": {
      "edit_chart": false
    },
    "requiresDetailByModel": {
      "edit_chart": false
    }
  },
  {
    "category": "up50",
    "id": "up50",
    "label": "500hPa",
    "patternByModel": {
      "edit_chart": "__proxy__"
    },
    "imageCountByModel": {
      "edit_chart": 1
    },
    "usesForecastHourByModel": {
      "edit_chart": false
    },
    "requiresDetailByModel": {
      "edit_chart": false
    }
  },
  {
    "category": "up30",
    "id": "up30",
    "label": "200hPa",
    "patternByModel": {
      "edit_chart": "__proxy__"
    },
    "imageCountByModel": {
      "edit_chart": 1
    },
    "usesForecastHourByModel": {
      "edit_chart": false
    },
    "requiresDetailByModel": {
      "edit_chart": false
    }
  },
  {
    "category": "up20",
    "id": "up20",
    "label": "200hPa",
    "patternByModel": {
      "edit_chart": "__proxy__"
    },
    "imageCountByModel": {
      "edit_chart": 1
    },
    "usesForecastHourByModel": {
      "edit_chart": false
    },
    "requiresDetailByModel": {
      "edit_chart": false
    }
  },
  {
    "category": "up10",
    "id": "up10",
    "label": "100hPa",
    "patternByModel": {
      "edit_chart": "__proxy__"
    },
    "imageCountByModel": {
      "edit_chart": 1
    },
    "usesForecastHourByModel": {
      "edit_chart": false
    },
    "requiresDetailByModel": {
      "edit_chart": false
    }
  }
];

const EDIT_PRODUCT_CATEGORY_UI_CONFIG={
  "surf": {
    "hideProductSelect": true
  },
  "ghmd_s24": {
    "hideProductSelect": true
  },
  "sfc3": {
    "hideProductSelect": true
  },
  "up92": {
    "hideProductSelect": true
  },
  "up85": {
    "hideProductSelect": true
  },
  "up70": {
    "hideProductSelect": true
  },
  "up50": {
    "hideProductSelect": true
  },
  "up30": {
    "hideProductSelect": true
  },
  "up20": {
    "hideProductSelect": true
  },
  "up10": {
    "hideProductSelect": true
  }
};

const EDIT_CATEGORY_MODEL_RESTRICTIONS={
  "sfc": {
    "allowedModels": [
      "edit_chart"
    ],
    "fallbackModel": "edit_chart"
  },
  "upper": {
    "allowedModels": [
      "edit_chart"
    ],
    "fallbackModel": "edit_chart"
  },
  "etc": {
    "allowedModels": [
      "edit_chart"
    ],
    "fallbackModel": "edit_chart"
  }
};

const EDIT_SELECTION_MODEL_RESTRICTIONS={};

const EDIT_DEFAULT_PRODUCT_BY_CATEGORY={
  "sfc": "sfc",
  "upper": "up85"
};
