import cv2
from ultralytics import YOLO
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import subprocess
import webbrowser

# yolo 모델 학습 커맨드
# yolo detect train data=data.yaml model=yolov8n.pt epochs=50 imgsz=640
# yolo detect train data=data.yaml model=yolov8n-seg.pt epochs=100 imgsz=640

# ======= YOLO 모델 불러오기 (예: ultralytics YOLOv8) =======
model = YOLO("best.pt")  

# ROI 좌표 예시 (x, y, w, h)
ROI_X, ROI_Y, ROI_W, ROI_H = 200, 150, 300, 300

# ======= Tkinter GUI 설정 =======
root = tk.Tk()
root.title("Defect Detection")

# 영상 표시 레이블
tk_label = tk.Label(root)
tk_label.pack()


# 웹캠 초기화
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("웹캠을 열 수 없습니다.")
    exit()

# 안내문구
info_text = "Press SPACE to save current status to defect_log.txt"
info_color = (255, 255, 0)

# 전역 변수로 탐지된 라벨 저장
defected_labels = None


# ======= Flask 서버로 로그 표시 =======

# 플라스크 서버 프로세스 관리 변수
flask_process = None

def show_defect_log():
    global flask_process
    if flask_process is None or flask_process.poll() is not None:
        # Flask 서버 실행 (flask_app.py)
        flask_process = subprocess.Popen(["python", "flask_app.py"])
    webbrowser.open("http://127.0.0.1:5000/log")

btn = ttk.Button(root, text="Show Defect Detection Dashboard", command=show_defect_log, takefocus=0)
btn.pack(pady=10)

# ======= 프레임 처리 함수 =======
def process_frame():
    global defected_labels

    ret, frame = cap.read()
    if not ret:
        root.after(10, process_frame)
        return

    # ROI 표시
    frame = cv2.flip(frame, 1)  # 좌우 반전
    cv2.rectangle(frame, (ROI_X, ROI_Y), (ROI_X+ROI_W, ROI_Y+ROI_H), (255,0,0), 2)
    cv2.putText(frame, info_text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, info_color, 2)

    # YOLO 추론
    # verbose 옵션을 False로 설정하여 불필요한 출력 방지
    results = model(frame, conf=0.7, verbose=False)
    annotated_frame = frame.copy()

    defected_labels = None  # 매 프레임마다 초기화

    for result in results[0].boxes:
        x1, y1, x2, y2 = map(int, result.xyxy[0])  # 박스 좌표
        conf = float(result.conf[0])                # 신뢰도
        cls = int(result.cls[0])                   # 클래스 ID
        tag = model.names[cls]
        # print(tag)
        defected_labels = tag + f"({conf:.2f})"

        # 바운딩 박스 중심 좌표
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        # ROI 내부에 있는지 확인
        if ROI_X <= cx <= ROI_X+ROI_W and ROI_Y <= cy <= ROI_Y+ROI_H:
            # ROI 내부라면 박스 표시
            # 클래스별 색상 지정
            if tag == "contaminated":
                rec_color = (255, 0, 255)   # 보라색 (BGR)
            elif tag == "tearing":
                rec_color = (0, 0, 255)     # 빨간색 (BGR)
            else:
                rec_color = (0, 255, 0)     # 기본 녹색 (BGR)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), rec_color, 2)

            cv2.putText(annotated_frame, f"{tag} {conf:.2f}", 
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.6, rec_color, 2)

    # 결과 화면 출력
    # cv2.imshow("Packaging Defect Inspection (ROI)", annotated_frame)

    # OpenCV BGR -> RGB 변환
    cv2image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)

    # Tkinter 레이블 업데이트
    tk_label.imgtk = imgtk
    tk_label.configure(image=imgtk)

    root.after(10, process_frame)  # 약 100FPS 갱신

# ======= 스페이스바 로그 기록 =======
def on_key(event):
    global info_text, info_color, defected_labels

    # 스페이스 키 누르면 기록
    # defected_labels가 None이 아닐 때
    if event.keysym == "space":
        if defected_labels is not None:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 결함 객체 결과 수집
            with open("defect_log.txt", "a", encoding="utf-8") as f:
                f.write(f"{now}, {defected_labels}\n")

            defected_labels = None  # 기록 후 초기화


            # 1초 동안 안내 메시지
            temp_text = f"Logged at {now}"
            info_text = temp_text
            # 초록색으로 변경
            info_color = (0, 255, 0)
            root.after(1000, lambda: restore_info_text())

def restore_info_text():
    global info_text, info_color
    info_text = "Press SPACE to save current status to defect_log.txt"
    info_color = (255, 255, 0)

root.bind("<Key>", on_key)

# ======= 영상 처리 시작 =======
process_frame()
root.mainloop()

cap.release()
cv2.destroyAllWindows()
