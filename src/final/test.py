import cv2
from ultralytics import YOLO
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# ======= YOLO 모델 불러오기 (예: ultralytics YOLOv8) =======
model = YOLO("best.pt")  

# ROI 좌표 예시 (x, y, w, h)
ROI_X, ROI_Y, ROI_W, ROI_H = 200, 150, 300, 300

# ======= Tkinter GUI 설정 =======
root = tk.Tk()
root.title("Defect Detection")

# 영상 표시 레이블
label = tk.Label(root)
label.pack()


# 웹캠 초기화
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

# 안내문구
info_text = "Press SPACE to save current status to defect_log.txt"

# 전역 변수로 탐지된 라벨 저장
detected_labels = None

# ======= 로그 표시 버튼 =======
def show_defect_log():
    try:
        df = pd.read_csv("defect_log.txt", header=None, names=["Timestamp", "Detected"])
        plt.figure(figsize=(8,5))
        plt.title("Defect Log")
        plt.axis('off')
        plt.table(cellText=df.values, colLabels=df.columns, loc='center')
        plt.show()
    except Exception as e:
        print("Error reading defect_log.txt:", e)

btn = ttk.Button(root, text="Show Defect Log", command=show_defect_log, takefocus=0)
btn.pack(pady=10)

# ======= 프레임 처리 함수 =======
def process_frame():
    global detected_labels

    ret, frame = cap.read()
    if not ret:
        root.after(10, process_frame)
        return

    # ROI 표시
    frame = cv2.flip(frame, 1)  # 좌우 반전
    cv2.rectangle(frame, (ROI_X, ROI_Y), (ROI_X+ROI_W, ROI_Y+ROI_H), (255,0,0), 2)
    cv2.putText(frame, info_text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

    # YOLO 추론
    results = model(frame, conf=0.7)
    annotated_frame = frame.copy()

    for result in results[0].boxes:
        x1, y1, x2, y2 = map(int, result.xyxy[0])  # 박스 좌표
        conf = float(result.conf[0])                # 신뢰도
        cls = int(result.cls[0])                   # 클래스 ID
        tag = model.names[cls]
        detected_labels = tag + f"({conf:.2f})"

        # 바운딩 박스 중심 좌표
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        # ROI 내부에 있는지 확인
        if ROI_X <= cx <= ROI_X+ROI_W and ROI_Y <= cy <= ROI_Y+ROI_H:
            # ROI 내부라면 박스 표시
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"{tag} {conf:.2f}", 
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.6, (0, 255, 0), 2)

    # 결과 화면 출력
    # cv2.imshow("Packaging Defect Inspection (ROI)", annotated_frame)

    # OpenCV BGR -> RGB 변환
    cv2image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)

    # Tkinter 레이블 업데이트
    label.imgtk = imgtk
    label.configure(image=imgtk)

    root.after(10, process_frame)  # 약 100FPS 갱신

# ======= 스페이스바 로그 기록 =======
def on_key(event):
    global info_text, detected_labels
    if event.keysym == "space":
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 결함 객체 결과 수집
        with open("defect_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{now}, {detected_labels}\n")
        # print(f"Logged at {now}: {', '.join(detected_labels)}")

        # 1초 동안 안내 메시지
        temp_text = f"Logged at {now}"
        info_text = temp_text
        root.after(1000, lambda: restore_info_text())

def restore_info_text():
    global info_text
    info_text = "Press SPACE to save current status to defect_log.txt"

root.bind("<Key>", on_key)

# ======= 영상 처리 시작 =======
process_frame()
root.mainloop()

cap.release()
cv2.destroyAllWindows()
