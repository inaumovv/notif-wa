import json

import redis


class Redis:

    def __init__(self, REDIS_URL: str):
        self.connection = redis.Redis.from_url(REDIS_URL)

    def query(self) -> redis.Redis:
        return self.connection

    def get(self, key) -> dict | None | redis.Redis:
        data = self.query().get(key)

        if data != 'null' or data:
            try:
                return json.loads(data)
            except Exception:
                return data

        return None

    def set(self, key, data, to_json=False) -> redis.Redis | bool:
        if to_json:
            try:
                for_write = json.dumps(data).encode('utf-8')
            except ValueError:
                return False
        else:
            for_write = data

        return self.query().set(key, for_write)

    def delete(self, key):
        self.query().delete(key)
