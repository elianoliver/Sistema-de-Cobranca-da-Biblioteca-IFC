"""
Módulo para gerenciar estilos da aplicação usando exclusivamente APIs nativas do Qt
Elimina o uso de CSS em favor de QPalette, QFont e métodos nativos do Qt
"""
from PyQt6.QtGui import QPalette, QColor, QFont, QIcon, QPen, QBrush
from PyQt6.QtCore import Qt, QMargins
from PyQt6.QtWidgets import QStyleFactory, QApplication, QStyle, QFrame, QTabWidget, QProxyStyle

# Definição das cores do sistema
class AppColors:
    PRIMARY = QColor('#3f51b5')       # Azul principal
    PRIMARY_DARK = QColor('#303f9f')  # Azul escuro
    PRIMARY_LIGHT = QColor('#e8eaf6') # Azul claro

    ACCENT = QColor('#4caf50')        # Verde para ações positivas
    ACCENT_DARK = QColor('#388e3c')   # Verde escuro
    ACCENT_LIGHT = QColor('#e8f5e9')  # Verde claro

    WARNING = QColor('#f44336')       # Vermelho para alertas
    WARNING_LIGHT = QColor('#ffebee') # Vermelho claro

    INFO = QColor('#2196f3')          # Azul informativo
    INFO_LIGHT = QColor('#e3f2fd')    # Azul claro informativo

    BACKGROUND = QColor('#f8f9fa')    # Fundo geral da aplicação
    CARD = QColor('#ffffff')          # Fundo de cards

    TEXT = QColor('#333333')          # Texto principal
    TEXT_LIGHT = QColor('#666666')    # Texto secundário
    TEXT_DISABLED = QColor('#9e9e9e') # Texto desabilitado

    BORDER = QColor('#e0e0e0')        # Borda padrão

    # Cores para relatórios específicos
    MULTAS = QColor('#e74c3c')        # Cor para relatório de multas
    MULTAS_LIGHT = QColor('#fff5f5')  # Fundo para relatório de multas
    MULTAS_BORDER = QColor('#ffcccc') # Borda para relatório de multas

    PENDENCIAS = QColor('#3498db')    # Cor para relatório de pendências
    PENDENCIAS_LIGHT = QColor('#f0f8ff')  # Fundo para relatório de pendências
    PENDENCIAS_BORDER = QColor('#cce5ff')  # Borda para relatório de pendências


# Estilo personalizado para abas
class TabStyle(QProxyStyle):
    def __init__(self, style=None):
        super(TabStyle, self).__init__(style)

    def drawControl(self, element, option, painter, widget=None):
        if element == QStyle.ControlElement.CE_TabBarTabShape:
            # Desenho personalizado para abas
            painter.save()

            # Define cores e características da aba
            selected = option.state & QStyle.StateFlag.State_Selected

            # Desenha o fundo da aba
            background = AppColors.PRIMARY_LIGHT if selected else AppColors.BACKGROUND
            painter.fillRect(option.rect, background)

            # Se selecionado, desenha uma linha na parte inferior
            if selected:
                highlight_rect = option.rect
                highlight_rect.setTop(highlight_rect.bottom() - 3)
                painter.fillRect(highlight_rect, AppColors.PRIMARY)

            painter.restore()
        else:
            # Para outros elementos, usa o estilo padrão
            super(TabStyle, self).drawControl(element, option, painter, widget)


class StyleManager:
    """Gerencia a aplicação de estilos usando exclusivamente APIs nativas do Qt"""

    @staticmethod
    def apply_application_theme(app):
        """Aplica o tema global usando Fusion style e QPalette"""
        # Define o estilo Fusion para aparência consistente em todas as plataformas
        app.setStyle(QStyleFactory.create("Fusion"))

        # Aplica a paleta de cores centralizada
        palette = StyleManager._create_application_palette()
        app.setPalette(palette)

        # Define a fonte padrão para toda a aplicação
        font = QFont("Segoe UI", 10)
        app.setFont(font)

        return app

    @staticmethod
    def _create_application_palette():
        """Cria a paleta de cores para toda a aplicação"""
        palette = QPalette()

        # Configurações básicas de interface
        palette.setColor(QPalette.ColorRole.Window, AppColors.BACKGROUND)
        palette.setColor(QPalette.ColorRole.WindowText, AppColors.TEXT)
        palette.setColor(QPalette.ColorRole.Base, AppColors.CARD)
        palette.setColor(QPalette.ColorRole.AlternateBase, AppColors.BACKGROUND)
        palette.setColor(QPalette.ColorRole.ToolTipBase, AppColors.CARD)
        palette.setColor(QPalette.ColorRole.ToolTipText, AppColors.TEXT)
        palette.setColor(QPalette.ColorRole.Text, AppColors.TEXT)
        palette.setColor(QPalette.ColorRole.Button, AppColors.PRIMARY)
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.white)

        # Seleção e highlighting
        palette.setColor(QPalette.ColorRole.Highlight, AppColors.PRIMARY)
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Link, AppColors.PRIMARY_DARK)
        palette.setColor(QPalette.ColorRole.LinkVisited, AppColors.PRIMARY)

        # Estados desativados
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, AppColors.TEXT_DISABLED)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, AppColors.TEXT_DISABLED)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, AppColors.TEXT_DISABLED)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor('#f5f5f5'))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor('#e0e0e0'))

        return palette

    @staticmethod
    def configure_header_frame(frame):
        """Configura o frame de cabeçalho com paleta nativa"""
        # Definir paleta para o cabeçalho
        palette = frame.palette()
        palette.setColor(QPalette.ColorRole.Window, AppColors.PRIMARY)
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        frame.setPalette(palette)

        # Configurações visuais
        frame.setAutoFillBackground(True)
        frame.setFixedHeight(70)  # Altura fixa
        frame.setFrameShape(QFrame.Shape.NoFrame)  # Sem borda

    @staticmethod
    def configure_logo_label(label):
        """Configura o label do logo com fonte maior e bold"""
        # Configurar fonte
        font = label.font()
        font.setPointSize(28)
        font.setBold(True)
        label.setFont(font)

        # Configurar cor do texto
        palette = label.palette()
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        label.setPalette(palette)

    @staticmethod
    def configure_footer_frame(frame):
        """Configura o frame de rodapé com altura fixa e cor de fundo"""
        # Definir paleta para o rodapé
        palette = frame.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor('#f5f5f5'))
        frame.setPalette(palette)

        # Configurações visuais
        frame.setAutoFillBackground(True)
        frame.setFixedHeight(30)
        frame.setFrameShape(QFrame.Shape.NoFrame)

    @staticmethod
    def configure_footer_text(label):
        """Configura o texto do rodapé com fonte menor"""
        font = label.font()
        font.setPointSize(9)
        label.setFont(font)

        palette = label.palette()
        palette.setColor(QPalette.ColorRole.WindowText, AppColors.TEXT_LIGHT)
        label.setPalette(palette)

    @staticmethod
    def configure_button(button, style_type='primary'):
        """Configura botões com estilo nativo avançado baseado no tipo"""
        # Configurar fonte em negrito
        font = QFont("Segoe UI", 10)
        font.setBold(True)
        button.setFont(font)

        # Determinar cores baseadas no tipo
        if style_type == 'primary':
            bg_color = AppColors.PRIMARY
            text_color = Qt.GlobalColor.white
            hover_color = AppColors.PRIMARY_DARK
            disabled_bg = AppColors.PRIMARY.lighter(150)
            disabled_text = QColor(255, 255, 255, 150)
        elif style_type == 'success':
            bg_color = AppColors.ACCENT
            text_color = Qt.GlobalColor.white
            hover_color = AppColors.ACCENT_DARK
            disabled_bg = AppColors.ACCENT.lighter(150)
            disabled_text = QColor(255, 255, 255, 150)
        elif style_type == 'warning':
            bg_color = AppColors.WARNING
            text_color = Qt.GlobalColor.white
            hover_color = AppColors.WARNING.darker(120)
            disabled_bg = AppColors.WARNING.lighter(150)
            disabled_text = QColor(255, 255, 255, 150)
        elif style_type == 'info':
            bg_color = AppColors.INFO
            text_color = Qt.GlobalColor.white
            hover_color = AppColors.INFO.darker(120)
            disabled_bg = AppColors.INFO.lighter(150)
            disabled_text = QColor(255, 255, 255, 150)
        elif style_type == 'secondary':
            bg_color = QColor('#f5f5f5')
            text_color = AppColors.TEXT
            hover_color = QColor('#e0e0e0')
            disabled_bg = QColor('#f9f9f9')
            disabled_text = AppColors.TEXT_DISABLED
        else:
            bg_color = AppColors.PRIMARY
            text_color = Qt.GlobalColor.white
            hover_color = AppColors.PRIMARY_DARK
            disabled_bg = AppColors.PRIMARY.lighter(150)
            disabled_text = QColor(255, 255, 255, 150)

        # Aplicar paleta de cores
        palette = button.palette()
        palette.setColor(QPalette.ColorRole.Button, bg_color)
        palette.setColor(QPalette.ColorRole.ButtonText, text_color)

        # Configurar estado desabilitado
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, disabled_bg)
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_text)

        button.setPalette(palette)

        # Configurar padding e bordas sem CSS
        button.setAutoFillBackground(True)
        button.setFlat(False)

        # Configuração de margens internas
        button.setContentsMargins(16, 8, 16, 8)

        # Configurar tamanho mínimo para melhor aparência
        button.setMinimumHeight(36)

        # Remover foco visual padrão
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Para monitorar estados do mouse
        button.enterEvent = lambda e, btn=button, hc=hover_color: StyleManager._button_hover_enter(btn, hc, e)
        button.leaveEvent = lambda e, btn=button, bc=bg_color: StyleManager._button_hover_leave(btn, bc, e)

    @staticmethod
    def _button_hover_enter(button, hover_color, event):
        """Trata evento de mouse entrando no botão"""
        if button.isEnabled():
            palette = button.palette()
            palette.setColor(QPalette.ColorRole.Button, hover_color)
            button.setPalette(palette)

        # Chamar o método original se existir
        try:
            original_method = button.__class__.enterEvent
            if original_method and original_method != StyleManager._button_hover_enter:
                original_method(button, event)
        except Exception:
            pass

    @staticmethod
    def _button_hover_leave(button, original_color, event):
        """Trata evento de mouse saindo do botão"""
        if button.isEnabled():
            palette = button.palette()
            palette.setColor(QPalette.ColorRole.Button, original_color)
            button.setPalette(palette)

        # Chamar o método original se existir
        try:
            original_method = button.__class__.leaveEvent
            if original_method and original_method != StyleManager._button_hover_leave:
                original_method(button, event)
        except Exception:
            pass

    @staticmethod
    def configure_text_edit(text_edit):
        """Configura áreas de texto com paleta nativa"""
        # Definir cores usando paleta
        palette = text_edit.palette()
        palette.setColor(QPalette.ColorRole.Base, AppColors.CARD)
        palette.setColor(QPalette.ColorRole.Text, AppColors.TEXT)
        palette.setColor(QPalette.ColorRole.Highlight, AppColors.PRIMARY)
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        text_edit.setPalette(palette)

        # Configurar borda
        text_edit.setFrameShape(QFrame.Shape.StyledPanel)
        text_edit.setFrameShadow(QFrame.Shadow.Sunken)

        # Configurar margens internas
        text_edit.setContentsMargins(8, 8, 8, 8)

    @staticmethod
    def configure_progress_bar(progress_bar):
        """Configura barra de progresso usando APIs nativas"""
        # Configurações básicas
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(8)

        # Configurar cores via paleta
        palette = progress_bar.palette()
        palette.setColor(QPalette.ColorRole.Highlight, AppColors.PRIMARY)
        palette.setColor(QPalette.ColorRole.Base, QColor('#e0e0e0'))
        progress_bar.setPalette(palette)

    @staticmethod
    def configure_frame(frame, style_type='card'):
        """Configura um QFrame com paleta nativa baseado no tipo"""
        # Configurações de forma
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setFrameShadow(QFrame.Shadow.Raised)

        # Determinar cores baseadas no tipo
        if style_type == 'card':
            bg_color = AppColors.CARD
            text_color = AppColors.TEXT
        elif style_type == 'info':
            bg_color = AppColors.INFO_LIGHT
            text_color = AppColors.TEXT
        elif style_type == 'success':
            bg_color = AppColors.ACCENT_LIGHT
            text_color = AppColors.TEXT
        elif style_type == 'warning':
            bg_color = AppColors.WARNING_LIGHT
            text_color = AppColors.TEXT
        else:
            bg_color = AppColors.CARD
            text_color = AppColors.TEXT

        # Aplicar paleta
        palette = frame.palette()
        palette.setColor(QPalette.ColorRole.Window, bg_color)
        palette.setColor(QPalette.ColorRole.WindowText, text_color)
        frame.setPalette(palette)
        frame.setAutoFillBackground(True)

        # Configurar margens internas
        frame.setContentsMargins(8, 8, 8, 8)

    @staticmethod
    def configure_tab_widget(tab_widget):
        """Configura o widget de abas com aparência nativa"""
        # Configurações básicas
        tab_widget.setDocumentMode(True)
        tab_widget.tabBar().setExpanding(False)

        # Configurar fonte
        font = tab_widget.font()
        font.setPointSize(10)
        font.setBold(True)
        tab_widget.tabBar().setFont(font)

        # Aplicar paleta
        palette = tab_widget.palette()
        palette.setColor(QPalette.ColorRole.Window, AppColors.CARD)
        palette.setColor(QPalette.ColorRole.WindowText, AppColors.TEXT)
        palette.setColor(QPalette.ColorRole.Button, AppColors.BACKGROUND)
        palette.setColor(QPalette.ColorRole.ButtonText, AppColors.TEXT)
        tab_widget.setPalette(palette)

        # Aplicar estilo personalizado para abas
        tab_widget.tabBar().setStyle(TabStyle())

        # Configurar altura das abas
        tab_widget.tabBar().setFixedHeight(36)

        # Configurar espaçamento entre abas
        tab_widget.tabBar().setTabsClosable(False)

    @staticmethod
    def configure_drop_area(widget, report_type="multas"):
        """Configura área de arrastar e soltar sem usar CSS"""
        # Determinar cores baseadas no tipo de relatório
        if report_type == "multas":
            border_color = AppColors.MULTAS_BORDER
            bg_color = AppColors.MULTAS_LIGHT
            text_color = AppColors.MULTAS
        else:
            border_color = AppColors.PENDENCIAS_BORDER
            bg_color = AppColors.PENDENCIAS_LIGHT
            text_color = AppColors.PENDENCIAS

        # Configurar aparência
        palette = widget.palette()
        palette.setColor(QPalette.ColorRole.Window, bg_color)
        palette.setColor(QPalette.ColorRole.WindowText, text_color)
        widget.setPalette(palette)
        widget.setAutoFillBackground(True)

        # Configurar margens e preenchimento
        widget.setContentsMargins(15, 15, 15, 15)

        # Configurar borda - se widget for QFrame ou derivado
        if isinstance(widget, QFrame):
            widget.setFrameShape(QFrame.Shape.Box)
            widget.setFrameShadow(QFrame.Shadow.Plain)

            # Criar caneta para borda pontilhada
            pen = QPen(border_color)
            pen.setStyle(Qt.PenStyle.DashLine)
            pen.setWidth(2)

            # Aplicar estilo manual (se APIs permitirem)
            try:
                widget.setPen(pen)
            except:
                pass

    @staticmethod
    def configure_status_label(label, has_file=False):
        """Configura label de status sem usar CSS"""
        font = label.font()
        font.setBold(True)
        label.setFont(font)

        # Definir cor baseada no status
        palette = label.palette()
        if has_file:
            palette.setColor(QPalette.ColorRole.WindowText, AppColors.ACCENT)
        else:
            palette.setColor(QPalette.ColorRole.WindowText, AppColors.TEXT_LIGHT)
        label.setPalette(palette)

    @staticmethod
    def configure_welcome_text_browser(text_browser):
        """Configura o componente QTextBrowser para a tela de boas-vindas"""
        # Configurar fonte e cores sem CSS
        palette = text_browser.palette()
        palette.setColor(QPalette.ColorRole.Base, AppColors.CARD)
        palette.setColor(QPalette.ColorRole.Text, AppColors.TEXT)
        text_browser.setPalette(palette)

        # Configurar fonte
        font = text_browser.font()
        font.setPointSize(10)
        text_browser.setFont(font)

        # Configurar margens e remover borda
        text_browser.setFrameShape(QFrame.Shape.NoFrame)
        text_browser.setContentsMargins(20, 20, 20, 20)

        # Definir conteúdo HTML simplificado
        text_browser.setHtml(get_welcome_html())

    @staticmethod
    def configure_categories_text_browser(text_browser, categories_data):
        """Configura o componente QTextBrowser para exibir categorias"""
        # Configurar fonte e cores sem CSS
        palette = text_browser.palette()
        palette.setColor(QPalette.ColorRole.Base, AppColors.CARD)
        palette.setColor(QPalette.ColorRole.Text, AppColors.TEXT)
        text_browser.setPalette(palette)

        # Configurar fonte
        font = text_browser.font()
        font.setPointSize(10)
        text_browser.setFont(font)

        # Configurar margens e remover borda
        text_browser.setFrameShape(QFrame.Shape.NoFrame)
        text_browser.setContentsMargins(15, 15, 15, 15)

        # Definir conteúdo HTML simplificado
        text_browser.setHtml(get_categories_html(categories_data))

    @staticmethod
    def configure_header_label(label):
        """Configura um label de cabeçalho com estilo de título"""
        # Configurar fonte
        font = label.font()
        font.setPointSize(18)
        font.setBold(True)
        label.setFont(font)

        # Configurar cor
        palette = label.palette()
        palette.setColor(QPalette.ColorRole.WindowText, AppColors.PRIMARY)
        label.setPalette(palette)

        # Alinhamento
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    @staticmethod
    def configure_subheader_label(label):
        """Configura um label de subcabeçalho"""
        # Configurar fonte
        font = label.font()
        font.setPointSize(12)
        label.setFont(font)

        # Configurar cor
        palette = label.palette()
        palette.setColor(QPalette.ColorRole.WindowText, AppColors.TEXT_LIGHT)
        label.setPalette(palette)

        # Alinhamento
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    @staticmethod
    def configure_radio_group(group_box):
        """Configura um QGroupBox com estilo nativo para grupo de radio buttons"""
        # Configurar fonte do título
        font = group_box.font()
        font.setBold(True)
        font.setPointSize(12)
        group_box.setFont(font)

        # Configurar cores
        palette = group_box.palette()
        palette.setColor(QPalette.ColorRole.WindowText, AppColors.PRIMARY)
        palette.setColor(QPalette.ColorRole.Window, AppColors.CARD)
        group_box.setPalette(palette)

        # Outras configurações
        group_box.setAutoFillBackground(True)

    @staticmethod
    def configure_radio_button(radio_button, style_type='default'):
        """Configura um QRadioButton com estilo nativo"""
        # Configurar fonte
        font = radio_button.font()
        font.setPointSize(11)
        radio_button.setFont(font)

        # Determinar cores baseadas no tipo
        if style_type == 'warning':
            text_color = AppColors.WARNING
        elif style_type == 'info':
            text_color = AppColors.INFO
        elif style_type == 'accent':
            text_color = AppColors.ACCENT
        elif style_type == 'primary':
            text_color = AppColors.PRIMARY
        else:
            text_color = AppColors.TEXT

        # Aplicar paleta
        palette = radio_button.palette()
        palette.setColor(QPalette.ColorRole.WindowText, text_color)
        radio_button.setPalette(palette)

        # Configurar margens
        radio_button.setContentsMargins(5, 5, 5, 5)

    @staticmethod
    def configure_date_check_container(container):
        """Configura o container de verificação de data com estilo nativo"""
        # Configurar cores
        palette = container.palette()
        palette.setColor(QPalette.ColorRole.Window, AppColors.CARD)
        palette.setColor(QPalette.ColorRole.WindowText, AppColors.TEXT)
        container.setPalette(palette)

        # Configurar visual
        container.setAutoFillBackground(True)
        container.setFrameShape(QFrame.Shape.StyledPanel)
        container.setFrameShadow(QFrame.Shadow.Raised)

        # Configurar margens
        container.setContentsMargins(10, 10, 10, 10)

# Funções para compatibilidade com código existente - versões minimalistas
def get_drop_area_style(report_type="multas"):
    """Função legada para compatibilidade"""
    # Esta função deve ser substituída por StyleManager.configure_drop_area
    return ""

def get_status_label_style(has_file=False):
    """Função legada para compatibilidade"""
    # Esta função deve ser substituída por StyleManager.configure_status_label
    return ""

def get_main_styles():
    """Função legada para compatibilidade"""
    # Não é mais necessário usar CSS para estilos principais
    return ""

def get_welcome_html():
    """Retorna HTML formatado para mensagem de boas-vindas sem usar CSS complexo"""
    return """
    <div>
        <h1>Bem-vindo ao Sistema de Cobrança</h1>
        <div>
            <h2>Como usar o sistema:</h2>
            <ol>
                <li>Na aba <strong>Importação</strong>, arraste ou selecione os relatórios</li>
                <li>Clique em <strong>Unificar Relatórios</strong> para processar</li>
                <li>Navegue às demais abas para ver resultados e exportar dados</li>
            </ol>
        </div>
        <p>© 2023 Biblioteca System • v1.0.0</p>
    </div>
    """

def get_categories_html(categories_data):
    """Retorna HTML formatado para categorias sem CSS complexo"""
    rel86_stats = categories_data.get('relatório 86', {})
    rel76_stats = categories_data.get('relatório 76', {})

    html = f"""
    <div>
        <h2>Categorias e Estatísticas</h2>

        <div>
            <h3>Relatório 86 (Multas)</h3>
            <p><strong>Total de registros:</strong> {rel86_stats.get('total_linhas', 0)}</p>
            <p><strong>Valor total de multas:</strong> R$ {rel86_stats.get('total_multas', 0):.2f}</p>
        </div>

        <div>
            <h3>Relatório 76 (Pendências)</h3>
            <p><strong>Total de registros:</strong> {rel76_stats.get('total_linhas', 0)}</p>
        </div>
    </div>
    """
    return html