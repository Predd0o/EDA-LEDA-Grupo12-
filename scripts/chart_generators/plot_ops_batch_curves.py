import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def gerar_grafico(df, tipo_carga, multiplicador, pasta_saida):
    """
    Filtra os dados e gera um gráfico 2x2 para a carga e multiplicador especificados,
    salvando-o na pasta de saída.
    """
    df_filtrado = df[
        (df['op'] == 'batch_ops') & 
        (df['load'] == tipo_carga) & 
        (df['m'] == df['n'] * multiplicador)
    ].copy()

    df_plot = df_filtrado.groupby(['language', 'n', 'm'])['tempo_medio_ms'].mean().reset_index()
    df_plot['tempo_por_op_us'] = (df_plot['tempo_medio_ms'] / df_plot['m']) * 1000

    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    titulo_carga = tipo_carga.capitalize()
    fig.suptitle(f'Curva de Tempo por Operação ({titulo_carga} - Lote de {multiplicador}N)', fontsize=16)

    linguagens = ['cpp', 'rust', 'java', 'python']
    cores = ['tab:blue', 'tab:red', 'tab:orange', 'tab:green']

    for ax, lang, cor in zip(axes.flatten(), linguagens, cores):
        data = df_plot[df_plot['language'] == lang].sort_values('n')
        
        if data.empty:
            continue
        
        sns.lineplot(ax=ax, data=data, x='n', y='tempo_por_op_us', marker='o', color=cor, linewidth=2)
        
        ultimo_n = data['n'].max()
        ultimo_y = data['tempo_por_op_us'].values[-1]
        
        constante_c = ultimo_y / np.log2(ultimo_n)
        
        x_suave = np.linspace(data['n'].min(), data['n'].max(), 500)
        y_suave = constante_c * np.log2(x_suave)
        
        ax.plot(x_suave, y_suave, linestyle='--', color='gray', alpha=0.7, label='Teoria O(log N)')
        
        ax.set_title(f'Linguagem: {lang.upper()}')
        ax.set_xlabel('Tamanho do Array (N) - Linear')
        ax.set_ylabel('Tempo ($\mu$s)')
        ax.legend()
        ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0)) 

    plt.tight_layout()
    
    # Monta o caminho completo da imagem apontando para a nova pasta
    nome_arquivo = f"grafico_batch_{tipo_carga}_{multiplicador}N.png"
    caminho_completo = os.path.join(pasta_saida, nome_arquivo)
    
    plt.savefig(caminho_completo, dpi=300)
    plt.close() 
    print(f"[{caminho_completo}] gerado com sucesso!")

def main():
    print("Iniciando a geração de gráficos das operações (Batch)...")
    
    # 1. Define o nome da pasta e a cria se não existir
    pasta_saida = "operation_charts"
    os.makedirs(pasta_saida, exist_ok=True)
    
    caminho_csv = "aggregated_results.csv"
    if not os.path.exists(caminho_csv):
        print(f"Erro: O arquivo '{caminho_csv}' não foi encontrado.")
        return
        
    df = pd.read_csv(caminho_csv)
    
    cargas = ['query', 'update', 'mixed']
    multiplicadores = [1, 5]
    
    # 2. Passa a variável da pasta_saida para a função
    for mult in multiplicadores:
        for carga in cargas:
            gerar_grafico(df, carga, mult, pasta_saida)
            
    print(f"Todos os 6 gráficos foram gerados e salvos na pasta '{pasta_saida}/'!")

if __name__ == "__main__":
    main()