### Collecting data from Twitter
`$ pip install tweepy==3.3.0`

In order to promote the separation of concerns between application logic and configuration, we're **storing the credentials in environment variables**.

Changing configuration between different deployments (for example, using personal credentials for local tests and a company account for production) doesn't require any change in the code base. Moreover, environment variables don't get accidentally checked into your source control system for everyone to see.

Once the environment is set up, we will wrap the Tweepy calls to create the Twitter client into two functions: one that **reads the environment variables** and performs the authentication, and the other that **creates the API object needed to interface with Twitter.**

The reason for breaking the logic down into two separate functions is that **the authentication code can also be reused for the Streaming API**, as we'll discuss in the following sections.

As a Twitter user, your **home timeline** is the screen that you see when you log in to Twitter. It contains a sequence of tweets from the accounts you've chosen to follow, with the most recent and interesting tweets at the top.

`tweepy.Cursor` is an *iterable* object, meaning that it provides an easy-to-use interface to perform iteration and pagination over different objects.

The `status` variable used in the iteration represents an instance of `tweepy.Status`, which is a model used by Tweepy to wrap statuses (that is, tweets). 
  
**The JSON Lines format**  
The file in the preceding example has a .jsonl extension rather than just .json. In fact, this file is in the JSON Lines format (http://jsonlines.org/), meaning that each line of the file is a valid JSON document.  

Trying to load the entire content of this file with, for example, `json.loads()` will raise `ValueError` as the entire content is not a valid JSON document. Rather, if we're using functions that expect valid JSON documents, we need to process one line at a time.

The JSON Lines format is particularly well suited for **large-scale processing**: many big data frameworks allow the developers to easily split the input file into chunks that can be processed in parallel by different workers.

**Note:** we can only retrieve up to the most recent 800 tweets from our `home timeline`.
If we retrieve tweets from a specific user timeline, that is, using the `user_timeline` method rather than `home_timeline`, this limit is increased to 3,200.

There are **two interesting aspects** to consider when analyzing tweets, as follows:
- The entities are already labeled
- The user profile is fully embedded

The first point means that entity analysis is simplified as we do not need to explicitly search for entities such as hashtags, user mentions, embedded URLs, or media, because these are all provided by the Twitter API together with their offset within the text (the attribute called indices).

The second point means that we do not need to store user profile information somewhere else and then join/merge the data via a foreign key, for example. The user profile is, in fact, redundantly replicated within each tweet.

**Note: Working with denormalized data**
The approach of embedding redundant data is related to the concept of denormalization. While normalization is considered a good practice in relational database design, denormalization finds its role in **large-scale processing and databases that belong to the wide NoSQL family**.

The rationale behind this approach is that **the additional disk space required to redundantly store the user profile only has a marginal cost**, while the **gain (in terms of performances) obtained by removing the need for a join/merge operation is substantial**.

#### Using the Streaming API
The core of the streaming logic is **implemented in the `CustomListener` class**, which extends `StreamListener` and overrides two methods: `on_data()` and `on_error()`. These are handlers that are triggered when data is coming through and an error is given by the API.

The return type for both these methods is a Boolean: `True` to continue the streaming and `False` to stop the execution. For this reason, it's important to return False only on fatal errors, so the application can continue downloading data. In this way, we can **avoid killing the application if a temporary error occurs**, such as a network hiccup on our side, or an HTTP 503 error from Twitter, which means that the service is temporarily unavailable (but likely to be back shortly).

Our implementation of the `on_error()` method will stop the execution only if there's error 420, meaning that we have been rate limited by the Twitter API. The more we exceed the rate limit, the more we need to wait before we can use the service again. Therefore, for this reason, it's better to stop downloading and investigating the problem. Every other error will simply be printed on the `stderr` interface. This is, in general, better than just using `print()`, so we can redirect the error output to a specific file if needed. Even better, we could use the `logging` module to build a proper log-handling mechanism, but this is beyond the scope of this chapter.

The `on_data()` method is called when data is coming through. This function simply stores the data as it is received in a `.jsonl` file. Each line of this file will then contain a single tweet, in the JSON format. Once the data is written, we will return `True` to continue the execution. If anything goes wrong in this process, we will catch any exception, print a message on `stderr`, put the application to sleep for five seconds, and then continue the execution by returning `True` again. **The short sleep, in case of exception, is simply to prevent an occasional network hiccup that causes the application to get stuck.**

The `CustomListener` class uses a helper to sanitize the query and use it for the filename. The `format_filename()` function, in fact, goes through the given string, one character at a time, and uses the `convert_valid()` function to convert invalid characters into underscores. In this context, the valid characters are the three symbols-dash, underscore, and dot (-, _, and .)-ASCII letters, and digits.
