"""Lightweight rendering contract, shared with the image cache."""
STYLE_VERSION = 12
PUBLIC_PROFILE = "cds-public-v6"
PUBLIC_IMAGE_SIZES = {"asia": (910, 660), "hkor": (640, 730)}
PUBLIC_MAP_AXES = {"hkor": (.004, .058, .910, .874)}


def precipitation_threshold(cycle,hours=3):
    return .5 if 5<=int(cycle[4:6])<=10 else .25


def winter_season(cycle):
    return int(cycle[4:6]) in (10,11,12,1,2,3,4)
PUBLIC_RAIN_LEVELS = tuple(range(0,101,5))
# Flat colorbar samples from the user-supplied operational KIM surface chart.
PUBLIC_RAIN_COLORS = ("#b8b8ff", "#7e99e4", "#7eb4d2", "#7ed2b4", "#c7ff95",
                      "#95ff78", "#63f963", "#31ef31", "#ffffb4", "#ffff82",
                      "#fff950", "#ffef31", "#ffd295", "#ffb478", "#ff955a",
                      "#ff6331", "#ff4a28", "#ff311e", "#ff1813", "#f90000")
# Flat colorbar pixels from the user's original KIM winter PNG, not its PDF copy.
PUBLIC_SNOW_LEVELS = (0,1,2,3,4,5,6,8,10,12,15,18,20,25,30,40,50,60,70,80,100)
PUBLIC_SNOW_COLORS = ("#b3b4de","#ffea6e","#ffdc1f","#e0b900","#ccaa00",
                      "#cdffb4","#68f24e","#35cc1b","#87d9ff","#07abff",
                      "#008dde","#0077b3","#da87ff","#c23eff","#ad07ff",
                      "#7f00bf","#fa8585","#f63e3e","#d50000","#bf0000")
PUBLIC_SNOW_OVER = "#0c6615"
SNOW_THRESHOLD = .25
WINTER_HATCH_COLOR = "#66cc55"

MAPS = {
    "asia": {"figsize": (10, 7.3), "center": (127.5, 38), "parallels": (40, 40),
             "xlim": (-5.9e6, 3.8e6), "ylim": (-2.8e6, 4.0e6),
             "axes": (.001, .063, .944, .904)},
    "hkor": {"figsize": (6.4, 7.35), "center": (126, 38), "parallels": (30, 60),
             "xlim": (-600000, 570000), "ylim": (-730000, 560000),
             "axes": (.001, .050, .944, .902)},
}

# Covers the northern Asia view as well as its curved western/eastern corners.
GRID_BOUNDS = {"asia": (-5, 85, 20, 220), "hkor": (29, 45, 115, 138)}
CENTER_MARKER_SIZE = 2.2
CENTER_MARKER_WIDTH = .25
BARB_LENGTH = 4.4
UPPER_CENTER_COLORS = {"H": "black", "L": "#b00000", "W": "red", "C": "blue"}
ISOTACH_LEVELS = tuple(range(50, 151, 10))
# Flat colorbar pixels from the KIM operational 200/300hPa charts.
ISOTACH_COLORS = ("#7ef1f1", "#66e5fb", "#4ccdff", "#32b5ff", "#189bff",
                  "#cdffb5", "#81ff81", "#68f34e", "#34cd1a", "#18b300")
# Streamline colorbars sampled from the user's original KIM PNGs, separately
# from the geopotential/isotach palette above.
STREAM_UPPER_COLORS = ("#7ef3f3", "#66e5fb", "#4ccdff", "#32b5ff", "#189bff",
                       "#cdffb5", "#81ff81", "#67f24e", "#34cd1a", "#18b300")
STREAM_LOWER_COLORS = ("#cdffb5", "#81ff81", "#68f34e", "#34cb1a", "#18b300",
                       "#ffffc1", "#fbfb91", "#f3eb68", "#e5d934", "#d9b300")
THETA_LEVELS = tuple(range(282, 370, 3))
THETA_COLORS = {
    "asia": ("#8166ff", "#9981ff", "#b39bff", "#cdb5ff", "#e5cbff", "#5ae54c", "#66f366",
             "#9bff81", "#cdffb3", "#4cb5ff", "#66cdff", "#99e5ff", "#cdf3ff", "#99b3f9",
             "#b3c7ff", "#c7d9ff", "#d9ebff", "#b5e581", "#cff38d", "#e5ff99", "#ffff91",
             "#ffeb8b", "#ffeb8b", "#fbcb80", "#fbcb80", "#fbaf6f", "#ff8e40", "#ff8e40", "#f96229"),
    "hkor": ("#8166ff", "#9981ff", "#b39bff", "#cdb5ff", "#e5cbff", "#5ae54c", "#66f366",
             "#9bff81", "#cdffb3", "#4cb5ff", "#66cdff", "#99e5ff", "#cdf3ff", "#a9bcfd",
             "#a9bcfd", "#c9cefc", "#dce7fe", "#c2ea85", "#c2ea85", "#e5ff99", "#fff791",
             "#fff791", "#ffd881", "#ffd881", "#ffc181", "#ffa559", "#ffa559", "#f88134", "#ff5734"),
}


def surface_steps(domain, profile=None):
    minor = 1 if domain == "hkor" else 2
    steps={"minor":minor,"major":4,"label":2}
    if profile==PUBLIC_PROFILE:
        steps.update(major=minor*4,anchor=1000)
    return steps


def barb_stride(domain):
    return (1, 2) if domain == "hkor" else (8, 8)


def center_parameters(domain, kind):
    if domain == "hkor":
        return 0, 60 if kind in ("temperature", "height") else 75
    return {"pressure": (.6, 500), "height": (4, 400), "temperature": (.35, 350)}[kind]


def numeric_extrema_parameters(domain, kind):
    korea = domain == "hkor"
    if kind == "precipitation":
        return {"radius": 90 if korea else 180, "prominence": .075 if korea else .2, "minimum": 1}
    if kind == "wind":
        return {"radius": 150 if korea else 350, "prominence": 1.5 if korea else 2.5, "minimum": 0}
    return {"radius": 125 if korea else 250, "prominence": .5 if korea else 1, "minimum": 2}


def stream_isotach_levels(domain, level):
    if level in (200, 300):
        return tuple(range(50, 251, 25))
    return tuple(range(5, 251, 5)) if domain == "hkor" else tuple(range(25, 251, 25))


def stream_shading(level):
    return (ISOTACH_LEVELS, STREAM_UPPER_COLORS) if level in (200,300) else (tuple(range(25,76,5)), STREAM_LOWER_COLORS)


def precipitation_edge_levels(maximum,threshold):
    upper=max(100,int(maximum//20)*20)
    return (threshold,*range(20,upper+1,20))


def upper_level(cycle):
    return 200 if 5 <= int(cycle[4:6]) <= 10 else 300


def seasonal_products(products,cycle):
    selected=upper_level(cycle)
    return tuple(product for product in products if product not in {"gph200","gph300","wnd200","wnd300"}
                 or product in {f"gph{selected}",f"wnd{selected}"})


def contour_steps(domain, level, profile=None):
    korea = domain == "hkor"
    height = (30 if korea else 60) if level == 500 else (60 if level in (200, 300) else 30)
    steps = {"height": height,
            "height_label": (120 if level in (200, 300) else height) if korea else 120,
            "height_major": (height*4 if level == 500 else height*2) if korea else 120,
            "height_anchor": 60 if not korea and level == 500 else 0,
            "temperature_major": 6 if level == 500 else (4 if korea and level in (700, 850, 925) else None),
            "temperature": 1 if korea else 3, "theta_e": 3 if korea else 6,
            "height_color": "#0000ff" if korea else "black"}
    if profile == PUBLIC_PROFILE and level in (200, 300, 500):
        steps.update(height_major=240, height_anchor=5580 if level == 500 else 9120,
                     temperature_major=12, temperature_anchor=0 if level == 500 else -48)
    if profile == PUBLIC_PROFILE and korea:
        if level in (200,300):
            steps.update(temperature_major=4,temperature_anchor=-40)
        elif level==500:
            steps.update(height_major=60,height_anchor=5580,temperature_major=2,temperature_anchor=0)
        elif level in (700,850,925):
            steps.update(height_major=120,height_anchor={700:3060,850:1500,925:810}[level])
    return steps
