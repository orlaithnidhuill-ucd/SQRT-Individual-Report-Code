import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

sqrt_df["timestamp_raw"] = pd.to_numeric(
    sqrt_df["timestamp_raw"],
    errors="coerce"
)

sqrt_df["pressure_mbar"] = pd.to_numeric(
    sqrt_df["pressure_mbar"],
    errors="coerce"
)

sqrt_df = sqrt_df.dropna(subset=["timestamp_raw", "pressure_mbar"])

sqrt_df = sqrt_df[
    (sqrt_df["pressure_mbar"] > 20) &
    (sqrt_df["pressure_mbar"] < 1050)
].reset_index(drop=True)

sqrt_df["relative_seconds"] = (
    sqrt_df["timestamp_raw"] - sqrt_df["timestamp_raw"].iloc[0]
)

ascent_start_index = sqrt_df.index[sqrt_df["pressure_mbar"] < 1000][0]
ascent_start_seconds = sqrt_df.loc[ascent_start_index, "relative_seconds"]

launch_time_local = pd.Timestamp("2026-04-12 12:06:00")

sqrt_df["timestamp_local"] = (
    launch_time_local
    + pd.to_timedelta(
        sqrt_df["relative_seconds"] - ascent_start_seconds,
        unit="s"
    )
)

sky_df = pd.read_csv("hk_20260412_063824.csv")

sky_df.columns = sky_df.columns.str.strip().str.lower()

sky_df["timestamp_utc"] = pd.to_datetime(
    sky_df["timestamp_utc"],
    errors="coerce"
)

sky_df["timestamp_local"] = sky_df["timestamp_utc"] + pd.Timedelta(hours=1)

sky_df["pressure_mbar"] = pd.to_numeric(
    sky_df["pressure_kpa"],
    errors="coerce"
) * 10

sky_df = sky_df.dropna(subset=["timestamp_local", "pressure_mbar"])

sky_df = sky_df.sort_values("timestamp_local")
sky_df = sky_df.drop_duplicates(subset=["timestamp_local"])

sky_df = sky_df[
    (sky_df["pressure_mbar"] > 20) &
    (sky_df["pressure_mbar"] < 1050)
]
sky_df = sky_df[
    sky_df["pressure_mbar"].diff().abs() < 40
]

plt.figure(figsize=(11, 6))

plt.plot(
    sky_df["timestamp_local"],
    sky_df["pressure_mbar"],
    color="blue",
    linewidth=1.8,
    label="Skynet Telemetry"
)

plt.plot(
    sqrt_df["timestamp_local"],
    sqrt_df["pressure_mbar"],
    color="red",
    linewidth=3,
    linestyle="--",
    label="SQRT Telemetry"
)

plt.gca().invert_yaxis()

ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
plt.xticks(rotation=20)

plt.xlim(
    pd.Timestamp("2026-04-12 11:55:00"),
    pd.Timestamp("2026-04-12 13:45:00")
)

plt.ylim(1050, 0)

plt.text(
    pd.Timestamp("2026-04-12 12:43:00"),
    340,
    "SQRT telemetry terminated\nprematurely during ascent",
    color="red",
    fontsize=10,
    ha="left"
)

plt.xlabel("Local Time")
plt.ylabel("Pressure (mbar)")
plt.title("Pressure Profile with Time: SQRT and Skynet Telemetry")

plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()

plt.savefig(
    "pressure_profile_time_sqrt_skynet_overlay.png",
    dpi=300
)

plt.show()
