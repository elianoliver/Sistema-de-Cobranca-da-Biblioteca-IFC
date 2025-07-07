from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QWidget, QFrame, QPushButton,
    QHBoxLayout, QMessageBox, QLineEdit, QFormLayout, QGroupBox, QCheckBox
)
from PyQt6.QtCore import pyqtSignal

from modules.tabs.base_tab import BaseTab
from modules.styles_fix import StyleManager
from modules.config_manager import ConfigManager

class ConfigTab(BaseTab):
    """Aba para configuração geral da aplicação."""

    config_updated = pyqtSignal()

    def __init__(self, parent=None):
        self.config_manager = ConfigManager()
        super().__init__(parent)
        self.load_config()

    def setup_ui(self):
        """Configura a interface da aba de configuração."""
        # Cabeçalho
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 10)

        header = QLabel("Configurações Gerais")
        StyleManager.configure_header_label(header)
        header_layout.addWidget(header)

        description = QLabel(
            "Gerencie as configurações de email e outras opções da aplicação."
        )
        StyleManager.configure_subheader_label(description)
        header_layout.addWidget(description)

        self.layout.addWidget(header_container)

        # Grupo de configurações de Email
        email_group = QGroupBox("Configurações de Email")
        email_layout = QFormLayout(email_group)

        self.email_remetente_input = QLineEdit()
        email_layout.addRow("Email do Remetente:", self.email_remetente_input)

        self.email_senha_app_input = QLineEdit()
        self.email_senha_app_input.setEchoMode(QLineEdit.EchoMode.Password)
        email_layout.addRow("Senha de App do Remetente:", self.email_senha_app_input)

        self.email_destinatario_padrao_input = QLineEdit()
        email_layout.addRow("Destinatário de Teste Padrão:", self.email_destinatario_padrao_input)

        self.email_assunto_padrao_input = QLineEdit()
        email_layout.addRow("Assunto Padrão do Email:", self.email_assunto_padrao_input)
        
        # Checkbox para modo de teste
        self.modo_teste_check = QCheckBox("Habilitar modo de teste (envia apenas para o destinatário de teste)")
        self.modo_teste_check.setToolTip(
            "Se marcado, todos os emails serão enviados para o 'Destinatário de Teste Padrão' em vez dos destinatários reais."
        )
        email_layout.addRow(self.modo_teste_check)

        self.layout.addWidget(email_group)

        # Botões de ação
        actions_container = QFrame()
        actions_layout = QHBoxLayout(actions_container)
        actions_layout.addStretch()

        self.save_button = QPushButton("Salvar Configurações")
        StyleManager.configure_button(self.save_button, 'primary')
        self.save_button.clicked.connect(self.save_config)
        actions_layout.addWidget(self.save_button)

        self.layout.addWidget(actions_container)
        self.layout.addStretch()

    def load_config(self):
        """Carrega as configurações e preenche os campos."""
        if hasattr(self, 'email_remetente_input'):
            self.email_remetente_input.setText(self.config_manager.get_value('email_remetente', ''))
            self.email_senha_app_input.setText(self.config_manager.get_value('email_senha_app', ''))
            self.email_destinatario_padrao_input.setText(self.config_manager.get_value('email_destinatario_padrao', ''))
            self.email_assunto_padrao_input.setText(self.config_manager.get_value('email_assunto_padrao', ''))
            self.modo_teste_check.setChecked(self.config_manager.get_value('modo_teste', True))

    def save_config(self):
        """Salva as configurações a partir dos campos."""
        try:
            # Log para debug - verificar os valores antes de salvar
            print(f"DEBUG - Salvando configurações:")
            print(f"  - email_remetente: '{self.email_remetente_input.text()}'")
            print(f"  - email_destinatario_padrao: '{self.email_destinatario_padrao_input.text()}'")
            print(f"  - email_assunto_padrao: '{self.email_assunto_padrao_input.text()}'")
            print(f"  - modo_teste: {self.modo_teste_check.isChecked()}")
            
            self.config_manager.set_value('email_remetente', self.email_remetente_input.text())
            self.config_manager.set_value('email_senha_app', self.email_senha_app_input.text())
            self.config_manager.set_value('email_destinatario_padrao', self.email_destinatario_padrao_input.text())
            self.config_manager.set_value('email_assunto_padrao', self.email_assunto_padrao_input.text())
            self.config_manager.set_value('modo_teste', self.modo_teste_check.isChecked())

            # Log para debug - verificar se foi salvo corretamente
            print(f"DEBUG - Configurações salvas. Verificando:")
            print(f"  - email_destinatario_padrao (após salvar): '{self.config_manager.get_value('email_destinatario_padrao', '')}'")

            self.config_updated.emit()
            self.show_message_box("Sucesso", "Configurações salvas com sucesso!")
        except Exception as e:
            self.show_message_box("Erro", f"Erro ao salvar configurações: {str(e)}", QMessageBox.Icon.Critical)

    def update_data(self, *args, **kwargs):
        """Recarrega as configurações quando a aba é selecionada, se necessário."""
        self.load_config()
        
        # Forçar atualização dos campos para garantir que estão sincronizados
        if hasattr(self, 'email_remetente_input'):
            self.email_remetente_input.setText(self.config_manager.get_value('email_remetente', ''))
            self.email_senha_app_input.setText(self.config_manager.get_value('email_senha_app', ''))
            self.email_destinatario_padrao_input.setText(self.config_manager.get_value('email_destinatario_padrao', ''))
            self.email_assunto_padrao_input.setText(self.config_manager.get_value('email_assunto_padrao', ''))
            self.modo_teste_check.setChecked(self.config_manager.get_value('modo_teste', True)) 