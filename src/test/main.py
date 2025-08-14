import cv2


# 카메라 캡쳐 활성화
cap = cv2.VideoCapture(0)


while cap.isOpened():
    ret, frame = cap.read()
    
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # 좌우 반전

    cv2.imshow('test', frame)

    key = cv2.waitKey(5) & 0xFF
    if key == 27:  # ESC 키
        break

cap.release()
cv2.destroyAllWindows()