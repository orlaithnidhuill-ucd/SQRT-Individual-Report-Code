import pandas as pd
import matplotlib.pyplot as plt

sqrt_df = pd.read_csv("housekeeping_log9963.csv", header=None)

sqrt_df.columns = [
    "timestamp_raw",
    "internal_temp",
    "pressure_mbar",
    "external_temp",
    "sensor_temp",
    "col6",
    "col7",
    "col8",
    "col9",
    "battery"
]

sqrt_df["pressure_mbar"] = pd.to_numeric(
    sqrt_df["pressure_mbar"],
    errors="coerce"
)

sqrt_df = sqrt_df.dropna(subset=["pressure_mbar"])

sqrt_df = sqrt_df[
    (sqrt_df["pressure_mbar"] > 20) &
    (sqrt_df["pressure_mbar"] < 1050)
].reset_index(drop=True)

P0 = 1013.25

sqrt_df["altitude_m"] = 44330 * (
    1 - (sqrt_df["pressure_mbar"] / P0) ** 0.1903
)

sqrt_df["altitude_km"] = sqrt_df["altitude_m"] / 1000

sky_df = pd.read_csv("hk_20260412_063824.csv")

sky_df.columns = sky_df.columns.str.strip().str.lower()

sky_df["pressure_mbar"] = pd.to_numeric(
    sky_df["pressure_kpa"],
    errors="coerce"
) * 10

altitude_candidates = [
    "gps_altitude_m",
    "altitude_m",
    "altitude",
    "gps_altitude",
    "pressure_altitude_m"
]

altitude_col = None

for col in altitude_candidates:
    if col in sky_df.columns:
        altitude_col = col
        break

if altitude_col is None:
    raise ValueError(
        f"No altitude column found. Available columns are: {list(sky_df.columns)}"
    )

sky_df[altitude_col] = pd.to_numeric(
    sky_df[altitude_col],
    errors="coerce"
)

sky_df = sky_df.dropna(subset=["pressure_mbar", altitude_col])

sky_df = sky_df[
    (sky_df["pressure_mbar"] > 20) &
    (sky_df["pressure_mbar"] < 1050)
].reset_index(drop=True)

sky_df["altitude_km"] = sky_df[al

sky_df = sky_df[
    (sky_df["altitude_km"] >= 0) &
    (sky_df["altitude_km"] < 40)
].reset_index(drop=True)

# Remove telemetry spikes/dropouts
sky_df = sky_df[
    sky_df["altitude_km"].diff().abs() < 2
].reset_index(drop=True)

plt.figure(figsize=(7, 9))

plt.plot(
    sky_df["pressure_mbar"],
    sky_df["altitude_km"],
    color="blue",
    linewidth=1.8,
    label="Skynet Telemetry"
)

plt.plot(
    sqrt_df["pressure_mbar"],
    sqrt_df["altitude_km"],
    color="red",
    linewidth=3,
    linestyle="--",
    label="SQRT Telemetry"
)
plt.text(
    400,
    7.8,
    "SQRT telemetry terminated\nbefore planned trigger region",
    color="red",
    fontsize=10
)

plt.text(
    80,
    23,
    "Planned trigger region:\n35 mbar (~23 km)",
    color="black",
    fontsize=10
)

plt.xlabel("Pressure (mbar)")
plt.ylabel("Altitude (km)")

plt.title("Pressure Profile with Altitude: SQRT and Skynet Telemetry")

plt.grid(True, alpha=0.3)
plt.legend()

plt.ylim(0, 25)

plt.tight_layout()

plt.savefig(
    "pressure_vs_altitude_sqrt_skynet_overlay_clean.png",
    dpi=300
)

plt.show()
