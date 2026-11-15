"""Literal operational KIM product titles; model names remain source-specific.

Compared against KMA's original 2026111500 +024h Asia/Korea PNGs, including
the three horizontal winter panels. Only lead times, levels and unavailable
model variables change; absent omega is never advertised in AIGFS titles.
"""


def product_title(product,domain,hour,interval,*,upper=300,has_omega=True,pressure_only=False):
    korea=domain=="hkor"
    window=f"[{hour-interval:03}-{hour:03}]"
    total=f"[000-{hour:03}]"
    if product in ("surfce","acptot"):
        if pressure_only:
            return "MSLP(hPa)"
        description="Accum. Precip" if korea else "Accumulated Precipitation"
        return f"MSLP(hPa) and {description}(mm){window}"
    titles={
        "acrain":f"MSLP(hPa) and Total Accum. Precip(mm){total}",
        "acptot_snow":f"925hPa CHT, 1000-850 Thick.(m), sfc_Tw(1.2C) and Accum.Snow(kg/m2){window}",
        "acptot_snowdepth":f"MSLP, Accum.Snow Amount(cm) by SR Ratio and Precip.Area{window}",
        "acrain_snow":f"MSLP(hPa) and Total Accum. Snow(kg/m2){total}",
        "acrain_snowdepth":f"MSLP, Total Accum. Snow Amount(cm) by SR Ratio{total}",
        "gph500":"500hPa GPH(m), Temp(C), Relative Vorticity(E-5/s)",
        "thk850":"925hPa Temp.(C), Wind(>5kt), 1000-850hPa Thick.(m) & 850hPa T-Td(C)",
        "ttd700":"500hPa Temperature(C), 700hPa T-Td(C)",
    }
    if product in titles:
        return titles[product]
    if product in ("gph200","gph300"):
        level=300 if product=="gph300" else upper
        return f"{level}hPa GPH(m), Temp(C), Isotach(>50kt)"
    if product in ("gph700","ept850","ept925"):
        level=int(product[-3:])
        minimum=5 if korea else 20 if level==700 else 10
        temperature="Temp(C), " if korea else ""
        return f"{level}hPa GPH(m), {temperature}Equiv.-P.Temp(K), Wind(>{minimum}kt)"
    if product.startswith("wnd"):
        level=int(product[-3:])
        return f"{level}hPa Stream Line and Isotach(>{50 if level in (200,300) else 25}kt)"
    if product in ("thk500","thk700"):
        level=int(product[-3:])
        minimum=5 if korea else 20
        fields=("700hPa P-Velocity(hPa/hr) & Wind" if has_omega else "700hPa Wind") if level==500 else "850hPa Equiv.-P.Temp(K) & Wind"
        return f"1000-{level}hPa Thickness(m), {fields}(>{minimum}kt)"
    if product in ("anl850","anl925"):
        return f"{product[-3:]}hPa T-Td(C), Td(C) and Wind(>{5 if korea else 20}kt)"
    if product=="anlsfc":
        return f"Surface T-Td(C), Td(C) and Wind(>{5 if korea else 15}kt)"
    raise ValueError(f"No verified KIM title for {product!r}")
