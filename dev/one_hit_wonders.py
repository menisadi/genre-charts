import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def main():
    data_path = "/Users/meni/Code/personal/tags-chart/menisadig.csv"
    df = pd.read_csv(data_path, header=None)
    df.columns = ["artist", "album", "track", "timestamp"]
    df["time"] = pd.to_datetime(df["timestamp"])
    df["year"] = df["time"].dt.year

    artists_uniques = df.groupby("artist").agg({"track": "nunique"})
    artists_uniques = artists_uniques.sort_values(by="track", ascending=False)
    top_song_portion = df.groupby("artist")["track"].apply(
        lambda ar: ar.value_counts(normalize=True).iloc[0]
    )

    aritst_count = df["artist"].value_counts()

    top_song_per_artist = (
        df.groupby(["artist", "track"])
        .size()
        .reset_index(name="count")
        .sort_values(["artist", "count"], ascending=[True, False])
    )
    top_song_per_artist = (
        df.groupby(["artist", "track"])
        .size()
        .reset_index(name="count")
        .sort_values(["artist", "count"], ascending=[True, False])
    )

    most_frequent_songs = top_song_per_artist.loc[
        top_song_per_artist.groupby("artist")["count"].idxmax()
    ]
    most_frequent_songs = most_frequent_songs.drop("count", axis=1).set_index("artist")

    # print(most_frequent_songs.head())
    # print(artists_uniques.head())
    art_df = pd.concat(
        [artists_uniques, aritst_count, top_song_portion, most_frequent_songs], axis=1
    )
    art_df.columns = ["tracks", "total_count", "top_song_frac", "top_song"]
    art_df["avg"] = art_df["total_count"].div(art_df["tracks"])

    art_df.sort_values(by="avg", ascending=False).head()

    # df.groupby("artist").agg({"album": "nunique"}).sort_values(
    #     by="album", ascending=False
    # ).head()

    # df[["artist", "track", "year"]].drop_dublicates().head()
    # df.groupby(["artist", "track"])["year"].nunique().head()

    # art_df[art_df["top_song_frac"] > 0.8].sort_values(
    #     by="total_count", ascending=False
    # ).head(20)

    print(art_df.describe())

    hit_thresh = 10
    one_hit_wonders = art_df[
        (art_df["top_song_frac"] == 1) & (art_df["total_count"] > hit_thresh)
    ]
    print(one_hit_wonders[["total_count", "top_song"]])

    art_scores = (art_df["total_count"] * art_df["top_song_frac"]).sort_values(
        ascending=False
    )
    art_scores.name = "score"
    top_k_scores = 15
    hear_more = pd.merge(
        left=art_scores.head(top_k_scores),
        right=art_df,
        how="left",
        left_index=True,
        right_index=True,
    )
    print(hear_more[["score", "top_song_frac", "top_song"]])


def plots(art_df):
    sns.histplot(data=art_df, x="avg", bins=30)
    sns.histplot(data=art_df, x="top_song", bins=30)
    sns.scatterplot(data=art_df, x="total_count", y="top_song")
    plt.show()


if __name__ == "__main__":
    main()
