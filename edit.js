const EDIT_CATEGORIES=[

{id:"surf",name:"지상12"},
{id:"ghmd_s24",name:"지상24H예상"},
{type:"header", name:"─────────────────"},
{id:"sfc3",name:"지상03"},
{id:"up92",name:"925hPa"},
{id:"up85",name:"850hPa"},
{id:"up70",name:"700hPa"},
{id:"up50",name:"500hPa"},
{id:"up30",name:"300hPa"},
{id:"up20",name:"200hPa"},
{id:"up10",name:"100hPa"}
];


const EDIT_PRODUCTS=[

{category:"surf",id:"surf",label:"지상12",
    patternByModel:{
        edit_chart:"surf_{run}.png"
    }
},
{category:"ghmd_s24",id:"ghmd_s24",label:"지상24H예상",
    patternByModel:{
        edit_chart:"ghmd_s24_{run}.png"
    }
},

{category:"sfc3",id:"sfc3",label:"지상03",
    patternByModel:{
        edit_chart:"sfc3_{run}.png"
    }
},
{category:"up92",id:"up92",label:"925hPa",
    patternByModel:{
        edit_chart:"up92_{run}.png"
    }
},
{category:"up85",id:"up85",label:"850hPa",
    patternByModel:{
        edit_chart:"up85_{run}.png"
    }
},
{category:"up70",id:"up70",label:"700hPa",
    patternByModel:{
        edit_chart:"up70_{run}.png"
    }
},
{category:"up50",id:"up50",label:"500hPa",
    patternByModel:{
        edit_chart:"up50_{run}.png"
    }
},
{category:"up30",id:"up30",label:"300hPa",
    patternByModel:{
        edit_chart:"up30_{run}.png"
    }
},
{category:"up20",id:"up20",label:"200hPa",
    patternByModel:{
        edit_chart:"up20_{run}.png"
    }
},
{category:"up10",id:"up10",label:"100hPa",
    patternByModel:{
        edit_chart:"up10_{run}.png"
    }
}

];

const EDIT_PRODUCT_CATEGORY_UI_CONFIG={
surf:{hideProductSelect:true},
ghmd_s24:{hideProductSelect:true},
sfc3:{hideProductSelect:true},
up92:{hideProductSelect:true},
up85:{hideProductSelect:true},
up70:{hideProductSelect:true},
up50:{hideProductSelect:true},
up30:{hideProductSelect:true},
up20:{hideProductSelect:true},
up10:{hideProductSelect:true}
};


const EDIT_CATEGORY_MODEL_RESTRICTIONS={

};


const EDIT_SELECTION_MODEL_RESTRICTIONS={

};


const EDIT_DEFAULT_PRODUCT_BY_CATEGORY={
surf:"surf",
ghmd_s24:"ghmd_s24",
sfc3:"sfc3",
up92:"up92",
up85:"up85",
up70:"up70",
up50:"up50",
up30:"up30",
up20:"up20",
up10:"up10"
};