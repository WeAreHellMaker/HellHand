## 📖 Documentation - Hell Hand Gear

* [Download Assembly Guide (PDF)](./assembly-guide-gear.pdf)


## 🔌 Arduino Nano I/O Connection

아두이노 나노와 로봇 핸드 구성 요소 간의 핀 연결 정보입니다.

<table>
  <thead>
    <tr style="background-color: #f8f9fa;">
      <th style="padding: 10px; border: 1px solid #dfe2e5;">부품 (Component)</th>
      <th style="padding: 10px; border: 1px solid #dfe2e5;">핀 번호 (Pin)</th>
      <th style="padding: 10px; border: 1px solid #dfe2e5;">기능 (Function)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 10px; border: 1px solid #dfe2e5;"><b>Servo</b></td>
      <td style="padding: 10px; border: 1px solid #dfe2e5; text-align: center;"><code style="color: #e83e8c;">D7</code></td>
      <td style="padding: 10px; border: 1px solid #dfe2e5;">오른손 엄지 제어 (PWM)</td>
    </tr>
    <tr>
      <td style="padding: 10px; border: 1px solid #dfe2e5;"><b>Servo</b></td>
      <td style="padding: 10px; border: 1px solid #dfe2e5; text-align: center;"><code style="color: #e83e8c;">D8</code></td>
      <td style="padding: 10px; border: 1px solid #dfe2e5;">오른손 검지 제어 (PWM)</td>
    </tr>
    <tr>
      <td style="padding: 10px; border: 1px solid #dfe2e5;"><b>Servo</b></td>
      <td style="padding: 10px; border: 1px solid #dfe2e5; text-align: center;"><code style="color: #e83e8c;">D9</code></td>
      <td style="padding: 10px; border: 1px solid #dfe2e5;">오른손 중지 제어 (PWM)</td>
    </tr>
    <tr>
      <td style="padding: 10px; border: 1px solid #dfe2e5;"><b>Servo</b></td>
      <td style="padding: 10px; border: 1px solid #dfe2e5; text-align: center;"><code style="color: #e83e8c;">D10</code></td>
      <td style="padding: 10px; border: 1px solid #dfe2e5;">오른손 약지 제어 (PWM)</td>
    </tr>
    <tr>
      <td style="padding: 10px; border: 1px solid #dfe2e5;"><b>Servo</b></td>
      <td style="padding: 10px; border: 1px solid #dfe2e5; text-align: center;"><code style="color: #e83e8c;">D11</code></td>
      <td style="padding: 10px; border: 1px solid #dfe2e5;">오른손 소지 제어 (PWM)</td>
    </tr>

  </tbody>
</table>

> **Note:** 서보 모터는 구동 시 높은 전류를 소모하므로, 아두이노의 5V 핀보다는 별도의 외부 전원(5V-6V) 사용을 강력히 권장합니다. (단, GND는 반드시 아두이노와 통합해야 합니다.)
