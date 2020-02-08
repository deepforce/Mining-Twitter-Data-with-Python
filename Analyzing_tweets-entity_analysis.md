### Analyzing tweets - entity analysis

We're going to perform some **frequency analysis** using the data collected in the previous section.

Analyzing entities such as **hashtags** is interesting as these annotations are an explicit way for the author to label the topic of the tweet.

`collections.Counter`, a special type of dictionary that is used to count hashable objects-in our case, strings. The counter holds the strings as keys of the dictionary and their respective frequency as values.

Being a subclass of `dict`, the `Counter` object per se is an unordered collection. The `most_common()` method is responsible for ordering the keys depending on their values (most frequent first) and returning a list of `(key, value)` tuples.

Since this is optional, we can't access `tweet['entities']` directly as this could raise `KeyError`, so we will use the `get()` function instead, specifying an empty dictionary as default value if the entities are not present.

For this breakdown, we will observe two different percentages: the first is calculated over the total number of tweets, while the second is calculated over **the number of tweets with at least one tweet (called elite set)**.

