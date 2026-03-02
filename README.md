# 📚 Sistema de Cobrança da Biblioteca IFC

Sistema para gestão de multas e pendências da biblioteca do Instituto Federal Catarinense Campus Camboriú. Desenvolvido como projeto de conclusão de curso, resolvendo um problema crítico de instabilidade no sistema Pergamum.

**Autor:** Elian Jardel de Oliveira  
**Instituição:** Instituto Federal Catarinense - Campus Camboriú  
**Período:** Maio - Agosto 2024  
**Status:** Em Produção ✅

---

## 🎯 O Problema Resolvido

O sistema Pergamum apresentava falhas intermitentes no envio automático de notificações de multas durante **2,5 anos** (Maio 2022 - Novembro 2024), impactando:

- 📉 **Redução de eficiência**: Funcionários redigiam e-mails manualmente
- 💬 **Comunicação unidirecional**: Notificações pouco detalhadas
- ❌ **Inconsistência**: Estrutura heterogênea de mensagens
- 😞 **Confiabilidade**: Afetava a confiança dos usuários

---

## ✨ Solução Desenvolvida

Uma **aplicação desktop modular** que:

- ✅ Automatiza a leitura de relatórios Excel do Pergamum
- ✅ Unifica dados de múltiplas fontes
- ✅ Gera notificações padronizadas e personalizadas
- ✅ Implementa canal bidirecional via e-mail principal da biblioteca
- ✅ Reduce sobrecarga operacional

---

## 📊 Resultados Alcançados

### Volume de Comunicação

| Métrica | 2023 (Manual) | 2024 (Aplicação) | Crescimento |
|---------|---------------|-----------------|------------|
| **E-mails enviados** | 45 | 350 | **677,8%** ↑ |
| **Usuários alcançados** | 26 | 189 | **626,9%** ↑ |
| **Multas abatidas** | R$ 3.976,00 | R$ 7.618,00 | **91,5%** ↑ |

### Eficiência Operacional

| Tarefa | Manual | Automatizado | Economia |
|--------|--------|--------------|----------|
| **1 e-mail** | 3-5 min | <5 seg | **99,3%** ⏱️ |
| **250 e-mails** | 12-20h | ~5 min | **99,6%** ⏱️ |

*Dados referentes a 4 meses de operação com sucesso*

---

## 🏗️ Arquitetura Técnica

### Stack Tecnológico

| Componente | Tecnologia |
|-----------|-----------|
| **Interface** | PyQt6 |
| **Processamento de Dados** | Pandas |
| **Leitura de Excel** | OpenPyXL |
| **Envio de E-mails** | SMTP (Gmail) |
| **Templates** | Markdown |
| **Persistência** | JSON |

### Arquitetura Modular

```
Sistema de Cobrança
│
├── Interface Principal (gui_interface.py)
│   └── Gerencia comunicação entre abas via sinais Qt
│
├── Abas (modules/tabs/)
│   ├── ImportTab          → Leitura e validação de Excel
│   ├── ResultsTab         → Dashboard com estatísticas
│   ├── TemplateTab        → Editor de templates de e-mail
│   ├── EmailTab           → Envio em lote com preview
│   └── ConfigTab          → Gerenciamento de configurações
│
├── Núcleo de Processamento
│   ├── read_excel.py      → Validação e leitura de arquivos
│   ├── data_processor.py  → Unificação e categorização
│   ├── email_sender.py    → SMTP e gerenciamento de envios
│   └── config_manager.py  → Persistência de configurações
│
└── Componentes Reutilizáveis
    └── components.py      → Cards, campos customizados
```

### Padrões de Projeto Implementados

- **Herança**: Todas as abas herdam de `BaseTab`
- **Observer Pattern**: Sinais Qt para comunicação
- **Factory Pattern**: Criação centralizada de componentes
- **Responsabilidade Única**: Cada módulo com função específica
- **Injeção de Dependência**: Configurações passadas via construtor

---

## 🚀 Fluxo de Processamento

### Etapa 1: Importação e Unificação
```
Relatório 86 (Multas)    ┐
                         ├─→ Leitura Excel
Relatório 76 (Pendências)┘    ↓
                         Normalização de nomes
                              ↓
                         Unificação em tabela mestra
```

### Etapa 2: Agrupamento e Categorização
```
Tabela Mestra
    ↓
Agrupamento por Código de Pessoa
    ↓
Atribuição de Categorias:
├─ apenas_multa
├─ apenas_devolucao_pendente
├─ multa_e_devolucao_pendente
└─ sem_email
```

### Etapa 3: Geração de Notificações
```
Template Personalizado (Markdown)
    ↓
Substituição de Tags:
├─ {NOME}
├─ {EMAIL}
├─ {VALOR_MULTA}
├─ {LIVROS_MULTA}
└─ {LIVROS_PENDENTES}
    ↓
E-mail Formatado e Enviado
```

---

## 💻 Requisitos do Sistema

### Software

- **Python 3.8+**
- **Windows**

### Dependências

```
PyQt6>=6.4.0       # Interface gráfica
pandas>=2.0.0      # Processamento de dados
markdown>=3.4.0    # Conversão de templates
openpyxl>=3.1.0    # Leitura de Excel
```

---

## 🔧 Instalação Rápida

### 1. Clone o Repositório

```bash
git clone https://github.com/elianoliver/Sistema-de-Cobranca-da-Biblioteca-IFC.git
cd Sistema-de-Cobranca-da-Biblioteca-IFC
```

### 2. Crie um Ambiente Virtual (Recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Instale as Dependências

```bash
pip install -r requirements.txt
```

### 4. Execute o Sistema

```bash
python main.py
```

---

## 📖 Guia de Uso

### 1️⃣ Importação de Dados

1. Clique na aba **"📤 Importação"**
2. Arraste os dois relatórios Excel ou selecione-os
3. **Relatório 86**: Dados de multas
4. **Relatório 76**: Dados de pendências
5. Clique **"Unificar Relatórios"**
6. Verifique a aba **"📊 Resultados"** para estatísticas

### 2️⃣ Visualização de Estatísticas

A aba **"📊 Resultados"** exibe:

- Total de multas e pendências
- Valores em reais
- Quantidade de usuários
- Usuários sem e-mail cadastrado
- Distribuição por categoria

### 3️⃣ Configuração de Templates

1. Acesse a aba **"📝 Templates"**
2. Edite os modelos para cada categoria:
   - **Apenas Multa**: Usuarios com multas pendentes
   - **Apenas Pendência**: Usuários com devoluções vencidas
   - **Multa e Pendência**: Usuarios com ambos
3. Use variáveis dinâmicas:
   - `{NOME}` → Nome do usuário
   - `{EMAIL}` → E-mail do usuário
   - `{VALOR_MULTA}` → Valor total de multas
   - `{LIVROS_MULTA}` → Lista de itens com multa
   - `{LIVROS_PENDENTES}` → Lista de itens não devolvidos
4. Clique **"Salvar Templates"**

### 4️⃣ Configuração de E-mail

1. Vá para **"⚙️ Configurações"**
2. Configure:
   - **E-mail do remetente**: Seu e-mail Gmail
   - **Senha de app**: Senha de aplicativo (veja abaixo)
   - **Destinatário de teste**: Para validação
   - **Assunto padrão**: Padrão para todos os e-mails
3. Clique **"Salvar Configurações"**

### 5️⃣ Envio de E-mails

1. Navegue para **"✉️ Emails"**
2. Selecione o tipo de usuário para filtrar
3. Clique **"Gerar Preview"** para visualizar
4. Use **"Testar Envio"** para validar primeiro
5. Clique **"Enviar Emails"** para envio em lote
6. Monitore a barra de progresso
7. Consulte o relatório final

---

## 🔐 Configuração do Gmail

Para usar o sistema de e-mails com segurança:

### Passo 1: Ativar Verificação em Duas Etapas

1. Acesse [myaccount.google.com](https://myaccount.google.com)
2. Vá para "Segurança"
3. Ative "Verificação em duas etapas"

### Passo 2: Gerar Senha de Aplicativo

1. Acesse [Senhas de app](https://myaccount.google.com/apppasswords)
2. Selecione "Email" e "Windows/Mac/Linux"
3. Google gerará uma senha de 16 caracteres
4. **Copie exatamente como mostrado** (sem espaços)

### Passo 3: Configurar no Sistema

1. Cole a senha no campo "Senha de app"
2. Clique **"Salvar Configurações"**
3. Use **"Testar Envio"** para validar

---

## 🛠️ Desenvolvimento e Extensão

### Adicionando uma Nova Aba

1. **Crie um novo arquivo** em `modules/tabs/minha_aba.py`
2. **Herde de BaseTab**:

```python
from modules.tabs.base_tab import BaseTab
from PyQt6.QtWidgets import QVBoxLayout, QLabel

class MinhaAba(BaseTab):
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Conteúdo da aba"))
        self.setLayout(layout)
    
    def update_data(self, data):
        # Atualizar quando dados mudam
        pass
```

3. **Registre em `modules/tabs/__init__.py`**
4. **Adicione à interface principal** em `gui_interface.py`

### Estrutura de Dados Processados

```python
{
    "101": {
        "nome": "Ana Silva",
        "email": "ana@email.com",
        "total_multas": 15.50,
        "categoria": "multa_e_devolucao_pendente",
        "multas": [
            {
                "titulo": "Livro A",
                "valor_final": 5.00,
                "devolucao_pendente": False
            }
        ]
    }
}
```

---

## 🐛 Solução de Problemas

### ❌ "O arquivo não é do dia atual"

- **Causa**: Validação de data ativa
- **Solução**: Desmarque "Verificar datas" na aba de importação

### ❌ "Erro ao enviar e-mail"

- **Causa**: Configurações SMTP inválidas
- **Solução**: 
  - Verifique e-mail e senha de app
  - Ative verificação 2FA no Gmail
  - Use **"Testar Envio"** para validar

### ❌ "Arquivo Excel não carrega"

- **Causa**: Formato inválido ou corrompido
- **Solução**: 
  - Confirme formato .xlsx ou .xls
  - Teste abrir no Excel
  - Verifique permissões de leitura

### ❌ "Sem e-mail" aparece frequente

- **Causa**: Usuários sem e-mail cadastrado no Pergamum
- **Solução**: 
  - Revise dados no Pergamum
  - Configure e-mail dos usuários manualmente
  - Considere filtro na aba de e-mail

---

## 📋 Estrutura dos Relatórios Esperados

### Relatório 86 (Multas)

Colunas necessárias:
- `Código da pessoa`
- `Nome da pessoa`
- `Email`
- `Título` (nome do item)
- `Valor multa` (em reais)
- `Data empréstimo`
- `Data devolução prevista`
- `Data devolução efetivada`

### Relatório 76 (Pendências)

Colunas necessárias:
- `Código da pessoa`
- `Nome da pessoa`
- `Email`
- `Título` (nome do item)
- `Data empréstimo`
- `Data devolução prevista`

---

## 🎓 Informações Acadêmicas

### Tipo de Trabalho
Projeto de Conclusão de Curso (TCC)

### Metodologia
- **Pesquisa Aplicada** com abordagem mista (qualitativa e quantitativa)
- **Análise de 79 e-mails** para identificar deficiências
- **Entrevista com funcionários** da biblioteca

### Referência Normativa
Regulamento Interno das Bibliotecas do Instituto Federal Catarinense, Art. 44

### Período de Desenvolvimento
- Desenvolvimento: Março - Maio 2024
- Implantação: Maio - Agosto 2024
- Análise de Resultados: Setembro - Dezembro 2024

---

## 📈 Perspectivas Futuras

- 🌐 **Conversão para Web**: Aplicação web para maior acessibilidade
- 🔌 **Integração API Pergamum**: Eliminação da dependência de relatórios
- 🏢 **Replicação em Outras Bibliotecas**: Potencial para adoção institucional
- 📱 **Aplicativo Mobile**: Notificações push para usuários
- 📊 **Dashboard Avançado**: Gráficos e relatórios mais complexos

---

## 📝 Licença

Este projeto é propriedade intelectual do Instituto Federal Catarinense e está disponível para uso institucional.

---

## 🤝 Contribuições

Para contribuir com melhorias:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/melhoria`)
3. Implemente seguindo os padrões do projeto
4. Teste todas as funcionalidades
5. Envie um pull request com descrição clara

### Padrões de Código

- **Nomeação**: snake_case para variáveis, PascalCase para classes
- **Docstrings**: Documentar funções públicas
- **Comentários**: Explicar lógica complexa
- **Type Hints**: Usar anotações de tipo

---

## 📧 Contato e Suporte

- **Desenvolvedor**: Elian Jardel de Oliveira
- **E-mail**: [elian.oliveira@estudantes.ifc.edu.br](mailto:elian.oliveira@estudantes.ifc.edu.br)
- **GitHub**: [@elianoliver](https://github.com/elianoliver)
- **Instituição**: Instituto Federal Catarinense - Campus Camboriú

---

## 🙏 Agradecimentos

- Instituto Federal Catarinense - Campus Camboriú
- Biblioteca do IFC pela colaboração
- Orientador/Professores do curso
- Comunidade Python e Qt

---

<div align="center">

**Desenvolvido com ❤️ como Projeto de Conclusão de Curso**

Demonstrando excelência técnica, inovação e impacto prático

</div>
