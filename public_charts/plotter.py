"""Shared KIM-style charts from native public model fields."""
from datetime import timedelta
from functools import lru_cache
import json
from pathlib import Path
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as effects
from scipy.interpolate import RegularGridInterpolator
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.cm import ScalarMappable
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as MplPath
from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch,FancyArrowPatch
from matplotlib.transforms import Affine2D
from matplotlib.ticker import FixedLocator
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io import shapereader
from shapely.ops import unary_union
from shapely.geometry import shape
import metpy.calc as mpcalc
from metpy.units import units
from pyproj import CRS
from scipy.ndimage import gaussian_filter, maximum_filter, minimum_filter, label, find_objects, binary_erosion

from .chart_style import (MAPS, STYLE_VERSION, CENTER_MARKER_SIZE, CENTER_MARKER_WIDTH, UPPER_CENTER_COLORS, BARB_LENGTH,
                         ISOTACH_LEVELS, ISOTACH_COLORS, THETA_LEVELS, THETA_COLORS, barb_stride,
                         center_parameters, numeric_extrema_parameters, contour_steps, surface_steps, upper_level,
                         stream_isotach_levels,stream_shading,
                         PUBLIC_PROFILE, PUBLIC_IMAGE_SIZES, PUBLIC_RAIN_LEVELS, PUBLIC_RAIN_COLORS,
                         PUBLIC_MAP_AXES, precipitation_edge_levels,precipitation_threshold,
                         PUBLIC_SNOW_LEVELS,PUBLIC_SNOW_COLORS,PUBLIC_SNOW_OVER,SNOW_THRESHOLD,WINTER_HATCH_COLOR)
from .dates import parse_cycle
from .chart_titles import product_title

import os
cartopy.config["data_dir"] = Path(os.environ.get("PUBLIC_CHARTS_MAP_DIR", Path(__file__).resolve().parent / "maps"))
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.linewidth": .6,
                     "savefig.facecolor": "white", "contour.negative_linestyle": "solid"})
RAIN_LEVELS = [.25, 1, 2, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100]
RAIN_COLORS = ["#c5c0ff", "#aaaaff", "#8ca7ef", "#75b5d9", "#79cfb3", "#8bdf94", "#a5ed75", "#c2f45f",
               "#29d835", "#ffff79", "#ffdf48", "#ffbd41", "#ff9842", "#ff7536", "#ff4d21", "#ff1515"]
VORT_COLORS = ["#ffffc1", "#fff59b", "#ffeb78", "#ffda58", "#ffc64a", "#ffac3b", "#ff902e", "#ff6e24", "#ff481c", "#f92314"]


def draw_time_footer(figure,pos,init,hour,size,*,public,korea):
    """Center proportional-font UTC/KST tokens in shared, borderless columns."""
    font=FontProperties(family="DejaVu Sans",size=size)
    renderer=figure.canvas.get_renderer()
    gap=renderer.get_text_width_height_descent(" ",font,False)[0]
    top_y=pos.y0-.023
    bottom_y=pos.y0-(.044 if public and korea else .051 if public else .043)
    blocks={}
    for key,prefix,date,forecast in (("valid","VALID",init+timedelta(hours=hour),True),("init","TIME",init,False)):
        kst=date+timedelta(hours=9)
        top=[prefix,":",date.strftime("%HUTC"),date.strftime("%d"),date.strftime("%b").upper(),date.strftime("%Y")]
        bottom=["","",kst.strftime("%HKST"),kst.strftime("%d"),kst.strftime("%b").upper(),kst.strftime("%Y")]
        roles=["prefix","colon","time","day","month","year"]
        if forecast:
            top.append(f"(+{hour:03}h)")
            bottom.append(top[-1])
            roles.append("lead")
        widths=[max(renderer.get_text_width_height_descent(text,font,False)[0] for text in pair)
                for pair in zip(top,bottom)]
        total=sum(widths)+gap*(len(widths)-1)
        start=pos.x0*figure.bbox.width if forecast else pos.x1*figure.bbox.width-total
        blocks[key]=(start/figure.bbox.width,(start+total)/figure.bbox.width)
        for row,y,color in ((top,top_y,"red"),(bottom,bottom_y,"black")):
            x=start
            for index,(text,width,role) in enumerate(zip(row,widths,roles)):
                if text:
                    suffix=("utc" if row is top else "kst") if role=="time" else role if row is top else f"kst-{role}"
                    figure.text((x+width/2)/figure.bbox.width,y,text,color=color,size=size,family="DejaVu Sans",
                                ha="center",gid=f"{key}-{suffix}")
                x+=width+gap
    return blocks


@lru_cache(maxsize=1)
def korean_admin_boundaries():
    path=shapereader.natural_earth(resolution="10m",category="cultural",name="admin_1_states_provinces")
    source=Path(__file__).resolve().parent/"maps/korea_ctp_law.geojson"
    collection=json.loads(source.read_text(encoding="utf-8-sig"))
    south=[shape(feature["geometry"]) for feature in collection["features"]]
    if collection.get("type")!="FeatureCollection" or len(south)<2 or any(geometry.is_empty for geometry in south):
        raise ValueError("MAP Korean province boundary snapshot is incomplete")
    groups={"KOR":south,"PRK":[]}
    reader=shapereader.Reader(path)
    try:
        for record in reader.records():
            code=record.attributes.get("adm0_a3")
            if code=="PRK":
                groups[code].append(record.geometry)
    finally:
        reader.close()
    if not groups["PRK"]:
        raise ValueError("Korean first-order administrative boundary dataset is incomplete")
    return tuple(unary_union([item.boundary for item in geometries]).difference(unary_union(geometries).boundary)
                 for geometries in groups.values())


def stream_direction_arrows(ax,segments,*,color="#0000ff",spacing=180):
    """Stagger small open heads along arc length, without changing integrated stream paths."""
    arrows=[]
    for index,segment in enumerate(segments):
        if len(segment)<2 or not np.isfinite(segment).all():
            continue
        screen=ax.transData.transform(segment)
        lengths=np.r_[0,np.cumsum(np.linalg.norm(np.diff(screen,axis=0),axis=1))]
        unique=np.r_[True,np.diff(lengths)>1e-6]
        screen,lengths=screen[unique],lengths[unique]
        if len(lengths)<2 or lengths[-1]<spacing*.3:
            continue
        offset=spacing*(.2+.65*((index*.61803398875)%1))
        for distance in np.arange(offset,lengths[-1]-5,spacing):
            positions=np.array([[np.interp(s,lengths,screen[:,axis]) for axis in (0,1)]
                                for s in (max(0,distance-4),min(lengths[-1],distance+4))])
            tail,head=ax.transData.inverted().transform(positions)
            arrow=FancyArrowPatch(tail,head,transform=ax.transData,arrowstyle="->",mutation_scale=4.5,
                                 color=color,linewidth=.3,fill=False,shrinkA=0,shrinkB=0,zorder=6,
                                 clip_on=True,gid="stream-direction-arrow")
            ax.add_patch(arrow)
            arrows.append(arrow)
    return arrows


def fit_heading(figure,heading,right):
    """Condense only glyph width when a long product title reaches its right boundary."""
    box=heading.get_window_extent(figure.canvas.get_renderer())
    available=right*figure.bbox.width-box.x0
    if box.width<=available:
        return 1.
    glyphs=TextPath((0,0),heading.get_text(),prop=heading.get_fontproperties())
    bounds=glyphs.get_extents()
    factor=figure.dpi/72
    scale=min(1.,available/(bounds.width*factor))
    transform=Affine2D().scale(factor*scale,factor).translate(box.x0-bounds.x0*factor*scale,box.y0-bounds.y0*factor)
    patch=PathPatch(glyphs,transform=transform,color=heading.get_color(),linewidth=0,
                    gid="compressed-product-title",clip_on=False)
    figure.add_artist(patch)
    heading.set_visible(False)
    return scale


def relative_vorticity(arrays, level=500):
    return mpcalc.vorticity(arrays[f"wind_u_{level}"] * units("m/s"), arrays[f"wind_v_{level}"] * units("m/s"),
                           longitude=arrays["longitude"] * units.degree, latitude=arrays["latitude"] * units.degree,
                           crs=CRS.from_epsg(4326)).to("1/s").m * 1e5


def equivalent_potential_temperature(arrays, level):
    q = np.maximum(arrays[f"specific_humidity_{level}"], 1e-9) * units("kg/kg")
    temp = arrays[f"temperature_{level}"] * units.kelvin
    dewpoint = mpcalc.dewpoint_from_specific_humidity(level * units.hPa, q)
    return mpcalc.equivalent_potential_temperature(level * units.hPa, temp, dewpoint).to("K").m


def smooth_valid(value, sigma, valid_mask=None):
    if valid_mask is None:
        return gaussian_filter(value, sigma)
    weights = gaussian_filter(np.asarray(valid_mask,dtype=float),sigma)
    values = gaussian_filter(np.where(valid_mask,value,0).astype(float),sigma)
    return np.divide(values,weights,out=np.zeros_like(values),where=weights>1e-8)


def extrema_candidates(value, latitude, longitude, radius_km, prominence, high, valid_mask=None):
    """Find distinct closed extrema, rejecting flat and weak undulations."""
    lat_step = float(np.median(np.abs(np.diff(latitude))))
    lon_step = float(np.median(np.abs(np.diff(longitude))))
    ry = max(2, int(radius_km / (111 * lat_step)))
    rx = max(2, int(radius_km / (111 * .8 * lon_step)))
    fy, fx = np.ogrid[-ry:ry+1, -rx:rx+1]
    footprint = (fy / ry)**2 + (fx / rx)**2 <= 1
    if valid_mask is not None and not np.any(valid_mask):
        return []
    smooth = smooth_valid(np.asarray(value, dtype=float),.8,valid_mask)
    search = smooth if valid_mask is None else np.where(valid_mask,smooth,-np.inf if high else np.inf)
    neighborhood = (maximum_filter if high else minimum_filter)(search, footprint=footprint, mode="nearest")
    background = smooth_valid(smooth,(max(2,ry/2),max(2,rx/2)),valid_mask)
    strength = (smooth - background) * (1 if high else -1)
    tolerance = 64*np.finfo(float).eps*max(1, float(np.nanmax(np.abs(value))))
    peaks = (smooth == neighborhood) & (strength > max(prominence, tolerance)) & np.isfinite(value)
    if valid_mask is not None:
        peaks &= binary_erosion(valid_mask,iterations=3)
    peaks[:2] = peaks[-2:] = False
    peaks[:, :2] = peaks[:, -2:] = False
    components, _ = label(peaks)
    result = []
    for number, region in enumerate(find_objects(components), 1):
        if region is None:
            continue
        cells = np.argwhere(components[region] == number)
        row, col = cells[np.argmax(strength[region][components[region] == number])]
        row, col = row + region[0].start, col + region[1].start
        # Refine to a native-grid extreme: the cross never uses a smoothed coordinate.
        y0, x0 = row-1, col-1
        local = value[row-1:row+2, col-1:col+2]
        if valid_mask is not None:
            local = np.where(valid_mask[row-1:row+2,col-1:col+2],local,np.nan)
        index = np.nanargmax(local) if high else np.nanargmin(local)
        dy, dx = np.unravel_index(index, local.shape)
        row, col = y0 + dy, x0 + dx
        result.append((float(strength[row, col]), row, col, float(value[row, col])))
    return sorted(result, reverse=True)


def center_candidates(value, latitude, longitude, domain, kind, high, valid_mask=None):
    prominence, radius = center_parameters(domain, kind)
    radii = (radius, radius*2) if domain == "asia" and kind in ("pressure", "height") else (radius,)
    candidates = {}
    # Broad closed systems can look weak against a small-radius background.
    for scale in radii:
        for item in extrema_candidates(value, latitude, longitude, scale, prominence, high,valid_mask):
            key = (item[1], item[2])
            if key not in candidates or item[0] > candidates[key][0]:
                candidates[key] = item
    return sorted(candidates.values(), reverse=True)


def merge_similar_centers(candidates,latitude,longitude,distance_km,temperature_difference=2):
    retained=[]
    for item in candidates:
        _,row,col,value=item[:4]
        duplicate=False
        for kept in retained:
            _,other_row,other_col,other_value=kept[:4]
            if abs(value-other_value)>temperature_difference:
                continue
            lat1,lat2=np.deg2rad(latitude[row]),np.deg2rad(latitude[other_row])
            dlat=lat2-lat1
            dlon=np.deg2rad(longitude[other_col]-longitude[col])
            distance=2*6371*np.arcsin(np.sqrt(np.clip(np.sin(dlat/2)**2+np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2,0,1)))
            if distance<distance_km:
                duplicate=True
                break
        if not duplicate:
            retained.append(item)
    return retained


def prune_closed_paths(paths,levels,predicate,inverse):
    """Remove entire suspect rings, preserving every vertex of every open contour."""
    result=[]
    for path,level in zip(paths,levels):
        if path.codes is None or not len(path.vertices):
            result.append(path)
            continue
        starts=np.flatnonzero(path.codes==MplPath.MOVETO)
        vertices,codes=[],[]
        for start,end in zip(starts,np.r_[starts[1:],len(path.vertices)]):
            ring=path.vertices[start:end]
            closed=path.codes[end-1]==MplPath.CLOSEPOLY or (len(ring)>2 and np.allclose(ring[0],ring[-1]))
            if closed and predicate(inverse(ring),float(level)):
                continue
            vertices.append(ring)
            codes.append(path.codes[start:end])
        result.append(MplPath(np.concatenate(vertices) if vertices else np.empty((0,2)),
                              np.concatenate(codes) if codes else np.empty(0,dtype=np.uint8)))
    return result


def render(arrays, cycle, hour, product, domain, target, accumulation=None, *,
           model_name="Public model", precipitation_hours=3,
           precipitation_field="total_precipitation_3h", source_note=None,
           pressure_only=False, upper_level_override=None, physical_barb_spacing=False,
           profile=None, model_id=None, field_masks=None,contour_filter=None,diagnostic_snowfall=False,
           return_frame=False):
    started = time.perf_counter()
    xx, yy = np.meshgrid(arrays["longitude"], arrays["latitude"])
    plate = ccrs.PlateCarree()
    spec = MAPS[domain]
    korea = domain == "hkor"
    public=profile==PUBLIC_PROFILE
    font_scale=(1.25 if korea else 1.35) if public else 1
    def fs(size):
        return size*font_scale
    field_masks = field_masks or {}
    figure = None
    try:
        figure = plt.figure(figsize=spec["figsize"], dpi=160)
        projection = ccrs.LambertConformal(central_longitude=spec["center"][0], central_latitude=spec["center"][1],
                                         standard_parallels=spec["parallels"])
        ax = figure.add_axes(PUBLIC_MAP_AXES.get(domain,spec["axes"]) if public else spec["axes"], projection=projection)
        ax.set_xlim(*spec["xlim"])
        ax.set_ylim(*spec["ylim"])
        coast = "#303030" if public else ("#252525" if korea else "#666666")
        ax.add_feature(cfeature.NaturalEarthFeature("physical", "coastline" if korea else "land", "10m" if korea else "50m",
                                                  edgecolor=coast, facecolor="none"), linewidth=.7 if public else .5, zorder=4)
        ax.add_feature(cfeature.NaturalEarthFeature("cultural", "admin_0_boundary_lines_land", "50m", edgecolor=coast, facecolor="none"), linewidth=.5 if public else .3, zorder=4)
        if korea:
            boundaries=ax.add_geometries(korean_admin_boundaries(),crs=plate,edgecolor="#666666",facecolor="none",
                                         linewidth=.35,zorder=4.2)
            boundaries.set_gid("korean-admin-boundaries")
        grid = ax.gridlines(crs=plate, draw_labels=True, linewidth=.35, color="#777777",
                           linestyle=(0, (2, 4)), x_inline=False, y_inline=False)
        grid.xlocator = FixedLocator(np.arange(30, 211, 5 if korea else 10))
        grid.ylocator = FixedLocator(np.arange(-20, 91, 5 if korea else 10))
        grid.xlabel_style = grid.ylabel_style = {"size": fs(5.4), "color": "#555555"}
        grid.top_labels = grid.right_labels = True
        grid.rotate_labels = False
        grid.xpadding = grid.ypadding = -3
        figure.canvas.draw()
        pos = ax.get_position()
        cax = figure.add_axes([pos.x1 + .012, pos.y0, .013, pos.height])
        sigma = .7 if korea else 1.1
        border = .04 if public and korea else .006
        def map_grid(latitude,longitude):
            gx,gy=np.meshgrid(longitude,latitude)
            coordinates=projection.transform_points(plate,gx,gy)
            inside=((coordinates[:,:,0]>=spec["xlim"][0]-border*np.ptp(spec["xlim"])) &
                    (coordinates[:,:,0]<=spec["xlim"][1]+border*np.ptp(spec["xlim"])) &
                    (coordinates[:,:,1]>=spec["ylim"][0]-border*np.ptp(spec["ylim"])) &
                    (coordinates[:,:,1]<=spec["ylim"][1]+border*np.ptp(spec["ylim"])))
            return {"latitude":latitude,"longitude":longitude,"xx":gx,"yy":gy,
                    "projected":coordinates,"visible":inside}
        base_grid=map_grid(arrays["latitude"],arrays["longitude"])
        projected,visible=base_grid["projected"],base_grid["visible"]
        rain_grid=(map_grid(arrays["precipitation_latitude"],arrays["precipitation_longitude"])
                   if product in {"surfce","acrain","acptot"} and "precipitation_latitude" in arrays else None)
        if not korea:
            ax.text(120, 70, "70N", transform=plate, fontsize=fs(5.4), color="#555555", ha="center", va="bottom",
                    bbox={"facecolor":"white", "edgecolor":"none", "alpha":.65, "pad":.3}, zorder=7)

        def contour(value, levels, color="black", width=.55, text_size=7.7, smooth=True, label_levels=None, label_color=None,valid_mask=None,quality_kind=None,sparse_zero=False):
            values = smooth_valid(value,sigma,valid_mask) if smooth else value
            allowed = visible if valid_mask is None else visible & valid_mask
            obj = ax.contour(projected[:, :, 0], projected[:, :, 1], np.ma.masked_where(~allowed, values),
                             levels=levels, colors=color, linewidths=width, linestyles="solid", transform=projection, zorder=5,corner_mask=True)
            if contour_filter is not None and quality_kind is not None:
                inverse=lambda points:plate.transform_points(projection,points[:,0],points[:,1])[:,:2]
                obj.set_paths(prune_closed_paths(obj.get_paths(),obj.levels,
                                                lambda points,level:contour_filter(points,level,quality_kind),inverse))
            labels = obj.levels if label_levels is None else np.intersect1d(obj.levels, label_levels)
            manual=None
            if sparse_zero and 0 in labels:
                segments=obj.allsegs[list(obj.levels).index(0)]
                choices=[]
                for segment in segments:
                    if len(segment)<3:
                        continue
                    screen=ax.transData.transform(segment)
                    length=np.sum(np.linalg.norm(np.diff(screen,axis=0),axis=1))
                    if length>350:
                        middle=segment[len(segment)//2]
                        nx=(middle[0]-spec["xlim"][0])/np.ptp(spec["xlim"])
                        ny=(middle[1]-spec["ylim"][0])/np.ptp(spec["ylim"])
                        if .04<nx<.96 and .04<ny<.96:
                            choices.append((length,middle))
                manual=[]
                for _,point in sorted(choices,key=lambda item:item[0],reverse=True):
                    if all(np.linalg.norm(ax.transData.transform(point)-ax.transData.transform(other))>300 for other in manual):
                        manual.append(point)
                    if len(manual)==3:
                        break
                if not manual:
                    labels=[]
            if len(labels):
                ax.clabel(obj, levels=labels, fmt="%.0f", fontsize=fs(text_size), inline=not sparse_zero, inline_spacing=2,
                          colors=label_color,manual=False)
                if sparse_zero:
                    retained=[]
                    for point in manual or []:
                        candidates=[text for text in obj.labelTexts if text not in retained]
                        if candidates:
                            retained.append(min(candidates,key=lambda text:np.linalg.norm(
                                ax.transData.transform(text.get_position())-ax.transData.transform(point))))
                    for text in obj.labelTexts:
                        if text not in retained:
                            text.remove()
                    obj.labelTexts=retained
            return obj

        def height_contour(value, level, color=None, major_every=None):
            steps = contour_steps(domain, level,profile)
            if major_every is not None:
                steps.update(height_major=steps["height"]*major_every,
                             height_anchor={850:1500,925:810}[level])
            levels = np.arange(0, 15001 if level in (200, 300, 500) else 4501, steps["height"])
            major = (levels-steps["height_anchor"]) % steps["height_major"] == 0
            labelled = (levels-steps["height_anchor"]) % steps["height_label"] == 0
            obj = contour(value, levels, color or steps["height_color"], np.where(major, .95, .4), label_levels=levels[labelled],valid_mask=field_masks.get(level),quality_kind=level)
            obj.set_gid("height-contours")

        def temperature_contour(value, level, major_every=None):
            steps = contour_steps(domain, level,profile)
            levels = np.arange(-99 if level < 700 else -60, 51, steps["temperature"])
            major = steps["temperature"]*major_every if major_every is not None else steps["temperature_major"]
            widths = np.where((levels-steps.get("temperature_anchor",0)) % major == 0, .85, .35) if major else .5
            obj = contour(value, levels, "red", widths, 7 if level >= 700 else 7.7,valid_mask=field_masks.get(level))
            obj.set_gid("temperature-contours")

        def filled(value, levels, colors, over,valid_mask=None,grid=None,colorbar_levels=None,colorbar_extendfrac=0):
            cmap = ListedColormap(colors)
            cmap.set_over(over)
            # Contour in projected coordinates so distant polygons cannot wrap across the map.
            coordinates=projected if grid is None else grid["projected"]
            allowed=visible if grid is None else grid["visible"]
            values = value if valid_mask is None and grid is None and colorbar_levels is None else np.ma.masked_where(~(allowed if valid_mask is None else allowed&valid_mask),value)
            fill = ax.contourf(coordinates[:, :, 0], coordinates[:, :, 1], values, levels=levels, cmap=cmap,
                               norm=BoundaryNorm(levels, cmap.N), extend="max", transform=projection, zorder=1,corner_mask=True)
            fill.set_gid("shaded-field")
            legend=fill if colorbar_levels is None else ScalarMappable(norm=BoundaryNorm(colorbar_levels,cmap.N),cmap=cmap)
            bar = figure.colorbar(legend, cax=cax, ticks=levels if colorbar_levels is None else colorbar_levels,
                                 format="%g", extend="max",extendrect=True, extendfrac=colorbar_extendfrac)
            bar.ax.tick_params(labelsize=fs(7), length=0, pad=3)
            bar.outline.set_linewidth(.4)
            return fill

        def barbs(level, minimum):
            row_stride, column_stride = barb_stride(domain)
            if physical_barb_spacing:
                row_stride = max(1, round(row_stride*.25/np.median(np.diff(arrays["latitude"]))))
                column_stride = max(1, round(column_stride*.25/np.median(np.diff(arrays["longitude"]))))
            cut = (slice(None, None, row_stride), slice(None, None, column_stride))
            factor = units("m/s").to("knots").m
            u, v = arrays[f"wind_u_{level}"][cut] * factor, arrays[f"wind_v_{level}"][cut] * factor
            chosen = visible[cut] & (np.hypot(u, v) >= minimum) & np.isfinite(u) & np.isfinite(v)
            if level in field_masks:
                chosen &= field_masks[level][cut]
            artist = ax.barbs(xx[cut][chosen], yy[cut][chosen], u[chosen], v[chosen],
                             transform=plate, length=BARB_LENGTH, linewidth=.35, color="black", zorder=6,
                             sizes={"emptybarb": .07})
            artist.set_gid("wind-barbs")

        def hatch(value,low,high,color,*,clip_to=None,gid="hatched-field",pattern="|||"):
            artist=ax.contourf(projected[:,:,0],projected[:,:,1],np.ma.masked_where(~visible,value),
                               levels=[low,high],colors="none",hatches=[pattern],transform=projection,zorder=3,
                               corner_mask=True)
            artist.set_edgecolor(color)
            artist.set_linewidth(.2)
            artist.set_gid(gid)
            if clip_to is not None:
                artist.set_clip_path(MplPath.make_compound_path(*clip_to.get_paths()),ax.transData)
                artist.set_clip_box(ax.bbox)
            return artist

        def streamlines(level):
            # Integrate on an even projected display grid; shading stays on the native source grid.
            x=np.linspace(*spec["xlim"],145 if korea else 200)
            y=np.linspace(*spec["ylim"],160 if korea else 140)
            gx,gy=np.meshgrid(x,y)
            geographic=plate.transform_points(projection,gx,gy)
            points=np.stack((geographic[:,:,1],geographic[:,:,0]%360),axis=-1)
            u=RegularGridInterpolator((arrays["latitude"],arrays["longitude"]),arrays[f"wind_u_{level}"],bounds_error=False,fill_value=np.nan)(points)
            v=RegularGridInterpolator((arrays["latitude"],arrays["longitude"]),arrays[f"wind_v_{level}"],bounds_error=False,fill_value=np.nan)(points)
            ru,rv=projection.transform_vectors(plate,geographic[:,:,0],geographic[:,:,1],u,v)
            existing={id(patch) for patch in ax.patches}
            stream=ax.streamplot(x,y,ru,rv,density=1.35,color="#0000ff",linewidth=.28,arrowsize=.65,zorder=6,
                                 broken_streamlines=False,minlength=.08,maxlength=8)
            stream.lines.set_gid("streamlines")
            for patch in list(ax.patches):
                if id(patch) not in existing:
                    patch.remove()
            stream_direction_arrows(ax,stream.lines.get_segments())

        def annotation_point(row, col,grid=None):
            selected=base_grid if grid is None else grid
            lon, lat = selected["xx"][row, col], selected["yy"][row, col]
            px, py = projection.transform_point(lon, lat, plate)
            nx = (px-spec["xlim"][0]) / np.ptp(spec["xlim"])
            ny = (py-spec["ylim"][0]) / np.ptp(spec["ylim"])
            if not (.025 < nx < .975 and .045 < ny < .955):
                return None
            sx, sy = ax.transData.transform((px, py))
            return lon, lat, px, py, sx, sy

        def pin(lon, lat, color, zorder=9):
            ax.plot(lon, lat, marker="o", markersize=CENTER_MARKER_SIZE, markerfacecolor="none", color=color,
                    markeredgewidth=CENTER_MARKER_WIDTH, transform=plate, zorder=zorder)
            ax.plot(lon, lat, marker="x", markersize=CENTER_MARKER_SIZE*.7, color=color,
                    markeredgewidth=CENTER_MARKER_WIDTH, transform=plate, zorder=zorder)

        def centers(value, modes, kind,valid_mask=None,*,strict=False):
            merged=None
            def candidates_for(high):
                if strict:
                    return extrema_candidates(value,arrays["latitude"],arrays["longitude"],180 if korea else 500,
                                              1 if korea else 1.5,high,valid_mask)
                if public and model_id in ("gfs","aigfs") and kind=="temperature":
                    radius=220 if korea else 500
                    prominence=.45 if korea else .65
                    return extrema_candidates(value,arrays["latitude"],arrays["longitude"],radius,prominence,high,valid_mask)
                if public and model_id=="aigfs" and korea and kind in ("height","pressure"):
                    return extrema_candidates(value,arrays["latitude"],arrays["longitude"],180,8 if kind=="height" else .7,high,valid_mask)
                return center_candidates(value,arrays["latitude"],arrays["longitude"],domain,kind,high,valid_mask)
            if strict or public and ((kind=="temperature" and model_id in ("gfs","aigfs")) or (model_id=="aigfs" and korea and kind in ("height","pressure"))):
                all_candidates=[]
                for mark,high,color in modes:
                    all_candidates.extend((*item,mark,color) for item in candidates_for(high)
                        if annotation_point(item[1],item[2]) is not None)
                # Large low-latitude smooth cores should not get repeated near-identical labels.
                limit=2 if kind=="temperature" else (16 if kind=="height" else 2)
                merged=merge_similar_centers(sorted(all_candidates,reverse=True),arrays["latitude"],arrays["longitude"],250 if korea else 1000,limit)
            for mark, high, color in modes:
                candidates=([item[:4] for item in merged if item[4]==mark] if merged is not None else
                            candidates_for(high))
                for _, row, col, actual in candidates:
                    point = annotation_point(row, col)
                    if point is None:
                        continue
                    lon, lat, px, py, _, _ = point
                    quality_kind="pressure" if kind=="pressure" else int(product[-3:]) if kind=="height" and not product.startswith("thk") else None
                    if contour_filter is not None and quality_kind is not None and contour_filter(np.array([[lon,lat]]),actual,quality_kind):
                        continue
                    pin(lon, lat, color)
                    stroke = [effects.withStroke(linewidth=1.2, foreground=(1, 1, 1, .7))]
                    for text, offset, size, va in ((mark, 5, 10.5, "bottom"), (f"{actual:.0f}", -5, 8.7, "top")):
                        ax.annotate(text, (px, py), xytext=(0, offset), textcoords="offset points", color=color,
                                    fontsize=fs(size), ha="center", va=va, zorder=9, annotation_clip=True,
                                    path_effects=stroke, clip_on=True, gid=f"center-{kind}-{mark}")

        def numeric_extrema(value, kind, threshold=0,valid_mask=None,grid=None,color="black"):
            settings = numeric_extrema_parameters(domain, kind)
            selected=base_grid if grid is None else grid
            modes = (True,) if kind == "precipitation" else (True, False)
            candidates = [item for high in modes for item in
                          extrema_candidates(value, selected["latitude"], selected["longitude"],
                                             settings["radius"], settings["prominence"], high,valid_mask)]
            occupied = []
            for _, row, col, actual in sorted(candidates, reverse=True):
                if kind == "precipitation" and actual < max(threshold, settings["minimum"]):
                    continue
                if kind == "vorticity" and abs(actual) < settings["minimum"]:
                    continue
                point = annotation_point(row, col,grid)
                if point is None:
                    continue
                lon, lat, px, py, sx, sy = point
                if any(np.hypot(sx-x, sy-y) < (48 if korea else 70) for x, y in occupied):
                    continue
                text = str(int(np.rint(actual)))
                pin(lon, lat, color, 8)
                ax.annotate(text, (px, py), xytext=(0, -4), textcoords="offset points", color=color,
                            fontsize=fs(7), ha="center", va="top", zorder=8, annotation_clip=True, clip_on=True,
                            path_effects=[effects.withStroke(linewidth=1, foreground=(1, 1, 1, .7))],
                            gid=f"{kind}-extreme")
                occupied.append((sx, sy))

        def pressure_centers():
            centers(arrays["pressure_msl"]/100,(("H",True,"blue"),("L",False,"red")),
                    "pressure",field_masks.get("pressure_msl"))

        footer = ""
        snow_products={"acptot_snow","acptot_snowdepth","acrain_snow","acrain_snowdepth"}
        if product in {"surfce","acrain","acptot",*snow_products}:
            if product in snow_products:
                key=("total_" if product.startswith("acrain") else "")+("snowfall_depth_diagnostic" if product.endswith("snowdepth") else "snowfall_water_equivalent")
                precip=arrays[key]
            else:
                precip = accumulation if product == "acrain" else (None if pressure_only else arrays[precipitation_field])
            if precip is None and not pressure_only:
                raise ValueError("Missing accumulated precipitation")
            levels = RAIN_LEVELS if product == "surfce" else [.25, 1, 5, 10, 20, 30, 50, 75, 100, 150, 200, 250, 300, 400, 500, 750, 1000]
            threshold = (SNOW_THRESHOLD if product in snow_products else precipitation_threshold(cycle)) if public else (.25 if int(cycle[4:6]) in (10,11,12,1,2,3,4) else .5)
            levels = [threshold, *levels[1:]]
            if not pressure_only:
                if public:
                    snow_panel=product in snow_products
                    legend_levels=PUBLIC_SNOW_LEVELS if snow_panel else tuple(range(0,201,10)) if product=="acrain" else PUBLIC_RAIN_LEVELS
                    rain_levels=(threshold,*legend_levels[1:])
                    palette=PUBLIC_SNOW_COLORS if snow_panel else PUBLIC_RAIN_COLORS
                    # contourf closes its top interval on the right; 100 belongs to the green overflow here.
                    shade=np.where(precip==100,np.nextafter(100.,np.inf),precip) if snow_panel else precip
                    rain_fill=filled(shade,rain_levels,palette,PUBLIC_SNOW_OVER if snow_panel else palette[-1],
                                     grid=rain_grid,colorbar_levels=legend_levels,colorbar_extendfrac=.045 if snow_panel else 0)
                    selected=base_grid if rain_grid is None else rain_grid
                    coordinates=selected["projected"]
                    rain_values=np.ma.masked_where(~selected["visible"],precip)
                    edge=ax.contour(coordinates[:,:,0],coordinates[:,:,1],rain_values,
                                    levels=precipitation_edge_levels(float(np.max(precip)),threshold),colors="#282828",
                                    linewidths=.35,transform=projection,zorder=3,corner_mask=True)
                    edge.set_gid("precipitation-edge")
                else:
                    filled(np.maximum(precip, 0), levels, RAIN_COLORS, "#c00000",grid=rain_grid)
            else:
                cax.set_axis_off()
            if product in {"surfce","acptot","acptot_snowdepth"} or (public and product in {"acrain","acrain_snow","acrain_snowdepth"}):
                pressure = arrays["pressure_msl"] / 100
                steps = surface_steps(domain,profile)
                levels = np.arange(880, 1083, steps["minor"])
                obj = contour(pressure, levels, width=np.where((levels-steps.get("anchor",0)) % steps["major"] == 0, .9, .42),
                              label_levels=levels[levels % steps["label"] == 0],valid_mask=field_masks.get("pressure_msl"),quality_kind="pressure")
                obj.set_gid("pressure-contours")
                if not pressure_only:
                    numeric_extrema(np.maximum(precip, 0), "precipitation", threshold,grid=rain_grid)
                pressure_centers()
                title = "MSLP(hPa)" if pressure_only else f"MSLP(hPa) and Accum. Precip(mm)[{hour-precipitation_hours:03}-{hour:03}]"
                if product=="acrain":
                    title=f"MSLP(hPa) and Total Accum. Precip(mm)[000-{hour:03}]"
                elif product=="acrain_snow":
                    title=f"MSLP(hPa) and Total Accum. Snow(kg/m2)[000-{hour:03}]"
                elif product=="acrain_snowdepth":
                    title=f"MSLP, Total Accum. Snow Amount(cm) by SR Ratio[000-{hour:03}]"
                elif product=="acptot_snowdepth":
                    title=f"MSLP, Accum.Snow Amount(cm) by SR Ratio and Precip.Area[{hour-precipitation_hours:03}-{hour:03}]"
                    rain=arrays["precipitation"]
                    hatch(rain,precipitation_threshold(cycle),max(float(np.max(rain))+1,1),WINTER_HATCH_COLOR,gid="rain-area-hatch")
                elif product=="acptot" and "snow_expected" in arrays:
                    hatch(arrays["snow_expected"],.5,1.5,"#ff00ff",clip_to=rain_fill if public else None,gid="snow-area-hatch")
            elif product=="acptot_snow":
                heights=np.arange(0,4501,30)
                obj=contour(arrays["geopotential_925"]/9.80665,heights,"black",np.where((heights-810)%60==0,.9,.42),quality_kind=925)
                obj.set_gid("snow-height-contours")
                temperatures=np.arange(-60,4,3)
                obj=contour(arrays["temperature_925"]-273.15,temperatures,"red",np.where(temperatures%6==0,.85,.35))
                obj.set_gid("snow-temperature-contours")
                obj=contour(arrays["wet_bulb_2m"],[1.2],"#f28c00",1.2,label_levels=[])
                obj.set_gid("wet-bulb-contour")
                thickness=(arrays["geopotential_850"]-arrays["geopotential_1000"])/9.80665
                hatch(thickness,1281,1297,WINTER_HATCH_COLOR,gid="thickness-hatch")
                obj=contour(thickness,[1281,1297],WINTER_HATCH_COLOR,.4,smooth=False,text_size=7,label_levels=[])
                obj.set_gid("snow-thickness-boundaries")
                label_points=[]
                for level,segments in zip(obj.levels,obj.allsegs):
                    choices=[]
                    for segment in segments:
                        inside=segment[(segment[:,0]>spec["xlim"][0]+.06*np.ptp(spec["xlim"])) &
                                       (segment[:,0]<spec["xlim"][1]-.06*np.ptp(spec["xlim"])) &
                                       (segment[:,1]>spec["ylim"][0]+.06*np.ptp(spec["ylim"])) &
                                       (segment[:,1]<spec["ylim"][1]-.06*np.ptp(spec["ylim"]))]
                        if len(inside)>2:
                            choices.append(inside)
                    if choices:
                        segment=max(choices,key=len)
                        label_points.append(segment[len(segment)//2])
                if label_points:
                    texts=ax.clabel(obj,manual=label_points,fmt="%.0f",inline=True,inline_spacing=2,
                                    fontsize=fs(7),colors=WINTER_HATCH_COLOR)
                    for text in texts:
                        text.set_zorder(8)
                        text.set_path_effects([effects.withStroke(linewidth=1.5,foreground="white")])
                barbs(925,5)
                title=f"925hPa CHT, 1000-850 Thick.(m), sfc_Tw(1.2C) and Accum.Snow(kg/m2)[{hour-precipitation_hours:03}-{hour:03}]"
            else:
                title = f"Total Accumulated Precip(mm)[000-{hour:03}]"
                if product=="acrain_snow":
                    title=f"Total {'Diagnostic ' if diagnostic_snowfall else ''}Snowfall WE(kg/m2)[000-{hour:03}]"
                elif product=="acrain_snowdepth":
                    title=f"Total Snowfall Depth by SLR(cm)[000-{hour:03}]"
            footer = "" if pressure_only and hour==0 else "Precipitation is not provided by this source" if pressure_only else f"Precip. > {threshold:g} mm"
            if product in snow_products:
                footer=f"Snow > {SNOW_THRESHOLD:g} {'cm' if product.endswith('snowdepth') else 'kg/m2'}"
        elif product.startswith("wnd"):
            level=int(product[-3:])
            speed=np.hypot(arrays[f"wind_u_{level}"],arrays[f"wind_v_{level}"])*units("m/s").to("knots").m
            levels,colors=stream_shading(level)
            filled(speed,levels,colors,colors[-1],visible)
            obj=contour(speed,stream_isotach_levels(domain,level),
                        "red",.35,smooth=False)
            obj.set_gid("stream-isotach-contours")
            streamlines(level)
            if korea:
                numeric_extrema(speed,"wind",color="blue")
            title=f"{level}hPa Stream Line and Isotach(>{50 if level in (200,300) else 25}kt)"
        elif product.startswith("thk"):
            level=int(product[-3:])
            thickness=(arrays[f"geopotential_{level}"]-arrays["geopotential_1000"])/9.80665
            if level==500:
                if "vertical_velocity_700" in arrays:
                    omega=arrays["vertical_velocity_700"]*36
                    colors=tuple(matplotlib.colors.to_hex(color) for color in plt.get_cmap("YlOrRd_r")(np.linspace(0,1,15)))
                    display_omega=np.maximum(omega,-75)
                    filled(display_omega,np.arange(-75,1,5),colors,"white",visible)
                    contour(display_omega,np.arange(-75,1,5),"#666666",.25,6.5,smooth=False)
                else:
                    cax.set_axis_off()
                levels=np.arange(3000,6601,30 if korea else 60)
                obj=contour(thickness,levels,"blue",np.where((levels-5580)%((30 if korea else 60)*4)==0,.95,.4))
                obj.set_gid("thickness-contours")
                centers(thickness,(("H",True,UPPER_CENTER_COLORS["H"]),("L",False,UPPER_CENTER_COLORS["L"])),"height")
                barbs(700,5 if korea else 20)
                title=("1000-500hPa Thickness(m), 700hPa P-Velocity(hPa/hr) & Wind(>5kt)"
                       if "vertical_velocity_700" in arrays else "1000-500hPa Thickness(m), 700hPa Wind(>5kt)")
            elif level==700:
                theta=equivalent_potential_temperature(arrays,850)
                colors=THETA_COLORS[domain]
                filled(theta,THETA_LEVELS,colors,colors[-1])
                contour(theta,np.arange(240,421,3 if korea else 6),"#666666",.25,6.5,smooth=False)
                levels=np.arange(1800,4201,30 if korea else 60)
                obj=contour(thickness,levels,"black",np.where((levels-3000)%((30 if korea else 60)*4)==0,.95,.4))
                obj.set_gid("thickness-contours")
                hatch(thickness,2760,2820,"red")
                centers(thickness,(("H",True,UPPER_CENTER_COLORS["H"]),("L",False,UPPER_CENTER_COLORS["L"])),"height")
                centers(theta,(("W",True,"red"),("C",False,"blue")),"temperature",strict=True)
                barbs(850,5 if korea else 20)
                title="1000-700hPa Thickness(m), 850hPa Equiv.-P.Temp(K) & Wind(>5kt)"
            else:
                dew=mpcalc.dewpoint_from_specific_humidity(850*units.hPa,np.maximum(arrays["specific_humidity_850"],1e-9)*units("kg/kg")).to("K").m
                depression=arrays["temperature_850"]-dew
                filled(np.maximum(depression,0),[0,1,2,3,4],["#228b22","#66c266","#a6dba0","#d9f0d3"],"white")
                hatch(thickness,1281,1297,"blue")
                temperature=arrays["temperature_925"]-273.15
                levels=np.arange(-60,51,1 if korea else 3)
                obj=contour(temperature,levels,"red",np.where(levels%4==0,.85,.35))
                obj.set_gid("thickness-temperature-contours")
                centers(temperature,(("W",True,"red"),("C",False,"blue")),"temperature",strict=True)
                if "snowfall_water_equivalent" in arrays:
                    snow=arrays["snowfall_water_equivalent"]
                    hatch(snow,SNOW_THRESHOLD,max(float(np.max(snow))+1,1),"#ff00ff",gid="thickness-snow-hatch",pattern="---")
                    footer=f"Snow > {SNOW_THRESHOLD:g} kg/m2"
                else:
                    footer="Snow unavailable"
                barbs(925,5)
                title="925hPa Temp.(C), Wind(>5kt), 1000-850hPa Thick.(m) & 850hPa T-Td(C)"
        elif product in {"ttd700","anl850","anl925","anlsfc"}:
            level={"ttd700":700,"anl850":850,"anl925":925,"anlsfc":"sfc"}[product]
            if level=="sfc":
                temperature=arrays["temperature_2m"]
                dew=np.minimum(arrays["dewpoint_2m"],temperature)
            else:
                temperature=arrays[f"temperature_{level}"]
                dew=mpcalc.dewpoint_from_specific_humidity(level*units.hPa,
                    np.maximum(arrays[f"specific_humidity_{level}"],1e-9)*units("kg/kg")).to("K").m
                dew=np.minimum(dew,temperature)
            depression=np.maximum(temperature-dew,0)
            shade=filled(depression,[0,1,2,3,4],["#228b22","#66c266","#a6dba0","#d9f0d3"],"white")
            shade.set_gid("dewpoint-depression-shading")
            if level==700:
                temperature=arrays["temperature_500"]-273.15
                temperature_contour(temperature,500,major_every=4)
                centers(temperature,(("W",True,"red"),("C",False,"blue")),"temperature",strict=True)
                title="500hPa Temperature(C), 700hPa T-Td(C)"
            else:
                levels=np.arange(-80,51,5)
                obj=contour(dew-273.15,levels,"red",np.where(levels%20==0,.85,.35),
                            label_levels=None if korea else levels[levels%10==0])
                obj.set_gid("dewpoint-contours")
                if level=="sfc":
                    steps=surface_steps(domain,profile)
                    levels=np.arange(880,1085,1 if korea else 4)
                    obj=contour(arrays["pressure_msl"]/100,levels,"blue",
                                np.where((levels-1000)%((1 if korea else 4)*4)==0,.9,.42),
                                label_levels=levels[levels%steps["label"]==0],quality_kind="pressure")
                    obj.set_gid("pressure-contours")
                    pressure_centers()
                    minimum=5 if korea else 15
                    barbs("10m",minimum)
                    title=f"MSLP(hPa), T-Td(C), Td(C) and Wind(>{minimum}kt)"
                else:
                    height_contour(arrays[f"geopotential_{level}"]/9.80665,level,"blue",major_every=4)
                    minimum=5 if korea else 20
                    barbs(level,minimum)
                    centers(arrays[f"geopotential_{level}"]/9.80665,
                            (("H",True,UPPER_CENTER_COLORS["H"]),("L",False,UPPER_CENTER_COLORS["L"])),"height")
                    title=f"{level}hPa T-Td(C), Td(C) and Wind(>{minimum}kt)"
                centers(dew-273.15,(("W",True,"red"),("C",False,"blue")),"temperature",strict=True)
        elif product in {"gph500", "gph200", "gph300"}:
            level = 500 if product == "gph500" else (upper_level_override or (300 if product == "gph300" else upper_level(cycle)))
            height = arrays[f"geopotential_{level}"] / 9.80665
            temp = arrays[f"temperature_{level}"] - 273.15
            steps = contour_steps(domain, level,profile)
            valid_mask=field_masks.get(level)
            if level == 500:
                vort_valid=binary_erosion(valid_mask) if valid_mask is not None else None
                vort = smooth_valid(relative_vorticity(arrays),sigma,vort_valid)
                filled(vort, np.arange(0, 22, 2), VORT_COLORS, "#d60000",vort_valid)
                obj=contour(vort,np.arange(-20,61,4),"#666666",.28,7,smooth=False,label_color="black",
                            label_levels=[0] if public else None,valid_mask=vort_valid,sparse_zero=public)
                obj.set_gid("vorticity-contours")
                numeric_extrema(vort, "vorticity",valid_mask=vort_valid)
                title = "500hPa GPH(m), Temp(C), Relative Vorticity(E-5/s)"
            else:
                speed = np.hypot(arrays[f"wind_u_{level}"], arrays[f"wind_v_{level}"]) * units("m/s").to("knots").m
                colors = list(ISOTACH_COLORS)
                if korea:
                    colors[0] = "#7ef3f3"
                filled(speed, ISOTACH_LEVELS, colors, colors[-1],visible if valid_mask is None else valid_mask)
                speed_contours=contour(speed, np.arange(50 if public else 25, 251, 25), "black", .3, 7,valid_mask=valid_mask,smooth=False)
                speed_contours.set_gid("isotach-contours")
                title = f"{level}hPa GPH(m), Temp(C), Isotach(>50kt)" if public else f"{level}hPa GPH(m), Temp(C), Wind Speed(kt)"
            height_contour(height, level)
            temperature_contour(temp, level)
            centers(height, (("H", True, UPPER_CENTER_COLORS["H"]), ("L", False, UPPER_CENTER_COLORS["L"])), "height",valid_mask)
            centers(temp, (("W", True, UPPER_CENTER_COLORS["W"]), ("C", False, UPPER_CENTER_COLORS["C"])), "temperature",valid_mask)
        else:
            level = int(product[-3:])
            theta = equivalent_potential_temperature(arrays, level)
            colors = THETA_COLORS[domain]
            valid_mask=field_masks.get(level)
            filled(theta, THETA_LEVELS, colors, colors[-1],valid_mask)
            steps = contour_steps(domain, level,profile)
            contour(theta, np.arange(240, 421, steps["theta_e"]), "#666666", .3, 6.7, label_color="black",valid_mask=valid_mask)
            height = arrays[f"geopotential_{level}"] / 9.80665
            height_contour(height, level)
            temp = arrays[f"temperature_{level}"] - 273.15
            if korea:
                temperature_contour(temp, level)
            minimum = 5 if korea else (20 if level == 700 else 10)
            barbs(level, minimum)
            centers(height, (("H", True, UPPER_CENTER_COLORS["H"]), ("L", False, UPPER_CENTER_COLORS["L"])), "height",valid_mask)
            if korea:
                centers(temp, (("W", True, UPPER_CENTER_COLORS["W"]), ("C", False, UPPER_CENTER_COLORS["C"])), "temperature",valid_mask)
            title = f"{level}hPa GPH(m), " + ("Temp(C), " if korea else "") + f"Equiv.P.Temp(K), Wind(>{minimum}kt)"

        if public:
            title=product_title(product,domain,hour,precipitation_hours,
                                upper=upper_level_override or upper_level(cycle),
                                has_omega="vertical_velocity_700" in arrays,pressure_only=pressure_only)
        title_y = pos.y1 + .005
        heading=figure.text(pos.x0,title_y,title,size=fs(8.6 if korea else 10.1),weight="bold",family="DejaVu Serif",va="bottom")
        model_text=figure.text(pos.x0 if korea else pos.x1,title_y+(.024 if korea and public else .020 if korea else 0),model_name,size=fs(9),
                               color="#0000cc",ha="left" if korea else "right",weight="bold",family="DejaVu Serif",va="bottom")
        heading.set_gid("product-title")
        title_scale=1.
        if public:
            right=pos.x1 if korea else model_text.get_window_extent(figure.canvas.get_renderer()).x0/figure.bbox.width-.005
            title_scale=fit_heading(figure,heading,right)
        init = parse_cycle(cycle)
        size = fs(7.5 if korea else 9)
        footer_blocks=draw_time_footer(figure,pos,init,hour,size,public=public,korea=korea)
        if footer:
            note_x=(pos.x0+pos.x1)/2
            if public and korea:
                note_x=(footer_blocks["valid"][1]+footer_blocks["init"][0])/2
            figure.text(note_x,pos.y0-(.019 if public else .010),footer,size=fs(5.5 if korea else 7),color="navy",ha="center",gid="rain-threshold-note")
        if source_note:
            note_y=.008 if korea else .012
            source_note="Plotted by WooJin Kim\n"+source_note.replace("Data Sourced from","Data sourced from",1)
            ax.text(.01, note_y, source_note, transform=ax.transAxes, fontsize=fs(4.7 if korea else 5.6),
                    color="#333333", ha="left", va="bottom", zorder=10, gid="source-note",
                    bbox={"facecolor":"white", "edgecolor":"none", "alpha":.9, "pad":1})
            ax.text(.99,note_y,"Chart style inspired by KMA",transform=ax.transAxes,fontsize=fs(4.7 if korea else 5.6),
                    color="#333333",ha="right",va="bottom",zorder=10,gid="style-inspiration-note",
                    bbox={"facecolor":"white","edgecolor":"none","alpha":.9,"pad":1})
        from PIL import Image
        figure.set_dpi(160)
        figure.canvas.draw()
        frame=Image.fromarray(np.asarray(figure.canvas.buffer_rgba())).convert("RGB")
        if profile==PUBLIC_PROFILE:
            frame=frame.resize(PUBLIC_IMAGE_SIZES[domain],Image.Resampling.LANCZOS)
        if return_frame:
            return frame
        target = Path(target)
        target.parent.mkdir(parents=True,exist_ok=True)
        temporary = target.with_suffix(".tmp")
        if target.suffix.lower()==".webp":
            frame.save(temporary,format="WEBP",lossless=True,quality=80,method=4)
        else:
            frame.save(temporary,format="PNG")
        temporary.replace(target)
        stamp = target.with_suffix(".style.tmp")
        stamp.write_text(json.dumps({"version": STYLE_VERSION, "profile":profile,"bytes": target.stat().st_size}), encoding="utf-8")
        stamp.replace(target.with_suffix(".style.json"))
        result={"seconds": round(time.perf_counter()-started, 3), "bytes": target.stat().st_size,
                "title":title,"title_width_scale":round(title_scale,4)}
        if product.startswith("wnd"):
            result["wind_extrema_count"]=sum(text.get_gid()=="wind-extreme" for text in ax.texts)
        return result
    finally:
        if figure is not None:
            plt.close(figure)
