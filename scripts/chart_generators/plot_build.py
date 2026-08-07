import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    print("Carregando dados agregados...")
    # 1. Carregar os dados que você limpou no passo anterior
    df = pd.read_csv("aggregated_results.csv")

    # 2. Filtrar apenas a operação de 'build'
    df_build = df[df['op'] == 'build'].copy()

    # Como temos várias configurações para o mesmo N (cargas, distribuições),
    # tiramos a média geral do build para cada N e Linguagem.
    # (O tempo de build só depende do N e não da distribuição dos dados).
    df_plot = df_build.groupby(['language', 'n'])['tempo_medio_ms'].mean().reset_index()

    # 3. Configurar o estilo visual (o Seaborn deixa com "cara de artigo científico")
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))

    # O PULO DO GATO: Se usarmos N como número, o gráfico espreme o 100, 1000 e 10000 
    # no canto esquerdo. Ao transformar em 'string', o gráfico dá o mesmo espaçamento para todos.
    df_plot['n_str'] = df_plot['n'].astype(str)
    
    # 4. Criar o gráfico de linhas
    sns.lineplot(
        data=df_plot, 
        x='n_str', 
        y='tempo_medio_ms', 
        hue='language', 
        marker='o',       # Coloca as "bolinhas" nos pontos
        linewidth=2,
        markersize=8
    )

    # 5. Colocar títulos e ajustar legendas
    plt.title('Tempo de Construção da Árvore (Build) por Tamanho do Array', fontsize=14, pad=15)
    plt.xlabel('Tamanho do Array (N)', fontsize=12)
    plt.ylabel('Tempo Médio (ms)', fontsize=12)
    plt.legend(title='Linguagem', fontsize=10)

    # 6. Salvar a imagem como PNG em alta resolução
    nome_imagem = "build_chart.png"
    plt.tight_layout()
    plt.savefig(nome_imagem, dpi=300)
    print(f"Sucesso! Imagem '{nome_imagem}' gerada na pasta do projeto.")

if __name__ == "__main__":
    main()