import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import warnings
warnings.filterwarnings('ignore')

# Configurações
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")
pd.set_option('display.max_columns', None)

print("="*80)
print("MINERAÇÃO DE DADOS - DATASET DE MEDICAMENTOS")
print("="*80)

# ============================================================================
# 1. ETL - EXTRAÇÃO, TRANSFORMAÇÃO E CARREGAMENTO
# ============================================================================
print("\n[1] FASE ETL - EXTRAÇÃO, TRANSFORMAÇÃO E CARREGAMENTO\n")

df = pd.read_csv("medications_details_complete.csv")

print("a) EXTRAÇÃO - Dados Brutos Carregados:")
print(f"   Linhas: {df.shape[0]} | Colunas: {df.shape[1]}")
print(f"\n   Primeiras linhas:\n{df.head()}\n")

# TRANSFORMAÇÃO
print("b) TRANSFORMAÇÃO - Limpeza e Preparação dos Dados:\n")

# Renomear colunas para facilitar
df.columns = ['Name', 'Quantidade', 'Dose', 'Preço', 'Codigo_Barras', 'Infos']

# Limpar preço: remover "R$", espaços e converter vírgula para ponto
df['Preço'] = df['Preço'].str.replace('R$', '', regex=False)
df['Preço'] = df['Preço'].str.strip()
df['Preço'] = df['Preço'].str.replace(',', '.', regex=False)
df['Preço'] = pd.to_numeric(df['Preço'], errors='coerce')
print(f"   ✓ Preço convertido para numérico")

# Limpar quantidade: remover "Unidades" e converter
df['Quantidade'] = df['Quantidade'].astype(str).str.replace('Unidades', '', regex=False)
df['Quantidade'] = df['Quantidade'].str.strip()
df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce')
print(f"   ✓ Quantidade convertida para numérico")

# Extrair valor numérico da dose
df['DoseValor'] = df['Dose'].astype(str).str.extract(r'(\d+\.?\d*)').astype(float)
print(f"   ✓ Extraído valor numérico da dose")

# Preço: preencher valores faltantes com a mediana
media_preco = df['Preço'].median()
df['Preço_limpo'] = df['Preço'].fillna(media_preco)
print(f"   ✓ Preços faltantes preenchidos com mediana: R$ {media_preco:.2f}")

# Quantidade: preencher valores faltantes com a moda
moda_quantidade = df['Quantidade'].mode()
if len(moda_quantidade) > 0:
    df['Quantidade'].fillna(moda_quantidade[0], inplace=True)
else:
    df['Quantidade'].fillna(1, inplace=True)
print(f"   ✓ Quantidade preenchida com moda")

# Criar categorias de preço
df['CategoriaPreco'] = pd.cut(df['Preço_limpo'], 
                               bins=[0, 50, 200, 1000, 5000],
                               labels=['Baixo', 'Médio', 'Alto', 'Muito Alto'])
print(f"   ✓ Categorias de preço criadas")

print(f"\n   Resumo após transformação:")
print(f"   Valores faltantes totais: {df.isnull().sum().sum()}")
print(f"   Dados prontos para análise!\n")

# CARREGAMENTO
print("c) CARREGAMENTO - Dataset Final:")
print(f"   Dataset em memória: {df.shape[0]} registros × {df.shape[1]} atributos")
print(f"\n   Amostra dos dados transformados:")
print(df[['Name', 'Quantidade', 'DoseValor', 'Preço_limpo', 'CategoriaPreco']].head(10).to_string())
print()

# ============================================================================
# 2. ANÁLISE EXPLORATÓRIA
# ============================================================================
print("\n" + "="*80)
print("[2] ANÁLISE EXPLORATÓRIA DOS DADOS")
print("="*80 + "\n")

print("Estatísticas Descritivas:\n")
print(df[['Quantidade', 'DoseValor', 'Preço_limpo']].describe())

print(f"\n\nDistribuição por Tipo de Medicamento:")
print(df['Infos'].value_counts().head(10))

print(f"\n\nDistribuição por Categoria de Preço:")
print(df['CategoriaPreco'].value_counts().sort_index())

# ============================================================================
# 3. PREPARAÇÃO PARA CLUSTERING
# ============================================================================
print("\n" + "="*80)
print("[3] PRÉ-PROCESSAMENTO PARA CLUSTERING")
print("="*80 + "\n")

# Remover linhas com NaN nas features essenciais
df_clean = df[['Name', 'Quantidade', 'DoseValor', 'Preço_limpo', 'Infos']].dropna()

# Selecionar features para clustering
features = ['Quantidade', 'DoseValor', 'Preço_limpo']
X = df_clean[features].copy()

print(f"Features selecionadas: {features}")
print(f"Registros com dados completos: {len(X)}")
print(f"\nDados antes da normalização:\n{X.describe()}\n")

# Normalização
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_scaled_df = pd.DataFrame(X_scaled, columns=features)

print(f"Dados após normalização (StandardScaler):\n{X_scaled_df.describe()}\n")

# ============================================================================
# 4. ALGORITMO K-MEANS CLUSTERING
# ============================================================================
print("="*80)
print("[4] ALGORITMO K-MEANS - CLUSTERING")
print("="*80 + "\n")

# Encontrar número ótimo de clusters (Elbow Method)
print("a) Determinação do número ótimo de clusters:\n")
inertias = []
silhouette_scores = []
K_range = range(2, 8)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(X_scaled, kmeans.labels_))
    print(f"   K={k}: Inércia={kmeans.inertia_:.2f} | Silhueta={silhouette_scores[-1]:.3f}")

# Escolher K com melhor silhueta
optimal_k = K_range[np.argmax(silhouette_scores)]
print(f"\n   → Número ótimo de clusters: K={optimal_k}\n")

# Aplicar K-means com k ótimo
kmeans_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df_clean['Cluster'] = kmeans_final.fit_predict(X_scaled)

print(f"b) Clusters Encontrados:\n")
for i in range(optimal_k):
    cluster_data = df_clean[df_clean['Cluster'] == i]
    print(f"   Cluster {i}: {len(cluster_data)} medicamentos")
    print(f"      Preço médio: R$ {cluster_data['Preço_limpo'].mean():.2f}")
    print(f"      Dose média: {cluster_data['DoseValor'].mean():.2f}mg")
    print(f"      Quantidade média: {cluster_data['Quantidade'].mean():.0f} unidades\n")

# ============================================================================
# 5. VISUALIZAÇÕES
# ============================================================================
print("="*80)
print("[5] GERANDO VISUALIZAÇÕES")
print("="*80 + "\n")

fig = plt.figure(figsize=(18, 12))

# Gráfico 1: Elbow Method
ax1 = plt.subplot(2, 3, 1)
ax1.plot(K_range, inertias, 'bo-', linewidth=2, markersize=8)
ax1.axvline(x=optimal_k, color='red', linestyle='--', linewidth=2, label=f'K ótimo = {optimal_k}')
ax1.set_xlabel('Número de Clusters (K)', fontsize=11, fontweight='bold')
ax1.set_ylabel('Inércia', fontsize=11, fontweight='bold')
ax1.set_title('Elbow Method - Determinação de K Ótimo', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Gráfico 2: Silhueta
ax2 = plt.subplot(2, 3, 2)
ax2.plot(K_range, silhouette_scores, 'ro-', linewidth=2, markersize=8)
ax2.axvline(x=optimal_k, color='green', linestyle='--', linewidth=2, label=f'K ótimo = {optimal_k}')
ax2.set_xlabel('Número de Clusters (K)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Coeficiente de Silhueta', fontsize=11, fontweight='bold')
ax2.set_title('Análise de Silhueta por K', fontsize=12, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)

# Gráfico 3: Distribuição de Preços
ax3 = plt.subplot(2, 3, 3)
df_clean.boxplot(column='Preço_limpo', by='Cluster', ax=ax3)
ax3.set_xlabel('Cluster', fontsize=11, fontweight='bold')
ax3.set_ylabel('Preço (R$)', fontsize=11, fontweight='bold')
ax3.set_title('Distribuição de Preços por Cluster', fontsize=12, fontweight='bold')
plt.sca(ax3)

# Gráfico 4: Scatter - Preço vs Dose
ax4 = plt.subplot(2, 3, 4)
colors = sns.color_palette("husl", optimal_k)
for i in range(optimal_k):
    cluster_data = df_clean[df_clean['Cluster'] == i]
    ax4.scatter(cluster_data['DoseValor'], cluster_data['Preço_limpo'], 
               label=f'Cluster {i}', s=100, alpha=0.7, color=colors[i])
ax4.set_xlabel('Dose (mg)', fontsize=11, fontweight='bold')
ax4.set_ylabel('Preço (R$)', fontsize=11, fontweight='bold')
ax4.set_title('Preço vs Dose por Cluster', fontsize=12, fontweight='bold')
ax4.legend()
ax4.grid(True, alpha=0.3)

# Gráfico 5: Scatter - Quantidade vs Preço
ax5 = plt.subplot(2, 3, 5)
for i in range(optimal_k):
    cluster_data = df_clean[df_clean['Cluster'] == i]
    ax5.scatter(cluster_data['Quantidade'], cluster_data['Preço_limpo'], 
               label=f'Cluster {i}', s=100, alpha=0.7, color=colors[i])
ax5.set_xlabel('Quantidade (unidades)', fontsize=11, fontweight='bold')
ax5.set_ylabel('Preço (R$)', fontsize=11, fontweight='bold')
ax5.set_title('Preço vs Quantidade por Cluster', fontsize=12, fontweight='bold')
ax5.legend()
ax5.grid(True, alpha=0.3)

# Gráfico 6: Contagem de medicamentos por cluster
ax6 = plt.subplot(2, 3, 6)
cluster_counts = df_clean['Cluster'].value_counts().sort_index()
bars = ax6.bar(cluster_counts.index, cluster_counts.values.astype(int), color=colors)
ax6.set_xlabel('Cluster', fontsize=11, fontweight='bold')
ax6.set_ylabel('Quantidade de Medicamentos', fontsize=11, fontweight='bold')
ax6.set_title('Distribuição de Medicamentos por Cluster', fontsize=12, fontweight='bold')
for bar in bars:
    height = bar.get_height()
    ax6.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('analise_medicamentos.png', dpi=300, bbox_inches='tight')
print("✓ Visualizações salvas em 'analise_medicamentos.png'\n")
plt.show()

# ============================================================================
# 6. INTERPRETAÇÃO DOS RESULTADOS
# ============================================================================
print("="*80)
print("[6] INTERPRETAÇÃO E INSIGHTS")
print("="*80 + "\n")

for i in range(optimal_k):
    cluster_data = df_clean[df_clean['Cluster'] == i]
    print(f"📊 CLUSTER {i}:")
    print(f"   Tamanho: {len(cluster_data)} medicamentos ({len(cluster_data)/len(df_clean)*100:.1f}%)")
    print(f"   Exemplos: {', '.join(cluster_data['Name'].unique()[:3])}")
    
    preco_min = cluster_data['Preço_limpo'].min()
    preco_max = cluster_data['Preço_limpo'].max()
    preco_media = cluster_data['Preço_limpo'].mean()
    
    print(f"   Preço - Mín: R$ {preco_min:.2f} | Máx: R$ {preco_max:.2f} | Média: R$ {preco_media:.2f}")
    print(f"   Dose - Min: {cluster_data['DoseValor'].min():.2f}mg | Máx: {cluster_data['DoseValor'].max():.2f}mg | Média: {cluster_data['DoseValor'].mean():.2f}mg")
    print(f"   Quantidade - Min: {cluster_data['Quantidade'].min():.0f} | Máx: {cluster_data['Quantidade'].max():.0f} | Média: {cluster_data['Quantidade'].mean():.0f}")
    print(f"   Tipos: {cluster_data['Infos'].value_counts().head(2).to_dict()}")
    print()

# ============================================================================
# 7. REGRAS DE ASSOCIAÇÃO (APRIORI)
# ============================================================================
print("="*80)
print("[7] ANÁLISE DE PADRÕES E ASSOCIAÇÕES")
print("="*80 + "\n")

# Criar variáveis categóricas para regras
df_clean['TipoPreco'] = pd.cut(df_clean['Preço_limpo'], 
                          bins=[0, 100, 500, 3000],
                          labels=['Baixo', 'Médio', 'Alto'])
df_clean['TipoDose'] = pd.cut(df_clean['DoseValor'],
                         bins=[0, 50, 200, float('inf')],
                         labels=['Baixa', 'Média', 'Alta'])

print("Padrões de Associação Descobertos:\n")

# Análise de correlação entre atributos
print("a) Correlações entre atributos numéricos:\n")
correlacao = df_clean[['Quantidade', 'DoseValor', 'Preço_limpo']].corr()
print(correlacao.to_string())

# Regras práticas
print("\n\nb) Regras Descobertas:\n")

for i in range(optimal_k):
    cluster_data = df_clean[df_clean['Cluster'] == i]
    preco_medio = cluster_data['Preço_limpo'].mean()
    dose_media = cluster_data['DoseValor'].mean()
    qtd_media = cluster_data['Quantidade'].mean()
    
    if preco_medio < 100:
        categoria = "Medicamentos ECONÓMICOS"
    elif preco_medio < 500:
        categoria = "Medicamentos de PREÇO MÉDIO"
    else:
        categoria = "Medicamentos PREMIUM"
    
    print(f"   Regra {i+1} (Cluster {i}):")
    print(f"      Categoria: {categoria}")
    print(f"      Padrão: Preço ~R${preco_medio:.2f} + Dose ~{dose_media:.0f}mg + Qtd ~{qtd_media:.0f} un")
    print()

# Exportar resultados
print("\n" + "="*80)
print("[8] EXPORTANDO RESULTADOS")
print("="*80 + "\n")

df_clean.to_csv('medicamentos_clusterizados.csv', index=False, encoding='utf-8')
print("✓ Dataset com clusters exportado: 'medicamentos_clusterizados.csv'")

print("\n" + "="*80)
print("✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
print("="*80)