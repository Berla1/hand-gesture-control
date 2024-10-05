import cv2
import math
import mediapipe as mp
import paho.mqtt.client as mqtt

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_styles = mp.solutions.drawing_styles

# Configura o cliente MQTT
broker_address = "18.208.160.16"
client = mqtt.Client("HandGestureClient")
client.connect(broker_address)

# Tópicos MQTT para publicação
mqtt_topic_motor = "/TEF/device010/motor/cmd"
mqtt_topic_servo = "/TEF/device010/servo/cmd"

def calculate_distance(point1, point2):
    return math.hypot(point2.x - point1.x, point2.y - point1.y)

# Funções para gestos da mão direita (servo)
def is_thumb_and_index_touching(hand_landmarks):
    thumb_tip = hand_landmarks[4]
    index_tip = hand_landmarks[8]
    distance = calculate_distance(thumb_tip, index_tip)
    return distance < 0.05

def is_thumb_and_middle_touching(hand_landmarks):
    thumb_tip = hand_landmarks[4]
    middle_tip = hand_landmarks[12]
    distance = calculate_distance(thumb_tip, middle_tip)
    return distance < 0.05

def is_thumb_and_ring_touching(hand_landmarks):
    thumb_tip = hand_landmarks[4]
    ring_tip = hand_landmarks[16]
    distance = calculate_distance(thumb_tip, ring_tip)
    return distance < 0.05

def is_thumb_and_pinky_touching(hand_landmarks):
    thumb_tip = hand_landmarks[4]
    pinky_tip = hand_landmarks[20]
    distance = calculate_distance(thumb_tip, pinky_tip)
    return distance < 0.05

def send_servo_angle(angle):
    client.publish(mqtt_topic_servo, str(angle))

# Funções para gestos da mão esquerda (motor)
def is_index_finger_down(hand_landmarks):
    return hand_landmarks[8].y > hand_landmarks[6].y  # Indicador abaixado

def is_middle_finger_down(hand_landmarks):
    return hand_landmarks[12].y > hand_landmarks[10].y  # Médio abaixado

def is_ring_finger_down(hand_landmarks):
    return hand_landmarks[16].y > hand_landmarks[14].y  # Anelar abaixado

def is_pinky_finger_down(hand_landmarks):
    return hand_landmarks[20].y > hand_landmarks[18].y  # Mindinho abaixado

def is_index_finger_up(hand_landmarks):
    return hand_landmarks[8].y < hand_landmarks[6].y  # Indicador levantado

def is_middle_finger_up(hand_landmarks):
    return hand_landmarks[12].y < hand_landmarks[10].y  # Médio levantado

def is_ring_finger_up(hand_landmarks):
    return hand_landmarks[16].y < hand_landmarks[14].y  # Anelar levantado

def is_pinky_finger_up(hand_landmarks):
    return hand_landmarks[20].y < hand_landmarks[18].y  # Mindinho levantado

def send_motor_state(state):
    client.publish(mqtt_topic_motor, str(state))

# Inicializa a webcam
cap = cv2.VideoCapture(0)

# Inicializa MediaPipe para detectar mãos
with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Falha ao acessar a webcam")
            break

        # Inverte a imagem horizontalmente para efeito de espelho
        frame = cv2.flip(frame, 1)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Processa a imagem
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True

        # Converte a imagem de volta para BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Verifica se há mãos detectadas
        if results.multi_hand_landmarks and results.multi_handedness:
            for idx, (hand_landmarks, handedness) in enumerate(zip(results.multi_hand_landmarks, results.multi_handedness)):
                hand_label = handedness.classification[0].label  # 'Left' ou 'Right'

                # Ajusta o label devido à inversão da imagem
                if hand_label == 'Left':
                    hand_label = 'Right'
                else:
                    hand_label = 'Left'

                hand_landmarks_list = hand_landmarks.landmark

                if hand_label == 'Left':
                    # Processa gestos da mão esquerda (motor)
                    if (is_index_finger_down(hand_landmarks_list) and 
                        is_middle_finger_down(hand_landmarks_list) and 
                        is_ring_finger_down(hand_landmarks_list) and 
                        is_pinky_finger_down(hand_landmarks_list)):
                        send_motor_state(0)
                        cv2.putText(image, "Mão fechada (Esquerda)", 
                                    (10, 30),  
                                    cv2.FONT_HERSHEY_SIMPLEX,  
                                    1,  
                                    (0, 0, 255),  
                                    2,  
                                    cv2.LINE_AA)
                    elif (is_index_finger_up(hand_landmarks_list) and 
                          is_middle_finger_up(hand_landmarks_list) and 
                          is_ring_finger_up(hand_landmarks_list) and 
                          is_pinky_finger_up(hand_landmarks_list)):
                        send_motor_state(1)
                        cv2.putText(image, "Mão aberta (Esquerda)", 
                                    (10, 30),  
                                    cv2.FONT_HERSHEY_SIMPLEX,  
                                    1,  
                                    (0, 0, 255),  
                                    2,  
                                    cv2.LINE_AA)
                elif hand_label == 'Right':
                    # Processa gestos da mão direita (servo)
                    if is_thumb_and_index_touching(hand_landmarks_list):
                        send_servo_angle(45)
                        cv2.putText(image, "Polegar e Indicador juntos (Direita)", 
                                    (10, 60),  
                                    cv2.FONT_HERSHEY_SIMPLEX,  
                                    1,  
                                    (0, 255, 0),  
                                    2,  
                                    cv2.LINE_AA)
                    elif is_thumb_and_middle_touching(hand_landmarks_list):
                        send_servo_angle(0)
                        cv2.putText(image, "Polegar e Médio juntos (Direita)", 
                                    (10, 60),  
                                    cv2.FONT_HERSHEY_SIMPLEX,  
                                    1,  
                                    (0, 255, 0),  
                                    2,  
                                    cv2.LINE_AA)
                    elif is_thumb_and_ring_touching(hand_landmarks_list):
                        send_servo_angle(90)
                        cv2.putText(image, "Polegar e Anelar juntos (Direita)", 
                                    (10, 60),  
                                    cv2.FONT_HERSHEY_SIMPLEX,  
                                    1,  
                                    (0, 255, 0),  
                                    2,  
                                    cv2.LINE_AA)
                    elif is_thumb_and_pinky_touching(hand_landmarks_list):
                        send_servo_angle(180)
                        cv2.putText(image, "Polegar e Mindinho juntos (Direita)", 
                                    (10, 60),  
                                    cv2.FONT_HERSHEY_SIMPLEX,  
                                    1,  
                                    (0, 255, 0),  
                                    2,  
                                    cv2.LINE_AA)

                # Desenha os pontos da mão
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=mp_styles.get_default_hand_landmarks_style(),
                    connection_drawing_spec=mp_styles.get_default_hand_connections_style()
                )

        # Exibe o vídeo na tela
        cv2.imshow("Webcam - Detecção de Mãos", image)
        # Fechar janela da webcam
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()