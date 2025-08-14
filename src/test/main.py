import cv2
import numpy as np
import os

# 웹캠 시작
cap = cv2.VideoCapture(0)

# baseline 이미지 불러오기
if os.path.exists("baseline.jpg"):
    baseline_img = cv2.imread("baseline.jpg")
    print("기존 baseline.jpg 불러옴")
else:
    baseline_img = None
    print("baseline 이미지 없음. 'S'를 눌러 저장하세요.")

# 색상 차이 판단 기준값
THRESHOLD = 30  # 평균 색상 차이 임계값

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # 좌우 반전
    display_frame = frame.copy()

    # 기준 이미지가 있으면 비교
    if baseline_img is not None:
        # 크기 맞추기
        current_resized = cv2.resize(frame, (baseline_img.shape[1], baseline_img.shape[0]))

        # HSV 변환
        baseline_hsv = cv2.cvtColor(baseline_img, cv2.COLOR_BGR2HSV)
        current_hsv = cv2.cvtColor(current_resized, cv2.COLOR_BGR2HSV)

        # 절대 차이 계산
        diff = cv2.absdiff(baseline_hsv, current_hsv)
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # 차이 평균값
        mean_diff = np.mean(diff_gray)

        # 결과 판단
        if mean_diff > THRESHOLD:
            cv2.putText(display_frame, "Defective", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        else:
            cv2.putText(display_frame, "Normal", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

        # 차이 화면 표시
        cv2.imshow("Difference", diff_gray)
    
    else:
        # 정상 기준 이미지 없을 경우
        # 안내 메세지 출력
        cv2.putText(display_frame, "Press 'S' to save baseline image", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)


    cv2.imshow("Packaging Check", display_frame)

    key = cv2.waitKey(5) & 0xFF

    # S키 → 기준 이미지 저장
    if key == ord('s'):
        baseline_img = frame.copy()
        cv2.imwrite("baseline.jpg", baseline_img)
        print("기준 이미지 저장 완료!")

    # ESC → 종료
    elif key == 27 :
        break

cap.release()
cv2.destroyAllWindows()
