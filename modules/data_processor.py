import pandas as pd
import json
from datetime import datetime

def sort_by_user_code(df):
    """
    Ordena o DataFrame pelo código da pessoa.

    Args:
        df: DataFrame pandas com os dados das multas

    Returns:
        DataFrame ordenado pelo código da pessoa
    """
    if 'Código da pessoa' in df.columns:
        return df.sort_values(by='Código da pessoa')
    else:
        print("Aviso: Coluna 'Código da pessoa' não encontrada.")
        return df

def extract_relevant_columns(df):
    """
    Extrai apenas as colunas relevantes para processamento.

    Args:
        df: DataFrame pandas com os dados completos

    Returns:
        DataFrame com apenas as colunas necessárias
    """
    # Lista das colunas que queremos extrair
    columns_to_extract = [
        "Código da pessoa",
        "Nome da pessoa",
        "Email",
        "Título",
        "Número chave",
        "Data de empréstimo",
        "Data devolução prevista",
        "Data devolução efetivada",
        "Valor multa",
        "Valor do desconto"
    ]

    # Verificar quais colunas existem no DataFrame
    available_columns = [col for col in columns_to_extract if col in df.columns]

    # Se "Número chave" não estiver disponível, tente "Número da chave"
    if "Número chave" not in available_columns and "Número da chave" in df.columns:
        available_columns.append("Número da chave")

    if not available_columns:
        raise ValueError("Nenhuma das colunas necessárias foi encontrada no arquivo.")

    return df[available_columns]

def format_date(date_str):
    """
    Formata uma data no formato brasileiro para ISO.

    Args:
        date_str: String de data no formato DD/MM/YYYY

    Returns:
        String de data no formato YYYY-MM-DD ou a string original se não for possível converter
    """
    if pd.isna(date_str) or not isinstance(date_str, str):
        return ""

    try:
        # Tenta converter do formato brasileiro para ISO
        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        # Se falhar, retorna a string original
        return date_str

def get_users_in_rel86(df):
    """
    Retorna um conjunto com os códigos das pessoas que estão no relatório 86.
    """
    rel86_df = df[df['Relatório'] == 'rel86']
    if 'Código da pessoa' in rel86_df.columns:
        return set(rel86_df['Código da pessoa'].astype(str).unique())
    return set()

def get_users_in_rel76(df):
    """
    Retorna um conjunto com os códigos das pessoas que estão no relatório 76.
    """
    rel76_df = df[df['Relatório'] == 'rel76']
    if 'Código da pessoa' in rel76_df.columns:
        return set(rel76_df['Código da pessoa'].astype(str).unique())
    return set()

def categorize_users(df):
    """
    Categoriza os usuários conforme as regras especificadas.

    Args:
        df: DataFrame pandas com os dados completos

    Returns:
        Dicionário com as categorias e seus respectivos usuários e estatísticas
    """
    # Importar pandas diretamente na função para garantir disponibilidade em todos os escopos
    import pandas as pd

    # Inicializar dicionário de categorias
    categories = {
        # Relatório 86 (multas)
        'rel86': {
            'total_linhas': 0,
            'pessoas_sem_email': set(),
            'total_multas': 0
        },
        # Relatório 76 (pendências)
        'rel76': {
            'total_linhas': 0,
            'pessoas_sem_email': set(),
            'dias_atraso': []  # Lista de tuplas (código_pessoa, nome, dias_atraso)
        },
        # Pessoas sem email (geral)
        'sem_email': {
            'pessoas': set()  # Conjunto com tuplas (código, nome)
        }
    }

    # Filtrar por relatório
    df_rel86 = df[df['Relatório'] == 'rel86']
    df_rel76 = df[df['Relatório'] == 'rel76']

    # Relatório 86 - Estatísticas
    categories['rel86']['total_linhas'] = len(df_rel86)
    categories['rel86']['total_multas'] = df_rel86['Valor multa'].sum() if 'Valor multa' in df_rel86.columns else 0

    # Relatório 76 - Estatísticas
    categories['rel76']['total_linhas'] = len(df_rel76)

    # Processar pessoas sem email e dias de atraso
    for _, row in df.iterrows():
        user_code = str(row.get('Código da pessoa', ''))
        if not user_code:
            continue

        nome = row.get('Nome da pessoa', '')
        if pd.isna(nome):
            nome = ''

        email = row.get('Email', '')
        if pd.isna(email) or email.strip() == '':
            has_email = False
            # Adicionar à lista geral de pessoas sem email
            categories['sem_email']['pessoas'].add((user_code, nome))
        else:
            has_email = True

        relatorio = row.get('Relatório', '')

        # Processar relatório 86
        if relatorio == 'rel86' and not has_email:
            categories['rel86']['pessoas_sem_email'].add(user_code)

        # Processar relatório 76
        if relatorio == 'rel76':
            if not has_email:
                categories['rel76']['pessoas_sem_email'].add(user_code)

            # Calcular dias de atraso
            data_prevista = row.get('Data devolução prevista', None)
            data_efetivada = row.get('Data devolução efetivada', None)

            # Se tiver data prevista mas não tiver data efetivada
            if not pd.isna(data_prevista) and (pd.isna(data_efetivada) or data_efetivada == ''):
                # Calcular dias de atraso até hoje
                try:
                    import datetime
                    hoje = datetime.datetime.now().date()

                    # Converter para datetime.date para garantir compatibilidade
                    if isinstance(data_prevista, pd.Timestamp):
                        data_prevista = data_prevista.date()
                    elif isinstance(data_prevista, str):
                        from datetime import datetime as dt
                        data_prevista = dt.strptime(data_prevista, '%d/%m/%Y').date()

                    # Garantir que data_prevista é um objeto date
                    if hasattr(data_prevista, 'date'):
                        data_prevista = data_prevista.date()

                    dias_atraso = (hoje - data_prevista).days

                    if dias_atraso > 0:
                        categories['rel76']['dias_atraso'].append((user_code, nome, dias_atraso))
                except Exception as e:
                    print(f"Erro ao calcular dias de atraso: {e}")

    # Ordenar a lista de dias de atraso (do maior para o menor)
    categories['rel76']['dias_atraso'].sort(key=lambda x: x[2], reverse=True)

    return categories

def group_fines_by_user(df):
    """
    Agrupa as multas por usuário e cria uma estrutura de dados adequada.
    Com tratamento especial para multas de chaves.

    Args:
        df: DataFrame pandas com os dados das multas

    Returns:
        Dicionário com dados agrupados por usuário
    """
    # Ordenar o DataFrame pelo código da pessoa
    df = sort_by_user_code(df)

    # Extrair colunas relevantes
    df_relevant = extract_relevant_columns(df)

    # Inicializar o dicionário de usuários
    users_data = {}

    # Adicionar categorias específicas
    categories = categorize_users(df)

    # Iterar sobre as linhas do DataFrame
    for _, row in df_relevant.iterrows():
        # Tratamento para código da pessoa (chave principal)
        if pd.isna(row.get('Código da pessoa')):
            # Pular registros sem código de pessoa válido
            continue

        user_code = str(row['Código da pessoa'])

        # Verificar se o usuário já existe no dicionário
        if user_code not in users_data:
            # Tratamento seguro para dados do usuário
            nome = row.get('Nome da pessoa', "")
            nome = "" if pd.isna(nome) else str(nome).strip()

            email = row.get('Email', "")
            email = "" if pd.isna(email) else str(email).strip()

            users_data[user_code] = {
                'codigo': user_code,
                'nome': nome,
                'email': email,
                'total_multas': 0.0,
                'multas': [],
                'tem_multa': False,
                'tem_devolucao_pendente': False,
                'sem_email': False,
                'categoria': []
            }

            # Verificar se o usuário tem email
            if not email:
                users_data[user_code]['sem_email'] = True
                users_data[user_code]['categoria'].append('sem_email')

            # Adicionar à categoria sem_email se estiver na lista
            sem_email_codigos = {codigo for codigo, _ in categories['sem_email']['pessoas']}
            if user_code in sem_email_codigos:
                users_data[user_code]['categoria'].append('sem_email')

            # Verificar se está nas listas de categorias específicas
            if user_code in categories['rel86']['pessoas_sem_email']:
                users_data[user_code]['categoria'].append('rel86_sem_email')

            if user_code in categories['rel76']['pessoas_sem_email']:
                users_data[user_code]['categoria'].append('rel76_sem_email')

        # Verificar devolução pendente (data efetivada está vazia)
        data_efetivada = row.get('Data devolução efetivada', "")
        if pd.isna(data_efetivada):
            tem_devolucao_pendente = True
            data_efetivada = ""  # Garantir que é string vazia para uso futuro
        elif isinstance(data_efetivada, str):
            tem_devolucao_pendente = not data_efetivada.strip()
            # Manter como string
        else:
            tem_devolucao_pendente = True  # Assume pendente para casos não-string
            data_efetivada = ""  # Converter para string vazia

        # Extrair e validar todos os valores com tratamento para NaN
        titulo = row.get('Título', "")
        titulo = "" if pd.isna(titulo) else str(titulo).strip()

        data_emprestimo = row.get('Data de empréstimo', "")
        data_emprestimo = "" if pd.isna(data_emprestimo) else data_emprestimo

        data_prevista = row.get('Data devolução prevista', "")
        data_prevista = "" if pd.isna(data_prevista) else data_prevista

        # Número chave pode estar em duas colunas diferentes
        numero_chave = row.get('Número chave', row.get('Número da chave', ""))
        numero_chave = "" if pd.isna(numero_chave) else str(numero_chave).strip()

        # Tratamento específico para multas de chaves
        tem_chave = bool(numero_chave.strip())

        # Calcular o valor com desconto - tratamento seguro para NaN
        try:
            valor_multa = 0.0
            if 'Valor multa' in row and not pd.isna(row['Valor multa']):
                valor_multa = float(row['Valor multa'])
        except (ValueError, TypeError):
            valor_multa = 0.0

        try:
            valor_desconto = 0.0
            if 'Valor do desconto' in row and not pd.isna(row['Valor do desconto']):
                valor_desconto = float(row['Valor do desconto'])
        except (ValueError, TypeError):
            valor_desconto = 0.0

        valor_final = max(0, valor_multa - valor_desconto)  # Garantir que nunca seja negativo

        # LÓGICA ESPECÍFICA PARA CHAVES
        # 1. Se tem chave e não tem data de empréstimo, usar a data prevista como data de empréstimo
        if tem_chave and not data_emprestimo and data_prevista:
            data_emprestimo = data_prevista

        # 2. Se tem chave, tem multa e não tem data de devolução efetiva, calcular a data
        data_efetivada_calculada = ""

        # Corrigir a verificação para evitar chamar strip() em float
        tem_data_efetivada = False
        if isinstance(data_efetivada, str) and data_efetivada.strip():
            tem_data_efetivada = True

        if tem_chave and valor_final > 0 and not tem_data_efetivada:
            try:
                # Converter data prevista para objeto de data
                data_obj = datetime.strptime(data_prevista, "%d/%m/%Y")

                # Se o valor da multa for 1, adicionar 1 dia à data prevista
                if valor_final == 1:
                    data_devolucao = data_obj + pd.Timedelta(days=1)
                else:
                    # Caso contrário, usar o valor da multa como dias de atraso
                    data_devolucao = data_obj + pd.Timedelta(days=int(valor_final))

                # Formatar de volta para string
                data_efetivada_calculada = data_devolucao.strftime("%d/%m/%Y")
                # Como calculamos a data, não está mais pendente
                tem_devolucao_pendente = False
            except (ValueError, TypeError):
                # Se não conseguir calcular, mantém como estava
                pass

        # Usar a data calculada se disponível
        if data_efetivada_calculada:
            data_efetivada = data_efetivada_calculada

        # Criar objeto de multa
        multa = {
            'titulo': titulo,
            'data_emprestimo': format_date(data_emprestimo),
            'data_prevista': format_date(data_prevista),
            'data_efetivada': format_date(data_efetivada),
            'valor': valor_multa,
            'desconto': valor_desconto,
            'valor_final': valor_final,
            'numero_chave': numero_chave,
            'devolucao_pendente': tem_devolucao_pendente,
            'eh_chave': tem_chave,
            'dias_atraso': int(valor_final) if tem_chave else 0
        }

        # Adicionar multa à lista de multas do usuário
        users_data[user_code]['multas'].append(multa)

        # Atualizar o total de multas do usuário
        users_data[user_code]['total_multas'] += valor_final

        # Atualizar flags de categoria
        if valor_final > 0:
            users_data[user_code]['tem_multa'] = True

        if tem_devolucao_pendente:
            users_data[user_code]['tem_devolucao_pendente'] = True

    # Atribuir categorias baseadas nas flags
    for user_code, user_data in users_data.items():
        # Categoria de valor alto (≥ 100)
        if user_data['total_multas'] >= 100:
            user_data['categoria'].append('multa_alta')

        # Categoria baseada em multa e devolução
        if user_data['tem_multa'] and user_data['tem_devolucao_pendente']:
            user_data['categoria'].append('multa_e_devolucao_pendente')
        elif user_data['tem_multa'] and not user_data['tem_devolucao_pendente']:
            user_data['categoria'].append('apenas_multa')
        elif not user_data['tem_multa'] and user_data['tem_devolucao_pendente']:
            user_data['categoria'].append('apenas_devolucao_pendente')

    return users_data

def filter_users_by_category(users_data, category):
    """
    Filtra usuários por uma categoria específica.

    Args:
        users_data: Dicionário com dados de usuários
        category: Categoria para filtrar ('apenas_multa', 'apenas_devolucao_pendente',
                 'multa_e_devolucao_pendente', 'sem_email', 'multa_alta')

    Returns:
        Dicionário com apenas os usuários da categoria especificada
    """
    return {k: v for k, v in users_data.items() if category in v['categoria']}

def print_category_summary(users_data):
    """
    Imprime um resumo da quantidade de usuários em cada categoria.

    Args:
        users_data: Dicionário com dados de usuários
    """
    # Definir as categorias que queremos contar
    categories = [
        'apenas_multa',
        'apenas_devolucao_pendente',
        'multa_e_devolucao_pendente',
        'sem_email',
        'multa_alta'
    ]

    print("\nResumo por Categoria:")
    print("=" * 60)

    for category in categories:
        filtered_users = filter_users_by_category(users_data, category)
        count = len(filtered_users)

        category_name = {
            'apenas_multa': 'Apenas Multa (sem devolução pendente)',
            'apenas_devolucao_pendente': 'Apenas Devolução Pendente (sem multa)',
            'multa_e_devolucao_pendente': 'Multa e Devolução Pendente',
            'sem_email': 'Sem Email Cadastrado',
            'multa_alta': 'Multa Alta (≥ R$100,00)'
        }.get(category, category)

        print(f"{category_name}: {count} usuários")

    print("=" * 60)

def print_users_by_category(users_data, category):
    """
    Imprime detalhes dos usuários em uma categoria específica.

    Args:
        users_data: Dicionário com dados de usuários
        category: Categoria para mostrar
    """
    filtered_users = filter_users_by_category(users_data, category)

    category_name = {
        'apenas_multa': 'Apenas Multa (sem devolução pendente)',
        'apenas_devolucao_pendente': 'Apenas Devolução Pendente (sem multa)',
        'multa_e_devolucao_pendente': 'Multa e Devolução Pendente',
        'sem_email': 'Sem Email Cadastrado',
        'multa_alta': 'Multa Alta (≥ R$100,00)'
    }.get(category, category)

    print(f"\nUsuários na categoria: {category_name}")
    print("=" * 80)
    print(f"{'Código':<15} {'Nome':<30} {'Total':<10} {'Email':<25}")
    print("-" * 80)

    # Ordenar por valor total (decrescente)
    sorted_users = sorted(filtered_users.values(), key=lambda x: x['total_multas'], reverse=True)

    for user in sorted_users:
        email = user['email'] if user['email'] else "[SEM EMAIL]"
        print(f"{user['codigo']:<15} {user['nome'][:28]:<30} R$ {user['total_multas']:<8.2f} {email[:23]:<25}")

    print("=" * 80)

# Melhorar a função generate_json_file para incluir categorias
def generate_json_file(df, output_path="multas_usuarios.json"):
    """
    Gera um arquivo JSON com as multas agrupadas por usuário, incluindo categorização.

    Args:
        df: DataFrame pandas com os dados das multas
        output_path: Caminho para salvar o arquivo JSON

    Returns:
        Caminho do arquivo JSON gerado
    """
    # Obter dados agrupados
    users_data = group_fines_by_user(df)

    # Imprimir resumo por categoria
    print_category_summary(users_data)

    # Opcional: imprimir detalhes de cada categoria
    for category in ['multa_alta', 'multa_e_devolucao_pendente', 'sem_email']:
        print_users_by_category(users_data, category)

    # Converter para lista (formato mais comum para JSON)
    users_list = list(users_data.values())

    # Gravar arquivo JSON
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(users_list, json_file, ensure_ascii=False, indent=2)

    print(f"Arquivo JSON gerado com sucesso: {output_path}")
    return output_path

def get_fines_summary(df):
    """
    Gera um resumo estatístico das multas.

    Args:
        df: DataFrame pandas com os dados das multas

    Returns:
        Dicionário com estatísticas das multas
    """
    users_data = group_fines_by_user(df)

    total_users = len(users_data)
    total_fines = sum(len(user['multas']) for user in users_data.values())
    total_value = sum(sum(multa['valor'] for multa in user['multas']) for user in users_data.values())

    # Identificar usuário com maior número de multas
    if users_data:
        max_fines_user = max(users_data.values(), key=lambda x: len(x['multas']))
        max_fines_count = len(max_fines_user['multas'])
        max_fines_user_name = max_fines_user['nome']
    else:
        max_fines_user_name = "N/A"
        max_fines_count = 0

    return {
        'total_users': total_users,
        'total_fines': total_fines,
        'total_value': total_value,
        'max_fines_user': max_fines_user_name,
        'max_fines_count': max_fines_count
    }

# Função de teste do módulo
if __name__ == "__main__":
    from read_excel import read_excel_file, clean_column_names

    try:
        # Carregar um arquivo de exemplo (substitua pelo caminho real)
        file_path = 'elian.oliveira_2025-03-27-0-38-19.xlsx'

        # Corrigindo: primeiro desativa a verificação de data, depois limpa colunas
        df = read_excel_file(file_path, verificar_data=False)
        df = clean_column_names(df)

        # Testar o processamento
        json_path = generate_json_file(df)

        # Mostrar resumo
        summary = get_fines_summary(df)
        print("\nResumo das multas:")
        print(f"Total de usuários com multas: {summary['total_users']}")
        print(f"Total de multas: {summary['total_fines']}")
        print(f"Valor total: R$ {summary['total_value']:.2f}")
        print(f"Usuário com mais multas: {summary['max_fines_user']} ({summary['max_fines_count']} multas)")

    except Exception as e:
        print(f"Erro: {str(e)}")