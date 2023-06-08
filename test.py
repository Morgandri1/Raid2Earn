import tweepy

client = tweepy.Client(bearer_token=r"AAAAAAAAAAAAAAAAAAAAAJDQfAEAAAAAunT6NcW8O8TdjpU1%2BhI%2F9kvSM68%3DkyCmgJCWkDnnm2wNHo6PWPYRWSaKNI6bAtwNa4QcRPEGZtb8lm")

def check_replies(tweet_ID, author: str, query: str = None):
        """
        author should be username, not user id.
        """
        if not query.startswith('"'):
            '"' + query
        if not query.endswith('"'):
            query + '"'             
        query = f'conversation_id:{tweet_ID} from:{author} ({query if query != None else ""}) is:reply'
        print(query)
        replies = client.search_recent_tweets(query=query)
        return replies

replies = check_replies("1666206939691245579", "__Phase__", "option")
print("yes") if replies > 0 else print("no")