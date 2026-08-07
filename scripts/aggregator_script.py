import pandas as pd

def main():
    print("Carregando os dados brutos...")
    # Lê o CSV gerado pelo orquestrador
    df = pd.read_csv("results.csv")

    #Converte nanosegundos para milissegundos
    df['time_ms'] = df['time_ns'] / 1_000_000.0

    print("Calculando médias e desvios padrões...")
    # Agrupa por cenário exato e calcula a média e o std (desvio padrão)
    df_agrupado = df.groupby(
        ['language', 'n', 'm', 'load', 'input_file', 'op']
    ).agg(
        tempo_medio_ms=('time_ms', 'mean'),
        desvio_padrao_ms=('time_ms', 'std'),
        nos_visitados=('nodes_visited', 'first') # Pega o primeiro valor, pois é igual em todas as 30 repetições
    ).reset_index()

    # Salva o resultado em um novo arquivo CSV
    nome_saida = "aggregated_results.csv"
    df_agrupado.to_csv(nome_saida, index=False)
    
    print(f"Sucesso! Arquivo '{nome_saida}' gerado com {len(df_agrupado)} linhas.")

if __name__ == "__main__":
    main()
