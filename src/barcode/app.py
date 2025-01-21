import toga
from toga.style import Pack
from toga.style.pack import COLUMN
from pyzbar.pyzbar import decode
from PIL import Image
import cv2


class BarcodeApp(toga.App):
    def startup(self):
        # Janela principal
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.running = False  # Flag para monitorar a execução da câmera

        # Botão para iniciar a câmera
        self.camera_button = toga.Button(
            "Iniciar Câmera",
            on_press=self.start_camera,
            style=Pack(padding=10)
        )

        # Label para mostrar o resultado
        self.result_label = toga.Label(
            "Resultado do Código de Barras aparecerá aqui",
            style=Pack(padding=10)
        )

        # Layout
        box = toga.Box(
            children=[self.camera_button, self.result_label],
            style=Pack(direction=COLUMN, padding=10)
        )

        self.main_window.content = box
        self.main_window.on_close = self.close_app  # Fechar o programa principal
        self.main_window.show()

    def close_app(self, *args):
        # Encerrar a câmera e fechar o programa principal
        self.running = False
        cv2.destroyAllWindows()
        self.main_window.close()

    def start_camera(self, widget):
        # Iniciar a captura da câmera
        cap = cv2.VideoCapture(0)  # 0 para a câmera padrão
        self.running = True
        self.result_label.text = "Pressione 'Q' para sair da câmera."

        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                self.result_label.text = "Erro ao acessar a câmera."
                break

            # Pré-processar o frame para melhorar a leitura do código de barras
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            barcodes = decode(Image.fromarray(gray_frame))

            if barcodes:
                for barcode in barcodes:
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    text = barcode.data.decode("utf-8")
                    cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    self.result_label.text = f"Código encontrado: {text}"

                cv2.imshow("Leitor de Código de Barras", frame)
                self.running = False  # Pausar leitura para o diálogo
                cap.release()
                cv2.destroyAllWindows()
                self.ask_to_continue()
                return  # Sair do loop para evitar travamento

            # Mostrar frame na janela sem códigos detectados
            cv2.imshow("Leitor de Código de Barras", frame)

            # Encerrar com 'Q' ou verificar se a janela foi fechada
            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.running = False
            if cv2.getWindowProperty("Leitor de Código de Barras", cv2.WND_PROP_VISIBLE) < 1:
                self.running = False

        cap.release()
        cv2.destroyAllWindows()
        self.result_label.text = "Câmera encerrada."

    def ask_to_continue(self):
        # Perguntar ao usuário se deseja continuar
        dialog = toga.ConfirmDialog(
            title="Continuar?",
            message="Você deseja ler outro código de barras?",
            confirm_label="Sim",
            cancel_label="Não"
        )
        dialog.on_result = self.handle_dialog_result
        dialog.show(self.main_window)

    def handle_dialog_result(self, result):
        if result:  # Se usuário escolher "Sim"
            self.start_camera(None)  # Reiniciar câmera
        else:
            self.result_label.text = "Leitura finalizada."


def main():
    return BarcodeApp("Leitor de Código de Barras", "com.example.barcode")
