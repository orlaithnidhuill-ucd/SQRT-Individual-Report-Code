import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("housekeeping_log9963.csv", header=None)

df.columns = [
    "timestamp",
    "temp_internal_1",
    "pressure_mbar",
    "temp_external",
    "temp_internal_2",
    "counter",
    "latitude",
    "longitude",
    "altitude_m",
    "misc"
]

numeric_cols = [
    "temp_internal_1",
    "temp_external",
    "temp_internal_2",
    "altitude_m"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(
    subset=[
        "temp_external",
        "temp_internal_2",
        "altitude_m"
    ]
)

df = df[
    (df["altitude_m"] >= 0) &
    (df["altitude_m"] < 10000)
]

df["altitude_km"] = df["altitude_m"] / 1000

df = df[
    df["altitude_km"].diff().abs() < 1
]

plt.figure(figsize=(7, 9))

# Interna temp
plt.plot(
    df["temp_internal_2"],
    df["altitude_km"],
    color="red",
    linewidth=2.8,
    label="Internal Temperature"
)

# External temp
plt.plot(
    df["temp_external"],
    df["altitude_km"],
    color="blue",
    linewidth=2.8,
    linestyle="--",
    label="External Temperature"
)

plt.text(
    22,
    7.2,
    "Telemetry terminated\nbefore trigger altitude",
    fontsize=10
)

plt.xlabel("Temperature (°C)")
plt.ylabel("Altitude (km)")

plt.title("SQRT Internal and External Temperature Profiles")

plt.grid(True, alpha=0.3)
plt.legend()

plt.ylim(0, 9)

plt.tight_layout()

plt.savefig(
    "sqrt_temperature_profiles_corrected.png",
    dpi=300
)

plt.show()
