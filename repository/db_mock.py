class NoSQLDatabaseMock:
    def __init__(self):
        self.db = {
            "feeds": [
                "https://status.openai.com/feed.rss",
                # We can add more feeds here as required as a simple DB entry
            ],
            "llm_providers": [
                {
                    "name": "openai",
                    "keywords": [
                        "openai",
                        "gpt-4",
                        "gpt-4o",
                        "chatgpt",
                        "chat completions",
                        "responses",
                    ],
                },
                {
                    "name": "anthropic",
                    "keywords": ["anthropic", "claude"],
                },
                {
                    "name": "gemini",
                    "keywords": ["gemini"],
                },
                {
                    "name": "deepseek",
                    "keywords": ["deepseek"],
                },
            ],
        }

    def get_collection(self, collection_name: str):
        return self.db[collection_name]

    def insert_one(self, collection_name: str, data: dict):
        if collection_name not in self.db:
            self.db[collection_name] = []
        self.db[collection_name].append(data)

    def find_one(self, collection_name: str, query: dict):
        if collection_name not in self.db:
            return None
        return next((item for item in self.db[collection_name] if item == query), None)

    def find_all(self, collection_name: str):
        if collection_name not in self.db:
            return []
        return self.db[collection_name]

    def update_one(self, collection_name: str, query: dict, data: dict):
        self.db[collection_name][query] = data

    def delete_one(self, collection_name: str, query: dict):
        del self.db[collection_name][query]

    def delete_all(self, collection_name: str):
        del self.db[collection_name]

    def close(self):
        self.db = {}


db_mock = NoSQLDatabaseMock()
