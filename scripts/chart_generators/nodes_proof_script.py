import pandas as pd
import re

def extrair_distribuicao(nome_arquivo):
    match = re.search(r'_s\d+_(.+?)_(query|update|mixed)', str(nome_arquivo))
    return match.group(1).capitalize() if match else 'N/A'

def main():
    print("Analisando a variância dos Nós Visitados...\n")
    
    # 1. Carrega os dados
    df = pd.read_csv("aggregated_results.csv")
    df_batch = df[df['op'] == 'batch_ops'].copy()
    
    # 2. Extrai a distribuição para deixar a tabela legível
    if 'input_file' in df_batch.columns:
        df_batch['Distribuição'] = df_batch['input_file'].apply(extrair_distribuicao)
    
    # 3. Vamos filtrar apenas o cenário de 100.000 e pegar os testes de Carga Aleatória
    df_amostra = df_batch[(df_batch['n'] == 100000) & (df_batch['Distribuição'] == 'Random')]
    
    # 4. Agrupa os dados e calcula a Média e o Desvio Padrão (std) dos nós visitados
    agrupamento = df_amostra.groupby(['load', 'n', 'm'])['nos_visitados']
    tabela = agrupamento.agg(['mean', 'std']).reset_index()
    
    # 5. Formata a tabela para apresentação
    tabela.rename(columns={
        'load': 'Tipo de Carga',
        'n': 'Tamanho (N)',
        'm': 'Operações (M)',
        'mean': 'Nós Visitados (Média)',
        'std': 'Desvio Padrão'
    }, inplace=True)
    
    # Preenche possíveis NaNs com 0 e formata os números
    tabela['Desvio Padrão'] = tabela['Desvio Padrão'].fillna(0).apply(lambda x: f"{x:.2f}")
    tabela['Nós Visitados (Média)'] = tabela['Nós Visitados (Média)'].astype(int)
    tabela['Tipo de Carga'] = tabela['Tipo de Carga'].str.capitalize()
    
    # 6. Salva a tabela diretamente em um arquivo CSV
    nome_arquivo_saida = "nodes_proof.csv"
    tabela.to_csv(nome_arquivo_saida, index=False, encoding='utf-8')
    print(f"✅ Sucesso! A tabela foi salva no arquivo: '{nome_arquivo_saida}'")
    
    # 7. Verificação de integridade global oculta
    desvio_maximo = df_batch.groupby(['load', 'n', 'm', 'Distribuição'])['nos_visitados'].std().max()
    print(f"Verificação Global: O maior desvio padrão encontrado em toda a base foi: {desvio_maximo:.2f}")

if __name__ == "__main__":
    main()