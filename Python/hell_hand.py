#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------
#   Pro Makers = Hell Hand
#-------------------------------------------------------------------

#-------------------------------------------------------------------
#   Requirements Installation (Terminal)
#   pip install mediapipe opencv-python numpy pyserial
#-------------------------------------------------------------------

# curl -o hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task

import argparse
import cv2 as cv
import numpy as np

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import math
import time
import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk

#*******************************************************************
#   FPS 계산 및 텍스트 렌더링 Class
#*******************************************************************
class CvFpsCalc:
    def __init__(self, buffer_len=10):
        self._start_tick = cv.getTickCount()
        self._freq = cv.getTickFrequency()
        self._buffer_len = buffer_len
        self._times = []

    def get(self):
        current_tick = cv.getTickCount()
        dt = (current_tick - self._start_tick) / self._freq
        self._start_tick = current_tick
        self._times.append(dt)
        if len(self._times) > self._buffer_len:
            self._times.pop(0)
        return int(1 / (sum(self._times) / len(self._times))) if sum(self._times) > 0 else 0


#-------------------------------------------------------------------
#   FingerControl Class
#-------------------------------------------------------------------
class FingerControl:
    def __init__(self, com_port):
        self.serial_port = None
        self.__time_tick_right = time.time()
        self.__time_tick_left = time.time()
        self.__servo_angle_right = [0, 0, 0, 0, 0]
        self.__servo_angle_left = [0, 0, 0, 0, 0]
        try:
            self.serial_port = serial.Serial(com_port, 115200, timeout=1)
            print(f"✅ Connected to {com_port}")
        except Exception as e:
            print(f"❌ Connection failed: {e}")

    def __vector_length(self, v): return math.sqrt(sum(x*x for x in v))
    def __dot_product(self, v1, v2): return sum(x*y for x, y in zip(v1, v2))
    def __angle_between_vectors(self, v1, v2):
        dot_prod = self.__dot_product(v1, v2)
        v1_len, v2_len = self.__vector_length(v1), self.__vector_length(v2)
        if v1_len * v2_len == 0: return 0
        cos_val = max(-1.0, min(1.0, dot_prod / (v1_len * v2_len)))
        return math.degrees(math.acos(cos_val))

    def __finger_angle(self, p1, p2, q1, q2):
        # Tasks API는 x, y, z 속성을 가짐
        vA = [(p2.x - p1.x), (p2.y - p1.y), (p2.z - p1.z)]
        vB = [(q2.x - q1.x), (q2.y - q1.y), (q2.z - q1.z)]
        return self.__angle_between_vectors(vA, vB)

    def __linear_transform(self, x, a_min, a_max, b_min, b_max):
        x = max(min(x, a_max), a_min)
        return (x - a_min) * (b_max - b_min) / (a_max - a_min) + b_min

    def finger_robot_right(self, world_landmarks):
        
        w_ang = [self.__finger_angle(world_landmarks[2], world_landmarks[3], world_landmarks[2], world_landmarks[17]),
                 self.__finger_angle(world_landmarks[5], world_landmarks[8], world_landmarks[5], world_landmarks[0]),
                 self.__finger_angle(world_landmarks[9], world_landmarks[12], world_landmarks[9], world_landmarks[0]),
                 self.__finger_angle(world_landmarks[13], world_landmarks[16], world_landmarks[13], world_landmarks[0]),
                 self.__finger_angle(world_landmarks[17], world_landmarks[20], world_landmarks[17], world_landmarks[0])]
        
        s_ang = [self.__linear_transform(w_ang[0], 60, 120, 180, 0),
            self.__linear_transform(w_ang[1], 30, 160, 180, 0),
            self.__linear_transform(w_ang[2], 30, 160, 180, 0),
            self.__linear_transform(w_ang[3], 30, 160, 180, 0),
            self.__linear_transform(w_ang[4], 30, 160, 180, 0)]
    

            
        now = time.time()
        if (now - self.__time_tick_right) >= 0.03:
            if self.serial_port and self.serial_port.is_open:
                cmd = "FR0%03d1%03d2%03d3%03d4%03d\n" % tuple(map(int, s_ang))
                self.serial_port.write(cmd.encode())
            self.__time_tick_right = now

    def finger_robot_left(self, world_landmarks):

        w_ang = [self.__finger_angle(world_landmarks[2], world_landmarks[3], world_landmarks[2], world_landmarks[17]),
                 self.__finger_angle(world_landmarks[5], world_landmarks[8], world_landmarks[5], world_landmarks[0]),
                 self.__finger_angle(world_landmarks[9], world_landmarks[12], world_landmarks[9], world_landmarks[0]),
                 self.__finger_angle(world_landmarks[13], world_landmarks[16], world_landmarks[13], world_landmarks[0]),
                 self.__finger_angle(world_landmarks[17], world_landmarks[20], world_landmarks[17], world_landmarks[0])]
        

        s_ang = [self.__linear_transform(w_ang[0], 60, 110, 180, 0),
                self.__linear_transform(w_ang[1], 30, 160, 0, 180),
                self.__linear_transform(w_ang[2], 30, 160, 0, 180),
                self.__linear_transform(w_ang[3], 30, 160, 180, 0),
                self.__linear_transform(w_ang[4], 30, 160, 0, 180)]

            
        now = time.time()

        if (now - self.__time_tick_left) >= 0.03:
            if self.serial_port and self.serial_port.is_open:
                cmd = "FL5%03d6%03d7%03d8%03d9%03d\n" % tuple(map(int, s_ang))
                self.serial_port.write(cmd.encode())
            self.__time_tick_left = now


#-------------------------------------------------------------------
#
#-------------------------------------------------------------------
def draw_text_pill(img, text, pos, font_size, color, align="left"):

    # OpenCV 기본 폰트 설정 (가장 깔끔한 폰트 중 하나)
    font = cv.FONT_HERSHEY_SIMPLEX
    
    # 폰트 크기 조절 (OpenCV는 scale 값을 사용하므로 적절히 변환)
    # font_size 25 기준 약 0.8~1.0 scale이 적당합니다.
    font_scale = font_size / 30.0 
    thickness = 2

    if align == "right":
        # 텍스트의 실제 가로 길이를 계산하여 좌표 수정
        (text_width, text_height), baseline = cv.getTextSize(text, font, font_scale, thickness)
        pos = (pos[0] - text_width, pos[1])

    # OpenCV는 BGR을 사용하므로 color가 (R, G, B)라면 (B, G, R)로 변환이 필요할 수 있습니다.
    # 만약 기존 color가 (0, 0, 255)라면 그대로 빨간색으로 나옵니다.
    cv.putText(img, text, pos, font, font_scale, color, thickness, cv.LINE_AA)
    
    return img


#-------------------------------------------------------------------
#   그리기 함수 (Tasks API 구조에 맞춤)
#-------------------------------------------------------------------
# 기존 HAND_CONNECTIONS 상수를 직접 가져오기 어렵다면 수동 정의하거나 라이브러리 참조
HAND_CONNECTIONS = [( 0,  1), ( 1,  2), ( 2,  3), ( 3,  4), ( 5,  6), ( 6,  7), ( 7,  8), 
                    ( 9, 10), (10, 11), (11, 12), (13, 14), (14, 15), (15, 16), (17, 18), 
                    (18, 19), (19, 20), ( 0,  5), ( 5,  9), ( 9, 13), (13, 17), ( 0, 17)]

def draw_styled_landmarks(image, landmarks, handedness):
    w, h = image.shape[1], image.shape[0]
    pts = [(min(int(lm.x * w), w-1), min(int(lm.y * h), h-1)) for lm in landmarks]
    
    # 손가락 연결선 그리기
    for start, end in HAND_CONNECTIONS:
        cv.line(image, pts[start], pts[end], (0, 255, 0), 2)
    
    # 마디 점 그리기
    for i, pt in enumerate(pts):
        color = (0, 0, 255) if i in [4, 8, 12, 16, 20] else (255, 255, 255)
        cv.circle(image, pt, 5, color, -1)
    
    # 손바닥 중심 계산 및 라벨 표시
    palm_array = np.array([pts[i] for i in [0, 1, 5, 9, 13, 17]])
    M = cv.moments(palm_array)
    if M['m00'] != 0:
        cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
        
        # --- 라벨 반전 로직 ---
        # MediaPipe가 판단한 실제 손 방향
        real_label = handedness[0].category_name

        # 화면(거울 모드)에 보일 라벨로 교체
        display_label = "R" if real_label == "Left" else "L"
        
        cv.putText(image, display_label, (cx-7, cy+7), 
                   cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
    return image

#-------------------------------------------------------------------
#   메인 루프 (Tasks API 적용)
#--------------------------------------------------------------------
def main_loop(selected_port, args):
    controller = FingerControl(selected_port)
    fps_calc = CvFpsCalc()

    #
    #   Hand Landmarker 설정
    #
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')

    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO, # 비디오 스트리밍 모드
        num_hands=2,
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.7,
        min_tracking_confidence=0.7
    )
    
    cap = cv.VideoCapture(args.device, cv.CAP_DSHOW)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, args.height)

    window_name = 'Hell Hand - Tasks API Mode'
    cv.namedWindow(window_name, cv.WND_PROP_FULLSCREEN)
    cv.setWindowProperty(window_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    with vision.HandLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            ret, image = cap.read()
            if not ret: break
            
            image = cv.flip(image, 1)
           
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv.cvtColor(image, cv.COLOR_BGR2RGB))

            timestamp_ms = int(time.time() * 1000)
            
            # 감지 실행
            result = landmarker.detect_for_video(mp_image, timestamp_ms)
            screen_w = image.shape[1]

            if result.hand_landmarks:

                # 1. 화면에 그리기 (변경된 라벨 적용)
                for hl, hd in zip(result.hand_landmarks, result.handedness):
                    image = draw_styled_landmarks(image, hl, hd)
                
                # 2. 로봇 제어 명령 전송 (제어 로직 반전)
                for wl, hd in zip(result.hand_world_landmarks, result.handedness):
                    label = hd[0].category_name # MediaPipe의 원래 판단값
                    
                    # MediaPipe가 'Left'라고 판단한 손 -> '오른쪽 로봇' 함수 호출
                    if label == 'Left': 
                        controller.finger_robot_right(wl)
                    # MediaPipe가 'Right'라고 판단한 손 -> '왼쪽 로봇' 함수 호출
                    else: 
                        controller.finger_robot_left(wl)


            # UI 요소
            cv.putText(image, f"FPS: {fps_calc.get()}", (20, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            
            debug_image = draw_text_pill(image, "ESC to Exit", (screen_w - 20, 20), 25, (0, 0, 255), align="right")
            
            cv.imshow(window_name, image)
            if cv.waitKey(1) == 27: break

    cap.release()
    cv.destroyAllWindows()

#-------------------------------------------------------------------
#   GUI Start
#-------------------------------------------------------------------
def start_gui():
    def on_start():
        port = combo.get()
        if port and port != "No Port Connected":
            root.destroy()
            main_loop(port, argparse.Namespace(device=0, width=1280, height=720))

    root = tk.Tk()
    root.title("Hell Hand - Serial Port")
    root.geometry("350x200")
    tk.Label(root, text="Select Serial Port", font=("Arial", 12, "bold")).pack(pady=15)
    
    ports = [p.device for p in serial.tools.list_ports.comports()]
    combo = ttk.Combobox(root, values=ports, width=25)
    combo.pack(pady=5)

    if ports: 
        combo.current(0)
    else: 
        combo.set("No Port Connected")

    start_btn = tk.Button(root, text="Start (Fullscreen)", command=on_start, 
                          bg="black", fg="white", font=("Arial", 11, "bold"), padx=30, pady=10)
    start_btn.pack(pady=20)

    root.mainloop()

if __name__ == '__main__':
    start_gui()
