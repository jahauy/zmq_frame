import cv2 as cv
import numpy as np
import time
import zmq


class Camera(cv.VideoCapture):
    def __init__(self):
        super().__init__(0)
        self.is_update = False
        self._frame = self._update()

    def __del__(self):
        cv.destroyAllWindows()
        self.release()

    def _update(self):
        ret, frame = self.read()
        if not ret:
            return None
        return frame

    def update(self)
        frame = self._update()
        if frame is None:
            print('[ERROR]No infos.')
            self.is_update = False
        else:
            self.is_update = True
            self._frame = frame

    def show(self, title='result'):
        if self.is_update:
            cv.imshow(title, self._frame)
            cv.waitKey(1)

    def _img2str(self, quality=30):
        ret, encode = cv.imencode('.jpg', self._frame, [int(cv.IMWRITE_JPEG_QUALITY), quality])
        if not ret:
            print('[ERROR]Encode failed.')
            return None
        encode = np.array(encode)
        return encode.tobytes()

    @property
    def frame_encode(self):
        if self.is_update:
            return self._img2str()
        return None


class Server:
    def __init__(self, port: int):
        self.ctx = zmq.Context()
        self.pub = self.ctx.socket(zmq.PUB)
        self.pub.bind(f'tcp://*:{port}')
        self.tick = 1
        self.camera = Camera()

    def _destroy(self):
        self.pub.close()
        self.ctx.destroy()
        self.tick = 1

    def __del__(self):
        del self.camera
        self._destroy()

    def _next(self, sleep_time):
        self.tick += 1
        time.sleep(sleep_time)

    def send(self, sleep_time: float = 1, max_ticks=15):
        while self.tick != max_ticks:
            self.camera.update()
            msg = self.camera.frame_encode
            self.pub.send(msg)
            self._next(sleep_time)
        self._destroy()


if __name__ == '__main__':
    srv = Server(5555)
    srv.send(sleep_time=0.5, max_ticks=15)
