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
