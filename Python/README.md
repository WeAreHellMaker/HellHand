# 🦾 HellHand: Pro Makers Project
> **Real-time Biomimetic Robot Hand Control System using MediaPipe Tasks API**

HellHand는 Python과 MediaPipe의 최신 **Tasks API**를 활용하여 인간의 손동작을 실시간으로 추적하고, 이를 기어 기반의 로봇 손으로 투영하는 고성능 미러링 시스템입니다.

---

## 📸 System Overview

<div align="center">
  <img src="https://raw.githubusercontent.com/WeAreHellMaker/HellHand/main/images/HellHand_Gear_Part.jpg" width="700" alt="HellHand Components">
  <p><i><b>Full Assembly Kit</b>: 3D Printed Parts, Servos, MCU, and Gear System</i></p>
</div>

---

## ✨ Key Technical Features

### 1. Advanced Hand Tracking (Tasks API)
기존의 Legacy MediaPipe 방식보다 성능이 향상된 **MediaPipe Tasks API**를 사용합니다.
* **VIDEO Running Mode**: 프레임 간 연속성을 분석하여 끊김 없는 추적 성능 제공.
* **Dual Hand Support**: 왼손과 오른손을 개별 인식하여 독립적인 제어 가능.

### 2. Geometric Angle Mapping

벡터 연산을 통해 손가락 관절의 물리적 각도를 계산합니다.
* **Vector Mathematics**: 관절 간의 벡터 내적($\cdot$)과 코사인 유사도를 이용해 각 마디의 굽힘 정도를 정밀하게 산출합니다.
* **Range Conversion**: `__linear_transform` 함수를 통해 인간의 관절 가동 범위(RoM)를 서보 모터의 가동 범위(0°~180°)로 정밀 매핑합니다.

### 3. High-Speed Control Pipeline
* **Low Latency**: 30ms 주기의 Serial 통신을 통해 사람의 움직임과 로봇의 반응 차이를 최소화했습니다.
* **Command Protocol**: 
  - `FR`: Right Hand Command (e.g., `FR01801090...`)
  - `FL`: Left Hand Command (e.g., `FL51806090...`)

---

## 🛠 Tech Stack

| Category | Technology |
| :--- | :--- |
| **Language** | Python 3.12+ |
| **AI Framework** | MediaPipe Tasks API (Vision) |
| **Libraries** | OpenCV, NumPy, PySerial, Tkinter |
| **Hardware** | Arduino Nano, MG90S/MG996R Servos |

---

## 🚀 Getting Started

### 1. Requirements Installation
```bash
pip install mediapipe opencv-python numpy pyserial

# 터미널에서 바로 다운로드
curl -o hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
