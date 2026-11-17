(function(){
'use strict';
window.CDS_USAGE_CONFIG={
  enabled:true,
  endpoint:'https://cds-usage-analytics.kwj1407.workers.dev/collect',
measurementId:'G-Q3DTERTT0J'
};
try{
if(localStorage.getItem('cds.analytics.optout')==='1' || navigator.globalPrivacyControl===true || navigator.doNotTrack==='1'){
window['ga-disable-G-Q3DTERTT0J']=true;
}
}
catch(error){}
})();
