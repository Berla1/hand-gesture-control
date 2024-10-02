import cv2
import mediapipe as mp
import paho.mqtt.client as mqtt

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

# Configura o cliente MQTT
broker_address = "18.208.160.16"  
client = mqtt.Client("HandGestureClient")
client.connect(broker_address)

# Tópico MQTT para publicação
mqtt_topic = "/TEF/device010/servo/cmd"  

# Função para enviar o ângulo do servo via MQTT
def send_servo_angle(angle):
    client.publish(mqtt_topic, str(angle))  

# Funções para identificar se os dedos estão levantados
def is_index_finger_down(hand_landmarks):
    return hand_landmarks[8].y > hand_landmarks[6].y  # Índice

def is_middle_finger_down(hand_landmarks):
    return hand_landmarks[12].y > hand_landmarks[10].y  # Médio

def is_pinky_finger_down(hand_landmarks):
    return hand_landmarks[20].y > hand_landmarks[18].y  # Mindinho

def is_thumb_finger_down(hand_landmarks):
    return hand_landmarks[4].x > hand_landmarks[2].x  # Dedão


# Inicializa a webcam
cap = cv2.VideoCapture(0)

# Inicializa MediaPipe para detectar mãos
with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Falha ao acessar a webcam")
            break

        # Converte a imagem para RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)

        # Verifica se há mãos detectadas
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                if is_index_finger_down(hand_landmarks.landmark):
                    print("Indicador levantado! Enviando valor 45 via MQTT...")
                    send_servo_angle(45)

                elif is_middle_finger_down(hand_landmarks.landmark):
                    print("Dedo médio levantado! Enviando valor 180 via MQTT...")
                    send_servo_angle(180)

                elif is_pinky_finger_down(hand_landmarks.landmark):
                    print("Mindinho levantado! Enviando valor 0 via MQTT...")
                    send_servo_angle(0)

                elif is_thumb_finger_down(hand_landmarks.landmark):
                    print("Dedão levantado levantado! Enviando valor 90 via MQTT...")
                    send_servo_angle(90)

                # Desenha os pontos da mão
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=mp_styles.get_default_hand_landmarks_style(),
                    connection_drawing_spec=mp_styles.get_default_hand_connections_style()
                )

        # Exibe o vídeo na tela
        cv2.imshow("Webcam - Detecção de Mãos", frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
