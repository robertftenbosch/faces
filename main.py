import cv2
import mediapipe as mp
import numpy as np

from PyQt5.QtWidgets import QApplication, QMainWindow

import socket

from numpy_socket import NumpySocket


def run():
    mp_drawing = mp.solutions.drawing_utils
    mp_face_mesh = mp.solutions.face_mesh
    mp_hands = mp.solutions.hands
    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
    cap = cv2.VideoCapture(0)
    sock_sender = NumpySocket()

    sock_sender.initialize_sender('192.168.56.1', 515)
    # cap.set(cv2.CAP_PROP_BRIGHTNESS, 200)
    BG_COLOR = (255, 255, 255)  # gray
    with mp_face_mesh.FaceMesh(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as face_mesh:
        with mp_hands.Hands(
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7) as hands:
            with mp_selfie_segmentation.SelfieSegmentation(
                    model_selection=1) as selfie_segmentation:
                while cap.isOpened():
                    success, image = cap.read()
                    if not success:
                        print("Ignoring empty camera frame.")
                        # If loading a video, use 'break' instead of 'continue'.
                        continue

                    # Flip the image horizontally for a later selfie-view display, and convert
                    # the BGR image to RGB.
                    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                    # To improve performance, optionally mark the image as not writeable to
                    # pass by reference.
                    image.flags.writeable = False
                    results = face_mesh.process(image)
                    hand_results = hands.process(image)
                    segmentation_results_ = selfie_segmentation.process(image)
                    # Draw the face mesh annotations on the image.
                    image.flags.writeable = True
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    face_and_hand_image = np.zeros(image.shape, dtype=np.uint8)
                    face_and_hand_image.flags.writeable = True
                    condition = np.stack(
                        (segmentation_results_.segmentation_mask,) * 3, axis=-1) > 0.1

                    if results.multi_face_landmarks:
                        for face_landmarks in results.multi_face_landmarks:
                            mp_drawing.draw_landmarks(
                                image=face_and_hand_image,
                                landmark_list=face_landmarks,
                                connections=mp_face_mesh.FACE_CONNECTIONS,
                                landmark_drawing_spec=drawing_spec,
                                connection_drawing_spec=drawing_spec)

                    if hand_results.multi_hand_landmarks:
                        for hand_landmarks in hand_results.multi_hand_landmarks:
                            mp_drawing.draw_landmarks(
                                face_and_hand_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    # seg_image=None
                    # # seg_image = cv2.GaussianBlur(image, (55, 55), 0)
                    # if seg_image is None:
                    #     seg_image = np.zeros(image.shape, dtype=np.uint8)
                    #     seg_image[:] = BG_COLOR
                    # output_image = np.where(condition, bg_image, seg_image)
                    #
                    # cv2.imshow('MediaPipe FaceMesh', face_and_hand_image)
                    # msgFromClient = "Hello UDP Server"
                    # bytesToSend = str.encode(msgFromClient)
                    # serverAddressPort = ("192.168.56.1", 515)
                    #
                    # bufferSize = 1024
                    # UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                    #
                    # # Send to server using created UDP socket
                    #
                    # UDPClientSocket.sendto(bytesToSend, serverAddressPort)
                    #
                    # # msgFromServer = UDPClientSocket.recvfrom(bufferSize)
                    # #
                    # # msg = "Message from Server {}".format(msgFromServer[0])
                    sock_sender.send_numpy_array(face_and_hand_image)
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    cv2.imshow('frame', gray)
                    if cv2.waitKey(5) & 0xFF == 27:
                        break
    cap.release()
    cv2.destroyAllWindows()
    app = QApplication([])
    win = QMainWindow()
    win.show()
    app.exit(app.exec_())


if __name__ == '__main__':
    run()
