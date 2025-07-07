from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QWidget, QFrame, QTextBrowser,
    QHBoxLayout, QToolButton, QScrollArea, QPushButton,
    QGridLayout, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QFont, QColor
from PyQt6.QtGui import QPalette
import pandas as pd

from modules.tabs.base_tab import BaseTab
from modules.styles_fix import StyleManager, AppColors
from modules.data_processor import categorize_users

class ExpandableCard(QFrame):
    """Widget de card expansível para exibir estatísticas."""

    def __init__(self, title, icon, bg_color, parent=None):
        super().__init__(parent)
        self.expanded = True
        self.bg_color = bg_color

        # Configurações do frame
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(1)

        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Cabeçalho do card
        self.header = QFrame()
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(15, 10, 15, 10)

        # Aplicar cor de fundo ao cabeçalho
        palette = self.header.palette()
        palette.setColor(QPalette.ColorRole.Window, bg_color)
        self.header.setPalette(palette)
        self.header.setAutoFillBackground(True)

        self.title_label = QLabel(title)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        self.title_label.setFont(title_font)

        # Cor do texto do cabeçalho (branco)
        palette = self.title_label.palette()
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        self.title_label.setPalette(palette)
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)

        # Botão de expansão/contração
        self.toggle_button = QToolButton()
        self.toggle_button.setText("▼")
        self.toggle_button.setStyleSheet("color: white; background: transparent; border: none;")
        self.toggle_button.clicked.connect(self.toggle_content)

        # Adicionar widgets ao layout do cabeçalho
        header_layout.addWidget(self.title_label, 1)
        header_layout.addWidget(self.toggle_button)

        # Conteúdo do card
        self.content = QFrame()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        self.content_layout.setSpacing(10)

        # Estilo do conteúdo
        palette = self.content.palette()
        palette.setColor(QPalette.ColorRole.Window, AppColors.CARD)
        self.content.setPalette(palette)
        self.content.setAutoFillBackground(True)

        # Adicionar ao layout principal
        self.main_layout.addWidget(self.header)
        self.main_layout.addWidget(self.content)

        # Configurar comportamento do mouse
        self.header.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header.mousePressEvent = self.header_clicked

    def header_clicked(self, event):
        self.toggle_content()

    def toggle_content(self):
        self.expanded = not self.expanded
        self.content.setVisible(self.expanded)
        self.toggle_button.setText("▼" if self.expanded else "▶")

    def add_content(self, widget):
        self.content_layout.addWidget(widget)

class StatisticsLabel(QLabel):
    """Label para estatísticas com formatação consistente."""

    def __init__(self, text, bold=False, parent=None):
        super().__init__(text, parent)
        font = self.font()
        if bold:
            font.setBold(True)
        self.setFont(font)
        self.setWordWrap(True)

class ResultsTab(BaseTab):
    """Aba para exibição dos resultados da unificação dos relatórios."""

    def __init__(self, parent=None):
        self.unified_data = None
        self.cards = {}  # Armazena referências aos cards criados
        super().__init__(parent)

    def setup_ui(self):
        """Configura a interface da aba de resultados."""
        # Título da aba de resultados
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 10)

        title = QLabel("Resultados da Unificação")
        StyleManager.configure_header_label(title)
        title_layout.addWidget(title)

        subtitle = QLabel("Visualize os dados processados e estatísticas")
        StyleManager.configure_subheader_label(subtitle)
        title_layout.addWidget(subtitle)

        self.layout.addWidget(title_container)

        # Área de scroll para os cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # Container para os cards
        dashboard_container = QWidget()
        self.dashboard_layout = QGridLayout(dashboard_container)
        self.dashboard_layout.setContentsMargins(0, 0, 0, 0)
        self.dashboard_layout.setSpacing(15)

        scroll_area.setWidget(dashboard_container)
        self.layout.addWidget(scroll_area)

        # Criar mensagem de boas-vindas
        self.show_welcome_message()

    def update_data(self, unified_data):
        """Atualiza os dados exibidos na aba com o dataframe unificado."""
        self.unified_data = unified_data
        self.display_unified_results()

    def display_unified_results(self):
        """Exibe os resultados da unificação usando widgets nativos"""
        if self.unified_data is None:
            return

        # Limpar layout
        self.clear_dashboard()

        # Obter categorias e estatísticas
        categories = categorize_users(self.unified_data)

        # Calcular estatísticas para os cards
        df_rel86 = self.unified_data[self.unified_data['Relatório'] == 'rel86']
        df_rel76 = self.unified_data[self.unified_data['Relatório'] == 'rel76']

        # Contagens de pessoas únicas
        unique_users_rel86 = df_rel86['Código da pessoa'].nunique() if 'Código da pessoa' in df_rel86.columns else 0
        unique_users_rel76 = df_rel76['Código da pessoa'].nunique() if 'Código da pessoa' in df_rel76.columns else 0

        # Filtrar registros com chaves emprestadas
        chaves_df = self.unified_data[
            (~self.unified_data['Número chave'].isna()) &
            (self.unified_data['Número chave'].str.strip() != "")
        ]

        # Quantidade de pessoas únicas com chaves
        unique_users_chaves = chaves_df['Código da pessoa'].nunique() if 'Código da pessoa' in chaves_df.columns else 0

        # Card Relatório 86
        rel86_card = self.create_card("Relatório 86 (Multas)", "📊", AppColors.MULTAS)
        rel86_content = self.create_statistics_widget([
            ("Número total de linhas:", str(len(df_rel86))),
            ("Pessoas únicas no relatório:", str(unique_users_rel86)),
            ("Pessoas sem e-mail:", str(len(categories['rel86']['pessoas_sem_email']))),
            ("Valor total de multas:", f"R$ {categories['rel86']['total_multas']:.2f}")
        ])
        rel86_card.add_content(rel86_content)
        self.dashboard_layout.addWidget(rel86_card, 0, 0)
        self.cards['rel86'] = rel86_card

        # Card Relatório 76
        rel76_card = self.create_card("Relatório 76 (Pendências)", "📚", AppColors.PENDENCIAS)
        rel76_content = self.create_statistics_widget([
            ("Número total de linhas:", str(len(df_rel76))),
            ("Pessoas únicas no relatório:", str(unique_users_rel76)),
            ("Pessoas sem e-mail:", str(len(categories['rel76']['pessoas_sem_email'])))
        ])
        rel76_card.add_content(rel76_content)
        self.dashboard_layout.addWidget(rel76_card, 0, 1)
        self.cards['rel76'] = rel76_card

        # Card Pessoas Sem Email
        sem_email_card = self.create_card("Pessoas Sem Email", "👤", AppColors.ACCENT)
        sem_email_content = self.create_statistics_widget([
            ("Total de pessoas sem email:", str(len(categories['sem_email']['pessoas']))),
            ("Pessoas do rel86 sem email:", str(len(categories['rel86']['pessoas_sem_email']))),
            ("Pessoas do rel76 sem email:", str(len(categories['rel76']['pessoas_sem_email'])))
        ])
        sem_email_card.add_content(sem_email_content)
        self.dashboard_layout.addWidget(sem_email_card, 1, 0)
        self.cards['sem_email'] = sem_email_card

        # Card Chaves Emprestadas
        chaves_card = self.create_card("Chaves Emprestadas", "🔑", QColor('#f39c12'))
        chaves_content = self.create_statistics_widget([
            ("Total de multas de chaves:", str(len(chaves_df))),
            ("Pessoas com multas de chaves:", str(unique_users_chaves))
        ])
        chaves_card.add_content(chaves_content)
        self.dashboard_layout.addWidget(chaves_card, 1, 1)
        self.cards['chaves'] = chaves_card

    def create_card(self, title, icon, bg_color):
        """Cria um card expansível"""
        card = ExpandableCard(title, icon, bg_color)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        return card

    def create_statistics_widget(self, stats_data):
        """Cria um widget com estatísticas formatadas"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Fundo do conteúdo
        widget.setAutoFillBackground(True)
        palette = widget.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor('#f8f9fa'))
        widget.setPalette(palette)

        # Adicionar cada item de estatística
        for label, value in stats_data:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(5, 3, 5, 3)

            label_widget = StatisticsLabel(label, True)
            value_widget = StatisticsLabel(value)

            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget, 1)

            layout.addWidget(row_widget)

        return widget

    def clear_dashboard(self):
        """Limpa os widgets do dashboard"""
        # Remover todos os widgets do layout
        while self.dashboard_layout.count():
            item = self.dashboard_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Limpar o dicionário de cards
        self.cards.clear()

    def show_welcome_message(self):
        """Exibe mensagem de boas-vindas usando widgets nativos."""
        welcome_card = self.create_card("Bem-vindo aos Resultados", "👋", AppColors.INFO)

        welcome_content = QWidget()
        content_layout = QVBoxLayout(welcome_content)

        message = QLabel(
            "Aqui serão exibidas estatísticas sobre os relatórios unificados.\n\n"
            "Para começar, importe os arquivos de relatórios na aba 'Importar' "
            "e depois clique em 'Processar' para visualizar os resultados."
        )
        message.setWordWrap(True)
        content_layout.addWidget(message)

        welcome_card.add_content(welcome_content)
        self.dashboard_layout.addWidget(welcome_card, 0, 0, 1, 2)
        self.cards['welcome'] = welcome_card