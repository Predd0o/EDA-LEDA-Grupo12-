import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re

def extrair_distribuicao(nome_arquivo):
    """
    Usa Regex para extrair a distribuição (ex: 'random', 'sorted') de dentro do nome do arquivo.
    """
    match = re.search(r'_s\d+_(.+?)_(query|update|mixed|build)', str(nome_arquivo))
    if not match:
        match = re.search(r'_s\d+_(.+?)\.txt', str(nome_arquivo))
    
    return match.group(1) if match else 'Desconhecida'

def gerar_grafico_barras(df, pasta_saida, operacao, titulo, tipo_carga=None, n_alvo=100000, mult_alvo=5):
    # Filtra pelo N máximo
    df_filtrado = df[df['n'] == n_alvo].copy()
    
    if operacao == 'build':
        df_plot = df_filtrado[df_filtrado['op'] == 'build'].copy()
        y_col = 'tempo_medio_ms'
        ylabel = 'Tempo Total (ms)'
        nome_arquivo = "grafico_distribuicao_build.png"
    else:
        df_plot = df_filtrado[
            (df_filtrado['op'] == 'batch_ops') & 
            (df_filtrado['load'] == tipo_carga) & 
            (df_filtrado['m'] == n_alvo * mult_alvo)
        ].copy()
        
        coluna_tempo = 'tempo_medio_ms' if 'tempo_medio_ms' in df_plot.columns else 'time_ms'
        if coluna_tempo not in df_plot.columns and 'time_ns' in df_plot.columns:
            df_plot['tempo_medio_ms'] = df_plot['time_ns'] / 1e6
            coluna_tempo = 'tempo_medio_ms'
            
        df_plot['tempo_por_op_us'] = (df_plot[coluna_tempo] / df_plot['m']) * 1000
        y_col = 'tempo_por_op_us'
        ylabel = 'Tempo Médio por Operação ($\mu$s)'
        nome_arquivo = f"grafico_distribuicao_{tipo_carga}.png"

    if df_plot.empty:
        print(f"Aviso: Sem dados para gerar {nome_arquivo}.")
        return

    # Verifica o nome da coluna de distribuição ou extrai na hora
    if 'distribution' in df_plot.columns:
        coluna_dist = 'distribution'
    elif 'dist' in df_plot.columns:
        coluna_dist = 'dist'
    elif 'input_file' in df_plot.columns:
        df_plot['dist_extraida'] = df_plot['input_file'].apply(extrair_distribuicao)
        coluna_dist = 'dist_extraida'
    else:
        print(f"Erro Crítico: Não foi possível encontrar a distribuição para {nome_arquivo}.")
        return

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 6))

    # === PADRONIZAÇÃO EXATA DAS CORES ===
    cores_oficiais = {
        'cpp': 'tab:blue',
        'rust': 'tab:red',
        'java': 'tab:orange',
        'python': 'tab:green'
    }

    sns.barplot(
        data=df_plot,
        x=coluna_dist,
        y=y_col,
        hue='language',
        palette=cores_oficiais, # Aplica o dicionário com os tons 'tab:'
        capsize=0.1 
    )

    plt.title(f'{titulo}\n(Tamanho do Array $N = {n_alvo}$)', fontsize=16, pad=15)
    plt.xlabel('Distribuição dos Dados', fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    
    # Formata os nomes no eixo X 
    xticks = plt.gca().get_xticklabels()
    plt.gca().set_xticklabels([t.get_text().replace('_', ' ').title() for t in xticks])
    
    plt.legend(title='Linguagem', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    caminho_completo = os.path.join(pasta_saida, nome_arquivo)
    plt.savefig(caminho_completo, dpi=300)
    plt.close()
    print(f"[{caminho_completo}] gerado com sucesso!")

def main():
    pasta_saida = "distribution_charts"
    os.makedirs(pasta_saida, exist_ok=True)
    
    caminho_csv = "aggregated_results.csv"
    if not os.path.exists(caminho_csv):
        print(f"Erro: Arquivo '{caminho_csv}' não encontrado.")
        return
        
    df = pd.read_csv(caminho_csv)
    
    print("Gerando gráficos de distribuição (N = 100.000)...")
    gerar_grafico_barras(df, pasta_saida, 'build', 'Comparação de Estabilidade: Tempo de Build')
    gerar_grafico_barras(df, pasta_saida, 'batch_ops', 'Comparação de Estabilidade: Consultas (Query - 5N)', tipo_carga='query')
    gerar_grafico_barras(df, pasta_saida, 'batch_ops', 'Comparação de Estabilidade: Atualizações (Update - 5N)', tipo_carga='update')
    gerar_grafico_barras(df, pasta_saida, 'batch_ops', 'Comparação de Estabilidade: Operações Mistas (Mixed - 5N)', tipo_carga='mixed')

    print("Todos os gráficos de distribuição foram processados!")

if __name__ == "__main__":
    main()