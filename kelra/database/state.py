from threading import Lock
from typing import Any, Dict


class State:

    def __init__(self):
        self._state: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()

    def set(self, client_id: str, key: str, value: Any) -> None:
        with self._lock:
            if client_id not in self._state:
                self._state[client_id] = {}
            self._state[client_id][key] = value

    def get(self, client_id: str, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._state.get(client_id, {}).get(key, default)

    def delete(self, client_id: str, key: str) -> bool:
        with self._lock:
            if client_id in self._state and key in self._state[client_id]:
                del self._state[client_id][key]
                return True
            return False

    def clear_client(self, client_id: str) -> None:
        with self._lock:
            self._state.pop(client_id, None)

    def clear_all(self) -> None:
        with self._lock:
            self._state.clear()

    def get_all_clients(self) -> list:
        with self._lock:
            return list(self._state.keys())

    def client_exists(self, client_id: str) -> bool:
        with self._lock:
            return client_id in self._state

    def get_client_keys(self, client_id: str) -> list:
        with self._lock:
            return list(self._state.get(client_id, {}).keys())

    def has_key(self, client_id: str, key: str) -> bool:
        with self._lock:
            return client_id in self._state and key in self._state[client_id]


state = State()
