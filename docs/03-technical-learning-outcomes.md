

## 📌 새로 학습한 기술

- **Roboflow** : 데이터셋 관리 및 라벨링 플랫폼, 모델 학습을 위한 이미지 전처리와 Augmentation 제공
- **YOLO** : 실시간 객체 탐지(Object Detection) 알고리즘, 빠르고 정확한 성능이 장점
- **OpenCV** : 컴퓨터 비전 라이브러리, 이미지/영상 처리 및 객체 인식 기능

---


## 📌 각 기술을 어떻게 프로젝트에 적용했는지

| 기술                      | 역할                                |
| ----------------------- | --------------------------------- |
| **Roboflow**            | 데이터 라벨링, 증강, segmentation mask 생성 |
| **YOLOv8-seg** | 객체 탐지 및 불량/정상 포장지 분류, 세그멘테이션      |
| **OpenCV**              | 웹캠 영상 캡처, ROI 지정, 실시간 결과 시각화      |

---

## 📌 학습 과정에서 어려웠던 점과 극복 방법

#### 1. 실시간 객체 인식 문제

- **직면한 구체적 문제** : 실시간으로 정상/비정상 제품 테스트 중 프로그램의 기본상태가 ‘비정상’이 되는 현상
- **문제 분석 과정** : 객체 인식에 대한 기준값을 설정하지 않아 제품이 화면에 보이지 않아도 ‘비정상’이라고 출력되는 것을 발견
- **시도한 해결 방법들** : 
    - ROI(관심영역) 설정으로 처리 영역 축소
    - 정상 제품에 대한 유사도 확인방법 추가
- **최종 해결 방법** : 정상 제품과 색상 및 템플릿 매칭 비교로 정상 제품과 실시간 객체를 비교
- **해결 결과** : 제품이 ROI 영역에 등장하지 않을 경우 측정을 하지 않으나 정상/비정상 판별의 정확도는 떨어지는 문제 발생
- **학습한 내용** : OpenCV에서 실시간 처리를 위한 최적화 기법

#### 2. roboflow 학습 데이터 인식 불가

- **직면한 구체적 문제** : roboflow - yolo 학습 모델을 프로그램에 적용하였으나 웹캠에서 인식을 제대로 하지 못하는 현상
- **문제 원인 파악** :
    - roboflow의 학습 방식이 잘못 되었나?
    - roboflow 학습 데이터셋의 수가 부족한가?
    - yolo 학습 모델 선택이 잘못 되었나?

- **시도한 해결 방법들** :
    - roboflow
        - 데이터 셋 증강 처리
        - 라벨링 방식 변경
        - 프로젝트 타입 변경
        - 사진 데이터 변경
    - yolo
        - 모델 변경(`yolov11n` → `yolov8n` → `yolov8n-seg`)
- **최종 해결 방법** :
    - roboflow 프로젝트 방식 instance segmentation으로 변경
    - yolo 학습 모델 변경 (`yolov8n.pt` → `yolov8n-seg.pt`)
    
- **해결 결과** :
> #### 해결 전
> <img width="315" height="307" alt="image" src="https://github.com/user-attachments/assets/14cd3abe-82cd-4cc5-8ae7-11f7095eb82e" />
>
> roi 영역에 결함 제품이 있음에도 아무것도 인식하지 못하는 상태


> #### 해결 후
> <div>
> <p align="center">
> <img width="250" height="309" alt="image" src="https://github.com/user-attachments/assets/f4bff39a-ceed-4d75-8ee0-cf316ce804fe" />
> <img width="250" height="309" alt="image" src="https://github.com/user-attachments/assets/9f7cc4fe-e0f6-4a18-9a11-da2a401144c5" />
> <img width="250" height="309" alt="image" src="https://github.com/user-attachments/assets/88cb9898-b016-4543-91b9-6317d8f9767c" />
> </p>
> </div>
> roboflow에서 학습한 내용대로 tearing, contaminated, normal을 정상적으로 분류하고 있는 모습

- **학습한 내용** :
    - roboflow 데이터셋 학습 방법(라벨링, 트레이닝)
    - yolo 모델 프로그램 적용

---
