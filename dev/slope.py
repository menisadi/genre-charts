import argparse
import pandas as pd


def calculate_period(start, end, resolution="days"):
    delta = end - start
    if resolution == "seconds":
        return delta.total_seconds()
    elif resolution == "hours":
        return delta.total_seconds() // 3600
    elif resolution == "days":
        return delta.days + 1  # Include both endpoints
    elif resolution == "weeks":
        return (delta.days // 7) + 1  # Include both endpoints as whole weeks
    else:
        raise ValueError("Resolution must be 'seconds', 'hours', 'days', or 'weeks'.")


def calculate_max_slope_with_details(group, resolution="days"):
    timestamps = group["timestamp"].to_list()
    n = len(timestamps)
    max_slope = 0
    start_time = None
    end_time = None
    track_count = 0

    # Iterate over all possible time windows
    for i in range(n):
        for j in range(i + 1, n):
            period = calculate_period(
                timestamps[i], timestamps[j], resolution=resolution
            )
            if period <= 0:  # Skip invalid periods
                continue
            play_count = j - i + 1  # Number of plays in this period
            slope = play_count / period
            if slope > max_slope:
                max_slope = slope
                start_time = timestamps[i]
                end_time = timestamps[j]
                track_count = play_count  # Update the track count for this period

    return pd.Series(
        {
            "max_slope": max_slope,
            "start_time": start_time,
            "end_time": end_time,
            "track_count": track_count,
        }
    )


def main(resolution="weeks", top_k=5):
    file_path = "./menisadig.csv"
    df = pd.read_csv(
        file_path, header=None, names=["artist", "album", "track", "timestamp"]
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(by=["artist", "timestamp"])

    result = (
        df.groupby("artist")
        .filter(lambda x: len(x) > 1)  # Filter artists with more than 1 play
        .groupby("artist")
        .apply(calculate_max_slope_with_details, resolution=resolution)
        .reset_index()
    )
    result[resolution] = result.apply(
        lambda row: calculate_period(
            row["start_time"], row["end_time"], resolution=resolution
        ),
        axis=1,
    )

    top_k_artists = result.sort_values(by="max_slope", ascending=False).head(top_k)
    # print(top_k_artists.drop(["start_time", "end_time"], axis=1))
    print(top_k_artists)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--resolution",
        default="weeks",
        choices=["seconds", "hours", "days", "weeks"],
        help="Time resolution for slope calculation",
    )
    parser.add_argument(
        "-k", "--top-k", type=int, default=5, help="Number of top artists to display"
    )
    args = parser.parse_args()

    main(resolution=args.resolution, top_k=args.top_k)
