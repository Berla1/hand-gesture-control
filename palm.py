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

#Tópico MQTT para publicação
mqtt_topic = "/TEF/device010/motor/cmd"  

def calculate_distance(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

def is_thumb_and_index_touching(hand_landmarks):
    thumb_tip = hand_landmarks[4]  
    index_tip = hand_landmarks[8]  
    distance = calculate_distance(thumb_tip, index_tip)
    return distance < 0.05  

# Função para enviar o ângulo do servo via MQTT
def send_motor_state(state):
    client.publish(mqtt_topic, str(state))  

# Funções para identificar se os dedos estão levantados
def is_index_finger_down(hand_landmarks):
    return hand_landmarks[8].y > hand_landmarks[6].y  # Indicador abaixado

def is_middle_finger_down(hand_landmarks):
    return hand_landmarks[12].y > hand_landmarks[10].y  # Médio abaixado

def is_ring_finger_down(hand_landmarks):
    return hand_landmarks[16].y > hand_landmarks[14].y  # Anelar abaixado

def is_pinky_finger_down(hand_landmarks):
    return hand_landmarks[2].x > hand_landmarks[18].x  # Mindinho abaixado

#############################################################################################################

def is_index_finger_up(hand_landmarks):
    return hand_landmarks[8].y < hand_landmarks[6].y  # Indicador levantado

def is_middle_finger_up(hand_landmarks):
    return hand_landmarks[12].y < hand_landmarks[10].y  # Médio levantado

def is_ring_finger_up(hand_landmarks):
    return hand_landmarks[16].y < hand_landmarks[14].y  # Anelar levantado

def is_pinky_finger_up(hand_landmarks):
    return hand_landmarks[2].x < hand_landmarks[18].x  # Mindinho levantado

# Inicializa a webcam
cap = cv2.VideoCapture(0)

# Inicializa MediaPipe para detectar mãos
with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Falha ao acessar a webcam")
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)

        # Verifica se há mãos detectadas
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                if is_index_finger_down(hand_landmarks.landmark) and is_middle_finger_down and is_ring_finger_down and is_pinky_finger_down:
                   send_motor_state(0)
                   cv2.putText(frame, "Mão fechada!", 
                                (50, 50),  # Posição (x, y) no vídeo
                                cv2.FONT_HERSHEY_SIMPLEX,  
                                1,  # Tamanho da fonte
                                (0, 0, 255),  # Cor (BGR): verde
                                2,  # Espessura da linha
                                cv2.LINE_AA)  # Tipo de linha
                   
                elif is_index_finger_up(hand_landmarks.landmark) and is_middle_finger_up and is_middle_finger_up and is_pinky_finger_up:
                    send_motor_state(1)
                    cv2.putText(frame, "Mão aberta", 
                                (50, 50),  # Posição (x, y) no vídeo
                                cv2.FONT_HERSHEY_SIMPLEX,  
                                1,  # Tamanho da fonte
                                (0, 0, 255),  # Cor (BGR): verde
                                2,  # Espessura da linha
                                cv2.LINE_AA)  # Tipo de linha


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
        # Fechar janela da webcam
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
