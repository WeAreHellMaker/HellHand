#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------
#   Pro Makers = Hell Hand  (Version 0.2.0)
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
#   FingerControl Class (시리얼 전송 로직 포함)
#-------------------------------------------------------------------
class FingerControl:
    def __init__(self, com_port):

        self.serial_port = None

        self.__time_tick_left = time.time()
        self.__time_tick_right = time.time()
       
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
        vA = [(p2.x - p1.x), (p2.y - p1.y), (p2.z - p1.z)]
        vB = [(q2.x - q1.x), (q2.y - q1.y), (q2.z - q1.z)]
        return self.__angle_between_vectors(vA, vB)

    def __linear_transform(self, x, a_min, a_max, b_min, b_max):
        x = max(min(x, a_max), a_min)
        return (x - a_min) * (b_max - b_min) / (a_max - a_min) + b_min

    # hand_prefix: 'FR' 또는 'FL'
    def send_single_finger(self, hand_prefix, finger_idx, angle):
        if self.serial_port and self.serial_port.is_open:
            cmd = f"{hand_prefix}{finger_idx-1}{int(angle):03d}\n"
            self.serial_port.write(cmd.encode())
            print(f"Sent: {cmd.strip()}")

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

        if (now - self.__time_tick_right) >= 0.3:

            if self.serial_port and self.serial_port.is_open:
                cmd = "FR0%03d1%03d2%03d3%03d4%03d\n" % tuple(map(int, s_ang))
                self.serial_port.write(cmd.encode())

                time.sleep(0.02)

            self.__time_tick_right = now

    def finger_robot_left(self, world_landmarks):
        w_ang = [self.__finger_angle(world_landmarks[2], world_landmarks[3], world_landmarks[2], world_landmarks[17]),
                 self.__finger_angle(world_landmarks[5], world_landmarks[8], world_landmarks[5], world_landmarks[0]),
                 self.__finger_angle(world_landmarks[9], world_landmarks[12], world_landmarks[9], world_landmarks[0]),
                 self.__finger_angle(world_landmarks[13], world_landmarks[16], world_landmarks[13], world_landmarks[0]),
                 self.__finger_angle(world_landmarks[17], world_landmarks[20], world_landmarks[17], world_landmarks[0])]
        
        s_ang = [self.__linear_transform(w_ang[0], 60, 110, 180, 0),
                self.__linear_transform(w_ang[1], 30, 160, 180, 0),
                self.__linear_transform(w_ang[2], 30, 160, 180, 0),
                self.__linear_transform(w_ang[3], 30, 160, 180, 0),
                self.__linear_transform(w_ang[4], 30, 160, 180, 0)]
            
        now = time.time()

        if (now - self.__time_tick_left) >= 0.3:
            
            if self.serial_port and self.serial_port.is_open:
                cmd = "FL5%03d6%03d7%03d8%03d9%03d\n" % tuple(map(int, s_ang))
                self.serial_port.write(cmd.encode())

                time.sleep(0.02)

            self.__time_tick_left = now

#-------------------------------------------------------------------
#   Drawing Helper Functions
#-------------------------------------------------------------------
def draw_text_pill(img, text, pos, font_size, color, align="left"):
    font = cv.FONT_HERSHEY_SIMPLEX
    font_scale = font_size / 30.0 
    thickness = 2
    if align == "right":
        (text_width, text_height), baseline = cv.getTextSize(text, font, font_scale, thickness)
        pos = (pos[0] - text_width, pos[1])
    cv.putText(img, text, pos, font, font_scale, color, thickness, cv.LINE_AA)
    return img

HAND_CONNECTIONS = [( 0,  1), ( 1,  2), ( 2,  3), ( 3,  4), ( 5,  6), ( 6,  7), ( 7,  8), 
                    ( 9, 10), (10, 11), (11, 12), (13, 14), (14, 15), (15, 16), (17, 18), 
                    (18, 19), (19, 20), ( 0,  5), ( 5,  9), ( 9, 13), (13, 17), ( 0, 17)]

def draw_styled_landmarks(image, landmarks, handedness):
    w, h = image.shape[1], image.shape[0]
    pts = [(min(int(lm.x * w), w-1), min(int(lm.y * h), h-1)) for lm in landmarks]
    for start, end in HAND_CONNECTIONS:
        cv.line(image, pts[start], pts[end], (0, 255, 0), 2)
    for i, pt in enumerate(pts):
        color = (0, 0, 255) if i in [4, 8, 12, 16, 20] else (255, 255, 255)
        cv.circle(image, pt, 5, color, -1)
    
    palm_array = np.array([pts[i] for i in [0, 1, 5, 9, 13, 17]])
    M = cv.moments(palm_array)
    if M['m00'] != 0:
        cx, cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
        real_label = handedness[0].category_name
        display_label = "R" if real_label == "Left" else "L"
        cv.putText(image, display_label, (cx-7, cy+7), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    return image

#-------------------------------------------------------------------
#   Main Loop (Tasks API)
#-------------------------------------------------------------------
def main_loop(selected_port, args):
    controller = FingerControl(selected_port)
    fps_calc = CvFpsCalc()

    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
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
            result = landmarker.detect_for_video(mp_image, timestamp_ms)
            
            if result.hand_landmarks:
                for hl, hd in zip(result.hand_landmarks, result.handedness):
                    image = draw_styled_landmarks(image, hl, hd)
                for wl, hd in zip(result.hand_world_landmarks, result.handedness):
                    label = hd[0].category_name
                    if label == 'Left': controller.finger_robot_right(wl)
                    else: controller.finger_robot_left(wl)

            cv.putText(image, f"FPS: {fps_calc.get()}", (20, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            draw_text_pill(image, "ESC to Exit", (image.shape[1] - 20, 20), 25, (0, 0, 255), align="right")
            cv.imshow(window_name, image)
            if cv.waitKey(1) == 27: break

    cap.release()
    cv.destroyAllWindows()

#-------------------------------------------------------------------
#   GUI Start (오른손/왼손 탭 통합 버전)
#-------------------------------------------------------------------
def start_gui():
    temp_controller = [None]
    # 각 손의 트랙바를 저장할 리스트 분리
    right_scales = []
    left_scales = []

    def get_temp_controller():
        port = combo.get()
        if not port or port == "No Port Connected":
            return None
        if temp_controller[0] is None or temp_controller[0].serial_port.port != port:
            temp_controller[0] = FingerControl(port)
        return temp_controller[0]

    def send_individual_finger(hand_prefix, finger_idx, value):
        ctrl = get_temp_controller()
        if ctrl:
            ctrl.send_single_finger(hand_prefix, finger_idx, value)

    def send_hand_pose(hand_prefix, angles):
        ctrl = get_temp_controller()
        if ctrl and ctrl.serial_port and ctrl.serial_port.is_open:
            # 프로토콜 형식 구성
            if hand_prefix == "FR":
                cmd = "FR0%03d1%03d2%03d3%03d4%03d\n" % tuple(map(int, angles))
                target_scales = right_scales
            else:
                # 왼손 인덱스는 기존 코드에 따라 56789 사용 가능하나, 
                # 테스트 편의상 FR과 동일한 01234 구조 혹은 지정된 프로토콜에 맞춤
                cmd = "FL5%03d6%03d7%03d8%03d9%03d\n" % tuple(map(int, angles))
                target_scales = left_scales
            
            ctrl.serial_port.write(cmd.encode())
            print(f"[{hand_prefix} POSE] {cmd.strip()}")
            
            # 해당 탭의 트랙바 업데이트
            for i, val in enumerate(angles):
                target_scales[i].set(val)

    def on_start():
        port = combo.get()
        if port and port != "No Port Connected":
            if temp_controller[0] and temp_controller[0].serial_port:
                temp_controller[0].serial_port.close()
            root.destroy()
            main_loop(port, argparse.Namespace(device=0, width=1280, height=720))

    root = tk.Tk()
    root.title("Hell Hand - Multi Control Center")
    root.geometry("600x700")

    # 1. 포트 선택
    tk.Label(root, text="Select Serial Port", font=("Arial", 11, "bold")).pack(pady=10)
    ports = [p.device for p in serial.tools.list_ports.comports()]
    combo = ttk.Combobox(root, values=ports, width=25)
    combo.pack(pady=5)
    if ports: combo.current(0)
    else: combo.set("No Port Connected")

    # 2. 메인 시작 버튼
    start_btn = tk.Button(root, text="START HAND TRACKING", command=on_start, 
                          bg="#1a1a1a", fg="white", font=("Arial", 10, "bold"), pady=5)
    start_btn.pack(pady=10, fill="x", padx=100)


    # 3. 탭 메뉴 구성
    notebook = ttk.Notebook(root)
    notebook.pack(pady=10, fill="both", expand=True, padx=10)

    # 공통 포즈 데이터
    num_poses = {
        "0": [180]*5, "1": [180, 0, 180, 180, 180], "2": [180, 0, 0, 180, 180],
        "3": [180, 0, 0, 0, 180], "4": [180, 0, 0, 0, 0], "5": [0]*5
    }

    special_poses = {
        "Thumbs 👍": [0, 180, 180, 180, 180], "Victory ✌️": [180, 0, 0, 180, 180],
        "Rock 🤟": [0, 0, 180, 180, 0], "OK 👌": [0, 180, 0, 0, 0]
    }

    # --- 오른손(FR) 탭 ---
    fr_tab = tk.Frame(notebook)
    notebook.add(fr_tab, text=" Right Hand (FR) ")
    
    # 트랙바
    fr_manual = tk.LabelFrame(fr_tab, text="Manual Control", padx=10, pady=10)
    fr_manual.pack(pady=10, fill="x", padx=10)
    for i in range(1, 6):
        row = tk.Frame(fr_manual)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=f"Finger {i}:", width=8).pack(side="left")
        s = tk.Scale(row, from_=0, to=180, orient=tk.HORIZONTAL, length=250)
        s.set(0); s.pack(side="left", padx=5)
        tk.Button(row, text="Send", command=lambda idx=i, sc=s: send_individual_finger("FR", idx, sc.get())).pack(side="left")
        right_scales.append(s)

    # 포즈
    fr_pose = tk.LabelFrame(fr_tab, text="Pose Presets", padx=10, pady=10)
    fr_pose.pack(pady=10, fill="x", padx=10)
    r_btn_row1 = tk.Frame(fr_pose); r_btn_row1.pack(fill="x")
    
    for lbl, angs in num_poses.items():
        tk.Button(r_btn_row1, text=lbl, width=4, command=lambda a=angs: send_hand_pose("FR", a)).pack(side="left", padx=3, expand=True)
    r_btn_row2 = tk.Frame(fr_pose); r_btn_row2.pack(fill="x", pady=10)
    
    for lbl, angs in special_poses.items():
        tk.Button(r_btn_row2, text=lbl, width=10, command=lambda a=angs: send_hand_pose("FR", a)).pack(side="left", padx=3, expand=True)

    # --- 왼손(FL) 탭 ---
    fl_tab = tk.Frame(notebook)
    notebook.add(fl_tab, text=" Left Hand (FL) ")

    # 트랙바
    fl_manual = tk.LabelFrame(fl_tab, text="Manual Control", padx=10, pady=10)
    fl_manual.pack(pady=10, fill="x", padx=10)
    
    for i in range(1, 6):
        row = tk.Frame(fl_manual)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=f"Finger {i}:", width=8).pack(side="left")
        s = tk.Scale(row, from_=0, to=180, orient=tk.HORIZONTAL, length=250)
        s.set(0); s.pack(side="left", padx=5)
        tk.Button(row, text="Send", command=lambda idx=i, sc=s: send_individual_finger("FL", idx + 5, sc.get())).pack(side="left")
        left_scales.append(s)

    #
    #   포즈
    #
    fl_pose = tk.LabelFrame(fl_tab, text="Pose Presets", padx=10, pady=10)
    fl_pose.pack(pady=10, fill="x", padx=10)
    l_btn_row1 = tk.Frame(fl_pose); l_btn_row1.pack(fill="x")
    
    for lbl, angs in num_poses.items():
        tk.Button(l_btn_row1, text=lbl, width=4, command=lambda a=angs: send_hand_pose("FL", a)).pack(side="left", padx=3, expand=True)
    l_btn_row2 = tk.Frame(fl_pose); l_btn_row2.pack(fill="x", pady=10)
    
    for lbl, angs in special_poses.items():
        tk.Button(l_btn_row2, text=lbl, width=10, command=lambda a=angs: send_hand_pose("FL", a)).pack(side="left", padx=3, expand=True)


    root.mainloop()

if __name__ == '__main__':
    start_gui()
