import json
from tqdm import tqdm
import pylast
import pandas as pd


def get_users_top_artists(network, user_name, period, limit=3) -> list[tuple[str, int]]:
    top_artists = network.get_user(user_name).get_top_artists(
        period=period, limit=limit
    )
    top_artists_names = [
        (artist.item.name, int(artist.weight)) for artist in top_artists
    ]

    return top_artists_names


def normalize_weights(tags: list[tuple[str, int]]) -> list[tuple[str, float]]:
    max_weight = max([w for _, w in tags])
    return [(t, w / max_weight) for t, w in tags]


def get_top_tags(
    network: pylast.LastFMNetwork,
    top_artists: list[tuple[str, int]],
    limit: int = 0,
    prune_tag_list: int = 0,
) -> list[tuple[str, float]]:
    tags: dict[str, float] = dict()
    for artist, artist_weight in top_artists:
        top_tags: list[pylast.Tag] = network.get_artist(artist).get_top_tags(
            limit=prune_tag_list
        )
        for one_tag in top_tags:
            # exclude the "seen live", as it is not interesting
            if one_tag.item.name == "seen live":
                continue
            if one_tag.item.name in tags:
                tags[one_tag.item.name] += int(one_tag.weight) * artist_weight
            else:
                tags[one_tag.item.name] = int(one_tag.weight) * artist_weight

    normalized_tags = normalize_weights(list(tags.items()))
    if limit == 0:
        return normalized_tags
    else:
        # return the top tags in descending order of weight
        limited_tags = sorted(normalized_tags, key=lambda x: x[1], reverse=True)[:limit]
        return limited_tags


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


if __name__ == "__main__":
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
