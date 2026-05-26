import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

df = pd.read_csv("hk_20260412_063824.csv")
df.columns = df.columns.str.strip().str.lower()

time_col = "timestamp_utc"
alt_col = "gps_altitude"

df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
df[alt_col] = pd.to_numeric(df[alt_col], errors="coerce")

df = df.dropna(subset=[time_col, alt_col])
df["timestamp_local"] = df[time_col] + pd.Timedelta(hours=1)
df["altitude_km"] = df[alt_col] / 1000

df = df[
    (df["altitude_km"] >= 0) &
    (df["altitude_km"] < 40)
].copy()

df = df.sort_values("timestamp_local").reset_index(drop=True)

df = df[
    df["altitude_km"].diff().abs() < 2
].reset_index(drop=True)

df["altitude_smooth_km"] = (
    df["altitude_km"]
    .rolling(window=15, center=True, min_periods=1)
    .mean()
)

burst_index = df["altitude_smooth_km"].idxmax()
burst_time = df.loc[burst_index, "timestamp_local"]
burst_altitude = df.loc[burst_index, "altitude_smooth_km"]

landing_time = df["timestamp_local"].iloc[-1]

plt.figure(figsize=(11, 6))

plt.plot(
    df["timestamp_local"],
    df["altitude_smooth_km"],
    color="blue",
    linewidth=2.5,
    label="Smoothed altitude profile"
)

plt.scatter(
    burst_time,
    burst_altitude,
    color="red",
    s=120,
    zorder=5,
    label="Burst point"
)

plt.text(
    burst_time,
    burst_altitude + 1,
    f"Burst ≈ {burst_altitude:.1f} km",
    color="red",
    fontsize=10,
    ha="center"
)

plt.text(
    pd.Timestamp("2026-04-12 11:30:00"),
    10,
    "Launch and steady ascent",
    color="black",
    fontsize=10
)

plt.text(
    burst_time + pd.Timedelta(minutes=17),
    burst_altitude * 0.55,
    "Descent under parachute",
    color="black",
    fontsize=10
)

plt.text(
    landing_time - pd.Timedelta(minutes=30),
    1.5,
    "Landing & recovery",
    color="black",
    fontsize=10
)

ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
plt.xticks(rotation=20)

plt.xlabel("Local Time")
plt.ylabel("Altitude (km)")
plt.title("Altitude-Time Profile of the Balloon Flight")

plt.grid(True, alpha=0.3)
plt.legend()

plt.ylim(0, burst_altitude + 3)

plt.tight_layout()

plt.savefig("altitude_time_profile_clean.png", dpi=300)
plt.show()

print(f"Burst altitude: {burst_altitude:.2f} km")
print(f"Burst time: {burst_time}")
print(f"Landing/recovery end time in telemetry: {landing_time}")
