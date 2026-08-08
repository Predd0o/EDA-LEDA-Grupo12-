import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    df = pd.read_csv("aggregated_results.csv")
    df_build = df[df['op'] == 'build'].copy()
    
    # Mantém o 'n' como número, ao invés de String
    df_plot = df_build.groupby(['language', 'n'])['tempo_medio_ms'].mean().reset_index()

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))

    sns.lineplot(
        data=df_plot, 
        x='n',            # Usa o N numérico
        y='tempo_medio_ms', 
        hue='language', 
        marker='o',
        linewidth=2,
        markersize=8
    )

    #Escala logarítmica nos dois eixos
    plt.xscale('log')
    plt.yscale('log')

    plt.title('Tempo de Construção (Build) - Escala Log-Log', fontsize=14, pad=15)
    plt.xlabel('Tamanho do Array (N)', fontsize=12)
    plt.ylabel('Tempo Médio (ms)', fontsize=12)
    plt.legend(title='Linguagem')

    plt.tight_layout()
    plt.savefig("build_chart_loglog.png", dpi=300)

if __name__ == "__main__":
    main()