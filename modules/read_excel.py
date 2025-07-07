import pandas as pd
import re
from datetime import datetime

def read_excel_file(file_path, verificar_data=True):
    """
    Lê um arquivo Excel e opcionalmente verifica se a data no nome do arquivo é a atual.

    Args:
        file_path: Caminho para o arquivo Excel
        verificar_data: Se True, verifica se o arquivo é do dia atual
    """
    if verificar_data:
        # Extrair a data do nome do arquivo usando regex
        padrao_data = r"_(\d{4}-\d{2}-\d{2})-"
        match = re.search(padrao_data, file_path)

        if match:
            data_arquivo_str = match.group(1)
            data_arquivo = datetime.strptime(data_arquivo_str, "%Y-%m-%d").date()
            hoje = datetime.now().date()

            if data_arquivo != hoje:
                raise ValueError(f"O arquivo não é do dia atual. Data do arquivo: {data_arquivo}, Data atual: {hoje}")
        else:
            print("Aviso: Formato de nome de arquivo inválido. O nome deve conter a data no formato '_YYYY-MM-DD-'.")

    try:
        return pd.read_excel(file_path)
    except FileNotFoundError:
        print(f"Erro: O arquivo {file_path} não foi encontrado.")
        raise
    except Exception as e:
        print(f"Erro ao ler o arquivo Excel: {str(e)}")
        raise

def clean_column_names(df):
    df.columns = df.columns.str.strip()
    return df

def get_users_with_fines(df):
    return df[df['Valor multa'] > 0] if 'Valor multa' in df.columns else pd.DataFrame()

def get_summary(df):
    """
    Obtém um resumo dos dados do DataFrame, priorizando as colunas corretas
    e verificando alternativas quando necessário
    """
    # Garantir que os nomes das colunas estejam limpos
    df = clean_column_names(df)

    # Contagem de linhas
    num_rows = len(df)

    # Verificar a coluna principal "Código da pessoa"
    if 'Código da pessoa' in df.columns:
        # Verificar se a coluna tem dados
        if not df['Código da pessoa'].isna().all() and df['Código da pessoa'].nunique() > 0:
            num_unique_users = df['Código da pessoa'].nunique()
        else:
            # Coluna existe mas está vazia, tentar "Código pessoa"
            if 'Código pessoa' in df.columns:
                num_unique_users = df['Código pessoa'].nunique()
            else:
                # Verificar outras variações como último recurso
                codigo_pessoa_colunas = ['Codigo da pessoa', 'Codigo pessoa', 'ID pessoa']
                for coluna in codigo_pessoa_colunas:
                    if coluna in df.columns and not df[coluna].isna().all():
                        num_unique_users = df[coluna].nunique()
                        break
                else:
                    num_unique_users = 0
                    print(f"Aviso: Nenhuma coluna válida de código de pessoa encontrada.")
    elif 'Código pessoa' in df.columns:
        # Se "Código da pessoa" não existir, usar diretamente "Código pessoa"
        num_unique_users = df['Código pessoa'].nunique()
    else:
        # Nenhuma das colunas principais existe, verificar outras variações
        codigo_pessoa_colunas = ['Codigo da pessoa', 'Codigo pessoa', 'ID pessoa']
        for coluna in codigo_pessoa_colunas:
            if coluna in df.columns and not df[coluna].isna().all():
                num_unique_users = df[coluna].nunique()
                break
        else:
            num_unique_users = 0
            print(f"Aviso: Nenhuma coluna válida de código de pessoa encontrada. Colunas disponíveis: {list(df.columns)}")

    # Verificar a coluna de valor de multa
    if 'Valor multa' in df.columns:
        total_fines = df['Valor multa'].sum()
    else:
        # Tentar variações alternativas
        multa_colunas = ['Valor da multa', 'Multa']
        for coluna in multa_colunas:
            if coluna in df.columns:
                total_fines = df[coluna].sum()
                break
        else:
            total_fines = 0

    summary = {
        "num_rows": num_rows,
        "num_unique_users": num_unique_users,
        "total_fines": total_fines
    }

    return summary

def unify_dataframes(df_multas, df_pendencias):
    """
    Unifica dados de dois dataframes (multas e pendências) em um único dataframe.

    Args:
        df_multas: DataFrame com dados de multas
        df_pendencias: DataFrame com dados de pendências

    Returns:
        DataFrame unificado contendo dados de ambos os relatórios
    """
    # Código de diagnóstico para verificar a estrutura dos dataframes de entrada
    print("Diagnóstico da função unify_dataframes:")
    print(f"DataFrame de multas: {len(df_multas)} registros")
    if 'Número chave' in df_multas.columns:
        num_chaves_multas = (~df_multas['Número chave'].isna() & df_multas['Número chave'].astype(str).str.strip().ne('')).sum()
        print(f"Registros com chaves no DataFrame de multas: {num_chaves_multas}")
        if num_chaves_multas > 0:
            print("Exemplo de chaves:", df_multas.loc[~df_multas['Número chave'].isna(), 'Número chave'].iloc[:3].tolist())

    print(f"DataFrame de pendências: {len(df_pendencias)} registros")
    if 'Número chave' in df_pendencias.columns:
        num_chaves_pendencias = (~df_pendencias['Número chave'].isna() & df_pendencias['Número chave'].astype(str).str.strip().ne('')).sum()
        print(f"Registros com chaves no DataFrame de pendências: {num_chaves_pendencias}")
        if num_chaves_pendencias > 0:
            print("Exemplo de chaves:", df_pendencias.loc[~df_pendencias['Número chave'].isna(), 'Número chave'].iloc[:3].tolist())

    # Colunas a manter na unificação
    colunas_essenciais = [
        'Código da pessoa',
        'Nome da pessoa',
        'Email',
        'Título',
        'Número chave',
        'Valor multa',
        'Data de empréstimo',
        'Data devolução prevista',
        'Data devolução efetivada',
        'Relatório'  # Nova coluna para identificar a origem
    ]

    # Mapear nomes de colunas entre os dois relatórios
    mapeamento_colunas = {
        'Código pessoa': 'Código da pessoa',  # No relatório de pendências
    }

    # Cópia dos dataframes originais para não alterá-los
    df_multas_temp = df_multas.copy()
    df_pendencias_temp = df_pendencias.copy()

    # Adicionar a coluna 'Relatório' para identificar a origem
    df_multas_temp['Relatório'] = 'rel86'
    df_pendencias_temp['Relatório'] = 'rel76'

    # Verificar e corrigir coluna vazia no relatório de pendências
    if 'Código da pessoa' in df_pendencias_temp.columns and 'Código pessoa' in df_pendencias_temp.columns:
        # Verificar se 'Código da pessoa' está vazio
        if df_pendencias_temp['Código da pessoa'].isna().all() or df_pendencias_temp['Código da pessoa'].astype(str).str.strip().eq('').all():
            # Copiar valores de 'Código pessoa' para 'Código da pessoa'
            df_pendencias_temp['Código da pessoa'] = df_pendencias_temp['Código pessoa']
            print("Coluna 'Código da pessoa' atualizada com valores de 'Código pessoa'")

    # Processar cada dataframe separadamente
    for df, nome in [(df_multas_temp, "Multas"), (df_pendencias_temp, "Pendências")]:
        # Renomear colunas conforme o mapeamento
        df.rename(columns=mapeamento_colunas, inplace=True)

        # Adicionar colunas faltantes com valores vazios
        for coluna in colunas_essenciais:
            if coluna not in df.columns:
                df[coluna] = ""
                print(f"Aviso: Coluna '{coluna}' não encontrada no relatório de {nome}. Adicionando coluna vazia.")

        # Garantir que 'Valor multa' seja numérico
        if 'Valor multa' in df.columns:
            df['Valor multa'] = pd.to_numeric(df['Valor multa'], errors='coerce').fillna(0)

        # Converter colunas de data para garantir compatibilidade
        for col in ['Data de empréstimo', 'Data devolução prevista', 'Data devolução efetivada']:
            if col in df.columns:
                try:
                    # Padronizar o formato de data - especificando formato brasileiro
                    df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
                except:
                    print(f"Aviso: Não foi possível converter coluna {col} para data")

    # Selecionar apenas as colunas essenciais
    df_multas_filtered = df_multas_temp[colunas_essenciais].copy()
    df_pendencias_filtered = df_pendencias_temp[colunas_essenciais].copy()

    # Modificar os dados do DataFrame para tratar as chaves
    # Para registros onde 'Número chave' não está vazio, ajustar o título e datas
    for df in [df_multas_filtered, df_pendencias_filtered]:
        mask_chave = (~df['Número chave'].isna()) & (df['Número chave'].astype(str).str.strip() != "")

        if mask_chave.any():
            print(f"Encontrados {mask_chave.sum()} registros com chaves.")

            # Adicionar uma coluna dias_atraso com o mesmo valor da multa para registros com chave
            if 'Valor multa' in df.columns:
                # Adicionar coluna dias_atraso se não existir
                if 'dias_atraso' not in df.columns:
                    df['dias_atraso'] = 0

                # Para registros com chave, definir dias_atraso igual ao valor da multa
                df.loc[mask_chave, 'dias_atraso'] = df.loc[mask_chave, 'Valor multa']
                print("Dias de atraso definidos como o valor da multa para registros com chaves.")

            # Para títulos vazios, usar apenas "Chave: número" como título
            mask_titulo_vazio = mask_chave & (df['Título'].isna() | df['Título'].astype(str).str.strip().eq(''))
            chaves_inteiras = df.loc[mask_titulo_vazio, 'Número chave'].astype(float).astype(int)
            df.loc[mask_titulo_vazio, 'Título'] = "Chave: " + chaves_inteiras.astype(str)

            # Para títulos não vazios, concatenar o número da chave
            mask_titulo_nao_vazio = mask_chave & ~mask_titulo_vazio
            chaves_inteiras = df.loc[mask_titulo_nao_vazio, 'Número chave'].astype(float).astype(int)
            df.loc[mask_titulo_nao_vazio, 'Título'] = df.loc[mask_titulo_nao_vazio, 'Título'] + " - Chave: " + chaves_inteiras.astype(str)

            # Fazer data de empréstimo igual à data de devolução prevista para registros com chave
            df.loc[mask_chave, 'Data de empréstimo'] = df.loc[mask_chave, 'Data devolução prevista']

            print("Títulos e datas de empréstimo atualizados para registros com chaves.")
        else:
            print("Nenhum registro com chave encontrado.")

    # Corrigir problema de colunas duplicadas
    # Verificar se há colunas duplicadas e renomeá-las se necessário
    if df_pendencias_filtered.columns.duplicated().any():
        # Criar lista de nomes de colunas únicos
        cols = pd.Series(df_pendencias_filtered.columns)
        for dup in cols[cols.duplicated()].unique():
            cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
        # Renomear as colunas do DataFrame
        df_pendencias_filtered.columns = cols
        print("Aviso: Colunas duplicadas encontradas e renomeadas no relatório de Pendências.")

    if df_multas_filtered.columns.duplicated().any():
        # Criar lista de nomes de colunas únicos
        cols = pd.Series(df_multas_filtered.columns)
        for dup in cols[cols.duplicated()].unique():
            cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
        # Renomear as colunas do DataFrame
        df_multas_filtered.columns = cols
        print("Aviso: Colunas duplicadas encontradas e renomeadas no relatório de Multas.")

    # Converter para dicionários para evitar problemas de índice
    multas_dict = df_multas_filtered.to_dict('records')
    pendencias_dict = df_pendencias_filtered.to_dict('records')

    # Criar um novo DataFrame a partir da combinação das listas
    df_unificado = pd.DataFrame(multas_dict + pendencias_dict)

    return df_unificado

# TESTANDO O MÓDULO
# if __name__ == "__main__":
#     # Exemplo de uso (pode ser removido ou usado para testes)
#     try:
#         # Use verificar_data=False para testes com arquivos antigos
#         df = read_excel_file('elian.oliveira_2025-02-24-23-42-07.xlsx', verificar_data=True)
#         df = clean_column_names(df)
#         print("Conteúdo do arquivo Excel:")
#         print(df)

#         summary = get_summary(df)
#         print("Resumo do arquivo:")
#         print(f"Linhas: {summary['num_rows']}\nPessoas únicas: {summary['num_unique_users']}\nTotal de multas: R$ {summary['total_fines']:.2f}")
#     except ValueError as e:
#         print(f"Erro de validação: {str(e)}")
#     except Exception as e:
#         print(f"Erro no processamento: {str(e)}")