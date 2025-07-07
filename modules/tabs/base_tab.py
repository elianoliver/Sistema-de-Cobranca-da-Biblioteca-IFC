from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtCore import pyqtSignal


class BaseTab(QWidget):
    """Classe base para todas as abas da aplicação.

    Fornece funcionalidades comuns e estrutura básica que todas as abas devem ter.
    """

    # Sinais que serão emitidos para a interface principal
    show_message = pyqtSignal(str, str, int)  # título, mensagem, tipo de ícone

    def __init__(self, parent=None):
        """Inicializa a aba base com layout e configurações padrão."""
        super().__init__(parent)

        # Layout principal da aba
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Configuração inicial da interface
        self.setup_ui()

        # Referência para o objeto principal
        self.main_interface = parent

    def setup_ui(self):
        """Método abstrato que deve ser implementado pelas subclasses.

        Este método é responsável por configurar todos os widgets da aba.
        """
        raise NotImplementedError("Cada aba deve implementar seu próprio setup_ui")

    def update_data(self, *args, **kwargs):
        """Método para atualizar os dados exibidos na aba.

        Deve ser implementado por cada aba específica quando necessário.
        """
        pass

    def show_message_box(self, title, message, icon=QMessageBox.Icon.Information):
        """Emite sinal para exibir uma caixa de mensagem na interface principal."""
        self.show_message.emit(title, message, icon)