import cv2
import numpy as np
import os
from datetime import datetime

# Define ROI coordinates (adjust as needed)
ROI_X, ROI_Y, ROI_W, ROI_H = 200, 150, 250, 150

def check_defect(baseline_img, current_img, threshold=30):
    """
    기준 이미지와 현재 이미지를 비교하여 불량 여부를 반환.
    :param baseline_img: 기준 이미지 (BGR)
    :param current_img: 현재 이미지 (BGR)
    :param threshold: 평균 색상 차이 임계값
    :return: (결과 텍스트, 차이 영상, 평균 차이 값)
    """
    current_resized = cv2.resize(current_img, (baseline_img.shape[1], baseline_img.shape[0]))

    baseline_hsv = cv2.cvtColor(baseline_img, cv2.COLOR_BGR2HSV)
    current_hsv = cv2.cvtColor(current_resized, cv2.COLOR_BGR2HSV)

    diff = cv2.absdiff(baseline_hsv, current_hsv)
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    mean_diff = np.mean(diff_gray)

    if mean_diff > threshold:
        return "Defective", diff_gray, mean_diff
    else:
        return "Normal", diff_gray, mean_diff


def get_roi_image(frame, roi_x, roi_y, roi_w, roi_h):
    cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), (0, 255, 0), 2)
    roi_image = frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]
    return roi_image


# =================== 메인 실행부 ===================

cap = cv2.VideoCapture(0)

if os.path.exists("baseline.jpg"):
    baseline_img = cv2.imread("baseline.jpg")
else:
    baseline_img = None
    print("baseline 이미지 없음. 'S'를 눌러 저장하세요.")

THRESHOLD = 20        # 평균 색상 차이 임계값
MATCH_THRESHOLD = 0.4 # 템플릿 매칭 유사도 기준

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    display_frame = frame.copy()

    current_product_img = get_roi_image(display_frame, ROI_X, ROI_Y, ROI_W, ROI_H)

    if baseline_img is not None:
        # 템플릿 매칭으로 baseline과 유사도 확인
        # TM_CCOEFF_NORMED는 정규화된 상관 계수를 이용해 두 이미지 패치의 유사도를 1에 가깝게 표현
        # 1 → 완전히 동일, 0 → 무관함, -1 → 완전히 반대
        res = cv2.matchTemplate(current_product_img, baseline_img, cv2.TM_CCOEFF_NORMED)

        # 최소값, 최대값, 최소값 위치, 최대값 위치
        _, max_val, _, _ = cv2.minMaxLoc(res)

        if max_val > MATCH_THRESHOLD:
            # baseline과 비슷한 형태가 ROI에 있다고 판단 → 검사 수행
            result_text, diff_gray, mean_diff = check_defect(baseline_img, current_product_img, THRESHOLD)
        else:
            # baseline과 전혀 다름 → 제품 없음
            result_text, diff_gray, mean_diff = "No product detected", None, 0

        # 결과 표시
        if result_text == "Normal":
            color = (0, 255, 0)
        elif result_text == "Defective":
            color = (0, 0, 255)

            # ★ 불량 발생 시 txt 파일에 로그 기록
            with open("defect_log.txt", "a", encoding="utf-8") as f:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"{now}, MeanDiff={mean_diff:.2f}, Match={max_val:.2f}\n")
                
        else:  # No product detected
            color = (255, 255, 0)

        cv2.putText(display_frame, f"{result_text} ({mean_diff:.1f}, match={max_val:.2f})", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    else:
        cv2.putText(display_frame, "Press 'S' to save baseline image", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    cv2.imshow("Packaging Check", display_frame)

    key = cv2.waitKey(5) & 0xFF
    if key == ord('s'):
        baseline_img = current_product_img.copy()
        cv2.imwrite("baseline.jpg", baseline_img)
        print("기준 이미지 저장 완료!")
    elif key == 27 or key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
