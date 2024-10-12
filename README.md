
# Hand Gesture Control with MQTT and OpenCV

Este projeto implementa um sistema de controle baseado em gestos da mão usando **Mediapipe**, **OpenCV**, e **MQTT** para controlar motores e um servo via comandos remotos. Com uma câmera, gestos são detectados em tempo real para realizar ações como mover um motor ou ajustar o ângulo de um servo.

## Funcionalidades
- **Detecção de gestos com a mão direita**: A mão direita controla o servo motor com gestos que detectam a proximidade do polegar com os outros dedos, definindo diferentes ângulos.
- **Detecção de gestos com a mão esquerda**: A mão esquerda controla o estado do motor, podendo abrir ou fechar a mão para ativar/desativar o motor.
- **Envio de comandos via MQTT**: Ações detectadas são enviadas para tópicos MQTT específicos para controle remoto do motor e servo.

## Tecnologias Utilizadas
- **OpenCV**: Para capturar o vídeo da câmera e exibir a detecção de gestos.
- **Mediapipe**: Para a detecção dos landmarks da mão e identificação de gestos.
- **Paho MQTT**: Para comunicação MQTT, enviando comandos de controle para o motor e servo.
- **Python**: Linguagem de programação utilizada para integração de todas as bibliotecas e lógica de controle.

## Instalação

1. Clone o repositório:
    \`\`\`bash
    git clone https://github.com/usuario/hand-gesture-control.git
    cd hand-gesture-control
    \`\`\`

2. Instale as dependências:
    \`\`\`bash
    pip install opencv-python mediapipe paho-mqtt
    \`\`\`

3. Execute o código:
    \`\`\`bash
    python main.py
    \`\`\`

## Configuração do MQTT
No código, o cliente MQTT está configurado para se conectar ao broker com o endereço **3.83.132.206**. Se você precisar alterar o endereço, modifique a linha no código:

\`\`\`python
broker_address = "seu-endereco-broker"
\`\`\`

## Tópicos MQTT

- **Tópico para o Motor**: \`/TEF/device010/motor/cmd\`
- **Tópico para o Servo**: \`/TEF/device010/servo/cmd\`

### Controle do Motor (Mão Esquerda)
- **Mão fechada**: Envia o comando \`0\` para o motor (desligar).
- **Mão aberta**: Envia o comando \`1\` para o motor (ligar).

### Controle do Servo (Mão Direita)
- **Polegar e indicador juntos**: Define o ângulo do servo para 45 graus.
- **Polegar e médio juntos**: Define o ângulo do servo para 90 graus.
- **Polegar e anelar juntos**: Define o ângulo do servo para 150 graus.

## Uso
1. Abra o vídeo da webcam.
2. Posicione sua mão direita ou esquerda em frente à câmera.
3. O sistema detectará os gestos e enviará os comandos correspondentes via MQTT.

## Encerramento
- Para sair, pressione a tecla \`q\` enquanto a janela da webcam estiver aberta.

## Demonstração
Aqui está uma prévia de como os gestos são detectados e processados no vídeo ao vivo:

- **Mão direita (servo)**: ![Servo Control](link-to-demo-image)
- **Mão esquerda (motor)**: ![Motor Control](link-to-demo-image)

