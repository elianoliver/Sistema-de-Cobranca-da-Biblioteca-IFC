from PyQt6.QtWidgets import (
    QLabel, QVBoxLayout, QWidget, QFrame, QPushButton,
    QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem,
    QProgressBar, QTextEdit, QComboBox, QGroupBox, QCheckBox
)
from PyQt6.QtCore import pyqtSignal, Qt, QDate, QTimer, QThread
import pandas as pd
import re
import json
import os
import datetime
import markdown
from datetime import datetime
import smtplib

from modules.tabs.base_tab import BaseTab
from modules.styles_fix import StyleManager, AppColors
from modules.config_manager import ConfigManager
from modules.data_processor import filter_users_by_category
from modules.email_sender import send_email


class EmailSenderThread(QThread):
    """Thread para envio assíncrono de emails."""
    
    # Sinais para comunicação com a interface principal
    progress_updated = pyqtSignal(int)  # Progresso atual
    email_sent_signal = pyqtSignal(int, str, bool)  # índice, destinatario, sucesso
    finished_signal = pyqtSignal(int, list)  # total_enviados, lista_erros
    
    def __init__(self, users, templates, config, parent=None):
        super().__init__(parent)
        self.users = users
        self.templates = templates
        self.config = config
        self._is_running = True
        self.delay_between_emails = 50  # 50ms entre emails (muito mais rápido)
        
    def run(self):
        """Executa o envio dos emails em background."""
        enviados = 0
        erros = []
        try:
            servidor = smtplib.SMTP('smtp.gmail.com', 587)
            servidor.starttls()
            servidor.login(self.config['remetente'], self.config['senha'])
            for i, user in enumerate(self.users):
                if not self._is_running:
                    break
                try:
                    email_content = self.process_template(user)
                    assunto = self.config['assunto_padrao']
                    destinatario = user['email']
                    ok, msg = send_email(
                        self.config['remetente'],
                        self.config['senha'],
                        destinatario,
                        assunto,
                        email_content,
                        modo_teste=self.config['modo_teste'],
                        destinatario_teste=self.config['destinatario_teste'],
                        servidor=servidor
                    )
                    if ok:
                        enviados += 1
                        self.email_sent_signal.emit(i, destinatario, True)
                    else:
                        erros.append(f"Erro ao enviar para {destinatario}: {msg}")
                        self.email_sent_signal.emit(i, destinatario, False)
                    self.progress_updated.emit(i + 1)
                    if self.delay_between_emails > 0:
                        self.msleep(self.delay_between_emails)
                except Exception as e:
                    error_msg = f"Erro inesperado ao enviar para {user.get('email', 'email não encontrado')}: {str(e)}"
                    erros.append(error_msg)
                    self.email_sent_signal.emit(i, user.get('email', ''), False)
                    self.progress_updated.emit(i + 1)
            servidor.quit()
        except Exception as e:
            erros.append(f'Erro geral: {e}')
        self.finished_signal.emit(enviados, erros)
    
    def stop(self):
        """Para a execução da thread."""
        self._is_running = False
    
    def process_template(self, user_data):
        """Processa o template com os dados do usuário."""
        category = self.get_user_category(user_data)
        if not category or category not in self.templates:
            return None

        template = self.templates[category]

        # Substituir nome (comum a todos os templates)
        template = template.replace("{NOME}", user_data['nome'].upper())

        # Formatação comum dependendo da categoria
        if category in ['apenas_multa', 'multa_e_pendencia']:
            # Substituir valor da multa
            template = template.replace("{VALOR_MULTA}",
                                    f"{user_data['valor_total_multas']:.2f}".replace('.', ','))

        # Template para apenas multa
        if category == 'apenas_multa':
            livros_multa = self.format_multas_text(user_data['multas'])
            template = self.replace_multa_placeholders(template, livros_multa)

        # Template para apenas pendências
        elif category == 'apenas_pendencia':
            livros_pendentes = self.format_pendencias_text(user_data['pendencias'])
            template = self.replace_pendencia_placeholders(template, livros_pendentes)

        # Template para multas e pendências
        elif category == 'multa_e_pendencia':
            # Substituir informações de pendências
            livros_pendentes = self.format_pendencias_text(user_data['pendencias'])
            template = self.replace_pendencia_placeholders(template, livros_pendentes)

            # Substituir informações de multas
            livros_multa = self.format_multas_text(user_data['multas'])
            template = self.replace_multa_placeholders(template, livros_multa)

        # Garantir que as quebras de linha estão normalizadas antes da conversão
        template = self.normalizar_quebras_de_linha(template)

        # Converter Markdown para HTML
        try:
            # Usar a extensão nl2br (newline to <br>) para preservar quebras de linha
            html_content = markdown.markdown(template, extensions=['nl2br'])

            # Adicionar estilos CSS para melhorar a aparência do email
            css_styles = """
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.4;
                    margin: 0;
                    padding: 10px;
                }
                p { margin: 0 0 8px 0; }
                ul { margin: 5px 0; padding-left: 20px; }
                li { margin-bottom: 3px; }
                strong { font-weight: bold; }
                a { color: #0066cc; }
                br { line-height: 1; }
            </style>
            """

            # Garantir que o conteúdo HTML seja renderizado corretamente com espaçamento adequado
            html_content = f"<html><head>{css_styles}</head><body>{html_content}</body></html>"

            return html_content
        except Exception as e:
            print(f"Erro ao converter Markdown para HTML: {e}")
            # Fallback para o template original - substituir todas as quebras de linha por <br>
            return f"<html><body>{template.replace('\n', '<br>')}</body></html>"

    def get_user_category(self, user_data):
        """Determina a categoria do usuário para selecionar o template correto."""
        if not user_data or 'multas' not in user_data or 'pendencias' not in user_data:
            return None

        has_multa = len(user_data['multas']) > 0
        has_pendencia = len(user_data['pendencias']) > 0

        if has_multa and has_pendencia:
            return 'multa_e_pendencia'
        elif has_multa:
            return 'apenas_multa'
        elif has_pendencia:
            return 'apenas_pendencia'
        return None

    def normalizar_quebras_de_linha(self, texto):
        """Normaliza as quebras de linha no texto para garantir compatibilidade."""
        texto = texto.replace('\r\n', '\n')
        texto = texto.replace('\r', '\n')
        return texto

    def format_multas_text(self, multas):
        """Formata o texto das multas para o template."""
        if not multas:
            return "Nenhuma multa encontrada"

        multas_text = []
        for multa in multas:
            titulo = multa.get('titulo', 'Item sem título')

            # Verificação mais rigorosa da data de empréstimo
            data_emp_raw = multa.get('data_emprestimo', '')
            data_emp = 'Data não disponível'

            if data_emp_raw and not pd.isna(data_emp_raw) and data_emp_raw != '':
                data_emp = self.format_date(data_emp_raw)

            # Verificação para data prevista
            data_prev_raw = multa.get('data_prevista', '')
            data_prev = 'Data não disponível'

            if data_prev_raw and not pd.isna(data_prev_raw) and data_prev_raw != '':
                data_prev = self.format_date(data_prev_raw)

            # Verificação para data efetivada
            data_efet_raw = multa.get('data_efetivada', '')
            data_efet = 'Data não disponível'

            if data_efet_raw and not pd.isna(data_efet_raw) and data_efet_raw != '':
                data_efet = self.format_date(data_efet_raw)

            # Se for uma chave e não tiver data efetivada, calcular a data efetivada baseada no valor da multa
            eh_chave = multa.get('eh_chave', False) or 'Chave:' in titulo
            if eh_chave and (not data_efet_raw or pd.isna(data_efet_raw) or data_efet_raw == ''):
                try:
                    # Se tiver data prevista, calcular a data efetivada
                    if data_prev_raw and not pd.isna(data_prev_raw) and data_prev_raw != '':
                        # Converter data prevista para objeto de data
                        if isinstance(data_prev_raw, str):
                            try:
                                data_obj = datetime.strptime(data_prev_raw, "%d/%m/%Y")
                            except ValueError:
                                try:
                                    data_obj = datetime.strptime(data_prev_raw, "%Y-%m-%d")
                                except ValueError:
                                    data_obj = None
                        elif isinstance(data_prev_raw, datetime):
                            data_obj = data_prev_raw
                        else:
                            data_obj = None

                        # Se conseguiu converter, calcular a data efetivada
                        if data_obj:
                            valor_multa = int(multa.get('valor', 1))
                            # Se o valor da multa for 1, adicionar 1 dia
                            if valor_multa == 1:
                                data_devolucao = data_obj + pd.Timedelta(days=1)
                            else:
                                data_devolucao = data_obj + pd.Timedelta(days=valor_multa)
                            data_efet = data_devolucao.strftime("%d/%m/%Y")
                except Exception as e:
                    print(f"Erro ao calcular data efetivada: {e}")

            # Calcular dias de atraso
            dias_atraso = ''

            # Caso seja uma chave, usar o valor da multa diretamente como dias de atraso
            if eh_chave:
                # Para chaves, usar o valor da multa como dias de atraso (R$ 1,00 por dia)
                valor_multa = float(multa.get('valor', 0))
                dias_atraso = str(int(valor_multa))
            # Caso contrário, calcular normalmente pelos dias
            elif data_prev_raw and data_efet_raw and data_efet != 'Data não disponível':
                try:
                    dias_atraso = str(self.calculate_days_difference(data_prev_raw, data_efet_raw))
                except Exception as e:
                    print(f"Erro ao calcular dias de atraso: {e}")

            # Se ainda estiver vazio e temos as duas datas, tenta novamente com as strings formatadas
            if dias_atraso == '' and data_prev != 'Data não disponível' and data_efet != 'Data não disponível':
                try:
                    dias_atraso = str(self.calculate_days_difference(data_prev, data_efet))
                except Exception as e:
                    print(f"Erro no segundo cálculo de dias de atraso: {e}")

            # Se mesmo assim dias_atraso estiver vazio, calcular com as datas convertidas manualmente
            if dias_atraso == '' and data_prev != 'Data não disponível' and data_efet != 'Data não disponível':
                try:
                    # Converter manualmente e garantir o formato correto
                    data_prev_obj = None
                    data_efet_obj = None

                    # Tenta converter data_prev
                    if isinstance(data_prev, str):
                        try:
                            data_prev_obj = datetime.strptime(data_prev, '%d/%m/%Y')
                        except ValueError:
                            pass

                    # Tenta converter data_efet
                    if isinstance(data_efet, str):
                        try:
                            data_efet_obj = datetime.strptime(data_efet, '%d/%m/%Y')
                        except ValueError:
                            pass

                    # Se conseguiu converter ambas, calcula a diferença
                    if data_prev_obj and data_efet_obj:
                        delta = data_efet_obj - data_prev_obj
                        dias_atraso = str(max(0, delta.days))
                except Exception as e:
                    print(f"Erro no terceiro cálculo de dias de atraso: {e}")

            # Se ainda estiver vazio, verificar se existe o campo dias_atraso diretamente no dicionário
            if dias_atraso == '':
                dias_atraso = str(multa.get('dias_atraso', ''))

            # Garantir que não fique vazio mesmo que falhe todo o resto
            if dias_atraso == '':
                # Tenta calcular os dias diretamente do valor da multa, considerando R$1,00 por dia
                valor_multa = float(multa.get('valor', 0))
                if valor_multa > 0:
                    dias_atraso = str(int(valor_multa))  # Considerando R$1,00 por dia
                else:
                    dias_atraso = "0"  # Valor padrão se não conseguir calcular

            # Montar o texto completo para este item no formato Markdown
            item_text = (
                f"**{titulo}**\n"
                f"\t- Data de Empréstimo: {data_emp}\n"
                f"\t- Data de Devolução Prevista: {data_prev}\n"
                f"\t- Data de Devolução Efetiva: {data_efet}\n"
                f"\t- Dias de Atraso: {dias_atraso}"
            )
            multas_text.append(item_text)

        return "- " + "\n\n- ".join(multas_text)

    def format_pendencias_text(self, pendencias):
        """Formata o texto das pendências para o template."""
        if not pendencias:
            return "Nenhuma pendência encontrada"

        pendencias_text = []
        for pendencia in pendencias:
            titulo = pendencia.get('titulo', 'Item sem título')

            # Verificação mais rigorosa da data de empréstimo
            data_emp_raw = pendencia.get('data_emprestimo', '')
            data_emp = 'Data não disponível'

            if data_emp_raw and not pd.isna(data_emp_raw) and data_emp_raw != '':
                data_emp = self.format_date(data_emp_raw)

            # Verificação similar para data prevista
            data_prev_raw = pendencia.get('data_prevista', '')
            data_prev = 'Data não disponível'

            if data_prev_raw and not pd.isna(data_prev_raw) and data_prev_raw != '':
                data_prev = self.format_date(data_prev_raw)

            # Calcular dias de atraso até hoje
            dias_atraso = ''
            if data_prev_raw and not pd.isna(data_prev_raw) and data_prev_raw != '':
                hoje = datetime.now()
                dias_atraso = str(self.calculate_days_difference(data_prev_raw, hoje))

            # Montar o texto completo para este item no formato Markdown
            item_text = (
                f"**{titulo}**\n"
                f"\t- Data de Empréstimo: {data_emp}\n"
                f"\t- Data de Devolução Prevista: {data_prev}\n"
                f"\t- Dias de Atraso: {dias_atraso}"
            )
            pendencias_text.append(item_text)

        return "- " + "\n\n- ".join(pendencias_text)

    def replace_multa_placeholders(self, template, livros_multa):
        """Substitui os placeholders relacionados a multas no template."""
        template = template.replace("{LIVROS_MULTA}", livros_multa)
        template = template.replace("    - Data de Empréstimo: {DATA_EMPRESTIMO}", "")
        template = template.replace("    - Data de Devolução Prevista: {DATA_PREVISTA}", "")
        template = template.replace("    - Data de Devolução Efetiva: {DATA_EFETIVA}", "")
        template = template.replace("    - Dias de Atraso: {DIAS_ATRASO}", "")
        return template

    def replace_pendencia_placeholders(self, template, livros_pendentes):
        """Substitui os placeholders relacionados a pendências no template."""
        template = template.replace("{LIVROS_PENDENTES}", livros_pendentes)
        template = template.replace("    - Data de Empréstimo: {DATA_EMPRESTIMO}", "")
        template = template.replace("    - Data de Devolução Prevista: {DATA_PREVISTA}", "")
        template = template.replace("    - Dias de Atraso: {DIAS_ATRASO}", "")
        return template

    def format_date(self, date_value):
        """Formata uma data para o padrão DD/MM/YYYY."""
        if isinstance(date_value, pd.Timestamp):
            return date_value.strftime('%d/%m/%Y')
        elif isinstance(date_value, datetime) or isinstance(date_value, QDate):
            return date_value.strftime('%d/%m/%Y')
        elif isinstance(date_value, str):
            try:
                date_obj = datetime.strptime(date_value, '%Y-%m-%d')
                return date_obj.strftime('%d/%m/%Y')
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_value, '%d/%m/%Y')
                    return date_value
                except ValueError:
                    return date_value
        return str(date_value)

    def calculate_days_difference(self, date1, date2):
        """Calcula a diferença em dias entre duas datas."""
        if isinstance(date1, str):
            try:
                date1 = datetime.strptime(date1, '%d/%m/%Y')
            except ValueError:
                try:
                    date1 = datetime.strptime(date1, '%Y-%m-%d')
                except ValueError:
                    return 0

        if isinstance(date2, str):
            try:
                date2 = datetime.strptime(date2, '%d/%m/%Y')
            except ValueError:
                try:
                    date2 = datetime.strptime(date2, '%Y-%m-%d')
                except ValueError:
                    return 0

        if not isinstance(date1, datetime):
            if hasattr(date1, 'to_pydatetime'):
                date1 = date1.to_pydatetime()
            else:
                return 0

        if not isinstance(date2, datetime):
            if hasattr(date2, 'to_pydatetime'):
                date2 = date2.to_pydatetime()
            else:
                return 0

        delta = date2 - date1
        return max(0, delta.days)


class EmailTab(BaseTab):
    """Aba para envio de emails usando os templates configurados."""

    # Sinais específicos desta aba
    email_sent = pyqtSignal(int)  # Número de emails enviados

    def __init__(self, parent=None):
        self.config_manager = ConfigManager()
        self.templates = {}
        self.unified_data = None
        self.user_data = {}
        self.filtered_users = []  # Lista de usuários filtrados para navegação
        self.current_preview_index = 0  # Índice do usuário atual no preview
        self.users_without_email = []  # Lista de usuários sem email
        
        # Variáveis para controle de envio em lote
        self.selected_users = []
        self.email_thread = None  # Thread para envio de emails
        
        super().__init__(parent)
        self.load_templates()

    def setup_ui(self):
        """Configura a interface da aba de emails."""
        # Cabeçalho
        header_container = QWidget()
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 10)

        header = QLabel("Envio de Emails")
        StyleManager.configure_header_label(header)
        header_layout.addWidget(header)

        description = QLabel(
            "Envie emails para os usuários com pendências ou multas usando os templates configurados."
        )
        StyleManager.configure_subheader_label(description)
        header_layout.addWidget(description)

        self.layout.addWidget(header_container)

        # Opções de filtro
        filter_group = QGroupBox("Filtros")
        filter_layout = QVBoxLayout(filter_group)

        # Tipo de usuário
        user_type_container = QWidget()
        user_type_layout = QHBoxLayout(user_type_container)
        user_type_layout.setContentsMargins(0, 0, 0, 0)

        user_type_label = QLabel("Tipo de usuário:")
        user_type_layout.addWidget(user_type_label)

        self.user_type_combo = QComboBox()
        self.user_type_combo.addItem("Todos os usuários", "all")
        self.user_type_combo.addItem("Apenas com Multas", "multas")
        self.user_type_combo.addItem("Apenas com Pendências", "pendencias")
        self.user_type_combo.addItem("Com Multas e Pendências", "ambos")
        self.user_type_combo.addItem("Sem Email", "sem_email")
        user_type_layout.addWidget(self.user_type_combo)

        filter_layout.addWidget(user_type_container)

        self.layout.addWidget(filter_group)

        # Preview do email
        preview_group = QGroupBox("Preview do Email")
        preview_layout = QVBoxLayout(preview_group)

        # Adicionar informação do usuário atual
        self.preview_info_label = QLabel("")
        preview_layout.addWidget(self.preview_info_label)

        self.email_preview = QTextEdit()
        self.email_preview.setReadOnly(True)
        self.email_preview.setMinimumHeight(200)
        preview_layout.addWidget(self.email_preview)

        # Botões de navegação
        navigation_container = QWidget()
        navigation_layout = QHBoxLayout(navigation_container)
        navigation_layout.setContentsMargins(0, 10, 0, 0)

        self.prev_button = QPushButton("← Anterior")
        StyleManager.configure_button(self.prev_button, 'secondary')
        self.prev_button.clicked.connect(self.show_previous_preview)
        self.prev_button.setEnabled(False)
        navigation_layout.addWidget(self.prev_button)

        navigation_layout.addStretch()

        self.next_button = QPushButton("Próximo →")
        StyleManager.configure_button(self.next_button, 'secondary')
        self.next_button.clicked.connect(self.show_next_preview)
        self.next_button.setEnabled(False)
        navigation_layout.addWidget(self.next_button)

        preview_layout.addWidget(navigation_container)

        self.layout.addWidget(preview_group)

        # Botões de ação
        actions_container = QFrame()
        actions_layout = QHBoxLayout(actions_container)

        self.preview_button = QPushButton("Gerar Preview")
        StyleManager.configure_button(self.preview_button, 'secondary')
        self.preview_button.clicked.connect(self.generate_preview)
        actions_layout.addWidget(self.preview_button)

        self.test_button = QPushButton("Testar Envio de Email")
        StyleManager.configure_button(self.test_button, 'info')
        self.test_button.clicked.connect(self.test_send_email)
        actions_layout.addWidget(self.test_button)

        self.send_button = QPushButton("Enviar Emails")
        StyleManager.configure_button(self.send_button, 'primary')
        self.send_button.clicked.connect(self.send_emails)
        actions_layout.addWidget(self.send_button)

        self.layout.addWidget(actions_container)

        # Barra de progresso
        progress_container = QFrame()
        progress_layout = QVBoxLayout(progress_container)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        StyleManager.configure_progress_bar(self.progress_bar)
        progress_layout.addWidget(self.progress_bar)

        self.layout.addWidget(progress_container)

    def load_templates(self):
        """Carrega os templates salvos no config.json."""
        try:
            # Se o dicionário de templates já estiver preenchido pelo ExcelInterface, usamos ele diretamente
            # Caso contrário, carregamos do ConfigManager
            if not self.templates:
                self.templates['apenas_multa'] = self.config_manager.get_value('template_apenas_multa', '')
                self.templates['apenas_pendencia'] = self.config_manager.get_value('template_apenas_pendencia', '')
                self.templates['multa_e_pendencia'] = self.config_manager.get_value('template_multa_e_pendencia', '')

            # Limpar o preview atual quando os templates são recarregados
            if hasattr(self, 'email_preview'):
                self.email_preview.clear()
                self.preview_info_label.setText("")

            # Atualizar o preview se houver um usuário selecionado
            if hasattr(self, 'filtered_users') and self.filtered_users and self.current_preview_index < len(self.filtered_users):
                self.show_current_preview()

            # Verificar se os templates foram carregados corretamente
            template_keys = ['apenas_multa', 'apenas_pendencia', 'multa_e_pendencia']
            for key in template_keys:
                if key not in self.templates or not self.templates[key]:
                    print(f"Aviso: Template '{key}' não foi carregado corretamente.")
                else:
                    print(f"Template '{key}' carregado: {len(self.templates[key])} caracteres")
        except Exception as e:
            self.show_message_box("Erro", f"Erro ao carregar templates: {str(e)}", QMessageBox.Icon.Critical)

    def reload_config(self):
        """Recarrega as configurações de email do arquivo de configuração."""
        try:
            # Recarregar templates
            self.load_templates()
            
            # Forçar recarga das configurações de email
            # Usar o método reload_config do ConfigManager
            self.config_manager.reload_config()
            
            # Limpar preview atual
            if hasattr(self, 'email_preview'):
                self.email_preview.clear()
                if hasattr(self, 'preview_info_label'):
                    self.preview_info_label.setText("")
            
            # Log para debug - verificar se as configurações foram recarregadas
            destinatario_teste_raw = self.config_manager.get_value('email_destinatario_padrao', '')
            remetente = self.config_manager.get_value('email_remetente', '')
            destinatario_teste = destinatario_teste_raw if destinatario_teste_raw.strip() else remetente
            modo_teste = self.config_manager.get_value('modo_teste', True)
            print(f"Configurações recarregadas - Destinatário de teste: {destinatario_teste}, Modo teste: {modo_teste}")
            
            # Log específico para verificar o campo email_destinatario_padrao
            print(f"  - email_destinatario_padrao (raw): '{destinatario_teste_raw}'")
            print(f"  - email_destinatario_padrao (com fallback): '{destinatario_teste}'")
            print(f"  - Usando fallback: {destinatario_teste_raw.strip() == ''}")
            
            print("Configurações de email recarregadas com sucesso.")
        except Exception as e:
            print(f"Erro ao recarregar configurações: {e}")

    def update_data(self, unified_data=None):
        """Atualiza os dados exibidos na aba."""
        if unified_data is not None:
            self.unified_data = unified_data
            self.process_user_data()

    def process_user_data(self):
        """Processa os dados dos usuários a partir do dataframe unificado."""
        if self.unified_data is None or self.unified_data.empty:
            return

        # Verificar e imprimir as colunas disponíveis para depuração
        if not hasattr(self, '_printed_columns'):
            print("Colunas disponíveis no DataFrame unificado:", self.unified_data.columns.tolist())

            # Verificar se há registros rel76 e imprimir suas colunas
            rel76_df = self.unified_data[self.unified_data['Relatório'] == 'rel76']
            if not rel76_df.empty:
                print("Número de registros rel76:", len(rel76_df))
                print("Colunas no relatório de pendências (rel76):", rel76_df.columns.tolist())
                # Imprimir o primeiro registro para ver os dados
                if len(rel76_df) > 0:
                    print("Exemplo de registro rel76:")
                    print(rel76_df.iloc[0])

            self._printed_columns = True  # Para imprimir apenas uma vez

        # Primeiro agrupamos por código de pessoa
        temp_user_data = {}
        self.users_without_email = []  # Lista de usuários sem email

        # Passo 1: Agrupar por código de pessoa primeiro (para organização interna)
        for _, row in self.unified_data.iterrows():
            codigo = str(row.get('Código da pessoa', ''))
            if not codigo or pd.isna(codigo):
                continue

            nome = row.get('Nome da pessoa', '')
            if pd.isna(nome):
                nome = ''

            email = row.get('Email', '')
            if pd.isna(email):
                email = ''

            # Criar ou atualizar registro do usuário
            if codigo not in temp_user_data:
                temp_user_data[codigo] = {
                    'codigo': codigo,
                    'nome': nome,
                    'email': email.strip().lower(),  # Normalizar email para agrupar corretamente
                    'multas': [],
                    'pendencias': [],
                    'valor_total_multas': 0.0
                }
                # NOVO: se não tem email, adiciona na lista
                if email.strip() == '':
                    self.users_without_email.append({'codigo': codigo, 'nome': nome})

            # Se for multa (rel86)
            relatorio = row.get('Relatório', '')
            if relatorio == 'rel86':
                titulo = row.get('Título', '')
                valor = row.get('Valor multa', 0.0)
                if pd.isna(valor):
                    valor = 0.0

                data_emprestimo = row.get('Data de empréstimo', '')
                data_prevista = row.get('Data devolução prevista', '')
                data_efetivada = row.get('Data devolução efetivada', '')

                temp_user_data[codigo]['multas'].append({
                    'titulo': titulo,
                    'valor': valor,
                    'data_emprestimo': data_emprestimo,
                    'data_prevista': data_prevista,
                    'data_efetivada': data_efetivada
                })

                temp_user_data[codigo]['valor_total_multas'] += valor

            # Se for pendência (rel76)
            elif relatorio == 'rel76':
                titulo = row.get('Título', '')

                # Usar o nome correto da coluna conforme identificado na saída de depuração
                data_emprestimo = row.get('Data de empréstimo', '')
                data_prevista = row.get('Data devolução prevista', '')

                temp_user_data[codigo]['pendencias'].append({
                    'titulo': titulo,
                    'data_emprestimo': data_emprestimo,
                    'data_prevista': data_prevista
                })

        # Passo 2: Agrupar por email
        # Se uma pessoa tiver várias contas/códigos mas o mesmo email,
        # consolidamos para enviar apenas um email
        email_grouped_data = {}

        for usuario in temp_user_data.values():
            email = usuario['email']
            if not email:  # Pular usuários sem email
                continue

            # Criar registro do email se não existir
            if email not in email_grouped_data:
                email_grouped_data[email] = {
                    'email': email,
                    'nome': usuario['nome'],  # Usamos o nome do primeiro usuário encontrado com este email
                    'codigos': [],
                    'multas': [],
                    'pendencias': [],
                    'valor_total_multas': 0.0
                }

            # Adicionar o código da pessoa à lista de códigos
            email_grouped_data[email]['codigos'].append(usuario['codigo'])

            # Adicionar multas
            for multa in usuario['multas']:
                email_grouped_data[email]['multas'].append(multa)

            # Adicionar pendências
            for pendencia in usuario['pendencias']:
                email_grouped_data[email]['pendencias'].append(pendencia)

            # Somar o valor total de multas
            email_grouped_data[email]['valor_total_multas'] += usuario['valor_total_multas']

        # Atribuir os dados agrupados por email à variável principal
        self.user_data = email_grouped_data

    def get_user_category(self, user_data):
        """Determina a categoria do usuário para selecionar o template correto."""
        # Verificar se o usuário tem dados válidos
        if not user_data or 'multas' not in user_data or 'pendencias' not in user_data:
            return None

        has_multa = len(user_data['multas']) > 0
        has_pendencia = len(user_data['pendencias']) > 0

        if has_multa and has_pendencia:
            return 'multa_e_pendencia'
        elif has_multa:
            return 'apenas_multa'
        elif has_pendencia:
            return 'apenas_pendencia'
        return None  # Categoria não definida

    def process_template(self, user_data):
        """Processa o template com os dados do usuário."""
        category = self.get_user_category(user_data)
        if not category or category not in self.templates:
            return None

        template = self.templates[category]

        # Substituir nome (comum a todos os templates)
        template = template.replace("{NOME}", user_data['nome'].upper())

        # Formatação comum dependendo da categoria
        if category in ['apenas_multa', 'multa_e_pendencia']:
            # Substituir valor da multa
            template = template.replace("{VALOR_MULTA}",
                                    f"{user_data['valor_total_multas']:.2f}".replace('.', ','))

        # Template para apenas multa
        if category == 'apenas_multa':
            livros_multa = self.format_multas_text(user_data['multas'])
            template = self.replace_multa_placeholders(template, livros_multa)

        # Template para apenas pendências
        elif category == 'apenas_pendencia':
            livros_pendentes = self.format_pendencias_text(user_data['pendencias'])
            template = self.replace_pendencia_placeholders(template, livros_pendentes)

        # Template para multas e pendências
        elif category == 'multa_e_pendencia':
            # Substituir informações de pendências
            livros_pendentes = self.format_pendencias_text(user_data['pendencias'])
            template = self.replace_pendencia_placeholders(template, livros_pendentes)

            # Substituir informações de multas
            livros_multa = self.format_multas_text(user_data['multas'])
            template = self.replace_multa_placeholders(template, livros_multa)

        # Garantir que as quebras de linha estão normalizadas antes da conversão
        template = self.normalizar_quebras_de_linha(template)

        # Converter Markdown para HTML
        try:
            # Usar a extensão nl2br (newline to <br>) para preservar quebras de linha
            html_content = markdown.markdown(template, extensions=['nl2br'])

            # Adicionar estilos CSS para melhorar a aparência do email
            css_styles = """
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.4;
                    margin: 0;
                    padding: 10px;
                }
                p { margin: 0 0 8px 0; }
                ul { margin: 5px 0; padding-left: 20px; }
                li { margin-bottom: 3px; }
                strong { font-weight: bold; }
                a { color: #0066cc; }
                br { line-height: 1; }
            </style>
            """

            # Garantir que o conteúdo HTML seja renderizado corretamente com espaçamento adequado
            html_content = f"<html><head>{css_styles}</head><body>{html_content}</body></html>"

            return html_content
        except Exception as e:
            print(f"Erro ao converter Markdown para HTML: {e}")
            # Fallback para o template original - substituir todas as quebras de linha por <br>
            return f"<html><body>{template.replace('\n', '<br>')}</body></html>"

    def normalizar_quebras_de_linha(self, texto):
        """Normaliza as quebras de linha no texto para garantir compatibilidade."""
        texto = texto.replace('\r\n', '\n')
        texto = texto.replace('\r', '\n')
        return texto

    def format_multas_text(self, multas):
        """Formata o texto das multas para o template."""
        if not multas:
            return "Nenhuma multa encontrada"

        multas_text = []
        for multa in multas:
            titulo = multa.get('titulo', 'Item sem título')

            # Verificação mais rigorosa da data de empréstimo
            data_emp_raw = multa.get('data_emprestimo', '')
            data_emp = 'Data não disponível'

            if data_emp_raw and not pd.isna(data_emp_raw) and data_emp_raw != '':
                data_emp = self.format_date(data_emp_raw)

            # Verificação para data prevista
            data_prev_raw = multa.get('data_prevista', '')
            data_prev = 'Data não disponível'

            if data_prev_raw and not pd.isna(data_prev_raw) and data_prev_raw != '':
                data_prev = self.format_date(data_prev_raw)

            # Verificação para data efetivada
            data_efet_raw = multa.get('data_efetivada', '')
            data_efet = 'Data não disponível'

            if data_efet_raw and not pd.isna(data_efet_raw) and data_efet_raw != '':
                data_efet = self.format_date(data_efet_raw)

            # Se for uma chave e não tiver data efetivada, calcular a data efetivada baseada no valor da multa
            eh_chave = multa.get('eh_chave', False) or 'Chave:' in titulo
            if eh_chave and (not data_efet_raw or pd.isna(data_efet_raw) or data_efet_raw == ''):
                try:
                    # Se tiver data prevista, calcular a data efetivada
                    if data_prev_raw and not pd.isna(data_prev_raw) and data_prev_raw != '':
                        # Converter data prevista para objeto de data
                        if isinstance(data_prev_raw, str):
                            try:
                                data_obj = datetime.strptime(data_prev_raw, "%d/%m/%Y")
                            except ValueError:
                                try:
                                    data_obj = datetime.strptime(data_prev_raw, "%Y-%m-%d")
                                except ValueError:
                                    data_obj = None
                        elif isinstance(data_prev_raw, datetime):
                            data_obj = data_prev_raw
                        else:
                            data_obj = None

                        # Se conseguiu converter, calcular a data efetivada
                        if data_obj:
                            valor_multa = int(multa.get('valor', 1))
                            # Se o valor da multa for 1, adicionar 1 dia
                            if valor_multa == 1:
                                data_devolucao = data_obj + pd.Timedelta(days=1)
                            else:
                                data_devolucao = data_obj + pd.Timedelta(days=valor_multa)
                            data_efet = data_devolucao.strftime("%d/%m/%Y")
                except Exception as e:
                    print(f"Erro ao calcular data efetivada: {e}")

            # Calcular dias de atraso
            dias_atraso = ''

            # Caso seja uma chave, usar o valor da multa diretamente como dias de atraso
            if eh_chave:
                # Para chaves, usar o valor da multa como dias de atraso (R$ 1,00 por dia)
                valor_multa = float(multa.get('valor', 0))
                dias_atraso = str(int(valor_multa))
            # Caso contrário, calcular normalmente pelos dias
            elif data_prev_raw and data_efet_raw and data_efet != 'Data não disponível':
                try:
                    dias_atraso = str(self.calculate_days_difference(data_prev_raw, data_efet_raw))
                except Exception as e:
                    print(f"Erro ao calcular dias de atraso: {e}")

            # Se ainda estiver vazio e temos as duas datas, tenta novamente com as strings formatadas
            if dias_atraso == '' and data_prev != 'Data não disponível' and data_efet != 'Data não disponível':
                try:
                    dias_atraso = str(self.calculate_days_difference(data_prev, data_efet))
                except Exception as e:
                    print(f"Erro no segundo cálculo de dias de atraso: {e}")

            # Se mesmo assim dias_atraso estiver vazio, calcular com as datas convertidas manualmente
            if dias_atraso == '' and data_prev != 'Data não disponível' and data_efet != 'Data não disponível':
                try:
                    # Converter manualmente e garantir o formato correto
                    data_prev_obj = None
                    data_efet_obj = None

                    # Tenta converter data_prev
                    if isinstance(data_prev, str):
                        try:
                            data_prev_obj = datetime.strptime(data_prev, '%d/%m/%Y')
                        except ValueError:
                            pass

                    # Tenta converter data_efet
                    if isinstance(data_efet, str):
                        try:
                            data_efet_obj = datetime.strptime(data_efet, '%d/%m/%Y')
                        except ValueError:
                            pass

                    # Se conseguiu converter ambas, calcula a diferença
                    if data_prev_obj and data_efet_obj:
                        delta = data_efet_obj - data_prev_obj
                        dias_atraso = str(max(0, delta.days))
                except Exception as e:
                    print(f"Erro no terceiro cálculo de dias de atraso: {e}")

            # Se ainda estiver vazio, verificar se existe o campo dias_atraso diretamente no dicionário
            if dias_atraso == '':
                dias_atraso = str(multa.get('dias_atraso', ''))

            # Garantir que não fique vazio mesmo que falhe todo o resto
            if dias_atraso == '':
                # Tenta calcular os dias diretamente do valor da multa, considerando R$1,00 por dia
                valor_multa = float(multa.get('valor', 0))
                if valor_multa > 0:
                    dias_atraso = str(int(valor_multa))  # Considerando R$1,00 por dia
                else:
                    dias_atraso = "0"  # Valor padrão se não conseguir calcular

            # Montar o texto completo para este item no formato Markdown
            item_text = (
                f"**{titulo}**\n"
                f"\t- Data de Empréstimo: {data_emp}\n"
                f"\t- Data de Devolução Prevista: {data_prev}\n"
                f"\t- Data de Devolução Efetiva: {data_efet}\n"
                f"\t- Dias de Atraso: {dias_atraso}"
            )
            multas_text.append(item_text)

        return "- " + "\n\n- ".join(multas_text)

    def format_pendencias_text(self, pendencias):
        """Formata o texto das pendências para o template."""
        if not pendencias:
            return "Nenhuma pendência encontrada"

        pendencias_text = []
        for pendencia in pendencias:
            titulo = pendencia.get('titulo', 'Item sem título')

            # Verificação mais rigorosa da data de empréstimo
            data_emp_raw = pendencia.get('data_emprestimo', '')
            data_emp = 'Data não disponível'

            if data_emp_raw and not pd.isna(data_emp_raw) and data_emp_raw != '':
                data_emp = self.format_date(data_emp_raw)

            # Verificação similar para data prevista
            data_prev_raw = pendencia.get('data_prevista', '')
            data_prev = 'Data não disponível'

            if data_prev_raw and not pd.isna(data_prev_raw) and data_prev_raw != '':
                data_prev = self.format_date(data_prev_raw)

            # Calcular dias de atraso até hoje
            dias_atraso = ''
            if data_prev_raw and not pd.isna(data_prev_raw) and data_prev_raw != '':
                hoje = datetime.now()
                dias_atraso = str(self.calculate_days_difference(data_prev_raw, hoje))

            # Montar o texto completo para este item no formato Markdown
            item_text = (
                f"**{titulo}**\n"
                f"\t- Data de Empréstimo: {data_emp}\n"
                f"\t- Data de Devolução Prevista: {data_prev}\n"
                f"\t- Dias de Atraso: {dias_atraso}"
            )
            pendencias_text.append(item_text)

        return "- " + "\n\n- ".join(pendencias_text)

    def replace_multa_placeholders(self, template, livros_multa):
        """Substitui os placeholders relacionados a multas no template."""
        template = template.replace("{LIVROS_MULTA}", livros_multa)
        template = template.replace("    - Data de Empréstimo: {DATA_EMPRESTIMO}", "")
        template = template.replace("    - Data de Devolução Prevista: {DATA_PREVISTA}", "")
        template = template.replace("    - Data de Devolução Efetiva: {DATA_EFETIVA}", "")
        template = template.replace("    - Dias de Atraso: {DIAS_ATRASO}", "")
        return template

    def replace_pendencia_placeholders(self, template, livros_pendentes):
        """Substitui os placeholders relacionados a pendências no template."""
        template = template.replace("{LIVROS_PENDENTES}", livros_pendentes)
        template = template.replace("    - Data de Empréstimo: {DATA_EMPRESTIMO}", "")
        template = template.replace("    - Data de Devolução Prevista: {DATA_PREVISTA}", "")
        template = template.replace("    - Dias de Atraso: {DIAS_ATRASO}", "")
        return template

    def format_date(self, date_value):
        """Formata uma data para o padrão DD/MM/YYYY."""
        if isinstance(date_value, pd.Timestamp):
            return date_value.strftime('%d/%m/%Y')
        elif isinstance(date_value, datetime) or isinstance(date_value, QDate):
            return date_value.strftime('%d/%m/%Y')
        elif isinstance(date_value, str):
            try:
                date_obj = datetime.strptime(date_value, '%Y-%m-%d')
                return date_obj.strftime('%d/%m/%Y')
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_value, '%d/%m/%Y')
                    return date_value
                except ValueError:
                    return date_value
        return str(date_value)

    def calculate_days_difference(self, date1, date2):
        """Calcula a diferença em dias entre duas datas."""
        if isinstance(date1, str):
            try:
                date1 = datetime.strptime(date1, '%d/%m/%Y')
            except ValueError:
                try:
                    date1 = datetime.strptime(date1, '%Y-%m-%d')
                except ValueError:
                    return 0

        if isinstance(date2, str):
            try:
                date2 = datetime.strptime(date2, '%d/%m/%Y')
            except ValueError:
                try:
                    date2 = datetime.strptime(date2, '%Y-%m-%d')
                except ValueError:
                    return 0

        if not isinstance(date1, datetime):
            if hasattr(date1, 'to_pydatetime'):
                date1 = date1.to_pydatetime()
            else:
                return 0

        if not isinstance(date2, datetime):
            if hasattr(date2, 'to_pydatetime'):
                date2 = date2.to_pydatetime()
            else:
                return 0

        delta = date2 - date1
        return max(0, delta.days)

    def generate_preview(self):
        """Gera um preview do email para o usuário selecionado."""
        if not self.user_data and not hasattr(self, 'users_without_email'):
            self.show_message_box(
                "Aviso",
                "Não há dados de usuários para gerar preview. Carregue os dados primeiro.",
                QMessageBox.Icon.Warning
            )
            return

        # Pegar os filtros
        user_type = self.user_type_combo.currentData()

        # Filtrar usuários
        self.filtered_users = []

        if user_type == 'sem_email':
            # Mostrar lista de usuários sem email
            self.filtered_users = self.users_without_email.copy() if hasattr(self, 'users_without_email') else []
        else:
            # Filtrar os usuários de acordo com o tipo selecionado
            for email, user in self.user_data.items():
                # Verificar se corresponde ao tipo selecionado
                category = self.get_user_category(user)
                if user_type != 'all':
                    if (user_type == 'multas' and category != 'apenas_multa') or \
                       (user_type == 'pendencias' and category != 'apenas_pendencia') or \
                       (user_type == 'ambos' and category != 'multa_e_pendencia'):
                        continue

                self.filtered_users.append(user)

        if not self.filtered_users:
            self.show_message_box(
                "Aviso",
                "Não foi encontrado nenhum usuário que atenda aos filtros para gerar o preview.",
                QMessageBox.Icon.Warning
            )
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            return

        # Resetar o índice e mostrar o primeiro usuário
        self.current_preview_index = 0
        self.show_current_preview()

        # Atualizar estado dos botões de navegação
        self.update_navigation_buttons()

    def show_current_preview(self):
        """Mostra o preview do usuário atual."""
        if not self.filtered_users or self.current_preview_index >= len(self.filtered_users):
            return

        user_type = self.user_type_combo.currentData() if hasattr(self, 'user_type_combo') else None

        if user_type == 'sem_email':
            # Exibir todas as pessoas sem email de uma vez
            self.preview_info_label.setText(
                f"Total de {len(self.filtered_users)} pessoas sem email cadastrado"
            )
            
            # Formatar a lista de todas as pessoas sem email
            users_text = "Pessoas sem email cadastrado:\n\n"
            for i, user in enumerate(self.filtered_users, 1):
                users_text += f"{i:3d}. Matrícula: {user['codigo']:<10} | Nome: {user['nome']}\n"
            
            self.email_preview.setPlainText(users_text)
            
            # Desabilitar botões de navegação para pessoas sem email
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
        else:
            current_user = self.filtered_users[self.current_preview_index]
            
            # Atualizar o rótulo de informação
            self.preview_info_label.setText(
                f"Visualizando usuário {self.current_preview_index + 1} de {len(self.filtered_users)}: "
                f"{current_user['nome']} ({current_user['email']})"
            )

            # Processar template
            preview_html = self.process_template(current_user)
            if preview_html:
                self.email_preview.setHtml(preview_html)
            else:
                self.email_preview.setPlainText("Não foi possível gerar o preview. Verifique se os templates estão configurados corretamente.")

    def show_next_preview(self):
        """Mostra o próximo usuário na lista filtrada."""
        if self.current_preview_index < len(self.filtered_users) - 1:
            self.current_preview_index += 1
            self.show_current_preview()
            self.update_navigation_buttons()

    def show_previous_preview(self):
        """Mostra o usuário anterior na lista filtrada."""
        if self.current_preview_index > 0:
            self.current_preview_index -= 1
            self.show_current_preview()
            self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """Atualiza o estado dos botões de navegação."""
        user_type = self.user_type_combo.currentData() if hasattr(self, 'user_type_combo') else None
        
        if user_type == 'sem_email':
            # Para pessoas sem email, não precisamos de navegação
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
        else:
            # Habilitar/desabilitar botão anterior
            self.prev_button.setEnabled(self.current_preview_index > 0)

            # Habilitar/desabilitar botão próximo
            self.next_button.setEnabled(self.current_preview_index < len(self.filtered_users) - 1)

    def send_emails(self):
        """Envia emails para os usuários que atendem aos critérios selecionados."""
        if not self.user_data:
            self.show_message_box(
                "Aviso",
                "Não há dados de usuários para enviar emails. Carregue os dados primeiro.",
                QMessageBox.Icon.Warning
            )
            return

        # Configurações de e-mail
        remetente = self.config_manager.get_value('email_remetente', '')
        senha = self.config_manager.get_value('email_senha_app', '')
        
        # Carregar destinatário de teste - se estiver vazio, usar o remetente como fallback
        destinatario_teste_raw = self.config_manager.get_value('email_destinatario_padrao', '')
        destinatario_teste = destinatario_teste_raw if destinatario_teste_raw.strip() else remetente
        
        assunto_padrao = self.config_manager.get_value('email_assunto_padrao', 'Notificação da Biblioteca')
        modo_teste = self.config_manager.get_value('modo_teste', True)

        # Log para debug - verificar quais valores estão sendo carregados
        print(f"DEBUG - Configurações carregadas no send_emails:")
        print(f"  - Remetente: {remetente}")
        print(f"  - Destinatário de teste: {destinatario_teste}")
        print(f"  - Modo teste: {modo_teste}")
        print(f"  - Assunto padrão: {assunto_padrao}")
        
        # Log específico para verificar o campo email_destinatario_padrao
        print(f"  - email_destinatario_padrao (raw): '{destinatario_teste_raw}'")
        print(f"  - email_destinatario_padrao (com fallback): '{destinatario_teste}'")
        print(f"  - Usando fallback: {destinatario_teste_raw.strip() == ''}")

        if not remetente or not senha:
            self.show_message_box(
                "Configuração de Email",
                "Configure o e-mail do remetente e a senha de app nas configurações.",
                QMessageBox.Icon.Warning
            )
            return

        # Pegar os filtros
        user_type = self.user_type_combo.currentData()

        # Filtrar usuários
        self.selected_users = []
        for email, user in self.user_data.items():
            category = self.get_user_category(user)
            if user_type != 'all':
                if (user_type == 'multas' and category != 'apenas_multa') or \
                   (user_type == 'pendencias' and category != 'apenas_pendencia') or \
                   (user_type == 'ambos' and category != 'multa_e_pendencia'):
                    continue
            self.selected_users.append(user)

        if not self.selected_users:
            self.show_message_box(
                "Aviso",
                "Não foi encontrado nenhum usuário que atenda aos filtros para enviar emails.",
                QMessageBox.Icon.Warning
            )
            return

        confirm_text = (
            f"Você está prestes a enviar emails para {len(self.selected_users)} usuários.\n\n"
            f"O MODO DE TESTE está {'ATIVADO' if modo_teste else 'DESATIVADO'}.\n"
        )
        if modo_teste:
            confirm_text += f"Todos os emails serão enviados para: {destinatario_teste}."
        else:
            confirm_text += "Os emails serão enviados para os destinatários REAIS."

        confirm = QMessageBox.question(
            self,
            "Confirmar Envio",
            confirm_text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.No:
            return

        # Criar e configurar a thread de envio
        self.email_thread = EmailSenderThread(self.selected_users, self.templates, {
            'remetente': remetente,
            'senha': senha,
            'destinatario_teste': destinatario_teste,
            'assunto_padrao': assunto_padrao,
            'modo_teste': modo_teste
        }, self)
        
        # Conectar sinais da thread
        self.email_thread.progress_updated.connect(self.update_progress)
        self.email_thread.email_sent_signal.connect(self.on_email_sent)
        self.email_thread.finished_signal.connect(self.on_email_finished)
        
        # Configurar barra de progresso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(self.selected_users))
        
        # Desabilitar botões durante o envio
        self.send_button.setEnabled(False)
        self.test_button.setEnabled(False)
        self.preview_button.setEnabled(False)
        
        # Iniciar a thread
        self.email_thread.start()

    def update_progress(self, value):
        """Atualiza a barra de progresso."""
        self.progress_bar.setValue(value)

    def on_email_sent(self, index, destinatario, success):
        """Chamado quando um email é enviado (sucesso ou erro)."""
        # Aqui você pode adicionar logs ou atualizações em tempo real se desejar
        pass

    def on_email_finished(self, total_enviados, erros):
        """Chamado quando todos os emails foram processados."""
        # Parar a thread
        if self.email_thread:
            self.email_thread.stop()
            self.email_thread.wait()  # Aguardar a thread terminar
            self.email_thread = None
        
        # Reabilitar botões
        self.send_button.setEnabled(True)
        self.test_button.setEnabled(True)
        self.preview_button.setEnabled(True)
        
        # Ocultar barra de progresso
        self.progress_bar.setVisible(False)
        
        # Mostrar resumo
        resumo = f"Foram enviados {total_enviados} emails."
        if self.config_manager.get_value('modo_teste', True):
            resumo += " (Modo de Teste)"

        if erros:
            resumo += f"\n\nOcorreram erros em {len(erros)} envios:\n" + "\n".join(erros[:5])  # Mostrar apenas os primeiros 5 erros
            if len(erros) > 5:
                resumo += f"\n... e mais {len(erros) - 5} erros."
        
        self.show_message_box(
            "Envio de Emails Concluído",
            resumo,
            QMessageBox.Icon.Information if total_enviados > 0 else QMessageBox.Icon.Warning
        )
        
        # Emitir sinal
        self.email_sent.emit(total_enviados)

    def test_send_email(self):
        """Envia um e-mail de teste para o destinatário de teste."""
        remetente = self.config_manager.get_value('email_remetente', '')
        senha = self.config_manager.get_value('email_senha_app', '')
        
        # Carregar destinatário de teste - se estiver vazio, usar o remetente como fallback
        destinatario_teste_raw = self.config_manager.get_value('email_destinatario_padrao', '')
        destinatario_teste = destinatario_teste_raw if destinatario_teste_raw.strip() else remetente
        
        assunto = "Teste de Email do Sistema Biblioteca"
        corpo = "<b>Este é um teste de envio de e-mail do sistema Biblioteca.</b><br>Se você recebeu este e-mail, a configuração está correta."
        
        # Log para debug - verificar quais valores estão sendo carregados
        print(f"DEBUG - Configurações carregadas no test_send_email:")
        print(f"  - Remetente: {remetente}")
        print(f"  - Destinatário de teste: {destinatario_teste}")
        
        # Log específico para verificar o campo email_destinatario_padrao
        print(f"  - email_destinatario_padrao (raw): '{destinatario_teste_raw}'")
        print(f"  - email_destinatario_padrao (com fallback): '{destinatario_teste}'")

        if not remetente or not senha:
            self.show_message_box(
                "Configuração de Email",
                "Configure o e-mail do remetente e a senha de app nas configurações.",
                QMessageBox.Icon.Warning
            )
            return
        ok, msg = send_email(remetente, senha, destinatario_teste, assunto, corpo, modo_teste=True, destinatario_teste=destinatario_teste)
        if ok:
            self.show_message_box("Teste de Email", f"Email de teste enviado para {destinatario_teste}.", QMessageBox.Icon.Information)
        else:
            self.show_message_box("Erro no Teste de Email", msg, QMessageBox.Icon.Critical)