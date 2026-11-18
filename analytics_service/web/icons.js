import {createIcons,createElement,ChartNoAxesCombined,LogOut,RefreshCw,Download,Pencil,Check,X} from 'lucide';
createIcons({icons:{ChartNoAxesCombined,LogOut,RefreshCw,Download}});
window.CDSAdminIcon=name=>createElement({Pencil,Check,X}[name],{'aria-hidden':'true',width:15,height:15});
