import json
from tqdm import tqdm
import pylast
import matplotlib.pyplot as plt
import pandas as pd


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
    trend_pivot.plot(kind="line", marker="o", title="Genre Trends Over Years")
    plt.show()


def rad_tracks_file(network, file_path: str, prune_tag_list: int = 1):
    df = pd.read_csv(file_path, header=None, names=["artist", "Album", "track", "time"])
    artists_series = df["artist"].value_counts()
    artists_weights = [(art, count) for art, count in artists_series.to_dict().items()]
    artists_list = df["artist"].unique()
    tags_dict = dict.fromkeys(artists_list)
    for artist in tqdm(artists_list):
        top_tags: list[pylast.Tag] = network.get_artist(artist).get_top_tags(
            limit=prune_tag_list
        )
        tags_of_artist = [tag.item.name for tag in top_tags]
        tags_dict[artist] = tags_of_artist

    tags_columns = ["tag_" + str(i) for i in range(prune_tag_list)]

    all_tags = get_top_tags(network, artists_weights, limit=0, prune_tag_list=3)

    return all_tags


def old_main():
    network, user_names = initialize()
    # convert the time period to the same format as pylast
    period_dict = {
        "overall": pylast.PERIOD_OVERALL,
        "weekly": pylast.PERIOD_7DAYS,
        "monthly": pylast.PERIOD_1MONTH,
        "yearly": pylast.PERIOD_12MONTHS,
        None: pylast.PERIOD_OVERALL,
    }

    people_names: list[str] = list(user_names.keys())

    # for fix the user name
    chosen_user = user_names.get(people_names[0])
    print(f"Showing tags for {chosen_user}")
    # for start lets pick a time period and user
    chosen_time_period = "yearly"
    print(f"Using time period: {chosen_time_period}")
    print(f"Pylast time period: {period_dict.get(chosen_time_period)}")

    artist_limit = 50
    user_top_artists = get_users_top_artists(
        network=network,
        user_name=chosen_user,
        period=period_dict.get(chosen_time_period),
        limit=artist_limit,
    )
    print("Top artists:")
    print(user_top_artists[:5])
    all_tags = get_top_tags(network, user_top_artists, limit=0, prune_tag_list=3)
    print("Top tags:")
    print(sorted(all_tags, key=lambda x: x[1], reverse=True)[:10])


def main():
    network, _ = initialize()
    plot_top_tags_trend(network, "menisadig.csv", play_threshold=100, top_k=5)


if __name__ == "__main__":
    main()
