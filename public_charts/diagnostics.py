"""Explicit experimental diagnostics, with the KMA manual's snow-ratio coefficients."""
import numpy as np
import metpy.calc as mpcalc
from metpy.units import units
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import newton


def interpolate(field,latitude,longitude,*,nearest=False):
    xx,yy=np.meshgrid(longitude,latitude)
    values=RegularGridInterpolator((field.latitude,field.longitude),field.values,
                                   method="nearest" if nearest else "linear",bounds_error=True)(np.stack((yy,xx),axis=-1))
    return values.astype(np.float32)


def snow_ratio(rain_mm,temperature_c,relative_humidity,t850_c,*,interval_hours=3):
    """Manual p88; natural log and a 3h-equivalent intensity are explicit conventions."""
    rain=np.asarray(rain_mm,dtype=float)
    rh=np.asarray(relative_humidity,dtype=float)
    temp=np.asarray(temperature_c,dtype=float)
    t850=np.asarray(t850_c,dtype=float)
    valid=(rain>0)&np.isfinite(rain)&np.isfinite(temp)&np.isfinite(rh)&np.isfinite(t850)&(rh>=0)&(rh<=100)
    possible=(((rh>=75)&(temp<=.9)&(rh<(-100/13)*temp+102.5)) |
              ((temp>.9)&(rh<(-100/13)*temp+89.5)) | ((temp<=.9)&(rh<75))) & valid
    a=np.where(t850>-8,np.where(temp>0,-2.912,-3.688),np.where(temp>0,-3.235,-3.738))
    b=np.where(t850>-8,np.where(temp>0,9.4944,14.914),np.where(temp>0,11.203,20.784))
    equivalent_3h=rain*3/interval_hours
    ratio=np.where(possible,np.maximum(a*np.log(np.maximum(equivalent_3h,1e-12))+b,0),0)
    # Ratio is snow depth / liquid depth in identical units: mm -> cm requires /10.
    depth_cm=rain*ratio/10
    return ratio.astype(np.float32),depth_cm.astype(np.float32),possible


def wet_bulb_psychrometric(temperature_k,dewpoint_k,pressure_pa):
    """Invert MetPy's WMO psychrometric relation; not a claim of KIM internal code."""
    temp=np.asarray(temperature_k,dtype=float)
    dew=np.minimum(np.asarray(dewpoint_k,dtype=float),temp)
    vapor=mpcalc.saturation_vapor_pressure(dew*units.kelvin).to("Pa").m
    def residual(wet):
        return mpcalc.psychrometric_vapor_pressure_wet(pressure_pa*units.Pa,temp*units.kelvin,
                                                      wet*units.kelvin).to("Pa").m-vapor
    result=newton(residual,(temp+dew)/2,x1=(temp+dew)/2+.1,tol=1e-5,maxiter=35)
    if not np.isfinite(result).all() or np.any(result>temp+.01) or np.any(result<dew-.01):
        raise ValueError("Psychrometric wet bulb did not converge within dewpoint/dry-bulb bounds")
    return (result-273.15).astype(np.float32)
