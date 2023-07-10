#!/usr/bin/python3

import cv2
import numpy as np
import requests


# OpenCV by default opens in BGR format, but the stream is in RGB format
# So we need a helper function to convert the images
def convert_to_opencv(image):
    # Convert RGB to BGR
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

def fetch_stream(url):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        bytes = b''
        for chunk in response.iter_content(chunk_size=1024):
            bytes += chunk
            a = bytes.find(b'\xff\xd8')
            b = bytes.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytes[a:b+2]
                bytes = bytes[b+2:]
                i = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                yield i
    else:
        print("Received unexpected status code {}".format(response.status_code))


if __name__ == '__main__':
    stream_url = "http://10.0.0.140:8000/stream.mjpg"
    cv2.namedWindow('Stream', cv2.WINDOW_NORMAL)

    for frame in fetch_stream(stream_url):
        cv2.imshow('Stream', frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()
