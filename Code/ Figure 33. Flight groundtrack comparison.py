import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx
from pyproj import Transformer

prediction_file = "/content/ascent_at11_7.csv"
skynet_file = "hk_20260412_063824.csv"

recovery_lat = 54 + 34/60 + 40.8/3600
recovery_lon = -(6 + 46/60 + 28.9/3600)

pred = pd.read_csv(prediction_file)
pred.columns = pred.columns.str.strip().str.lower()
pred["latitude"] = pd.to_numeric(pred["latitude"], errors="coerce")
pred["longitude"] = pd.to_numeric(pred["longitude"], errors="coerce")
pred = pred.dropna(subset=["latitude", "longitude"])
pred = pred[
    (pred["latitude"] > 54) & (pred["latitude"] < 56) &
    (pred["longitude"] > -8) & (pred["longitude"] < -5)
].reset_index(drop=True)

sky = pd.read_csv(skynet_file)
sky.columns = sky.columns.str.strip().str.lower()

lat_col = "latitude"
lon_col = "longitude"

sky[lat_col] = pd.to_numeric(sky[lat_col], errors="coerce")
sky[lon_col] = pd.to_numeric(sky[lon_col], errors="coerce")
sky = sky.dropna(subset=[lat_col, lon_col])
sky = sky[
    (sky[lat_col] > 54) & (sky[lat_col] < 56) &
    (sky[lon_col] > -8) & (sky[lon_col] < -5)
].reset_index(drop=True)

pred_gdf = gpd.GeoDataFrame(
    pred,
    geometry=[Point(xy) for xy in zip(pred["longitude"], pred["latitude"])],
    crs="EPSG:4326"
).to_crs(epsg=3857)

sky_gdf = gpd.GeoDataFrame(
    sky,
    geometry=[Point(xy) for xy in zip(sky[lon_col], sky[lat_col])],
    crs="EPSG:4326"
).to_crs(epsg=3857)

recovery_gdf = gpd.GeoSeries(
    [Point(recovery_lon, recovery_lat)],
    crs="EPSG:4326"
).to_crs(epsg=3857)

# Plotting it out
fig, ax = plt.subplots(figsize=(9, 9))

pred_gdf.plot(
    ax=ax,
    color="blue",
    linestyle="-",
    linewidth=1.5,
    label="Predicted Trajectory"
)

sky_gdf.plot(
    ax=ax,
    color="red",
    linewidth=1.5,
    label="Actual Groundtrack"
)

ax.scatter(
    pred_gdf.geometry.iloc[0].x,
    pred_gdf.geometry.iloc[0].y,
    color="green",
    s=120,
    marker="o",
    label="Launch Site",
    zorder=5
)

ax.scatter(
    pred_gdf.geometry.iloc[-1].x,
    pred_gdf.geometry.iloc[-1].y,
    color="black",
    s=180,
    marker="x",
    linewidths=3,
    label="Predicted Landing",
    zorder=6
)

ax.scatter(
    recovery_gdf.x.iloc[0],
    recovery_gdf.y.iloc[0],
    color="gold",
    edgecolors="black",
    s=320,
    marker="*",
    label="Actual Recovery",
    zorder=7
)

xmin, ymin, xmax, ymax = pd.concat([pred_gdf, sky_gdf]).total_bounds
padding = 6000
ax.set_xlim(xmin - padding, xmax + padding)
ax.set_ylim(ymin - padding, ymax + padding)

ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)

xticks = ax.get_xticks()
yticks = ax.get_yticks()

lon_labels = []
for x in xticks:
    lon, lat = transformer.transform(x, yticks[0])
    lon_labels.append(f"{lon:.2f}")

lat_labels = []
for y in yticks:
    lon, lat = transformer.transform(xticks[0], y)
    lat_labels.append(f"{lat:.2f}")

ax.set_xticks(xticks)
ax.set_yticks(yticks)
ax.set_xticklabels(lon_labels)
ax.set_yticklabels(lat_labels)

ax.set_title("Flight Groundtrack Compared with Pre-Flight Prediction", fontsize=14)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

ax.grid(True, alpha=0.3)
ax.legend(loc="lower left")

plt.tight_layout()

plt.savefig(
    "flight_groundtrack_openstreetmap_axes.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
