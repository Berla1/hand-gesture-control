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

# Tópico MQTT para publicação
mqtt_topic = "/TEF/device010/servo/cmd"  

def calculate_distance(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

def is_thumb_and_index_touching(hand_landmarks):
    thumb_tip = hand_landmarks[4]  
    index_tip = hand_landmarks[8]  
    distance = calculate_distance(thumb_tip, index_tip) # Indicador e dedão
    return distance < 0.05  


def is_thumb_and_middle_touching(hand_landmarks):
    thumb_tip = hand_landmarks[4]  
    middle_tip = hand_landmarks[12]  
    distance = calculate_distance(thumb_tip, middle_tip) # Dedo do meio e dedão
    return distance < 0.05  

def is_thumb_and_ring_touching(hand_landmarks):
    thumb_tip = hand_landmarks[4]  
    ring_tip = hand_landmarks[16]  
    distance = calculate_distance(thumb_tip, ring_tip) # Anelar dedão
    return distance < 0.05
  
def is_thumb_and_pinky_touching(hand_landmarks):
    thumb_tip = hand_landmarks[4]  
    ring_tip = hand_landmarks[20]  
    distance = calculate_distance(thumb_tip, ring_tip) # Mindinho e dedão
    return distance < 0.05  

# Função para enviar o ângulo do servo via MQTT
def send_servo_angle(angle):
    client.publish(mqtt_topic, str(angle))  

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
                if is_thumb_and_index_touching(hand_landmarks.landmark):
                   cv2.putText(frame, "Polegar e Indicador juntos!", 
                                (50, 50),  
                                cv2.FONT_HERSHEY_SIMPLEX,  
                                1,  
                                (0, 0, 255),  
                                2,  
                                cv2.LINE_AA)  
                elif is_thumb_and_middle_touching(hand_landmarks.landmark):
                    cv2.putText(frame, "Polegar e dedo do meio juntos!", 
                                (50, 50),  
                                cv2.FONT_HERSHEY_SIMPLEX,  
                                1,  
                                (0, 0, 255),  
                                2,  
                                cv2.LINE_AA)  
                    
                elif is_thumb_and_ring_touching(hand_landmarks.landmark):
                    cv2.putText(frame, "Polegar e anelar juntos!", 
                                (50, 50),  
                                cv2.FONT_HERSHEY_SIMPLEX,  
                                1,  
                                (0, 0, 255),  
                                2,  
                                cv2.LINE_AA)
                      
                elif is_thumb_and_pinky_touching(hand_landmarks.landmark):
                    cv2.putText(frame, "Polegar e mindinho juntos!", 
                                (50, 50),  
                                cv2.FONT_HERSHEY_SIMPLEX,  
                                1,  
                                (0, 0, 255),  
                                2,  
                                cv2.LINE_AA)  
                    

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
