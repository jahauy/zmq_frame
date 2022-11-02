import cv2 as cv
import numpy as np
import time
import zmq


class Listener:
    def __init__(self, port, topic='', timeout=0.01):
        self.ctx = zmq.Context()
        self.sub = self.ctx.socket(zmq.SUB)
        self.sub.setsockopt(zmq.SUBSCRIBE, topic.encode())
        self.sub.connect(f'tcp://localhost:{port}')

        self.poller = zmq.Poller()
        self.poller.register(self.sub, zmq.POLLIN)
        self.timeout = timeout
        self.tick = 1

    def _destroy(self):
        self.sub.close()
        self.ctx.destroy()

    def __del__(self):
        self._destroy()

    @property
    def get(self):
        return self.sub.recv()

    @property
    def waiting(self):
        return self.poller.poll(int(self.timeout * 1000))


class Client(Listener):
    def __init__(self, port, topic='', timeout=0.01, max_ticks=1000):
        super().__init__(port, topic=topic, timeout=timeout)
        self.max_tick = max_ticks
        self.image = None

    def __del__(self):
        super().__del__()
        cv.destroyAllWindows()

    def _frame_decode(self, msg):
        if msg is None:
            print('[ERROR]Load msg failed.')
            return False
        data = np.frombuffer(msg, dtype='uint8')
        self.image = cv.imdecode(data, 1)
        return True

    def _show(self, is_valid, title='result_client', wait_key: float = 2):
        if is_valid:
            cv.imshow(title, self.image)
            cv.waitKey(int(wait_key * 1000))

    def _next(self, sleep_time):
        self.tick += 1
        time.sleep(sleep_time)

    def display(self, sleep_time: float = 0.01, show='opencv', server_max_ticks=15):
        i = 1
        while self.tick != self.max_tick and i != server_max_ticks:
            self._next()
            if len(self.waiting) > 0:
                i += 1
                is_valid = self._frame_decode(self.get)
                if show == 'opencv':
                    self._show(is_valid, wait_key=sleep_time)


if __name__ == '__main__':
    client = Client(5555)
    client.display(sleep_time=0.01, server_max_ticks=15)
