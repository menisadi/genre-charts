import pylast
from tqdm import tqdm
import pandas as pd


def create_tag_map(network, artists: list[str], chunk_size: int = 200) -> dict:
    tags_dict = dict.fromkeys(artists)
    for i, artist in tqdm(enumerate(artists)):
        top_tags = network.get_artist(artist).get_top_tags(limit=1)
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
        if i % chunk_size == 0:
            tqdm.write(f"Checkpoint: {i}")
            pd.Series(tags_dict).dropna().to_csv(f"tags_backup_{i}.csv")
            tags_dict = dict.fromkeys(artists)

    return tags_dict


def create_tag_dict(network, file_path, play_threshold, filter_list):
    df = pd.read_csv(file_path, header=None, names=["artist", "Album", "track", "time"])
    artists_series = df["artist"].value_counts()
    top_artists = list(artists_series[artists_series > play_threshold].index)
    top_artists = [a for a in top_artists if a not in filter_list]

    tags_dict = create_tag_map(network=network, artists=top_artists)

    print("Finish")


if __name__ == "__main__":
    # create_tag_map()
    print()
