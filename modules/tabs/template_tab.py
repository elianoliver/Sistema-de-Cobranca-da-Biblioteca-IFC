from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QWidget, QFrame, QTextEdit, QPushButton,
    QHBoxLayout, QMessageBox, QTabWidget, QGroupBox
)
from PyQt6.QtCore import pyqtSignal, Qt
import os

from modules.tabs.base_tab import BaseTab
from modules.styles_fix import StyleManager, AppColors
from modules.config_manager import ConfigManager


class TemplateTab(BaseTab):
    """Aba para configuração de templates de email para notificações."""

    # Sinais específicos desta aba
    templates_updated = pyqtSignal(dict)  # Dicionário com todos os templates

    def __init__(self, parent=None):
        self.config_manager = ConfigManager()
        self.templates = {
            'apenas_multa': '',
            'apenas_pendencia': '',
            'multa_e_pendencia': ''
        }
        super().__init__(parent)
        self.load_templates()

    def setup_ui(self):
        """Configura a interface da aba de templates."""
        # Cabeçalho
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 10)

        header = QLabel("Templates de Email")
        StyleManager.configure_header_label(header)
        header_layout.addWidget(header)

        description = QLabel(
            "Configure os modelos de email que serão usados para notificar os usuários."
            " Use as tags especiais para incluir dados dinâmicos."
        )
        StyleManager.configure_subheader_label(description)
        header_layout.addWidget(description)

        self.layout.addWidget(header_container)

        # Card com informações sobre as tags disponíveis
        help_card = QFrame()
        help_card.setObjectName("helpCard")
        help_layout = QVBoxLayout(help_card)

        help_title = QLabel("<b>Tags Disponíveis:</b>")
        help_layout.addWidget(help_title)

        tags_text = QLabel(
            "<b>{NOME}</b>: Nome do usuário<br>"
            "<b>{VALOR_MULTA}</b>: Valor total das multas<br>"
            "<b>{LIVROS_MULTA}</b>: Lista de itens com multa<br>"
            "<b>{LIVROS_PENDENTES}</b>: Lista de itens pendentes<br>"
        )
        tags_text.setTextFormat(Qt.TextFormat.RichText)
        help_layout.addWidget(tags_text)

        # Área de edição de templates usando abas
        template_tabs = QTabWidget()

        # Template para apenas multas
        multa_tab = QWidget()
        multa_layout = QVBoxLayout(multa_tab)

        multa_label = QLabel("Este template será usado para usuários que possuem apenas multas:")
        multa_layout.addWidget(multa_label)

        self.multa_template = QTextEdit()
        self.multa_template.setMinimumHeight(150)
        multa_layout.addWidget(self.multa_template)

        template_tabs.addTab(multa_tab, "Apenas Multa")

        # Template para apenas pendências
        pendencia_tab = QWidget()
        pendencia_layout = QVBoxLayout(pendencia_tab)

        pendencia_label = QLabel("Este template será usado para usuários que possuem apenas pendências:")
        pendencia_layout.addWidget(pendencia_label)

        self.pendencia_template = QTextEdit()
        self.pendencia_template.setMinimumHeight(150)
        pendencia_layout.addWidget(self.pendencia_template)

        template_tabs.addTab(pendencia_tab, "Apenas Pendência")

        # Template para multas e pendências
        ambos_tab = QWidget()
        ambos_layout = QVBoxLayout(ambos_tab)

        ambos_label = QLabel("Este template será usado para usuários que possuem multas E pendências:")
        ambos_layout.addWidget(ambos_label)

        self.ambos_template = QTextEdit()
        self.ambos_template.setMinimumHeight(150)
        ambos_layout.addWidget(self.ambos_template)

        template_tabs.addTab(ambos_tab, "Multa e Pendência")

        self.layout.addWidget(template_tabs, 1)

        # Botões de ação
        actions_container = QFrame()
        actions_layout = QHBoxLayout(actions_container)

        self.save_button = QPushButton("Salvar Templates")
        self.save_button.setObjectName("saveButton")
        StyleManager.configure_button(self.save_button, 'primary')
        self.save_button.clicked.connect(self.save_templates)
        actions_layout.addWidget(self.save_button)

        self.reset_button = QPushButton("Restaurar Padrões")
        self.reset_button.setObjectName("resetButton")
        StyleManager.configure_button(self.reset_button, 'secondary')
        self.reset_button.clicked.connect(self.reset_templates)
        actions_layout.addWidget(self.reset_button)

        self.layout.addWidget(actions_container)

    def load_templates(self):
        """Carrega os templates salvos das configurações."""
        self.templates['apenas_multa'] = self.config_manager.get_value('template_apenas_multa', self.get_default_template('multa'))
        self.templates['apenas_pendencia'] = self.config_manager.get_value('template_apenas_pendencia', self.get_default_template('pendencia'))
        self.templates['multa_e_pendencia'] = self.config_manager.get_value('template_multa_e_pendencia', self.get_default_template('ambos'))

        # Atualizar a interface se já estiver configurada
        if hasattr(self, 'multa_template'):
            self.multa_template.setText(self.templates['apenas_multa'])
            self.pendencia_template.setText(self.templates['apenas_pendencia'])
            self.ambos_template.setText(self.templates['multa_e_pendencia'])

    def save_templates(self):
        """Salva os templates nas configurações."""
        try:
            # Obter os templates diretamente dos campos de texto
            # Garantir que as quebras de linha sejam normalizadas para \n
            # QTextEdit pode usar diferentes tipos de quebras de linha em diferentes sistemas
            self.templates['apenas_multa'] = self.normalizar_quebras_de_linha(self.multa_template.toPlainText())
            self.templates['apenas_pendencia'] = self.normalizar_quebras_de_linha(self.pendencia_template.toPlainText())
            self.templates['multa_e_pendencia'] = self.normalizar_quebras_de_linha(self.ambos_template.toPlainText())

            # Salvar no ConfigManager
            self.config_manager.set_value('template_apenas_multa', self.templates['apenas_multa'])
            self.config_manager.set_value('template_apenas_pendencia', self.templates['apenas_pendencia'])
            self.config_manager.set_value('template_multa_e_pendencia', self.templates['multa_e_pendencia'])

            # Log para debug
            print("Templates salvos:")
            print(f"Apenas Multa: {len(self.templates['apenas_multa'])} caracteres")
            print(f"Apenas Pendência: {len(self.templates['apenas_pendencia'])} caracteres")
            print(f"Multa e Pendência: {len(self.templates['multa_e_pendencia'])} caracteres")

            # Garantir que emitimos uma cópia do dicionário para evitar problemas de referência
            templates_copy = self.templates.copy()
            self.templates_updated.emit(templates_copy)
            print("Sinal templates_updated emitido")

            self.show_message_box("Sucesso", "Templates salvos com sucesso!")
        except Exception as e:
            self.show_message_box("Erro", f"Erro ao salvar templates: {str(e)}", QMessageBox.Icon.Critical)

    def normalizar_quebras_de_linha(self, texto):
        """Normaliza as quebras de linha no texto para garantir compatibilidade."""
        # Primeiro substituir CRLF (\r\n) por LF (\n)
        texto = texto.replace('\r\n', '\n')
        # Depois substituir CR (\r) sozinhos por LF (\n)
        texto = texto.replace('\r', '\n')
        return texto

    def reset_templates(self):
        """Restaura os templates para os valores padrão."""
        # Confirmar antes de resetar
        confirm = QMessageBox.question(
            self, "Confirmar Restauração",
            "Tem certeza que deseja restaurar todos os templates para os valores padrão?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            # Restaurar para os valores padrão
            self.multa_template.setText(self.get_default_template('multa'))
            self.pendencia_template.setText(self.get_default_template('pendencia'))
            self.ambos_template.setText(self.get_default_template('ambos'))

            # Salvar as alterações
            self.save_templates()

    def get_default_template(self, template_type):
        """Retorna o template padrão para o tipo especificado."""
        if template_type == 'multa':
            return (
                "**Prezado(a) {NOME}**,\n\n"
                "Conforme estabelecido no [Regulamento Interno das Bibliotecas do Instituto Federal Catarinense](https://biblioteca.ifc.edu.br/wp-content/uploads/sites/53/2023/04/SIBI-Regulamento.pdf), artigo 44, é nossa responsabilidade notificá-lo(a) sobre as pendências em sua conta de usuário na biblioteca.\n\n"
                "Constata-se a existência de multa acumulada no valor total de **R$ {VALOR_MULTA}**. referente ao(s) seguinte(s) item(ns):\n\n"
                "{LIVROS_MULTA}\n\n"
                "Salientamos que, para renovar ou realizar novos empréstimos, as multas devem estar abaixo de R$ 10,00. No entanto, para emitir a Declaração de Nada Consta, é necessário que todas as multas e pendências na biblioteca sejam totalmente quitadas.\n\n"
                "**Em caso de perda do material emprestado, deverá ser informado e proceder com a reposição do mesmo.**\n\n"
                "Regularize sua situação com a biblioteca o mais breve possível, para juntos, mantermos funcionando de forma eficiente e acessível para toda a comunidade acadêmica.\n\n"
                "Estamos à disposição para esclarecer dúvidas, ou para mais informações.\n\n"
                "Atenciosamente,"
            )
        elif template_type == 'pendencia':
            return (
                "**Prezado(a) {NOME}**,\n\n"
                "Conforme estabelecido no [Regulamento Interno das Bibliotecas do Instituto Federal Catarinense](https://biblioteca.ifc.edu.br/wp-content/uploads/sites/53/2023/04/SIBI-Regulamento.pdf), artigo 44, é nossa responsabilidade notificá-lo(a) sobre as pendências em sua conta de usuário na biblioteca.\n\n"
                "De acordo com os registros em nosso sistema, observamos que você possui o(s) seguinte(s) item(ns) em atraso:\n\n"
                "{LIVROS_PENDENTES}\n\n"
                "Conforme o artigo 44, Inciso I, do Regulamento, informamos que a multa aplicada é de R$ 1,00 (um real) por dia útil de atraso para cada material emprestado.\n\n"
                "Salientamos que, para renovar ou realizar novos empréstimos, as multas devem estar abaixo de R$ 10,00. No entanto, para emitir a Declaração de Nada Consta, é necessário que todas as multas e pendências na biblioteca sejam totalmente quitadas.\n\n"
                "**Em caso de perda do material emprestado, deverá ser informado e proceder com a reposição do mesmo.**\n\n"
                "Regularize sua situação com a biblioteca o mais breve possível, para juntos, mantermos funcionando de forma eficiente e acessível para toda a comunidade acadêmica.\n\n"
                "Estamos à disposição para esclarecer dúvidas, ou para mais informações.\n\n"
                "Agradecemos sua atenção e colaboração.\n\n"
                "Atenciosamente,"
            )
        else:  # ambos
            return (
                "**Prezado(a) {NOME}**,\n\n"
                "Conforme estabelecido no [Regulamento Interno das Bibliotecas do Instituto Federal Catarinense](https://biblioteca.ifc.edu.br/wp-content/uploads/sites/53/2023/04/SIBI-Regulamento.pdf), artigo 44, é nossa responsabilidade notificá-lo(a) sobre as pendências em sua conta de usuário na biblioteca.\n\n"
                "De acordo com os registros em nosso sistema, observamos que você possui o(s) seguinte(s) item(ns) em atraso:\n\n"
                "{LIVROS_PENDENTES}\n\n"
                "Conforme o artigo 44, Inciso I, do Regulamento, informamos que a multa aplicada é de R$ 1,00 (um real) por dia útil de atraso para cada material emprestado.\n\n"
                "Constata-se também a existência de multa acumulada no valor total de **R$ {VALOR_MULTA}** referente ao(s) seguinte(s) item(ns):\n\n"
                "{LIVROS_MULTA}\n\n"
                "Salientamos que, para renovar ou realizar novos empréstimos, as multas devem estar abaixo de R$ 10,00. No entanto, para emitir a Declaração de Nada Consta, é necessário que todas as multas e pendências na biblioteca sejam totalmente quitadas.\n\n"
                "**Em caso de perda do material emprestado, deverá ser informado e proceder com a reposição do mesmo.**\n\n"
                "Regularize sua situação com a biblioteca o mais breve possível, para juntos, mantermos funcionando de forma eficiente e acessível para toda a comunidade acadêmica.\n\n"
                "Estamos à disposição para esclarecer dúvidas, ou para mais informações.\n\n"
                "Agradecemos sua atenção e colaboração.\n\n"
                "Atenciosamente,"
            )

    def update_data(self, unified_data=None):
        """Atualiza os dados exibidos na aba."""
        # Esta aba não precisa atualizar dados baseado no dataframe unificado
        pass