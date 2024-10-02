import cv2
import mediapipe as mp

# Inicializa o MediaPipe Hands
mp_hands = mp.solutions.hands

# Função para identificar e contar dedos
def identify_fingers(hand_landmarks):
    finger_names = ['Polegar', 'Indicador', 'Médio', 'Anelar', 'Mindinho']
    fingers_status = [0, 0, 0, 0, 0]  # Status de cada dedo: 1 = levantado, 0 = abaixado

    # Identifica se o polegar está levantado
    if hand_landmarks[4].x < hand_landmarks[3].x:  # Verifica a posição do polegar em relação ao dedo anterior
        fingers_status[0] = 1

    # Identifica os outros quatro dedos (indicador, médio, anelar, mindinho)
    for i, tip in enumerate([8, 12, 16, 20]):
        if hand_landmarks[tip].y < hand_landmarks[tip - 2].y:  # Verifica a posição da ponta em relação à articulação
            fingers_status[i + 1] = 1

    return dict(zip(finger_names, fingers_status))

# Inicializa a webcam
cap = cv2.VideoCapture(0)

with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while cap.isOpened():
        ret, frame = cap.read()

        # Converte a imagem para RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        
        # Detecta as mãos
        results = hands.process(image)

        # Converte de volta para BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Verifica se há mãos detectadas
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Identifica e conta os dedos
                fingers = identify_fingers(hand_landmarks.landmark)

                # Exibe o status de cada dedo na tela
                y_offset = 50
                for finger, status in fingers.items():
                    text = f'{finger}: {"Levantado" if status else "Abaixado"}'
                    cv2.putText(image, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
                    y_offset += 30

                # Verifica se apenas o polegar está levantado
                if fingers['Polegar'] == 1 and sum(fingers.values()) == 1:
                    # Exibe "joia" na tela
                    cv2.putText(image, 'Joia', (300, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3, cv2.LINE_AA)

        # Exibe o frame
        cv2.imshow('Hand Tracking', image)

        # Sai do loop quando a tecla 'q' é pressionada
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

# Libera a webcam e fecha as janelas
cap.release()
cv2.destroyAllWindows()
