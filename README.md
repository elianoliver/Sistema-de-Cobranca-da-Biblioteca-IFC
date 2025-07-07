# Sistema de Cobrança da Biblioteca IFC

Sistema para gestão de multas e pendências da biblioteca do Instituto Federal Catarinense. Permite a unificação de relatórios Excel, visualização de estatísticas detalhadas, configuração de templates de e-mail personalizados e envio automatizado de notificações, tudo através de uma interface gráfica moderna e intuitiva baseada em PyQt6.

## 🚀 Funcionalidades Principais

### 📤 Importação e Processamento
- **Importação de Relatórios Excel**: Suporte para arquivos .xlsx e .xls
- **Validação Automática**: Verificação de datas e integridade dos dados
- **Unificação Inteligente**: Combina relatórios de multas (86) e pendências (76)
- **Processamento de Chaves**: Tratamento especial para multas de chaves emprestadas

### 📊 Visualização e Análise
- **Dashboard Interativo**: Cards expansíveis com estatísticas em tempo real
- **Categorização Automática**: Separação por tipo de pendência (multas, pendências, ambos)
- **Estatísticas Detalhadas**: Contadores de usuários, valores e itens por categoria
- **Identificação de Problemas**: Lista de usuários sem e-mail cadastrado

### ✉️ Sistema de E-mails
- **Templates Personalizáveis**: Editor com suporte a Markdown
- **Variáveis Dinâmicas**: Substituição automática de dados do usuário
- **Preview em Tempo Real**: Visualização do e-mail antes do envio
- **Envio em Lote**: Processamento automático com delay entre envios
- **Modo de Teste**: Envio para destinatário de teste para validação
- **Configuração SMTP**: Suporte completo ao Gmail com senha de app

### ⚙️ Configurações
- **Gerenciamento de Configurações**: Interface para configurações de e-mail
- **Persistência de Dados**: Salva configurações em arquivo JSON
- **Templates Padrão**: Modelos pré-configurados seguindo regulamento da biblioteca

## 🏗️ Arquitetura Modular

O projeto segue uma arquitetura modular bem estruturada, facilitando manutenção e evolução:

### Organização dos Módulos

```
modules/
├── tabs/                    # Abas da interface
│   ├── __init__.py         # Configuração e exportação das abas
│   ├── base_tab.py         # Classe base abstrata
│   ├── import_tab.py       # Importação de arquivos Excel
│   ├── results_tab.py      # Visualização de resultados
│   ├── template_tab.py     # Configuração de templates
│   ├── email_tab.py        # Envio de e-mails
│   └── config_tab.py       # Configurações gerais
├── components.py           # Componentes UI reutilizáveis
├── config_manager.py       # Gerenciador de configurações
├── data_processor.py       # Processamento e análise de dados
├── email_sender.py         # Envio de e-mails via SMTP
├── gui_interface.py        # Interface principal
├── read_excel.py          # Leitura e validação de Excel
└── styles_fix.py          # Sistema de estilos nativo Qt
```

### Padrões de Projeto Implementados

- **Herança**: Todas as abas herdam de `BaseTab`
- **Signals e Slots**: Comunicação assíncrona entre componentes
- **Injeção de Dependência**: Dependências passadas via construtor
- **Responsabilidade Única**: Cada classe tem uma função específica
- **Factory Pattern**: Criação centralizada de abas
- **Observer Pattern**: Notificações de mudanças via sinais

## 📋 Requisitos do Sistema

### Software
- **Python**: 3.8 ou superior
- **Sistema Operacional**: Windows, macOS ou Linux

### Dependências Python
```
PyQt6>=6.4.0      # Interface gráfica
pandas>=2.0.0     # Processamento de dados
markdown>=3.4.0   # Conversão de templates
openpyxl>=3.1.0   # Leitura de arquivos Excel
```

## 🚀 Instalação e Execução

### 1. Clone o Repositório
```bash
git clone <url-do-repositorio>
cd cobrancav3
```

### 2. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 3. Execute o Sistema
```bash
python main.py
```

## 📖 Como Usar

### 1. Importação de Dados
1. Na aba **"📤 Importação"**, arraste ou selecione os relatórios Excel
2. **Relatório 86**: Arquivo com dados de multas
3. **Relatório 76**: Arquivo com dados de pendências
4. Clique em **"Unificar Relatórios"** para processar

### 2. Visualização de Resultados
1. Navegue para a aba **"📊 Resultados"**
2. Visualize estatísticas em cards interativos
3. Expanda/contraia cards para ver detalhes
4. Identifique usuários sem e-mail cadastrado

### 3. Configuração de Templates
1. Acesse a aba **"📝 Templates"**
2. Edite os três modelos disponíveis:
   - **Apenas Multa**: Para usuários só com multas
   - **Apenas Pendência**: Para usuários só com pendências
   - **Multa e Pendência**: Para usuários com ambos
3. Use as tags disponíveis: `{NOME}`, `{VALOR_MULTA}`, `{LIVROS_MULTA}`, `{LIVROS_PENDENTES}`
4. Clique em **"Salvar Templates"**

### 4. Configuração de E-mail
1. Vá para a aba **"⚙️ Configurações"**
2. Configure:
   - **E-mail do remetente**: Seu e-mail Gmail
   - **Senha de app**: Senha de aplicativo do Gmail
   - **Destinatário de teste**: E-mail para testes
   - **Assunto padrão**: Assunto dos e-mails
   - **Modo de teste**: Ativar/desativar

### 5. Envio de E-mails
1. Acesse a aba **"✉️ Emails"**
2. Selecione o tipo de usuário para filtrar
3. Clique em **"Gerar Preview"** para visualizar
4. Use **"Testar Envio"** para validar configuração
5. Clique em **"Enviar Emails"** para envio em lote

## 🔧 Configuração do Gmail

Para usar o sistema de e-mails, configure uma **senha de aplicativo** no Gmail:

1. Ative a verificação em duas etapas na sua conta Google
2. Acesse [Senhas de app](https://myaccount.google.com/apppasswords)
3. Gere uma senha para "Email"
4. Use essa senha no campo "Senha de app" do sistema

## 📊 Estrutura dos Relatórios

### Relatório 86 (Multas)
- **Código da pessoa**: Identificador único do usuário
- **Nome da pessoa**: Nome completo
- **Email**: Endereço de e-mail
- **Título**: Nome do item emprestado
- **Valor multa**: Valor da multa em reais
- **Data de empréstimo**: Data do empréstimo
- **Data devolução prevista**: Data prevista para devolução
- **Data devolução efetivada**: Data real da devolução

### Relatório 76 (Pendências)
- **Código da pessoa**: Identificador único do usuário
- **Nome da pessoa**: Nome completo
- **Email**: Endereço de e-mail
- **Título**: Nome do item emprestado
- **Data de empréstimo**: Data do empréstimo
- **Data devolução prevista**: Data prevista para devolução

## 🛠️ Desenvolvimento

### Adicionando uma Nova Aba

1. **Crie a classe** em `modules/tabs/` herdando de `BaseTab`
2. **Implemente `setup_ui()`** para configurar a interface
3. **Adicione ao `__init__.py`** do pacote tabs
4. **Configure sinais** no método `setup_tabs()`
5. **Conecte à interface principal** via sinais

### Exemplo de Nova Aba
```python
from modules.tabs.base_tab import BaseTab

class MinhaNovaAba(BaseTab):
    def setup_ui(self):
        # Configurar interface
        pass
    
    def update_data(self, data):
        # Atualizar dados
        pass
```

## 🐛 Solução de Problemas

### Erro de Data no Arquivo
- **Problema**: "O arquivo não é do dia atual"
- **Solução**: Desmarque "Verificar datas" na aba de importação

### Erro de E-mail
- **Problema**: "Erro ao enviar e-mail"
- **Solução**: Verifique configurações SMTP e senha de app

### Arquivo Excel Não Carrega
- **Problema**: "Erro ao ler arquivo Excel"
- **Solução**: Verifique se o arquivo não está corrompido e tem formato .xlsx/.xls

## 📝 Licença

Este projeto foi desenvolvido para o Instituto Federal Catarinense e está sob licença interna.

## 🤝 Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças seguindo os padrões do projeto
4. Teste todas as funcionalidades
5. Envie um pull request