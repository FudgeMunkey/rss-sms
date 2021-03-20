import feedparser


class RssFeedManager:
    post_cache = {}

    def get_feed(self, url):
        if url in self.post_cache:
            return self.post_cache[url]
        else:
            posts = feedparser.parse(url)
            self.post_cache[url] = posts
            return self.post_cache[url]
