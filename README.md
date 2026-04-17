# TiCLE Lite

## 교재 개요

이 교재는 중학생과 고등학생이 IoT와 파지컬 인공지능을 문제해결 활동으로 배우도록 구성한 실습형 교재이다. 목표는 파이썬 문법을 외우는 것이 아니라, 현실 문제를 작은 단계로 나누고 센서, 통신, 데이터, 제어를 연결해 해결하는 힘을 기르는 데 있다.

이 교재의 모든 실습은 다음 질문에서 출발한다.

- 무엇을 관찰해야 하는가?
- 어떤 정보만 골라서 써야 하는가?
- 장치는 그 정보를 어떻게 다른 장치와 나누는가?
- 받은 정보를 바탕으로 무엇을 판단하고 어떤 행동을 해야 하는가?

## 교육 목표

### IoT 교육 목표

- 센서로 주변 세계의 변화를 읽는 힘을 기르는 것이 목표이다.
- 장치와 장치가 데이터를 주고받는 구조를 이해하는 것이 목표이다.
- 원격 제어와 상태 모니터링을 스스로 설계하는 힘을 기르는 것이 목표이다.

### 파지컬 인공지능 교육 목표

- 카메라, 마이크, 움직임 센서처럼 다양한 입력을 의미 있는 정보로 바꾸는 힘을 기르는 것이 목표이다.
- 분류, 판단, 반응을 하나의 시스템으로 연결하는 힘을 기르는 것이 목표이다.
- 사람의 행동과 기계의 동작이 상호작용하는 구조를 이해하는 것이 목표이다.

## 학습 방법

Chapter03부터 Chapter13까지의 실습은 모두 같은 흐름을 따른다.

1. 도전 문제를 읽고 무엇을 해결해야 하는지 이해한다.
2. 작은 실험으로 핵심 원리를 먼저 확인한다.
3. 필요한 개념을 문제해결 맥락에서 이해한다.
4. 중간 미션을 묶어 최종 프로젝트를 완성한다.
5. 프로젝트를 확장하거나 바꾸어 보며 자기 방식으로 재설계한다.

## 학습 경로

### 1단계. 장치와 연결하기

- [1-1. TiCLE Lite 개요](Chapter01.%20Overview/1-1.%20TiCLE%20Lite%20개요.md)
- [2-1. TiCLE Lite 기본 제어](Chapter02.%20Peripheral/2-1.%20TiCLE%20Lite%20기본%20제어.md)
- [2-2. TiCLE Lite 고급 제어](Chapter02.%20Peripheral/2-2.%20TiCLE%20Lite%20고급%20제어.md)
- [3-1. MQTT](Chapter03.%20Connection/3-1.%20MQTT.md)
- [3-2. BLE](Chapter03.%20Connection/3-2.%20BLE.md)

이 단계에서는 센서, 화면, 무선 통신의 기본 구조를 익힌다. 문제를 해결하기 위해 장치가 다른 장치와 어떻게 연결되는지 이해하는 것이 핵심이다.

### 2단계. 환경을 읽고 반응하기

- [4-1. Environment response project](Chapter04.%20Environment/4-1.%20Environment%20response%20project.md)
- [5-1. Sound spectrum analyzer project](Chapter05.%20Sound%20Equalizer/5-1.%20Sound%20spectrum%20analyzer%20project.md)
- [6-1. Sand effector project](Chapter06.%20Sand%20effector/6-1.%20Sand%20effector%20project.md)

이 단계에서는 센서값을 단순히 읽는 데서 멈추지 않고, 여러 입력을 합쳐 화면과 움직임으로 바꾸는 경험을 한다. 관찰, 변환, 시각화가 핵심이다.

### 3단계. 규칙으로 시스템 만들기

- [7-1. Snake Game](Chapter07.%20Snake%20Game/7-1.%20Snake%20Game.md)
- [8-A. Qt](Chapter08.%20Integration%20Control/8-A.%20Qt.md)
- [8-1. Integrated control project](Chapter08.%20Integration%20Control/8-1.%20Integrated%20control%20project.md)
- [9-1. Web control project](Chapter09.%20Web%20Control/9-1.%20Web%20control%20project.md)
- [10-1. Mobile control project](Chapter10.%20Mobile%20Control/10-1.%20Mobile%20control%20project.md)
- [11-1. BLE control project](Chapter11.%20BLE%20Control/11-1.%20BLE%20control%20project.md)

이 단계에서는 입력, 상태, 규칙, 출력의 연결 구조를 만든다. 사용자가 무엇을 입력하면 시스템이 어떤 규칙으로 반응해야 하는지 설계하는 것이 핵심이다.

### 4단계. 사람의 행동을 읽고 반응하기

- [12-1. Face control project](Chapter12.%20Face%20control/12-1.%20Face%20control%20project.md)
- [13-1. Hand control project](Chapter13.%20Hand%20control/13-1.%20Hand%20control%20project.md)

이 단계에서는 카메라와 인공지능 모델을 활용해 사람의 표정과 손동작을 읽고, 그 결과를 장치의 반응으로 연결한다. 인식, 판단, 제어의 연결이 핵심이다.

## 이 교재에서 기르는 힘

- 작은 문제를 먼저 해결하고 이를 연결해 큰 문제를 해결하는 힘
- 센서 입력과 데이터 흐름을 그림처럼 이해하는 힘
- 사람, 장치, 네트워크가 함께 동작하는 시스템을 설계하는 힘
- 실습 결과를 바탕으로 더 나은 방법을 스스로 제안하는 힘

## 권장 학습 방식

- 코드를 한 줄씩 외우기보다, 각 미션이 해결하려는 문제를 먼저 말로 설명해 본다.
- 실행 결과가 예상과 다를 때는 값이 어디에서 바뀌었는지 흐름을 추적한다.
- 최종 프로젝트를 그대로 끝내지 말고, 입력 장치나 출력 방식을 바꾸어 다시 설계해 본다.
