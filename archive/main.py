# import pandas as pd
#
# artists_series = df["artist"].value_counts()
# top_artists = artists_series[artists_series > 10].index
# for artist in tqdm(top_artists):
#     top_tags: list[pylast.Tag] = network.get_artist(artist).get_top_tags(limit=1)
#     if top_tags:
#         tags_of_artist = [tag.item.name for tag in top_tags]
#         tags_dict[artist] = tags_of_artist[0]
#         if tags_of_artist[0] == "seen live":
#             top_tags: list[pylast.Tag] = network.get_artist(artist).get_top_tags(
#                 limit=2
#             )
#             if len(top_tags) > 1:
#                 tags_of_artist = [tag.item.name for tag in top_tags]
#                 tags_dict[artist] = tags_of_artist[1]
# top_genres_df = top_data.loc[top_data["tag"].isin(top_genres)].copy()
# top_genres_df["timestamp"] = pd.to_datetime(top_genres_df["time"])
# top_genres_df["year"] = top_genres_df["timestamp"].dt.year
# trend_data = top_genres_df.groupby(["year", "tag"]).size().reset_index(name="count")
# trend_pivot = trend_data.pivot(index="year", columns="tag", values="count").fillna(0)
# trend_pivot.plot(kind="line", marker="o", title="Genre Trends Over Years")
