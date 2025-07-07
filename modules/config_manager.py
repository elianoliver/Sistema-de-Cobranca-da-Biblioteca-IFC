"""
Gerenciador de configurações da aplicação.

Este módulo contém a classe ConfigManager responsável por carregar,
salvar e gerenciar as configurações da aplicação.
"""

import os
import json

class ConfigManager:
    """Gerencia a configuração da aplicação usando um arquivo JSON"""
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self):
        """Carrega a configuração do arquivo ou cria uma nova se não existir"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar configuração: {e}")
                return self._create_default_config()
        else:
            return self._create_default_config()

    def _save_config(self, config=None):
        """Salva a configuração no arquivo"""
        if config is None:
            config = self.config
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")

    def get_value(self, key, default=None):
        """Obtém um valor da configuração"""
        return self.config.get(key, default)

    def set_value(self, key, value):
        """Define um valor na configuração"""
        self.config[key] = value
        self._save_config()

    def reload_config(self):
        """Força a recarga das configurações do arquivo"""
        self.config = self._load_config()

    def _create_default_config(self):
        """Cria uma configuração padrão"""
        default_config = {
            'template_apenas_multa': '**Prezado(a) {NOME}**,\n\nConforme estabelecido no [Regulamento Interno das Bibliotecas do Instituto Federal Catarinense](https://biblioteca.ifc.edu.br/wp-content/uploads/sites/53/2023/04/SIBI-Regulamento.pdf), artigo 44, é nossa responsabilidade notificá-lo(a) sobre as pendências em sua conta de usuário na biblioteca.\n\nConstata-se a existência de multa acumulada no valor total de **R$ {VALOR_MULTA}**. referente ao(s) seguinte(s) item(ns):\n\n{LIVROS_MULTA}\n\nSalientamos que, para renovar ou realizar novos empréstimos, as multas devem estar abaixo de R$ 10,00. No entanto, para emitir a Declaração de Nada Consta, é necessário que todas as multas e pendências na biblioteca sejam totalmente quitadas.\n\n**Em caso de perda do material emprestado, deverá ser informado e proceder com a reposição do mesmo.**\n\nRegularize sua situação com a biblioteca o mais breve possível, para juntos, mantermos funcionando de forma eficiente e acessível para toda a comunidade acadêmica.\n\nEstamos à disposição para esclarecer dúvidas, ou para mais informações.\n\nAtenciosamente,',
            'template_apenas_pendencia': '**Prezado(a) {NOME}**,\n\nConforme estabelecido no [Regulamento Interno das Bibliotecas do Instituto Federal Catarinense](https://biblioteca.ifc.edu.br/wp-content/uploads/sites/53/2023/04/SIBI-Regulamento.pdf), artigo 44, é nossa responsabilidade notificá-lo(a) sobre as pendências em sua conta de usuário na biblioteca.\n\nDe acordo com os registros em nosso sistema, observamos que você possui o(s) seguinte(s) item(ns) em atraso:\n\n{LIVROS_PENDENTES}\n\nConforme o artigo 44, Inciso I, do Regulamento, informamos que a multa aplicada é de R$ 1,00 (um real) por dia útil de atraso para cada material emprestado.\n\nSalientamos que, para renovar ou realizar novos empréstimos, as multas devem estar abaixo de R$ 10,00. No entanto, para emitir a Declaração de Nada Consta, é necessário que todas as multas e pendências na biblioteca sejam totalmente quitadas.\n\n**Em caso de perda do material emprestado, deverá ser informado e proceder com a reposição do mesmo.**\n\nRegularize sua situação com a biblioteca o mais breve possível, para juntos, mantermos funcionando de forma eficiente e acessível para toda a comunidade acadêmica.\n\nEstamos à disposição para esclarecer dúvidas, ou para mais informações.\n\nAgradecemos sua atenção e colaboração.\n\nAtenciosamente,',
            'template_multa_e_pendencia': '**Prezado(a) {NOME}**,\n\nConforme estabelecido no [Regulamento Interno das Bibliotecas do Instituto Federal Catarinense](https://biblioteca.ifc.edu.br/wp-content/uploads/sites/53/2023/04/SIBI-Regulamento.pdf), artigo 44, é nossa responsabilidade notificá-lo(a) sobre as pendências em sua conta de usuário na biblioteca.\n\nDe acordo com os registros em nosso sistema, observamos que você possui o(s) seguinte(s) item(ns) em atraso:\n\n{LIVROS_PENDENTES}\n\nConforme o artigo 44, Inciso I, do Regulamento, informamos que a multa aplicada é de R$ 1,00 (um real) por dia útil de atraso para cada material emprestado.\n\nConstata-se também a existência de multa acumulada no valor total de **R$ {VALOR_MULTA}** referente ao(s) seguinte(s) item(ns):\n\n{LIVROS_MULTA}\n\nSalientamos que, para renovar ou realizar novos empréstimos, as multas devem estar abaixo de R$ 10,00. No entanto, para emitir a Declaração de Nada Consta, é necessário que todas as multas e pendências na biblioteca sejam totalmente quitadas.\n\n**Em caso de perda do material emprestado, deverá ser informado e proceder com a reposição do mesmo.**\n\nRegularize sua situação com a biblioteca o mais breve possível, para juntos, mantermos funcionando de forma eficiente e acessível para toda a comunidade acadêmica.\n\nEstamos à disposição para esclarecer dúvidas, ou para mais informações.\n\nAgradecemos sua atenção e colaboração.\n\nAtenciosamente,',
            'ultimo_diretorio': '',
            # Configurações de disparo de e-mails
            'email_remetente': '',              # Endereço de e-mail do remetente
            'email_senha_app': '',              # Senha de app do remetente
            'email_destinatario_padrao': '',    # Destinatário padrão (opcional)
            'email_assunto_padrao': '',          # Assunto padrão do e-mail (opcional)
            'modo_teste': True                  # Habilitar modo de teste por padrão
        }
        self._save_config(default_config)
        return default_config