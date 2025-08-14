import cv2
import numpy as np
import os

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
    # 크기 맞추기
    current_resized = cv2.resize(current_img, (baseline_img.shape[1], baseline_img.shape[0]))

    # HSV 변환
    baseline_hsv = cv2.cvtColor(baseline_img, cv2.COLOR_BGR2HSV)
    current_hsv = cv2.cvtColor(current_resized, cv2.COLOR_BGR2HSV)

    # 절대 차이 계산
    diff = cv2.absdiff(baseline_hsv, current_hsv)
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    # 차이 평균값
    mean_diff = np.mean(diff_gray)

    # 결과 판단
    if mean_diff > threshold:
        return "Defective", diff_gray, mean_diff
    else:
        return "Normal", diff_gray, mean_diff


def get_roi_image(frame, roi_x, roi_y, roi_w, roi_h):
    """
    웹캠 화면에 ROI를 표시하고, 그 영역의 이미지를 반환.
    :param frame: 웹캠 프레임
    :param roi_x, roi_y: ROI 좌측 상단 좌표
    :param roi_w, roi_h: ROI 너비와 높이
    :return: ROI 내부의 이미지
    """
    # ROI 영역 표시 (초록색 사각형)
    cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), (0, 255, 0), 2)
    
    # ROI 내부 이미지 추출
    roi_image = frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]
    return roi_image


# =================== 메인 실행부 ===================

# 웹캠 시작
cap = cv2.VideoCapture(0)

# baseline 이미지 불러오기
if os.path.exists("baseline.jpg"):
    baseline_img = cv2.imread("baseline.jpg")
    # baseline 이미지도 ROI로 자르기
    baseline_img = baseline_img[ROI_Y:ROI_Y + ROI_H, ROI_X:ROI_X + ROI_W]
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

    # ROI 영역 이미지 가져오기
    current_product_img = get_roi_image(display_frame, ROI_X, ROI_Y, ROI_W, ROI_H)

    # 기준 이미지가 있으면 비교
    if baseline_img is not None:
        
        # ROI 내부의 이미지로 불량 여부 확인
        result_text, diff_gray, mean_diff = check_defect(baseline_img, current_product_img, THRESHOLD)

        # 결과 텍스트 표시
        color = (0, 255, 0) if result_text == "Normal" else (0, 0, 255)
        cv2.putText(display_frame, f"{result_text} ({mean_diff:.1f})", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

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
        # ROI 영역만 기준 이미지로 저장
        baseline_img = current_product_img.copy()
        cv2.imwrite("baseline.jpg", baseline_img)
        print("기준 이미지 저장 완료!")

    # 종료
    elif key == 27 or key == ord('q'):  # Esc 또는 q로 종료
        break

cap.release()
cv2.destroyAllWindows()