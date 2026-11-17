(function(){
const checkbox=document.getElementById('usagePreference');
const status=document.getElementById('usagePreferenceStatus');
if(!checkbox || !window.CDSUsage) return;
function sync(){checkbox.checked=CDSUsage.isAllowed();status.textContent=checkbox.checked?'허용됨':'수집 안 함';}
checkbox.addEventListener('change',()=>{CDSUsage.setEnabled(checkbox.checked);sync();});
sync();
})();
