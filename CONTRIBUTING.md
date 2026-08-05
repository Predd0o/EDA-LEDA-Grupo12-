	# Como contribuir

Este documento descreve os fluxos de trabalho do projeto **Análise Comparativa de Desempenho de Segment Trees** (Python, Rust, C++ e Java). Cada atividade pertence a um de quatro tipos: **Implementação**, **Experimentação**, **Análise** ou **Utilitários**.

---

## Padrões gerais

### Idioma

Todos os commits, nomes de branch e comentários de código devem ser escritos em **inglês**.

### Convenção de commits

Os commits devem seguir o padrão [Conventional Commits](https://www.conventionalcommits.org):

```
<tipo>(<escopo>): <descrição curta>
```

**Tipos disponíveis:**

| Tipo | Quando usar |
|---|---|
| `feat` | Adição de nova funcionalidade (ex: implementação de uma operação da árvore) |
| `fix` | Correção de bug ou comportamento incorreto |
| `refactor` | Refatoração de código sem mudança de comportamento |
| `perf` | Mudança com foco exclusivo em performance |
| `test` | Adição ou correção de testes |
| `docs` | Alterações em documentação |
| `chore` | Tarefas de manutenção (dependências, configurações, Docker) |

**Escopo:** use a linguagem ou componente afetado — `cpp`, `rust`, `java`, `python`, `scripts`, `analysis`.

**Exemplos:**

```bash
feat(rust): implement lazy propagation for range update
fix(java): correct off-by-one in build() recursion
perf(cpp): use iterative build instead of recursive
test(python): add stress test for range sum query
docs: update methodology section in README
```

---

### Nomenclatura de branches

Use sempre **inglês** e o prefixo adequado ao tipo de trabalho:

| Prefixo | Uso |
|---|---|
| `impl/` | Implementação da Segment Tree em uma linguagem |
| `script/` | Scripts de geração de entradas, orquestração ou análise |
| `fix/` | Correção de bug em qualquer componente |
| `util/` | Tarefas utilitárias (Docker, README, board) |

**Exemplos:**

```
impl/rust-segment-tree
impl/java-lazy-propagation
script/input-generator
script/orchestrator
fix/cpp-lazy-propagation-bounds
util/docker-setup
util/final-report
```

---

### Padrão de Pull Request

Todo PR aberto no repositório deve seguir o formato abaixo no título e na descrição.

**Título:**

```
<tipo>(<escopo>): <descrição curta>
```

Seguindo a mesma convenção de commits.

**Descrição (corpo do PR):**

```markdown
## O que foi feito
Descrição objetiva da mudança implementada e a motivação por trás dela.

## Como testar
Passos para reproduzir e verificar o comportamento localmente (ex: comandos de build/run/test).

## Issue relacionada
Closes #<número>
```

Todo PR deve passar por revisão de pelo menos um outro integrante antes do merge para `Main`.

---

### Nomenclatura de arquivos

| Prefixo | Tipo | Localização | Exemplo |
|---|---|---|---|
| `gen_` | Script de geração de entradas | `scripts/` | `gen_input.py` |
| `orchestrator` | Script de orquestração dos experimentos | `scripts/` | `orchestrator.sh` |
| `analyze_` | Script de análise/geração de gráficos | `scripts/` | `analyze_results.py` |
| `results.csv` | Resultado bruto agregado de um batch de experimentos | `results/` | `results.csv` |
| `Dockerfile` | Ambiente isolado para execução dos benchmarks | `setup/` | `Dockerfile` |

O `orchestrator.sh` grava uma linha por execução (linguagem, N, M, carga, operação, tempo e nós visitados) em `results/results.csv`, consumido pelos scripts de análise.

---

## Estrutura do repositório

```
EDA-LEDA-Grupo12-/
├── segtree_cpp/          # implementação em C++
├── segtree_rust/         # implementação em Rust
├── segtree_java/         # implementação em Java
├── segtree_python/       # implementação em Python
├── scripts/              # geração de entradas, orquestração, análise
├── setup/                # Dockerfile e instruções de ambiente
├── data/                 # entradas geradas (CSV)
├── results/              # resultados brutos (CSV), gráficos e relatório final
└── README.md             # metodologia, resultados e conclusões
```

| Pasta | Conteúdo |
|---|---|
| `segtree_<linguagem>/` | Implementação da estrutura de dados em cada linguagem |
| `scripts/` | Geração de entradas, orquestração dos experimentos, geração de gráficos |
| `setup/` | Dockerfile e instruções do ambiente isolado |
| `data/` | Entradas geradas (CSV) |
| `results/` | Resultados brutos (CSV), gráficos e relatório final |

---

## Tipos de atividade

### 1. Implementação

O membro responsável implementa a Segment Tree (build, query, update e, em seguida, lazy propagation) em sua linguagem designada.

**Fluxo:**

```bash
git clone https://github.com/Predd0o/EDA-LEDA-Grupo12-.git
cd EDA-LEDA-Grupo12-

# 1. Criar uma branch descritiva (em inglês)
git checkout -b impl/rust-segment-tree

# 2. Implementar dentro da pasta da linguagem
cd segtree_rust

# 3. Commitar seguindo a convenção de commits (em inglês)
git add .
git commit -m "feat(rust): implement build, query and update"
git push origin impl/rust-segment-tree

# 4. Abrir Pull Request no GitHub
# origem:  impl/rust-segment-tree
# destino: Main
```

**Critérios de correção (antes de abrir o PR):**

- A implementação segue a mesma lógica algorítmica das demais linguagens (array de tamanho ~4n, indexação 1-based com filhos em 2i e 2i+1)
- Testes locais confirmam que os resultados batem com uma implementação de referência (ex: força bruta em Python) para entradas pequenas
- Medição de tempo usa o cronômetro nativo definido no relatório (`std::chrono`, `Instant`, `System.nanoTime()`, `time.perf_counter()`)

---

### 2. Experimentação

O membro responsável executa a bateria de testes de performance em ambiente Docker isolado, seguindo a matriz de experimentos definida no relatório.

**Ambiente:** Docker (definido em `setup/`). Todos os experimentos devem ser executados dentro deste ambiente para garantir reprodutibilidade e evitar viés de máquina.

**Cuidados obrigatórios (ver seção de metodologia do relatório):**

- Warm-up antes das medições em todas as linguagens (5 execuções de aquecimento)
- Nenhum outro processo pesado competindo por CPU durante a execução
- Mesmas entradas (mesma seed) para todas as linguagens em cada configuração

**Fluxo:**

```bash
git checkout Main
git checkout -b script/run-experiments-<config>

# Executar via orquestrador dentro do Docker
bash scripts/orchestrator.sh

# Commitar scripts e resultado CSV
git add scripts/ data/
git commit -m "perf: add experiment results for N=1e6 query-only"
git push origin script/run-experiments-<config>

# Abrir PR para Main
```

**Critérios de validade estatística:**

- Cada configuração (linguagem × N × M × tipo de carga) executada **30 vezes** (com 5 execuções de warm-up), reportando média, mediana e desvio padrão
- Resultados salvos incrementalmente para evitar perda de dados em caso de interrupção

---

### 3. Análise

O membro responsável processa os CSVs em `data/` e gera os gráficos e tabelas-resumo descritos na metodologia (tempo × tamanho da entrada em escala log-log, gráficos facetados por tipo de operação).

**Fluxo:**

```bash
git checkout Main
git checkout -b script/analysis-<tema>

# Gerar gráficos com pandas/matplotlib/seaborn
python scripts/analyze_results.py

git add scripts/ results/
git commit -m "docs: add log-log comparison chart for query time"
git push origin script/analysis-<tema>

# Abrir PR para Main
```

---

### 4. Utilitários

Atividades de suporte ao projeto: ambiente Docker, board do GitHub Projects, README, relatório final.

**Exemplos de tarefas:**

- Criar ou atualizar o `Dockerfile` em `setup/`
- Escrever ou atualizar o `README.md` (metodologia, resultados, conclusões, **ameaças à validade**)
- Configurar o board no GitHub Projects
- Redigir o relatório final do projeto

**Fluxo:**

```bash
git checkout Main
git checkout -b util/docker-setup

git add .
git commit -m "chore: add docker setup for all languages"
git push origin util/docker-setup

# Abrir PR para Main
```

---

## Resumo

| Tipo | Onde trabalha | Branch | PR para |
|---|---|---|---|
| Implementação | `segtree_<linguagem>/` | `impl/<linguagem>-<feature>` | `Main` |
| Experimentação | `scripts/` + Docker | `script/run-experiments-<config>` | `Main` |
| Análise | `scripts/` + `results/` | `script/analysis-<tema>` | `Main` |
| Utilitários | Raiz do repositório | `util/<nome>` | `Main` |
