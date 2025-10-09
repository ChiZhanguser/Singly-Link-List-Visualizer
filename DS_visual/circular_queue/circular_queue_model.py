from typing import Any, List, Optional, Dict

class CircularQueueModel:
    """
    Attributes:
        capacity: maximum number of elements the queue can hold
        buffer: list of length == capacity storing elements or None
        head: index of the current front element (next to dequeue)
        tail: index of the next insertion slot (next to enqueue)
        size: current number of elements
    """

    def __init__(self, capacity: int = 8):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.capacity: int = int(capacity)
        self.buffer: List[Optional[Any]] = [None] * self.capacity
        self.head: int = 0
        self.tail: int = 0
        self.size: int = 0

    # Basic operations

    def enqueue(self, value: Any) -> bool:
        """
        Insert value at tail. Returns True on success, False if the queue is full.
        """
        if self.size >= self.capacity:
            return False
        self.buffer[self.tail] = value
        self.tail = (self.tail + 1) % self.capacity
        self.size += 1
        return True

    def dequeue(self) -> Optional[Any]:
        """
        Remove and return front element. Returns None if the queue is empty.
        """
        if self.size == 0:
            return None
        v = self.buffer[self.head]
        self.buffer[self.head] = None
        self.head = (self.head + 1) % self.capacity
        self.size -= 1
        return v

    def peek(self) -> Optional[Any]:
        """
        Return front element without removing it. None if empty.
        """
        if self.size == 0:
            return None
        return self.buffer[self.head]

    def is_full(self) -> bool:
        return self.size == self.capacity

    def is_empty(self) -> bool:
        return self.size == 0

    def clear(self) -> None:
        """
        Reset the queue to empty state (keeps same capacity).
        """
        self.buffer = [None] * self.capacity
        self.head = 0
        self.tail = 0
        self.size = 0

    def to_list(self) -> List[Optional[Any]]:
        """
        Return a shallow copy of underlying buffer (length == capacity).
        Useful for serializing / saving state.
        """
        return list(self.buffer)

    def to_dict(self) -> Dict:
        """
        Serialize model state to a dict for saving.
        """
        return {
            "capacity": self.capacity,
            "buffer": list(self.buffer),
            "head": int(self.head),
            "tail": int(self.tail),
            "size": int(self.size),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CircularQueueModel":
        """
        Restore a model instance from a dict produced by to_dict.
        """
        cap = int(data.get("capacity", 8))
        inst = cls(cap)
        buf = data.get("buffer", [])
        # If buffer length differs, truncate or extend
        if not isinstance(buf, list):
            buf = []
        if len(buf) != cap:
            # adjust to capacity
            newbuf = [None] * cap
            for i, v in enumerate(buf[:cap]):
                newbuf[i] = v
            buf = newbuf
        inst.buffer = list(buf)
        inst.head = int(data.get("head", 0)) % inst.capacity
        inst.tail = int(data.get("tail", 0)) % inst.capacity
        inst.size = int(data.get("size", sum(1 for x in inst.buffer if x is not None)))
        # safety clamp
        if inst.size > inst.capacity:
            inst.size = inst.capacity
        return inst

    def resize(self, new_capacity: int, preserve: bool = True) -> None:
        """
        Resize the ring buffer to new_capacity.
        If preserve is True, retain existing elements in logical order (front -> back).
        If preserve is False, clear the queue.
        """
        new_capacity = max(1, int(new_capacity))
        if new_capacity == self.capacity:
            return
        if not preserve:
            self.capacity = new_capacity
            self.buffer = [None] * self.capacity
            self.head = 0
            self.tail = 0
            self.size = 0
            return

        # preserve elements in order
        items = []
        for _ in range(self.size):
            items.append(self.dequeue())
        self.capacity = new_capacity
        self.buffer = [None] * self.capacity
        self.head = 0
        self.tail = 0
        self.size = 0
        for it in items[:self.capacity]:
            self.enqueue(it)

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return f"CircularQueueModel(cap={self.capacity}, head={self.head}, tail={self.tail}, size={self.size}, buffer={self.buffer})"

# 自测代码
# if __name__ == "__main__":
#     q = CircularQueueModel(5)
#     assert q.is_empty()
#     assert not q.is_full()
#     for i in range(5):
#         ok = q.enqueue(i)
#         assert ok
#     assert q.is_full()
#     assert q.enqueue(99) is False
#     out = [q.dequeue() for _ in range(5)]
#     assert out == [0, 1, 2, 3, 4]
#     assert q.dequeue() is None
#     q.enqueue("a"); q.enqueue("b")
#     d = q.to_dict()
#     q2 = CircularQueueModel.from_dict(d)
#     assert q2.to_list() == q.to_list()
#     print("CircularQueueModel self-test passed.")
