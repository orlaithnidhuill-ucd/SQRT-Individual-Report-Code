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


df["timestamp_local"] = df[time_col] + pd.Timedelta(hours=1) # Convert UTC to local time


df["altitude_m"] = df[alt_col] # Altitude in metres and km
df["altitude_km"] = df["altitude_m"] / 1000

# Clean it up
df = df[
    (df["altitude_km"] >= 0) &
    (df["altitude_km"] < 40)
].copy()

df = df.sort_values("timestamp_local").reset_index(drop=True) # Sort by time
df = df[
    df["altitude_km"].diff().abs() < 2 # Remove obvious GPS jumps
].reset_index(drop=True)


df["altitude_smooth_m"] = (
    df["altitude_m"]
    .rolling(window=15, center=True, min_periods=1)
    .mean()
)

df["time_seconds"] = (
    df["timestamp_local"] -
    df["timestamp_local"].iloc[0]
).dt.total_seconds()

df["velocity_mps"] = (
    df["altitude_smooth_m"].diff() /
    df["time_seconds"].diff()
)

df["velocity_smooth_mps"] = (
    df["velocity_mps"]
    .rolling(window=25, center=True, min_periods=1)
    .mean()
)

df["acceleration_mps2"] = (
    df["velocity_smooth_mps"].diff() /
    df["time_seconds"].diff()
)

df["acceleration_smooth_mps2"] = (
    df["acceleration_mps2"]
    .rolling(window=45, center=True, min_periods=1)
    .mean()
)

burst_index = df["altitude_smooth_m"].idxmax()
burst_time = df.loc[burst_index, "timestamp_local"]
burst_altitude_km = df.loc[burst_index, "altitude_smooth_m"] / 1000

ascent = df[df["timestamp_local"] < burst_time]
descent = df[df["timestamp_local"] > burst_time]

avg_ascent_rate = ascent["velocity_smooth_mps"].mean()
max_ascent_rate = ascent["velocity_smooth_mps"].max()

avg_descent_rate = descent["velocity_smooth_mps"].mean()
max_descent_rate = descent["velocity_smooth_mps"].min()

# Plotting it all out

plt.figure(figsize=(11, 5.5))

plt.plot(
    df["timestamp_local"],
    df["velocity_smooth_mps"],
    color="darkgreen",
    linewidth=2.5
)

plt.axhline(
    0,
    color="black",
    linestyle="--",
    linewidth=1
)

plt.axvline(
    burst_time,
    color="red",
    linestyle="--",
    linewidth=1.5,
    label="Burst Event"
)

plt.text(
    pd.Timestamp("2026-04-12 12:20:00"),
    7,
    "Steady ascent",
    fontsize=10,
    color="darkgreen"
)

plt.text(
    burst_time + pd.Timedelta(minutes=6),
    -12,
    "Parachute descent",
    fontsize=10,
    color="darkgreen"
)

plt.text(
    burst_time,
    8,
    f"Burst\n{burst_altitude_km:.1f} km",
    color="red",
    fontsize=10,
    ha="left"
)

ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
plt.xticks(rotation=20)

plt.xlim(
    pd.Timestamp("2026-04-12 11:50:00"),
    pd.Timestamp("2026-04-12 13:45:00")
)

plt.xlabel("Local Time")
plt.ylabel("Vertical Velocity (m/s)")
plt.title("Vertical Velocity Profile of the Flight")

plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig("vertical_velocity_profile_clean.png", dpi=300)
plt.show()

plt.figure(figsize=(11, 5.5))

plt.plot(
    df["timestamp_local"],
    df["acceleration_smooth_mps2"],
    color="purple",
    linewidth=2
)

plt.axhline(
    0,
    color="black",
    linestyle="--",
    linewidth=1
)

plt.axvline(
    burst_time,
    color="red",
    linestyle="--",
    linewidth=1.5,
    label="Burst Event"
)

plt.text(
    burst_time + pd.Timedelta(minutes=3),
    df["acceleration_smooth_mps2"].max() * 0.6,
    "Dynamic disturbance\naround burst/descent",
    color="purple",
    fontsize=10
)

ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
plt.xticks(rotation=20)

plt.xlim(
    pd.Timestamp("2026-04-12 11:50:00"),
    pd.Timestamp("2026-04-12 13:45:00")
)

plt.xlabel("Local Time")
plt.ylabel("Vertical Acceleration (m/s²)")
plt.title("Smoothed Vertical Acceleration Profile")

plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig("vertical_acceleration_profile_clean.png", dpi=300)
plt.show()

print(f"Burst altitude: {burst_altitude_km:.2f} km")
print(f"Average ascent rate: {avg_ascent_rate:.2f} m/s")
print(f"Maximum ascent rate: {max_ascent_rate:.2f} m/s")
print(f"Average descent rate: {avg_descent_rate:.2f} m/s")
print(f"Maximum descent rate: {max_descent_rate:.2f} m/s")
