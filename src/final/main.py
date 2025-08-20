import cv2
from ultralytics import YOLO

# 1. YOLO 모델 불러오기
# 학습된 모델 사용 (예: best.pt), 없으면 COCO 사전학습 모델(yolov8n.pt) 사용
model = YOLO("best.pt")   # <-- 여기서 본인 모델 경로 지정
print(model.names)

# 2. 웹캠 열기
cap = cv2.VideoCapture(0)  # 0번 웹캠

if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # 좌우 반전

    # 3. YOLO 추론 (실시간)
    results = model(frame, conf=0.25) # 신뢰도 0.25 이상
    # 4. 결과 시각화
    annotated_frame = results[0].plot()  # YOLO가 자동으로 박스 + 라벨 표시

    # 5. 화면 출력
    cv2.imshow("Packaging Defect Inspection", annotated_frame)

    # 6. 종료 키 설정
    key = cv2.waitKey(1) & 0xFF
    if key == 27 or key == ord('q'):  # ESC 또는 q
        break

cap.release()
cv2.destroyAllWindows()
