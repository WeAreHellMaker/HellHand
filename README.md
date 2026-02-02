# 🦾 HellHand: Real-time Biomimetic Robot Hand

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**HellHand**는 Python 기반의 Computer Vision 기술을 활용하여 사람의 손동작을 실시간으로 추적하고 미러링하는 지능형 로봇 손 프로젝트입니다. 

단순한 관절 구동을 넘어, 사용자의 움직임을 데이터화하여 로봇에 즉각적으로 투영하는 **Embodied AI(체감형 AI)**의 기초를 목표로 제작되었습니다.


<table align="center">
  <tr>
    <td align="center">
      <img src="https://raw.githubusercontent.com/WeAreHellMaker/HellHand/main/images/HellHand_Gear_1.jpg" width="200"><br>
      <sub><b>Hell Hand Gear</b><br>Front</sub>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/WeAreHellMaker/HellHand/main/images/HellHand_Gear_2.jpg" width="200"><br>
      <sub><b>Hell Hand Gear</b><br>Back</sub>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/WeAreHellMaker/HellHand/main/images/HellHand_Gear_3.jpg" width="200"><br>
      <sub><b>Hell Hand Gear</b><br>Side</sub>
    </td>
  </tr>
</table>


## 📸 Full Assembly Overview
전체 조립 부품 구성도입니다. 모든 메커니즘은 정밀한 동력 전달을 위한 기어 시스템을 기반으로 설계되었습니다.

<div align="center">
  <img src="https://raw.githubusercontent.com/WeAreHellMaker/HellHand/main/images/HellHand_Gear_Part.jpg" width="400">
  <p><b>Full Assembly Parts List</b></p>
  <p><i>3D Printed / Servo  / Microcontroller Unit / Etc</i></p>
</div>


### 📦 Components Specification (부품 구성)

| Category | Component Description | Qty |
| :--- | :--- | :---: |
| **3D Printed** | Structural frames, gear joints, and finger segments | 1 Set |
| **Servo** | 5x High-torque actuators for independent finger articulation | 5 EA |
| **MCU** | Arduino Nano with Dedicated IO Expansion Shield | 1 Set |
| **Etc** | Precision Gear meshing system & Fastener set (Bolts/Nuts) | Full Set |

<div align="center">
  <img src="https://raw.githubusercontent.com/WeAreHellMaker/HellHand/main/images/HellHand_Gear_PartsList.jpg" width="500">
  <p><b>Parts List</b></p>
</div>

## ✨ Key Features (주요 기능)

* **Real-time Hand Tracking**: Python(MediaPipe)을 이용한 21개 손 관절 포인트의 고정밀 실시간 캡처.
* **Precision Gear System**: 서보 모터의 동력을 효율적으로 각 손가락 마디에 전달하는 기어 메커니즘 적용.
* **Adaptive Control**: 사용자의 손가락 굽힘 각도를 계산하여 로봇 관절의 가동 범위(RoM)에 맞게 매핑.
* **Scalable Architecture**: Python 기반의 모듈화된 코드로 작성되어 추후 AI 제어 알고리즘 확장이 용이함.

---

## 🛠 Tech Stack (기술 스택)

* **Language:** Python 3.12+
* **Vision AI:** MediaPipe / OpenCV (Real-time Hand Landmark Detection)
* **Communication:** PySerial (High-speed Serial Communication)
* **Hardware:** Arduino / ATMega328P based MCU

---

## 🏗 Installation (설치 방법)

```bash
# Clone this repository
git clone [https://github.com/WeAreHellMaker/HellHand.git](https://github.com/WeAreHellMaker/HellHand.git)

# Install required Python libraries
pip install mediapipe opencv-python pyserial

---

## 📚 Education (교육 활용 가이드)

HellHand 프로젝트는 로보틱스, 컴퓨터 비전, 그리고 하드웨어 제어의 통합 학습을 돕기 위한 교육용 자료를 포함하고 있습니다. `Education` 폴더 내의 가이드를 통해 다음 내용을 학습할 수 있습니다.

### 1. 로보틱스 기초 및 메커니즘
- **기어 시스템 이해**: 서보 모터의 회전력을 손가락의 선형 운동으로 변환하는 기어 설계 원리 학습.
- **3D 설계와 조립**: 3D 프린팅 부품을 활용한 구조물 조립 및 기구학적 구조 이해.

### 2. 컴퓨터 비전 기반 AI 제어
- **MediaPipe 핸드 트래킹**: 카메라를 통해 21개의 손 관절 좌표를 추출하고 데이터를 정규화하는 과정 실습.
- **데이터 매핑 알고리즘**: 추출된 좌표 데이터를 로봇 관절의 가동 범위(RoM, Range of Motion)에 맞춰 변환하는 알고리즘 학습.

### 3. 임베디드 시스템 및 통신
- **Serial Communication**: Python(PC)과 Arduino(MCU) 간의 고속 시리얼 통신 프로토콜 설계.
- **다중 서보 모터 제어**: 다자유도(multi-DOF) 하드웨어를 제어하기 위한 효율적인 전력 관리 및 신호 처리.

> [!TIP]
> 상세한 학습 단계별 가이드는 [Education 폴더](./Education) 내의 문서들을 참조하세요.
