import cv2
from ultralytics import YOLO
import time

# yolo 모델 학습 커맨드
# yolo detect train data=data.yaml model=yolov8n.pt epochs=50 imgsz=640

# 1. YOLO 모델 불러오기
model = YOLO("best.pt")   # 학습된 모델 경로 지정
# print(model.names)

# ROI 좌표 (x, y, w, h) - 필요에 맞게 조정
ROI_X, ROI_Y, ROI_W, ROI_H = 200, 150, 300, 300

# 2. 웹캠 열기
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()


while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)  # 좌우 반전

    # time.sleep(0.3)  # 프레임 속도 조절

    # ROI 영역 시각화 (파란색 박스)
    cv2.rectangle(frame, (ROI_X, ROI_Y), (ROI_X+ROI_W, ROI_Y+ROI_H), (255, 0, 0), 2)

    # 3. YOLO 추론
    results = model(frame, conf=0.5)

    annotated_frame = frame.copy()

    # 4. 탐지 결과 필터링 (ROI 내부만)
    for result in results[0].boxes:
        x1, y1, x2, y2 = map(int, result.xyxy[0])  # 박스 좌표
        conf = float(result.conf[0])                # 신뢰도
        cls = int(result.cls[0])                   # 클래스 ID
        label = model.names[cls]

        # 바운딩 박스 중심 좌표
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        # ROI 내부에 있는지 확인
        if ROI_X <= cx <= ROI_X+ROI_W and ROI_Y <= cy <= ROI_Y+ROI_H:
            # ROI 내부라면 박스 표시
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"{label} {conf:.2f}", 
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.6, (0, 255, 0), 2)

    # 5. 결과 화면 출력
    cv2.imshow("Packaging Defect Inspection (ROI)", annotated_frame)

    # 종료 키 설정
    key = cv2.waitKey(1) & 0xFF
    if key == 27 or key == ord('q'):  # ESC 또는 q
        break

cap.release()
cv2.destroyAllWindows()
