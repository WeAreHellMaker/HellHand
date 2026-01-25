#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import argparse
import cv2 as cv
import numpy as np
import mediapipe as mp
import math
import time
import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk
from PIL import ImageFont, ImageDraw, Image


HANDTYPE = 2;           #   New Version


# -------------------------------------------------------------------
#   FPS 계산 클래스
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
#   텍스트 렌더링 (고딕체 지원)
# -------------------------------------------------------------------
def draw_text_pill(img, text, pos, font_size, color, align="left"):
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)
    try:
        font = ImageFont.truetype("malgun.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    if align == "right":
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        pos = (pos[0] - text_width, pos[1])
        
    draw.text(pos, text, font=font, fill=color)
    return np.array(img_pil)

# -------------------------------------------------------------------
#   FingerControl 클래스
# -------------------------------------------------------------------
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

    def __finger_angle(self, x1, x2, q1, q2):
        vA = [(x2.x - x1.x), (x2.y - x1.y), (x2.z - x1.z)]
        vB = [(q2.x - q1.x), (q2.y - q1.y), (q2.z - q1.z)]
        return self.__angle_between_vectors(vA, vB)

    def __linear_transform(self, x, a_min, a_max, b_min, b_max):
        x = max(min(x, a_max), a_min)
        return (x - a_min) * (b_max - b_min) / (a_max - a_min) + b_min

    def finger_robot_right(self, world_landmarks):

        w_ang = [self.__finger_angle(world_landmarks.landmark[2], world_landmarks.landmark[3], world_landmarks.landmark[2], world_landmarks.landmark[17]),
                 self.__finger_angle(world_landmarks.landmark[5], world_landmarks.landmark[8], world_landmarks.landmark[5], world_landmarks.landmark[0]),
                 self.__finger_angle(world_landmarks.landmark[9], world_landmarks.landmark[12], world_landmarks.landmark[9], world_landmarks.landmark[0]),
                 self.__finger_angle(world_landmarks.landmark[13], world_landmarks.landmark[16], world_landmarks.landmark[13], world_landmarks.landmark[0]),
                 self.__finger_angle(world_landmarks.landmark[17], world_landmarks.landmark[20], world_landmarks.landmark[17], world_landmarks.landmark[0])]
        

        if HANDTYPE == 2 :

            s_ang = [self.__linear_transform(w_ang[0], 60, 120, 90, 180),
                    self.__linear_transform(w_ang[1], 30, 160, 180, 0),
                    self.__linear_transform(w_ang[2], 30, 160, 180, 0),
                    self.__linear_transform(w_ang[3], 30, 160, 0, 180),
                    self.__linear_transform(w_ang[4], 30, 160, 0, 180)]        
        
        else :
            s_ang = [self.__linear_transform(w_ang[0], 60, 120, 90, 0),
                    self.__linear_transform(w_ang[1], 30, 160, 180, 0),
                    self.__linear_transform(w_ang[2], 30, 160, 0, 180),
                    self.__linear_transform(w_ang[3], 30, 160, 180, 0),
                    self.__linear_transform(w_ang[4], 30, 160, 0, 180)]
            
        now = time.time()
        if (now - self.__time_tick_right) >= 0.03 and any(abs(self.__servo_angle_right[i] - s_ang[i]) >= 30 for i in range(5)):
            if self.serial_port and self.serial_port.is_open:
                cmd = "FR0%03d1%03d2%03d3%03d4%03d\n" % tuple(map(int, s_ang))
                self.serial_port.write(cmd.encode())
            self.__time_tick_right, self.__servo_angle_right = now, s_ang

    def finger_robot_left(self, world_landmarks):
        w_ang = [self.__finger_angle(world_landmarks.landmark[2], world_landmarks.landmark[3], world_landmarks.landmark[2], world_landmarks.landmark[17]),
                 self.__finger_angle(world_landmarks.landmark[5], world_landmarks.landmark[8], world_landmarks.landmark[5], world_landmarks.landmark[0]),
                 self.__finger_angle(world_landmarks.landmark[9], world_landmarks.landmark[12], world_landmarks.landmark[9], world_landmarks.landmark[0]),
                 self.__finger_angle(world_landmarks.landmark[13], world_landmarks.landmark[16], world_landmarks.landmark[13], world_landmarks.landmark[0]),
                 self.__finger_angle(world_landmarks.landmark[17], world_landmarks.landmark[20], world_landmarks.landmark[17], world_landmarks.landmark[0])]
        s_ang = [self.__linear_transform(w_ang[0], 60, 110, 180, 0),
                 self.__linear_transform(w_ang[1], 30, 160, 0, 180),
                 self.__linear_transform(w_ang[2], 30, 160, 0, 180),
                 self.__linear_transform(w_ang[3], 30, 160, 180, 0),
                 self.__linear_transform(w_ang[4], 30, 160, 0, 180)]
        now = time.time()
        if (now - self.__time_tick_left) >= 0.03 and any(abs(self.__servo_angle_left[i] - s_ang[i]) >= 25 for i in range(5)):
            if self.serial_port and self.serial_port.is_open:
                cmd = "FL5%03d6%03d7%03d8%03d9%03d\n" % tuple(map(int, s_ang))
                self.serial_port.write(cmd.encode())
            self.__time_tick_left, self.__servo_angle_left = now, s_ang

# -------------------------------------------------------------------
#   그리기 함수
# -------------------------------------------------------------------
def draw_styled_landmarks(image, landmarks, handedness):
    w, h = image.shape[1], image.shape[0]
    pts = [(min(int(lm.x * w), w-1), min(int(lm.y * h), h-1)) for lm in landmarks.landmark]
    if not pts: return image

    for start, end in mp.solutions.hands.HAND_CONNECTIONS:
        cv.line(image, pts[start], pts[end], (0, 255, 0), 2)

    for i, pt in enumerate(pts):
        color = (0, 0, 255) if i in [4, 8, 12, 16, 20] else (255, 255, 255)
        cv.circle(image, pt, 5, color, -1)
    
    palm_array = np.array([pts[i] for i in [0, 1, 5, 9, 13, 17]])
    M = cv.moments(palm_array)
    if M['m00'] != 0:
        cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
        cv.circle(image, (cx, cy), 12, (0, 0, 255), 2)
        label = handedness.classification[0].label[0]
        cv.putText(image, label, (cx-7, cy+7), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    return image

# -------------------------------------------------------------------
#   메인 루프
# -------------------------------------------------------------------
def main_loop(selected_port, args):

    controller = FingerControl(selected_port)
    
    cap = cv.VideoCapture(args.device, cv.CAP_DSHOW)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, args.height)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(model_complexity=1, max_num_hands=2, min_detection_confidence=0.7)
    fps_calc = CvFpsCalc()

    window_name = 'Hell Hand - Fullscreen Mode'
    cv.namedWindow(window_name, cv.WND_PROP_FULLSCREEN)
    cv.setWindowProperty(window_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    while True:
        ret, image = cap.read()
        if not ret: break
        
        image = cv.flip(image, 1)
        debug_image = copy.deepcopy(image)
        results = hands.process(cv.cvtColor(image, cv.COLOR_BGR2RGB))
        screen_w = debug_image.shape[1]

        if results.multi_hand_landmarks:
            for hl, hd in zip(results.multi_hand_landmarks, results.multi_handedness):
                debug_image = draw_styled_landmarks(debug_image, hl, hd)
            for wl, hd in zip(results.multi_hand_world_landmarks, results.multi_handedness):
                if hd.classification[0].label == 'Left': controller.finger_robot_left(wl)
                else: controller.finger_robot_right(wl)

        # FPS 표시 (왼쪽 상단)
        cv.putText(debug_image, f"FPS: {fps_calc.get()}", (20, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
        # ★ 수정 사항: ESC to Exit 빨간색 고딕체 (오른쪽 상단 정렬)
        debug_image = draw_text_pill(debug_image, "ESC to Exit", (screen_w - 20, 20), 25, (0, 0, 255), align="right")

        
        cv.imshow(window_name, debug_image)
        if cv.waitKey(1) == 27: break

    cap.release()
    cv.destroyAllWindows()

# -------------------------------------------------------------------
#   GUI (시작 버튼 검은색 바탕 수정)
# -------------------------------------------------------------------
def start_gui():
    def on_start():
        port = combo.get()
        if port and port != "No Port Connected":
            root.destroy()
            main_loop(port, argparse.Namespace(device=0, width=1280, height=720))

    root = tk.Tk()
    root.title("Hell Hand - Serial Port (Ver 0.01)")
    root.geometry("350x200")
    
    # Text changed to English
    tk.Label(root, text="Select Serial Port", font=("Arial", 12, "bold")).pack(pady=15)
    
    ports = [p.device for p in serial.tools.list_ports.comports()]
    combo = ttk.Combobox(root, values=ports, width=25)
    combo.pack(pady=5)
    
    if ports: 
        combo.current(0)
    else: 
        combo.set("No Port Connected")
    
    # Black Background Button
    start_btn = tk.Button(root, text="Start (Fullscreen)", command=on_start, 
                          bg="black", fg="white", 
                          font=("Arial", 11, "bold"), 
                          padx=30, pady=10,
                          activebackground="#333333", activeforeground="white")
    start_btn.pack(pady=20)
    
    root.mainloop()

if __name__ == '__main__':
    start_gui()
