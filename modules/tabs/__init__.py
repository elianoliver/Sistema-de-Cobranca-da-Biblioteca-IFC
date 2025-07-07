"""
Pacote de módulos para abas da interface gráfica.

Este pacote contém as classes para cada aba da aplicação,
facilitando a modularização e manutenção do código.

Estrutura do pacote:
- base_tab.py: Classe base abstrata que todas as abas herdam
- import_tab.py: Aba de importação de arquivos Excel
- results_tab.py: Aba de exibição de resultados da unificação
- template_tab.py: Aba de configuração de templates de e-mail
- email_tab.py: Aba de envio de emails com templates personalizados

Cada aba implementa sua própria interface gráfica e lógica de
negócios específica, enquanto herda funcionalidades comuns da classe
BaseTab. A comunicação entre as abas é feita através de sinais
(pyqtSignal) que são conectados na interface principal.

O padrão de modularização adotado segue o princípio de
responsabilidade única, onde cada classe é responsável por uma
parte específica da interface e suas funcionalidades.
"""

from modules.tabs.base_tab import BaseTab
from modules.tabs.import_tab import ImportTab
from modules.tabs.results_tab import ResultsTab
from modules.tabs.template_tab import TemplateTab
from modules.tabs.email_tab import EmailTab
from modules.tabs.config_tab import ConfigTab

__all__ = [
    'BaseTab',
    'ImportTab',
    'ResultsTab',
    'TemplateTab',
    'EmailTab',
    'ConfigTab'
]

def setup_tabs(main_interface):
    """
    Configura todas as abas da aplicação e as conecta à interface principal.

    Args:
        main_interface: Referência à interface principal

    Returns:
        Uma lista com instâncias de todas as abas configuradas
    """
    # Instanciar e configurar as abas
    tabs = []

    # Aba de importação
    import_tab = ImportTab(main_interface)
    import_tab.files_loaded.connect(main_interface.handle_files_loaded)
    import_tab.unify_requested.connect(main_interface.unify_reports)
    import_tab.show_message.connect(main_interface.show_message)
    main_interface.tabs.addTab(import_tab, "📤 Importação")
    tabs.append(import_tab)

    # Aba de resultados
    results_tab = ResultsTab(main_interface)
    results_tab.show_message.connect(main_interface.show_message)
    main_interface.tabs.addTab(results_tab, "📊 Resultados")
    tabs.append(results_tab)

    # Aba de templates
    template_tab = TemplateTab(main_interface)
    template_tab.show_message.connect(main_interface.show_message)
    template_tab.templates_updated.connect(main_interface.handle_templates_updated)
    main_interface.tabs.addTab(template_tab, "📝 Templates")
    tabs.append(template_tab)

    # Aba de emails
    email_tab = EmailTab(main_interface)
    email_tab.show_message.connect(main_interface.show_message)
    email_tab.email_sent.connect(lambda count: main_interface.handle_email_sent(count))
    main_interface.tabs.addTab(email_tab, "✉️ Emails")
    tabs.append(email_tab)

    # Aba de Configurações
    config_tab = ConfigTab(main_interface)
    config_tab.show_message.connect(main_interface.show_message)
    config_tab.config_updated.connect(main_interface.handle_config_updated)
    main_interface.tabs.addTab(config_tab, "⚙️ Configurações")
    tabs.append(config_tab)

    return tabs