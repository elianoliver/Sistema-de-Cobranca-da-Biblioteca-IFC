"""
Componentes reutilizáveis para a interface gráfica.

Este módulo contém widgets e componentes personalizados que são utilizados
em diferentes partes da interface gráfica.
"""

import os
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtGui import QCursor, QPalette
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from modules.styles_fix import StyleManager, AppColors

class FileDropArea(QFrame):
    """Área de arrastar e soltar para arquivos Excel com identificação do tipo"""
    fileDropped = pyqtSignal(str, str)  # Sinal que emite caminho do arquivo e tipo

    def __init__(self, report_type="multas", parent=None):
        super().__init__(parent)
        self.setObjectName("dropArea")
        self.setMinimumHeight(150)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.report_type = report_type  # 'multas' ou 'pendencias'
        self.file_path = None
        self.setAcceptDrops(True)

        # Configurar tamanho mínimo para evitar elementos comprimidos
        self.setMinimumWidth(250)

        # Layout e componentes visuais
        self.setup_ui()

        # Aplicar estilo usando StyleManager
        StyleManager.configure_drop_area(self, self.report_type)

        # Timer para animar o highlight quando o mouse entra
        self.highlight_timer = QTimer(self)
        self.highlight_timer.setSingleShot(True)
        self.highlight_timer.timeout.connect(self.reset_highlight)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        # Descrição do tipo de relatório
        title = "💰 Relatório de Multas (86)" if self.report_type == "multas" else "📚 Relatório de Pendências (76)"
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setObjectName("dropTitle")
        layout.addWidget(self.title_label)

        # Instrução
        self.text_label = QLabel("Arraste o arquivo Excel \nou clique para procurar")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setWordWrap(True)
        layout.addWidget(self.text_label)

        # Status do arquivo
        self.status_label = QLabel("Nenhum arquivo selecionado")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("fileStatusLabel")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Configurar o label de status usando StyleManager
        StyleManager.configure_status_label(self.status_label, False)

        # Adiciona espaçamento ao final
        layout.addStretch()

    def set_file(self, file_path):
        """Define o arquivo e atualiza o visual"""
        self.file_path = file_path
        if file_path:
            filename = os.path.basename(file_path)
            # Limita o tamanho do nome do arquivo para evitar que ultrapasse a largura do componente
            if len(filename) > 30:
                display_name = filename[:27] + "..."
            else:
                display_name = filename

            self.status_label.setText(f"Arquivo: {display_name}")
            # Atualizar o estilo do status_label usando StyleManager
            StyleManager.configure_status_label(self.status_label, True)
            self.text_label.setText("Clique para trocar o arquivo")

            # Destacar visualmente a borda para indicar seleção
            self.highlight_success()
        else:
            self.status_label.setText("Nenhum arquivo selecionado")
            # Atualizar o estilo do status_label usando StyleManager
            StyleManager.configure_status_label(self.status_label, False)
            self.text_label.setText("Arraste o arquivo Excel \nou clique para procurar")

            # Restaurar o estilo original
            StyleManager.configure_drop_area(self, self.report_type)

    def mousePressEvent(self, event):
        """Quando clicado, abre diálogo para selecionar arquivo"""
        from modules.config_manager import ConfigManager
        from PyQt6.QtWidgets import QFileDialog

        last_dir = ConfigManager().get_value('ultimo_diretorio', '')

        file_path, _ = QFileDialog.getOpenFileName(
            self, f"Selecione o {self.title_label.text()}",
            last_dir,
            "Excel Files (*.xlsx *.xls)"
        )

        if file_path:
            # Salva o diretório para uso futuro
            ConfigManager().set_value('ultimo_diretorio', os.path.dirname(file_path))

            self.set_file(file_path)
            self.fileDropped.emit(file_path, self.report_type)
            self.highlight_success()

    def dragEnterEvent(self, event):
        """Permite a entrada de arquivos arrastados"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

            # Aplicar estilo de destaque na área de drop
            # Usar QPalette para destaque
            palette = self.palette()
            border_color = AppColors.MULTAS if self.report_type == "multas" else AppColors.PENDENCIAS
            palette.setColor(QPalette.ColorRole.Window, AppColors.ACCENT_LIGHT)
            self.setPalette(palette)
            self.setAutoFillBackground(True)

    def dragLeaveEvent(self, event):
        """Remove o estilo de destaque quando o arquivo sai da área"""
        # Restaurar o estilo original usando StyleManager
        StyleManager.configure_drop_area(self, self.report_type)

        # Se um arquivo já estiver selecionado, restaura o visual adequado
        if self.file_path:
            self.set_file(self.file_path)

    def dropEvent(self, event):
        """Processa o arquivo quando solto na área"""
        from PyQt6.QtWidgets import QMessageBox

        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.endswith((".xlsx", ".xls")):
                self.set_file(file_path)
                self.fileDropped.emit(file_path, self.report_type)
                self.highlight_success()
            else:
                QMessageBox.warning(self, "Formato Inválido",
                                   "Por favor, arraste um arquivo Excel válido (.xlsx ou .xls).")
                self.highlight_error()
        else:
            # Restaura o estilo se nenhum arquivo for válido
            StyleManager.configure_drop_area(self, self.report_type)

    def highlight_success(self):
        """Adiciona um efeito visual temporário de sucesso"""
        # Aplicar destaque usando QPalette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, AppColors.ACCENT_LIGHT)
        if self.report_type == "multas":
            palette.setColor(QPalette.ColorRole.WindowText, AppColors.MULTAS)
        else:
            palette.setColor(QPalette.ColorRole.WindowText, AppColors.PENDENCIAS)

        # Destacar a borda
        self.setFrameShape(QFrame.Shape.Box)
        self.setLineWidth(2)
        self.setFrameShadow(QFrame.Shadow.Raised)

        self.setPalette(palette)
        self.highlight_timer.start(800)  # Reseta após 800ms

    def highlight_error(self):
        """Adiciona um efeito visual temporário de erro"""
        # Aplicar destaque usando QPalette
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, AppColors.WARNING_LIGHT)
        palette.setColor(QPalette.ColorRole.WindowText, AppColors.WARNING)

        # Destacar a borda
        self.setFrameShape(QFrame.Shape.Box)
        self.setLineWidth(2)
        self.setFrameShadow(QFrame.Shadow.Raised)

        self.setPalette(palette)
        self.highlight_timer.start(800)  # Reseta após 800ms

    def reset_highlight(self):
        """Restaura o estilo após uma animação"""
        if self.file_path:
            # Restaurar estilo básico
            StyleManager.configure_drop_area(self, self.report_type)

            # Aplicar efeito de "arquivo selecionado"
            palette = self.palette()
            if self.report_type == "multas":
                palette.setColor(QPalette.ColorRole.WindowText, AppColors.MULTAS)
            else:
                palette.setColor(QPalette.ColorRole.WindowText, AppColors.PENDENCIAS)

            self.setPalette(palette)

            # Configurar status label
            StyleManager.configure_status_label(self.status_label, True)
        else:
            # Restaurar completamente o estilo original
            StyleManager.configure_drop_area(self, self.report_type)