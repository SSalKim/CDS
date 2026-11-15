"""Selective display filtering of complete closed contours, never terrain holes."""
import numpy as np

GRAVITY = 9.80665
QUALITY_VERSION = 3
TIBET_BOUNDS = (25, 40, 70, 105)


def terrain_masks(arrays):
    # Preserve the old call contract; no altitude or below-ground field is hidden.
    return {}


def mask_statistics(masks):
    return {str(key): {"masked_cells": int(np.count_nonzero(~value)), "total_cells": int(value.size)}
            for key,value in masks.items()}


def closed_contour_predicate(arrays):
    latitude,longitude=arrays["latitude"],arrays["longitude"]
    terrain=arrays["terrain_height"]
    gradients={}
    def suspicious(points,level,kind):
        if kind!="pressure" and kind not in (700,850,925):
            return False
        points=np.asarray(points)
        south,north,west,east=TIBET_BOUNDS
        inside=((points[:,1]>=south)&(points[:,1]<=north)&(points[:,0]>=west)&(points[:,0]<=east))
        rows=np.clip(np.searchsorted(latitude,points[:,1]),0,len(latitude)-1)
        cols=np.clip(np.searchsorted(longitude,points[:,0]),0,len(longitude)-1)
        highland=inside&(terrain[rows,cols]>=3000)
        if np.mean(highland)<.6:
            return False
        if kind not in gradients:
            value=arrays["pressure_msl"]/100 if kind=="pressure" else arrays[f"geopotential_{kind}"]/GRAVITY
            dy,dx=np.gradient(value,latitude*111,longitude*111)
            gradients[kind]=np.hypot(dy,dx/np.maximum(.1,np.cos(np.deg2rad(latitude[:,None]))))*100
        high_limit=1040 if kind=="pressure" else {700:3500,850:1850,925:1100}[kind]
        steep_limit=6 if kind=="pressure" else 80
        return bool(level>=high_limit or np.percentile(gradients[kind][rows,cols],90)>=steep_limit)
    return suspicious
