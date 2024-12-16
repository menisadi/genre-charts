import json
from tqdm import tqdm
import pylast
import matplotlib.pyplot as plt
import pandas as pd
import plotting


def initialize():
    with open("tokens.json", "r") as file:
        tokens: dict[str, str] = json.load(file)
    with open("user_names.json", "r") as file:
        user_names: dict[str, str] = json.load(file)

    API_KEY = tokens.get("last_api_key")
    API_SECRET = tokens.get("last_secret")
    USERNAME = tokens.get("last_username")
    PASSWORD_HASH = pylast.md5(tokens.get("last_password"))

    # if any of the tokens are not found, the app will not work
    try:
        assert API_KEY is not None
        assert API_SECRET is not None
        assert USERNAME is not None
        assert PASSWORD_HASH is not None
    except AssertionError:
        raise Exception(
            "API_KEY, API_SECRET, USERNAME, and PASSWORD_HASH must be set in tokens.json"
        )

    network = pylast.LastFMNetwork(
        api_key=API_KEY,
        api_secret=API_SECRET,
        username=USERNAME,
        password_hash=PASSWORD_HASH,
    )

    return network, user_names


def plot_top_tags_trend(
    network, file_path: str, play_threshold: int = 10, top_k: int = 5
):
    df = pd.read_csv(file_path, header=None, names=["artist", "Album", "track", "time"])
    artists_series = df["artist"].value_counts()
    top_artists = list(artists_series[artists_series > play_threshold].index)
    top_data = df.loc[df["artist"].isin(top_artists)].copy()
    tags_dict = dict.fromkeys(top_artists)
    for artist in tqdm(top_artists):
        top_tags: list[pylast.Tag] = network.get_artist(artist).get_top_tags(limit=1)
        if top_tags:
            tags_of_artist = [tag.item.name for tag in top_tags]
            tags_dict[artist] = tags_of_artist[0]
            if tags_of_artist[0] == "seen live":
                top_tags: list[pylast.Tag] = network.get_artist(artist).get_top_tags(
                    limit=2
                )
                if len(top_tags) > 1:
                    tags_of_artist = [tag.item.name for tag in top_tags]
                    tags_dict[artist] = tags_of_artist[1]

    top_data["tag"] = top_data["artist"].replace(tags_dict)
    top_genres = top_data["tag"].value_counts().nlargest(top_k).index
    top_genres_df = top_data.loc[top_data["tag"].isin(top_genres)].copy()
    top_genres_df["timestamp"] = pd.to_datetime(top_genres_df["time"])
    top_genres_df["year"] = top_genres_df["timestamp"].dt.year
    trend_data = top_genres_df.groupby(["year", "tag"]).size().reset_index(name="count")
    trend_pivot = trend_data.pivot(index="year", columns="tag", values="count").fillna(
        0
    )
    trend_pivot = trend_pivot.div(trend_pivot.sum(axis=1), axis=0) * 100

    return trend_pivot


def main():
    network, _ = initialize()
    trend_pivot = plot_top_tags_trend(
        network, "menisadig.csv", play_threshold=100, top_k=5
    )
    trend_pivot.to_csv("trend_pivot.csv")

    plotting.simple_plot(trend_pivot)


if __name__ == "__main__":
    main()
