from flask import Flask, render_template, Response, request
import cv2

app = Flask(__name__)

cameras = {
    0: cv2.VideoCapture(0),
    1: cv2.VideoCapture(1)  # Assuming a second camera is available
}

current_camera = 0
filter_mode = 'normal'

def apply_filter(frame, mode):
    if mode == 'grayscale':
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    elif mode == 'edge':
        return cv2.Canny(frame, 100, 200)
    return frame

def generate_frames():
    while True:
        success, frame = cameras[current_camera].read()
        if not success:
            break
        else:
            frame = apply_filter(frame, filter_mode)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/switch_camera/<int:camera_id>')
def switch_camera(camera_id):
    global current_camera
    if camera_id in cameras:
        current_camera = camera_id
    return '', 204

@app.route('/set_filter/<filter_name>')
def set_filter(filter_name):
    global filter_mode
    filter_mode = filter_name
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)