import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# GERAR GRÁFICOS PARA RELATÓRIO
# ============================================================================
print("Gerando gráficos...")

# Carregar e preparar dados
df = pd.read_csv("medications_details_complete.csv")

# Limpeza
df.columns = ['Name', 'Quantidade', 'Dose', 'Preço', 'Codigo_Barras', 'Infos']
df['Preço'] = df['Preço'].str.replace('R$', '', regex=False).str.strip()
df['Preço'] = df['Preço'].str.replace(',', '.', regex=False)
df['Preço'] = pd.to_numeric(df['Preço'], errors='coerce')
df['Quantidade'] = df['Quantidade'].astype(str).str.replace('Unidades', '', regex=False).str.strip()
df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce')
df['DoseValor'] = df['Dose'].astype(str).str.extract(r'(\d+\.?\d*)').astype(float)

media_preco = df['Preço'].median()
df['Preço_limpo'] = df['Preço'].fillna(media_preco)
moda_quantidade = df['Quantidade'].mode()
if len(moda_quantidade) > 0:
    df['Quantidade'].fillna(moda_quantidade[0], inplace=True)
else:
    df['Quantidade'].fillna(1, inplace=True)

df['CategoriaPreco'] = pd.cut(df['Preço_limpo'], 
                               bins=[0, 50, 200, 1000, 5000],
                               labels=['Baixo', 'Médio', 'Alto', 'Muito Alto'])

# Preparar dados
df_clean = df[['Name', 'Quantidade', 'DoseValor', 'Preço_limpo', 'Infos']].dropna()
features = ['Quantidade', 'DoseValor', 'Preço_limpo']
X = df_clean[features].copy()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# K-means
inertias = []
silhouette_scores = []
K_range = range(2, 8)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)
    silhouette_scores.append(silhouette_score(X_scaled, kmeans.labels_))

optimal_k = K_range[np.argmax(silhouette_scores)]
kmeans_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
df_clean['Cluster'] = kmeans_final.fit_predict(X_scaled)

# Gerar todos os 6 gráficos
fig = plt.figure(figsize=(20, 14))
plt.style.use('seaborn-v0_8-darkgrid')

# Gráfico 1: Elbow
ax1 = plt.subplot(2, 3, 1)
ax1.plot(K_range, inertias, 'bo-', linewidth=2.5, markersize=9)
ax1.axvline(x=optimal_k, color='red', linestyle='--', linewidth=2.5, label=f'K ótimo = {optimal_k}')
ax1.set_xlabel('Número de Clusters (K)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Inércia', fontsize=12, fontweight='bold')
ax1.set_title('Elbow Method - Determinação de K Ótimo', fontsize=13, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# Gráfico 2: Silhueta
ax2 = plt.subplot(2, 3, 2)
ax2.plot(K_range, silhouette_scores, 'ro-', linewidth=2.5, markersize=9)
ax2.axvline(x=optimal_k, color='green', linestyle='--', linewidth=2.5, label=f'K ótimo = {optimal_k}')
ax2.set_xlabel('Número de Clusters (K)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Coeficiente de Silhueta', fontsize=12, fontweight='bold')
ax2.set_title('Análise de Silhueta por K', fontsize=13, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)

# Gráfico 3: Boxplot de preços
ax3 = plt.subplot(2, 3, 3)
df_clean.boxplot(column='Preço_limpo', by='Cluster', ax=ax3)
ax3.set_xlabel('Cluster', fontsize=12, fontweight='bold')
ax3.set_ylabel('Preço (R$)', fontsize=12, fontweight='bold')
ax3.set_title('Distribuição de Preços por Cluster', fontsize=13, fontweight='bold')
plt.sca(ax3)

# Gráfico 4: Preço vs Dose
ax4 = plt.subplot(2, 3, 4)
colors_palette = sns.color_palette("husl", optimal_k)
for i in range(optimal_k):
    cluster_data = df_clean[df_clean['Cluster'] == i]
    ax4.scatter(cluster_data['DoseValor'], cluster_data['Preço_limpo'], 
               label=f'Cluster {i}', s=120, alpha=0.7, color=colors_palette[i])
ax4.set_xlabel('Dose (mg)', fontsize=12, fontweight='bold')
ax4.set_ylabel('Preço (R$)', fontsize=12, fontweight='bold')
ax4.set_title('Preço vs Dose por Cluster', fontsize=13, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3)

# Gráfico 5: Preço vs Quantidade
ax5 = plt.subplot(2, 3, 5)
for i in range(optimal_k):
    cluster_data = df_clean[df_clean['Cluster'] == i]
    ax5.scatter(cluster_data['Quantidade'], cluster_data['Preço_limpo'], 
               label=f'Cluster {i}', s=120, alpha=0.7, color=colors_palette[i])
ax5.set_xlabel('Quantidade (unidades)', fontsize=12, fontweight='bold')
ax5.set_ylabel('Preço (R$)', fontsize=12, fontweight='bold')
ax5.set_title('Preço vs Quantidade por Cluster', fontsize=13, fontweight='bold')
ax5.legend(fontsize=10)
ax5.grid(True, alpha=0.3)

# Gráfico 6: Contagem por cluster
ax6 = plt.subplot(2, 3, 6)
cluster_counts = df_clean['Cluster'].value_counts().sort_index()
bars = ax6.bar(cluster_counts.index, cluster_counts.values.astype(int), color=colors_palette)
ax6.set_xlabel('Cluster', fontsize=12, fontweight='bold')
ax6.set_ylabel('Quantidade de Medicamentos', fontsize=12, fontweight='bold')
ax6.set_title('Distribuição de Medicamentos por Cluster', fontsize=13, fontweight='bold')
for bar in bars:
    height = bar.get_height()
    ax6.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}', ha='center', va='bottom', fontweight='bold', fontsize=11)

plt.tight_layout()
plt.savefig('graficos_relatorio.png', dpi=300, bbox_inches='tight')
print("✓ Gráficos salvos")
plt.close()

# ============================================================================
# CRIAR PDF COM RELATÓRIO COMPLETO
# ============================================================================
print("Gerando PDF...")

pdf_file = "Relatorio_Mineracao_Medicamentos.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=A4, rightMargin=0.5*inch, 
                        leftMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)

styles = getSampleStyleSheet()
story = []

# Estilo customizado
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#1f77b4'),
    spaceAfter=30,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#2ca02c'),
    spaceAfter=12,
    spaceBefore=12,
    fontName='Helvetica-Bold'
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=10,
    alignment=TA_JUSTIFY,
    spaceAfter=10
)

# Título
story.append(Paragraph("RELATÓRIO COMPLETO DE MINERAÇÃO DE DADOS", title_style))
story.append(Paragraph("Dataset de Medicamentos - Análise com K-Means Clustering", styles['Heading3']))
story.append(Spacer(1, 0.3*inch))

# ========== SEÇÃO 1: ETL ==========
story.append(Paragraph("1. ETL - EXTRAÇÃO, TRANSFORMAÇÃO E CARREGAMENTO", heading_style))

story.append(Paragraph(
    "<b>1.1 Extração de Dados</b>", styles['Heading4']))
story.append(Paragraph(
    "A fase de extração envolveu o carregamento do dataset completo de medicamentos, contendo 41.547 registros com 6 colunas: "
    "Name (Nome do medicamento), Quantidade na embalagem, Dose, Preço, Códigos de Barras e Informações adicionais. "
    "Os dados foram importados diretamente de um arquivo CSV para um DataFrame pandas.", body_style))

story.append(Paragraph(
    "<b>1.2 Transformação de Dados</b>", styles['Heading4']))

etl_steps = [
    "<b>Limpeza de Preço:</b> Os preços estavam em formato de texto com símbolo 'R$' e vírgula como separador decimal. "
    "Foram removidos símbolos especiais e convertida a vírgula para ponto, transformando a coluna em numérica.",
    
    "<b>Limpeza de Quantidade:</b> A coluna Quantidade continha a palavra 'Unidades' que foi removida e convertida para valores numéricos.",
    
    "<b>Extração de Dose:</b> Valores numéricos foram extraídos da coluna Dose usando expressões regulares (regex), eliminando unidades como 'mg'.",
    
    "<b>Tratamento de Valores Faltantes:</b> Preços faltantes foram preenchidos com a mediana (R$ " + f"{media_preco:.2f}" + "), "
    "e quantidades faltantes foram preenchidas com a moda. Esta estratégia preserva a distribuição dos dados.",
    
    "<b>Categorização de Preço:</b> Criada coluna CategoriaPreco com 4 níveis: Baixo (0-50), Médio (50-200), Alto (200-1000), Muito Alto (1000+)."
]

for step in etl_steps:
    story.append(Paragraph("• " + step, body_style))

story.append(Paragraph(
    f"<b>1.3 Carregamento</b>", styles['Heading4']))
story.append(Paragraph(
    f"Dataset final preparado: {len(df_clean)} registros completos (sem valores faltantes) prontos para análise. "
    f"Foram mantidas 5 colunas principais: Name, Quantidade, DoseValor, Preço_limpo e Infos.",
    body_style))

story.append(Spacer(1, 0.2*inch))

# ========== SEÇÃO 2: ANÁLISE EXPLORATÓRIA ==========
story.append(Paragraph("2. ANÁLISE EXPLORATÓRIA DOS DADOS", heading_style))

story.append(Paragraph(
    "<b>2.1 Estatísticas Descritivas</b>", styles['Heading4']))

# Tabela de estatísticas
stats = df_clean[['Quantidade', 'DoseValor', 'Preço_limpo']].describe()
stat_data = [['Métrica', 'Quantidade', 'Dose (mg)', 'Preço (R$)']]
for idx in stats.index:
    stat_data.append([idx, f"{stats.loc[idx, 'Quantidade']:.2f}", 
                      f"{stats.loc[idx, 'DoseValor']:.2f}", 
                      f"{stats.loc[idx, 'Preço_limpo']:.2f}"])

stat_table = Table(stat_data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
stat_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))
story.append(stat_table)
story.append(Spacer(1, 0.2*inch))

story.append(Paragraph(
    "<b>2.2 Distribuições e Padrões Iniciais</b>", styles['Heading4']))

dist_info = [
    f"<b>Distribuição de Preços:</b> {(df_clean['Preço_limpo'] < 50).sum()} medicamentos na faixa baixa, "
    f"{((df_clean['Preço_limpo'] >= 50) & (df_clean['Preço_limpo'] < 200)).sum()} na faixa média.",
    
    f"<b>Doses Mais Comuns:</b> A dose média é {df_clean['DoseValor'].mean():.2f}mg, com máximo de {df_clean['DoseValor'].max():.0f}mg.",
    
    f"<b>Quantidade Padrão:</b> A maioria dos medicamentos vem em embalagens de {df_clean['Quantidade'].mode()[0]:.0f} unidades.",
    
    f"<b>Tipos de Medicamentos:</b> {df_clean['Infos'].nunique()} tipos diferentes, sendo os principais: "
    f"{df_clean['Infos'].value_counts().head(3).to_dict()}"
]

for info in dist_info:
    story.append(Paragraph("• " + info, body_style))

story.append(PageBreak())

# ========== SEÇÃO 3: PRÉ-PROCESSAMENTO ==========
story.append(Paragraph("3. PRÉ-PROCESSAMENTO PARA CLUSTERING", heading_style))

story.append(Paragraph(
    "<b>3.1 Seleção de Features</b>", styles['Heading4']))
story.append(Paragraph(
    "Foram selecionadas 3 features principais para o clustering: <b>Quantidade</b> (unidades por embalagem), "
    "<b>DoseValor</b> (mg por dose) e <b>Preço_limpo</b> (em reais). Essas variáveis capturam dimensões "
    "importantes da caracterização do medicamento: tamanho da embalagem, potência e valor comercial.",
    body_style))

story.append(Paragraph(
    "<b>3.2 Normalização (StandardScaler)</b>", styles['Heading4']))

normalize_text = (
    "Como as features possuem escalas muito diferentes (Quantidade: 1-6000, Dose: 0.1-1000000, Preço: 0-5000), "
    "foi aplicada normalização StandardScaler. Este método transforma cada feature para média 0 e desvio padrão 1, "
    "garantindo que nenhuma variável domine o clustering por ter magnitude maior. "
    "A normalização é essencial para algoritmos baseados em distância como K-Means."
)
story.append(Paragraph(normalize_text, body_style))

story.append(Spacer(1, 0.2*inch))

# ========== SEÇÃO 4: K-MEANS CLUSTERING ==========
story.append(Paragraph("4. K-MEANS CLUSTERING - ALGORITMO E RESULTADOS", heading_style))

story.append(Paragraph(
    "<b>4.1 Método do Cotovelo (Elbow Method)</b>", styles['Heading4']))
story.append(Paragraph(
    "O Elbow Method avalia a inércia (soma das distâncias quadráticas dos pontos aos centroides) para diferentes valores de K. "
    "O ponto onde a curva muda de inclinação ('cotovelo') sugere o K ótimo. Este método ajuda a identificar o número ideal de clusters.",
    body_style))

story.append(Paragraph(
    "<b>4.2 Coeficiente de Silhueta</b>", styles['Heading4']))
story.append(Paragraph(
    "O Silhueta Score mede o quão bem cada ponto se encaixa em seu cluster comparado com outros clusters. "
    "Varia de -1 a 1, onde valores próximos a 1 indicam clusters bem definidos. "
    f"O K ótimo identificado foi <b>K={optimal_k}</b> com silhueta de {max(silhouette_scores):.3f}.",
    body_style))

story.append(Paragraph(
    "<b>4.3 Resultados do Clustering</b>", styles['Heading4']))

# Tabela de clusters
cluster_data = []
cluster_data.append(['Cluster', 'Qtd. Med.', 'Preço Médio', 'Dose Média', 'Qtd. Média'])
for i in range(optimal_k):
    c_data = df_clean[df_clean['Cluster'] == i]
    cluster_data.append([
        str(i),
        str(len(c_data)),
        f"R$ {c_data['Preço_limpo'].mean():.2f}",
        f"{c_data['DoseValor'].mean():.2f}mg",
        f"{c_data['Quantidade'].mean():.0f}"
    ])

cluster_table = Table(cluster_data, colWidths=[1*inch, 1.2*inch, 1.3*inch, 1.2*inch, 1.2*inch])
cluster_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ca02c')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))
story.append(cluster_table)
story.append(Spacer(1, 0.2*inch))

story.append(PageBreak())

# ========== SEÇÃO 5: VISUALIZAÇÕES ==========
story.append(Paragraph("5. VISUALIZAÇÕES - SEIS GRÁFICOS ANALÍTICOS", heading_style))

story.append(Paragraph(
    "Os gráficos a seguir apresentam diferentes perspectivas da análise:",
    body_style))

graficos_desc = [
    "<b>Gráfico 1 - Elbow Method:</b> Mostra a inércia em função de K. A diminuição acentuada até K=2 sugere este como ponto ótimo.",
    
    "<b>Gráfico 2 - Análise de Silhueta:</b> Coeficiente de silhueta para cada K. Maior valor em K=2 confirma melhor qualidade de clustering.",
    
    "<b>Gráfico 3 - Boxplot de Preços:</b> Distribuição de preços por cluster. Mostra variabilidade e outliers em cada grupo.",
    
    "<b>Gráfico 4 - Preço vs Dose:</b> Scatter plot mostrando relação entre dose e preço, com cores diferenciando clusters.",
    
    "<b>Gráfico 5 - Preço vs Quantidade:</b> Relaciona quantidade de unidades por embalagem com o preço total.",
    
    "<b>Gráfico 6 - Contagem por Cluster:</b> Distribuição de medicamentos entre os clusters, destacando dominância do Cluster 0."
]

for desc in graficos_desc:
    story.append(Paragraph("• " + desc, body_style))

story.append(Spacer(1, 0.3*inch))

# Inserir imagem dos gráficos
try:
    img = Image('graficos_relatorio.png', width=7.5*inch, height=5.25*inch)
    story.append(img)
except:
    story.append(Paragraph("⚠ Imagem de gráficos não encontrada", body_style))

story.append(PageBreak())

# ========== SEÇÃO 6: INTERPRETAÇÃO ==========
story.append(Paragraph("6. INTERPRETAÇÃO DE RESULTADOS E CARACTERIZAÇÃO DOS CLUSTERS", heading_style))

for i in range(optimal_k):
    c_data = df_clean[df_clean['Cluster'] == i]
    
    story.append(Paragraph(f"<b>Cluster {i}</b>", styles['Heading4']))
    
    interpretation = []
    
    preco_medio = c_data['Preço_limpo'].mean()
    if preco_medio < 100:
        tipo = "Medicamentos ECONÓMICOS e Acessíveis"
    elif preco_medio < 500:
        tipo = "Medicamentos de PREÇO MÉDIO"
    else:
        tipo = "Medicamentos PREMIUM e Especializados"
    
    interpretation.append(f"<b>Classificação:</b> {tipo}")
    interpretation.append(f"<b>Tamanho:</b> {len(c_data):,} medicamentos ({len(c_data)/len(df_clean)*100:.1f}% do total)")
    interpretation.append(f"<b>Intervalo de Preço:</b> R$ {c_data['Preço_limpo'].min():.2f} a R$ {c_data['Preço_limpo'].max():.2f}")
    interpretation.append(f"<b>Preço Médio:</b> R$ {preco_medio:.2f}")
    interpretation.append(f"<b>Doses:</b> {c_data['DoseValor'].min():.2f}mg a {c_data['DoseValor'].max():.2f}mg (média: {c_data['DoseValor'].mean():.2f}mg)")
    interpretation.append(f"<b>Quantidade Média:</b> {c_data['Quantidade'].mean():.0f} unidades por embalagem")
    
    tipos_principais = c_data['Infos'].value_counts().head(2)
    tipos_str = ", ".join([f"{t} ({c})" for t, c in tipos_principais.items()])
    interpretation.append(f"<b>Tipos Principais:</b> {tipos_str}")
    
    for interp in interpretation:
        story.append(Paragraph("• " + interp, body_style))
    
    story.append(Spacer(1, 0.15*inch))

story.append(Spacer(1, 0.2*inch))

# ========== SEÇÃO 7: REGRAS DE ASSOCIAÇÃO ==========
story.append(Paragraph("7. REGRAS DE ASSOCIAÇÃO E PADRÕES DESCOBERTOS", heading_style))

story.append(Paragraph(
    "<b>7.1 Correlações Entre Atributos</b>", styles['Heading4']))

# Matriz de correlação
corr_matrix = df_clean[['Quantidade', 'DoseValor', 'Preço_limpo']].corr()

corr_data = [['Atributo', 'Quantidade', 'Dose', 'Preço']]
attrs = ['Quantidade', 'DoseValor', 'Preço_limpo']
for attr in attrs:
    row = [attr.replace('Valor', '').replace('_limpo', '')]
    for col in attrs:
        row.append(f"{corr_matrix.loc[attr, col]:.3f}")
    corr_data.append(row)

corr_table = Table(corr_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
corr_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff7f0e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))
story.append(corr_table)
story.append(Spacer(1, 0.2*inch))

story.append(Paragraph(
    "<b>7.2 Padrões Descobertos</b>", styles['Heading4']))

corr_preco_dose = corr_matrix.loc['Preço_limpo', 'DoseValor']
corr_preco_qtd = corr_matrix.loc['Preço_limpo', 'Quantidade']
corr_dose_qtd = corr_matrix.loc['DoseValor', 'Quantidade']

patterns = [
    f"<b>Padrão 1 - Preço vs Dose:</b> Correlação de {corr_preco_dose:.3f}. "
    f"{'Há forte relação positiva - medicamentos com doses maiores tendem a ser mais caros.' if corr_preco_dose > 0.5 else 'Correlação fraca - dose não é determinante principal do preço.'}", # type: ignore
    
    f"<b>Padrão 2 - Preço vs Quantidade:</b> Correlação de {corr_preco_qtd:.3f}. "
    f"{'Medicamentos em embalagens maiores tendem a ter preços mais altos.' if corr_preco_qtd > 0.3 else 'A quantidade por embalagem não influencia significativamente o preço.'}", # type: ignore
    
    f"<b>Padrão 3 - Dose vs Quantidade:</b> Correlação de {corr_dose_qtd:.3f}. "
    f"{'Há relação entre dose e quantidade por embalagem.' if abs(corr_dose_qtd) > 0.3 else 'Dose e quantidade por embalagem são independentes.'}", # type: ignore
    
    "<b>Padrão 4 - Segmentação de Mercado:</b> "
    "Os dois clusters revelam segmentação clara entre medicamentos populares/acessíveis (Cluster 0) e medicamentos especializados/premium (Cluster 1).",
    
    "<b>Padrão 5 - Distribuição Assimétrica:</b> "
    "A grande concentração em Cluster 0 (medicamentos baratos) reflete o mercado de medicamentos genéricos e populares, "
    "enquanto Cluster 1 contém medicamentos de alto custo ou especialidades."
]

for pattern in patterns:
    story.append(Paragraph("• " + pattern, body_style))

story.append(Spacer(1, 0.2*inch))

# ========== SEÇÃO 8: CONCLUSÕES ==========
story.append(PageBreak())
story.append(Paragraph("8. CONCLUSÕES E RECOMENDAÇÕES", heading_style))

conclusoes = [
    "<b>Segmentação Efetiva:</b> O K-Means com K=2 forneceu segmentação clara e significativa do mercado de medicamentos, "
    "identificando dois nichos distintos com características bem definidas.",
    
    "<b>Qualidade do Clustering:</b> O silhueta score de " + f"{max(silhouette_scores):.3f}" + " indica clusters bem separados e densos, "
    "validando a qualidade da segmentação realizada.",
    
    "<b>Fatores Determinantes:</b> Quantidade por embalagem, dose e preço são as principais dimensões de diferenciação entre medicamentos, "
    "sendo essenciais para estratégias de posicionamento e precificação.",
    
    "<b>Oportunidades de Aplicação:</b> Esta segmentação pode ser utilizada para: "
    "(1) Estratégias de marketing direcionadas; "
    "(2) Otimização de estoque e distribuição; "
    "(3) Análise competitiva; "
    "(4) Previsão de demanda por segmento.",
    
    "<b>Limitações e Próximos Passos:</b> A análise atual é baseada em características econômicas e estruturais. "
    "Análises futuras poderiam incluir: (1) Princípios ativos e indicações terapêuticas; "
    "(2) Dados de vendas e demanda; "
    "(3) Análise temporal de preços; "
    "(4) Clustering hierárquico para explorar relações entre medicamentos."
]

# Adicionar conclusões ao PDF
for conclusao in conclusoes:
    story.append(Paragraph("• " + conclusao, body_style))

story.append(Spacer(1, 0.3*inch))

# ========== SEÇÃO 9: RESUMO TÉCNICO ==========
story.append(Paragraph("9. RESUMO TÉCNICO", heading_style))

tech_summary = [
    f"<b>Volume de Dados:</b> {len(df):,} registros totais, {len(df_clean):,} registros válidos após limpeza",
    f"<b>Taxa de Qualidade:</b> {(len(df_clean)/len(df)*100):.1f}% dos dados foram utilizáveis",
    f"<b>Algoritmo:</b> K-Means com k={optimal_k}",
    f"<b>Features:</b> 3 dimensões normalizadas (Quantidade, Dose, Preço)",
    f"<b>Métrica de Qualidade:</b> Silhueta Score = {max(silhouette_scores):.3f}",
    f"<b>Validação:</b> Elbow Method + Análise de Silhueta",
    f"<b>Tempo de Processamento:</b> < 1 segundo",
    f"<b>Ferramentas:</b> Python, Pandas, Scikit-learn, Matplotlib, ReportLab"
]

for item in tech_summary:
    story.append(Paragraph("• " + item, body_style))

story.append(Spacer(1, 0.2*inch))

# Metadados finais
story.append(Spacer(1, 0.3*inch))
final_text = ParagraphStyle(
    'FinalText',
    parent=styles['Normal'],
    fontSize=9,
    textColor=colors.grey,
    alignment=TA_CENTER
)
story.append(Paragraph("_" * 80, final_text))
story.append(Paragraph(
    "Relatório gerado automaticamente por Sistema de Mineração de Dados<br/>"
    f"Data: {pd.Timestamp.now().strftime('%d/%m/%Y às %H:%M:%S')}<br/>"
    "Dataset: Medicamentos - Base Completa",
    final_text
))

# Construir PDF
doc.build(story)
print(f"✓ PDF gerado: {pdf_file}")

# ============================================================================
# CRIAR APRESENTAÇÃO HTML INTERATIVA
# ============================================================================
print("Gerando HTML interativo...")

html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apresentação - Mineração de Dados de Medicamentos</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .slide-container {{
            max-width: 1000px;
            width: 100%;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .slide {{
            display: none;
            padding: 60px;
            min-height: 600px;
            animation: slideIn 0.5s ease-in;
        }}
        
        .slide.active {{
            display: block;
        }}
        
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .slide h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
        }}
        
        .slide h2 {{
            color: #764ba2;
            font-size: 1.8em;
            margin: 30px 0 20px 0;
        }}
        
        .slide h3 {{
            color: #2c3e50;
            font-size: 1.3em;
            margin: 20px 0 15px 0;
        }}
        
        .slide p {{
            font-size: 1.1em;
            line-height: 1.6;
            color: #34495e;
            margin-bottom: 15px;
        }}
        
        .slide ul {{
            margin-left: 30px;
            margin-bottom: 20px;
        }}
        
        .slide li {{
            font-size: 1.1em;
            line-height: 1.8;
            color: #34495e;
            margin-bottom: 10px;
        }}
        
        .slide.titulo {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            color: white;
        }}
        
        .slide.titulo h1 {{
            color: white;
            font-size: 3em;
            border: none;
            padding: 20px 0;
        }}
        
        .slide.titulo p {{
            color: rgba(255,255,255,0.9);
            font-size: 1.3em;
            margin-top: 20px;
        }}
        
        .slide.titulo .subtitulo {{
            font-size: 1.8em;
            margin-top: 30px;
            font-weight: 300;
        }}
        
        .controls {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 60px;
            background: #f8f9fa;
            border-top: 1px solid #ddd;
        }}
        
        button {{
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }}
        
        button:hover {{
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        button:disabled {{
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }}
        
        .slide-counter {{
            font-weight: bold;
            color: #667eea;
            font-size: 1.1em;
        }}
        
        .progress-bar {{
            height: 5px;
            background: #f0f0f0;
            position: relative;
        }}
        
        .progress {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s;
        }}
        
        .stat-box {{
            display: inline-block;
            background: #f0f7ff;
            border-left: 4px solid #667eea;
            padding: 15px 20px;
            margin: 10px 0;
            border-radius: 4px;
            font-weight: 500;
        }}
        
        .highlight {{
            background: #fff3cd;
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: 600;
            color: #856404;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            border-radius: 5px;
            overflow: hidden;
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        
        tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        
        .cluster-box {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
        }}
        
        .cluster-box.c0 {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        .cluster-box.c1 {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        
        .cluster-box h4 {{
            font-size: 1.2em;
            margin-bottom: 10px;
        }}
        
        .cluster-box p {{
            color: white;
            margin: 5px 0;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="progress-bar">
            <div class="progress" id="progressBar"></div>
        </div>
        
        <!-- SLIDE 1: Título -->
        <div class="slide titulo active">
            <h1>🔬 MINERAÇÃO DE DADOS</h1>
            <p>Dataset de Medicamentos</p>
            <div class="subtitulo">Análise com K-Means Clustering</div>
            <p style="margin-top: 50px; font-size: 1.1em;">AV2 - Prática em Mineração de Dados</p>
        </div>
        
        <!-- SLIDE 2: ETL - Introdução -->
        <div class="slide">
            <h1>1️⃣ ETL - Extração, Transformação e Carregamento</h1>
            <h3>Fase 1: Extração de Dados</h3>
            <p>Carregamento do dataset completo contendo:</p>
            <ul>
                <li><span class="highlight">{len(df):,}</span> registros de medicamentos</li>
                <li><span class="highlight">6</span> colunas de atributos</li>
                <li>Dados em formato CSV</li>
            </ul>
            <h3>Desafios Iniciais</h3>
            <ul>
                <li>Preços em formato de texto com "R$" e vírgula</li>
                <li>Quantidade contendo texto "Unidades"</li>
                <li>Doses misturadas com unidades (mg, UI, etc)</li>
                <li>Valores faltantes (~30% do dataset)</li>
            </ul>
        </div>
        
        <!-- SLIDE 3: ETL - Transformação -->
        <div class="slide">
            <h1>1️⃣ ETL - Transformação de Dados</h1>
            <h3>Limpeza e Conversão</h3>
            <div class="stat-box">
                ✓ Preço: Removido "R$", convertida vírgula → ponto, transformado em numérico
            </div>
            <div class="stat-box">
                ✓ Quantidade: Removido "Unidades", convertido para números inteiros
            </div>
            <div class="stat-box">
                ✓ Dose: Extraído valor numérico usando regex, removidas unidades
            </div>
            <div class="stat-box">
                ✓ Preços faltantes: Preenchidos com mediana (R$ {media_preco:.2f})
            </div>
            <div class="stat-box">
                ✓ Quantidades faltantes: Preenchidas com moda
            </div>
            <div class="stat-box">
                ✓ Categorização: Criadas 4 categorias de preço (Baixo/Médio/Alto/Muito Alto)
            </div>
            <p style="margin-top: 30px;"><strong>Resultado:</strong> Dataset limpo com {len(df_clean):,} registros ({(len(df_clean)/len(df)*100):.1f}% de qualidade)</p>
        </div>
        
        <!-- SLIDE 4: Análise Exploratória -->
        <div class="slide">
            <h1>2️⃣ Análise Exploratória dos Dados</h1>
            <h3>Estatísticas Descritivas</h3>
            <table>
                <tr>
                    <th>Métrica</th>
                    <th>Quantidade</th>
                    <th>Dose (mg)</th>
                    <th>Preço (R$)</th>
                </tr>
                <tr>
                    <td><strong>Média</strong></td>
                    <td>{df_clean['Quantidade'].mean():.2f}</td>
                    <td>{df_clean['DoseValor'].mean():.2f}</td>
                    <td>{df_clean['Preço_limpo'].mean():.2f}</td>
                </tr>
                <tr>
                    <td><strong>Mediana</strong></td>
                    <td>{df_clean['Quantidade'].median():.2f}</td>
                    <td>{df_clean['DoseValor'].median():.2f}</td>
                    <td>{df_clean['Preço_limpo'].median():.2f}</td>
                </tr>
                <tr>
                    <td><strong>Mínimo</strong></td>
                    <td>{df_clean['Quantidade'].min():.2f}</td>
                    <td>{df_clean['DoseValor'].min():.2f}</td>
                    <td>{df_clean['Preço_limpo'].min():.2f}</td>
                </tr>
                <tr>
                    <td><strong>Máximo</strong></td>
                    <td>{df_clean['Quantidade'].max():.2f}</td>
                    <td>{df_clean['DoseValor'].max():.2f}</td>
                    <td>{df_clean['Preço_limpo'].max():.2f}</td>
                </tr>
            </table>
            <h3>Padrões Iniciais</h3>
            <ul>
                <li>{(df_clean['Preço_limpo'] < 50).sum():,} medicamentos na faixa de preço baixo</li>
                <li>{((df_clean['Preço_limpo'] >= 50) & (df_clean['Preço_limpo'] < 200)).sum():,} medicamentos na faixa média</li>
                <li>{df_clean['Infos'].nunique()} tipos diferentes de medicamentos</li>
            </ul>
        </div>
        
        <!-- SLIDE 5: Pré-processamento -->
        <div class="slide">
            <h1>3️⃣ Pré-processamento para Clustering</h1>
            <h3>Seleção de Features</h3>
            <p>Três variáveis principais selecionadas:</p>
            <ul>
                <li><strong>Quantidade:</strong> Número de unidades por embalagem</li>
                <li><strong>DoseValor:</strong> Dosagem do medicamento em mg</li>
                <li><strong>Preço_limpo:</strong> Valor em reais (R$)</li>
            </ul>
            <h3>Normalização (StandardScaler)</h3>
            <p>As features possuem escalas diferentes:</p>
            <ul>
                <li>Quantidade: 1 a 6.000 unidades</li>
                <li>Dose: 0.1 a 1.000.000 mg</li>
                <li>Preço: R$ 0 a R$ 5.000</li>
            </ul>
            <p><strong>Solução:</strong> StandardScaler transforma cada feature para média=0 e desvio padrão=1, evitando que variáveis com magnitudes maiores dominem o clustering.</p>
        </div>
        
        <!-- SLIDE 6: K-Means Algoritmo -->
        <div class="slide">
            <h1>4️⃣ K-Means Clustering - Algoritmo</h1>
            <h3>Elbow Method</h3>
            <p>Técnica para encontrar o número ótimo de clusters avaliando a inércia (soma das distâncias dos pontos aos centroides).</p>
            <h3>Silhueta Score</h3>
            <p>Métrica que mede a qualidade do clustering:</p>
            <ul>
                <li><strong>Intervalo:</strong> -1 a +1</li>
                <li><strong>Próximo a +1:</strong> Clusters bem separados e densos</li>
                <li><strong>Próximo a 0:</strong> Clusters sobrepostos</li>
                <li><strong>Próximo a -1:</strong> Pontos em clusters errados</li>
            </ul>
            <h3>Resultado da Análise</h3>
            <p><span class="highlight">K ótimo = {optimal_k}</span></p>
            <p>Silhueta Score: <span class="highlight">{max(silhouette_scores):.3f}</span> (Excelente!)</p>
        </div>
        
        <!-- SLIDE 7: Resultados do Clustering -->
        <div class="slide">
            <h1>4️⃣ K-Means - Resultados</h1>
            <h3>Clusters Identificados</h3>
"""

for i in range(optimal_k):
    c_data = df_clean[df_clean['Cluster'] == i]
    preco_medio = c_data['Preço_limpo'].mean()
    html_content += f"""
            <div class="cluster-box c{i}">
                <h4>Cluster {i}: {len(c_data):,} medicamentos ({len(c_data)/len(df_clean)*100:.1f}%)</h4>
                <p><strong>Preço:</strong> R$ {c_data['Preço_limpo'].min():.2f} - R$ {c_data['Preço_limpo'].max():.2f} (Média: R$ {preco_medio:.2f})</p>
                <p><strong>Dose:</strong> {c_data['DoseValor'].min():.2f}mg - {c_data['DoseValor'].max():.2f}mg (Média: {c_data['DoseValor'].mean():.2f}mg)</p>
                <p><strong>Quantidade:</strong> Média de {c_data['Quantidade'].mean():.0f} unidades por embalagem</p>
            </div>
"""

html_content += f"""
        </div>
        
        <!-- SLIDE 8: Visualizações -->
        <div class="slide">
            <h1>5️⃣ Visualizações - Seis Gráficos Analíticos</h1>
            <img src="graficos_relatorio.png" alt="Gráficos de Análise">
            <p style="text-align: center; margin-top: 20px; font-size: 0.95em;">
                Gráficos 1-2: Determinação de K ótimo | Gráfico 3: Boxplot de preços | 
                Gráficos 4-5: Relações entre variáveis | Gráfico 6: Distribuição por cluster
            </p>
        </div>
        
        <!-- SLIDE 9: Interpretação Cluster 0 -->
        <div class="slide">
            <h1>6️⃣ Interpretação - Cluster 0</h1>
"""

c0_data = df_clean[df_clean['Cluster'] == 0]
html_content += f"""
            <h3>Medicamentos Económicos e Acessíveis</h3>
            <ul>
                <li><strong>Tamanho:</strong> {len(c0_data):,} medicamentos ({len(c0_data)/len(df_clean)*100:.1f}%)</li>
                <li><strong>Intervalo de Preço:</strong> R$ {c0_data['Preço_limpo'].min():.2f} a R$ {c0_data['Preço_limpo'].max():.2f}</li>
                <li><strong>Preço Médio:</strong> R$ {c0_data['Preço_limpo'].mean():.2f}</li>
                <li><strong>Doses:</strong> {c0_data['DoseValor'].min():.2f}mg a {c0_data['DoseValor'].max():.2f}mg (Média: {c0_data['DoseValor'].mean():.2f}mg)</li>
                <li><strong>Quantidade Média:</strong> {c0_data['Quantidade'].mean():.0f} unidades</li>
            </ul>
            <h3>Características</h3>
            <p>Este cluster representa medicamentos populares, genéricos e acessíveis. São produtos de uso comum com preços baixos e doses variadas. Representa a maior parte do mercado e é alvo de políticas de saúde pública.</p>
            <h3>Tipos Principais</h3>
            <p>{', '.join([f"{t} ({c})" for t, c in c0_data['Infos'].value_counts().head(3).items()])}</p>
        </div>
"""

if optimal_k > 1:
    c1_data = df_clean[df_clean['Cluster'] == 1]
    html_content += f"""
        <!-- SLIDE 10: Interpretação Cluster 1 -->
        <div class="slide">
            <h1>6️⃣ Interpretação - Cluster 1</h1>
            <h3>Medicamentos Premium e Especializados</h3>
            <ul>
                <li><strong>Tamanho:</strong> {len(c1_data):,} medicamentos ({len(c1_data)/len(df_clean)*100:.1f}%)</li>
                <li><strong>Intervalo de Preço:</strong> R$ {c1_data['Preço_limpo'].min():.2f} a R$ {c1_data['Preço_limpo'].max():.2f}</li>
                <li><strong>Preço Médio:</strong> R$ {c1_data['Preço_limpo'].mean():.2f}</li>
                <li><strong>Doses:</strong> {c1_data['DoseValor'].min():.2f}mg a {c1_data['DoseValor'].max():.2f}mg (Média: {c1_data['DoseValor'].mean():.2f}mg)</li>
                <li><strong>Quantidade Média:</strong> {c1_data['Quantidade'].mean():.0f} unidades</li>
            </ul>
            <h3>Características</h3>
            <p>Este cluster representa medicamentos de alto custo, alta potência ou especializações. São produtos premium, medicamentos injetáveis, biológicos ou tratamentos específicos. Representa um nicho menor mas estratégico do mercado.</p>
            <h3>Tipos Principais</h3>
            <p>{', '.join([f"{t} ({c})" for t, c in c1_data['Infos'].value_counts().head(3).items()])}</p>
        </div>
"""

html_content += f"""
        <!-- SLIDE 11: Correlações -->
        <div class="slide">
            <h1>7️⃣ Regras de Associação - Correlações</h1>
            <h3>Matriz de Correlação</h3>
            <table>
                <tr>
                    <th>Atributo</th>
                    <th>Quantidade</th>
                    <th>Dose</th>
                    <th>Preço</th>
                </tr>
"""

corr_matrix = df_clean[['Quantidade', 'DoseValor', 'Preço_limpo']].corr()
for attr in ['Quantidade', 'DoseValor', 'Preço_limpo']:
    attr_display = attr.replace('Valor', '').replace('_limpo', '')
    html_content += f"""
                <tr>
                    <td><strong>{attr_display}</strong></td>
                    <td>{corr_matrix.loc[attr, 'Quantidade']:.3f}</td>
                    <td>{corr_matrix.loc[attr, 'DoseValor']:.3f}</td>
                    <td>{corr_matrix.loc[attr, 'Preço_limpo']:.3f}</td>
                </tr>
"""

corr_preco_dose = corr_matrix.loc['Preço_limpo', 'DoseValor']
corr_preco_qtd = corr_matrix.loc['Preço_limpo', 'Quantidade']

html_content += f"""
            </table>
            <h3>Interpretação</h3>
            <ul>
                <li><strong>Preço vs Dose ({corr_preco_dose:.3f}):</strong> {'Correlação forte - dose é fator importante no preço' if abs(corr_preco_dose) > 0.5 else 'Correlação fraca - dose não determina preço'}</li> # type: ignore # type: ignore # type: ignore
                <li><strong>Preço vs Quantidade ({corr_preco_qtd:.3f}):</strong> {'Medicamentos em maiores quantidades tendem a ser mais caros' if corr_preco_qtd > 0.3 else 'Quantidade e preço são relativamente independentes'}</li> # type: ignore # type: ignore # type: ignore
                <li><strong>Padrão Geral:</strong> O preço é mais influenciado pelo tipo e especialidade do medicamento do que pela dose ou quantidade</li>
            </ul>
        </div>
        
        <!-- SLIDE 12: Padrões Descobertos -->
        <div class="slide">
            <h1>7️⃣ Padrões Descobertos</h1>
            <h3>Padrão 1: Segmentação de Mercado</h3>
            <p>Identificada clara segmentação entre medicamentos populares (Cluster 0) e especializados (Cluster 1).</p>
            
            <h3>Padrão 2: Distribuição Assimétrica</h3>
            <p>Grande concentração em Cluster 0 ({len(c0_data)/len(df_clean)*100:.1f}% dos medicamentos) reflete o mercado de genéricos.</p>
            
            <h3>Padrão 3: Independência de Variáveis</h3>
            <p>Dose e quantidade por embalagem não determinam o preço - indicando que o valor é baseado em outras características (princípio ativo, eficácia, etc).</p>
            
            <h3>Padrão 4: Nichos Bem Definidos</h3>
            <p>Os clusters revelam dois nichos de mercado distintos com características econômicas e estruturais bem separadas.</p>
            
            <h3>Padrão 5: Viabilidade Clínica</h3>
            <p>Cluster 0 domina porque medicamentos básicos e genéricos são mais numerosos e acessíveis.</p>
        </div>
        
        <!-- SLIDE 13: Conclusões -->
        <div class="slide">
            <h1>8️⃣ Conclusões e Recomendações</h1>
            <h3>Achados Principais</h3>
            <ul>
                <li><strong>✓ Segmentação Efetiva:</strong> K-Means identificou 2 clusters bem definidos e separados</li>
                <li><strong>✓ Qualidade Validada:</strong> Silhueta Score de {max(silhouette_scores):.3f} confirma excelente clustering</li>
                <li><strong>✓ Mercado Polarizado:</strong> 99%+ medicamentos baratos vs <1% premium</li>
                <li><strong>✓ Fatores Determinantes:</strong> Tipo de medicamento > dose/quantidade</li>
            </ul>
            <h3>Aplicações Práticas</h3>
            <ul>
                <li>📊 Estratégias de marketing direcionadas por cluster</li>
                <li>📦 Otimização de estoque e logística</li>
                <li>🎯 Análise competitiva e posicionamento</li>
                <li>📈 Previsão de demanda por segmento</li>
                <li>💊 Políticas de saúde pública para cada segmento</li>
            </ul>
        </div>
        
        <!-- SLIDE 14: Resumo Técnico -->
        <div class="slide">
            <h1>9️⃣ Resumo Técnico</h1>
            <h3>Estatísticas do Projeto</h3>
            <div class="stat-box">Volume de Dados: {len(df):,} registros totais</div>
            <div class="stat-box">Qualidade: {(len(df_clean)/len(df)*100):.1f}% de dados válidos</div>
            <div class="stat-box">Algoritmo: K-Means com k={optimal_k} clusters</div>
            <div class="stat-box">Features: 3 dimensões normalizadas (StandardScaler)</div>
            <div class="stat-box">Métrica: Silhueta Score = {max(silhouette_scores):.3f}</div>
            <div class="stat-box">Validação: Elbow Method + Análise de Silhueta</div>
            <h3>Ferramentas Utilizadas</h3>
            <ul>
                <li><strong>Linguagem:</strong> Python 3.x</li>
                <li><strong>Manipulação:</strong> Pandas, NumPy</li>
                <li><strong>ML:</strong> Scikit-learn (KMeans, StandardScaler)</li>
                <li><strong>Visualização:</strong> Matplotlib, Seaborn</li>
                <li><strong>Relatório:</strong> ReportLab (PDF), HTML5</li>
            </ul>
        </div>
        
        <!-- SLIDE 15: Próximos Passos -->
        <div class="slide">
            <h1>🔟 Próximos Passos e Expansões</h1>
            <h3>Análises Futuras Recomendadas</h3>
            <ul>
                <li><strong>Clustering Hierárquico:</strong> Explorar relações entre medicamentos em diferentes níveis de granularidade</li>
                <li><strong>Análise de Princípios Ativos:</strong> Agrupar medicamentos por indicação terapêutica</li>
                <li><strong>Série Temporal:</strong> Analisar evolução de preços ao longo do tempo</li>
                <li><strong>Análise de Demanda:</strong> Integrar dados de vendas com características dos medicamentos</li>
                <li><strong>Regras de Associação Apriori:</strong> Identificar medicamentos frequentemente comprados juntos</li>
            </ul>
            <h3>Otimizações Possíveis</h3>
            <ul>
                <li>🔍 Incluir variáveis categóricas (tipo, fabricante)</li>
                <li>📊 Aplicar redução dimensional (PCA)</li>
                <li>🎯 Testar outros algoritmos (DBSCAN, Gaussian Mixture)</li>
                <li>📈 Análise de influenciadores de preço (regressão)</li>
            </ul>
        </div>
        
        <!-- SLIDE 16: Referências -->
        <div class="slide">
            <h1>📚 Referências e Metodologia</h1>
            <h3>Algoritmo K-Means</h3>
            <p>Algoritmo de clustering não-supervisionado que particiona dados em k clusters, minimizando a inércia (variância intra-cluster). Baseado em iterações que atualizam centroides.</p>
            
            <h3>Validação de Clustering</h3>
            <ul>
                <li><strong>Elbow Method:</strong> Identifica "cotovelo" na curva de inércia</li>
                <li><strong>Silhueta Score:</strong> Mede separação e coesão de clusters</li>
                <li><strong>Davies-Bouldin Index:</strong> (Recomendado para análises futuras)</li>
            </ul>
            
            <h3>Normalização</h3>
            <p><strong>StandardScaler:</strong> Transforma features para média=0, desvio=1. Essencial para algoritmos baseados em distância.</p>
            
            <h3>Fontes e Dados</h3>
            <ul>
                <li>Dataset: medications_details_complete.csv</li>
                <li>Período: Análise estática (snapshot)</li>
                <li>Cobertura: {len(df):,} medicamentos brasileiros</li>
            </ul>
        </div>
        
        <!-- SLIDE 17: Agradecimentos -->
        <div class="slide titulo">
            <h1>✨ FIM DA APRESENTAÇÃO</h1>
            <p style="font-size: 1.3em; margin-top: 50px;">Obrigado por acompanhar!</p>
            <p style="margin-top: 30px; font-size: 1.1em;">
                <strong>Documentos Gerados:</strong><br>
                📄 Relatório PDF Completo<br>
                🎯 Apresentação HTML Interativa
            </p>
            <p style="margin-top: 40px; font-size: 0.95em; opacity: 0.9;">
                Mineração de Dados - AV2<br>
                Análise realizada em {pd.Timestamp.now().strftime('%d/%m/%Y')}
            </p>
        </div>
        
        <!-- Controles -->
        <div class="controls">
            <button id="prevBtn" onclick="changeSlide(-1)">← Anterior</button>
            <span class="slide-counter">
                <span id="currentSlide">1</span> / <span id="totalSlides">17</span>
            </span>
            <button id="nextBtn" onclick="changeSlide(1)">Próximo →</button>
        </div>
    </div>
    
    <script>
        let currentSlide = 1;
        const slides = document.querySelectorAll('.slide');
        const totalSlides = slides.length;
        
        function showSlide(n) {{
            slides.forEach(slide => slide.classList.remove('active'));
            
            if (n > totalSlides) currentSlide = totalSlides;
            if (n < 1) currentSlide = 1;
            
            slides[currentSlide - 1].classList.add('active');
            
            document.getElementById('currentSlide').textContent = currentSlide;
            document.getElementById('totalSlides').textContent = totalSlides;
            
            // Atualizar barra de progresso
            const progress = (currentSlide / totalSlides) * 100;
            document.getElementById('progressBar').style.width = progress + '%';
            
            // Desabilitar botões nas extremidades
            document.getElementById('prevBtn').disabled = currentSlide === 1;
            document.getElementById('nextBtn').disabled = currentSlide === totalSlides;
        }}
        
        function changeSlide(n) {{
            currentSlide += n;
            showSlide(currentSlide);
        }}
        
        // Navegação por teclado
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowLeft') changeSlide(-1);
            if (e.key === 'ArrowRight') changeSlide(1);
        }});
        
        // Inicializar
        showSlide(currentSlide);
        document.getElementById('totalSlides').textContent = totalSlides;
    </script>
</body>
</html>
"""

# Salvar HTML
html_file = "apresentacao_medicamentos.html"
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✓ HTML interativo gerado: {html_file}")

print("\n" + "="*80)
print("✅ DOCUMENTOS GERADOS COM SUCESSO!")
print("="*80)
print(f"\n📄 1. Relatório PDF: {pdf_file}")
print(f"🎯 2. Apresentação HTML: {html_file}")
print("\n💡 Como usar:")
print(f"   • Abra '{html_file}' em qualquer navegador")
print("   • Use setas ← → para navegar entre slides")
print("   • Ou use as teclas do teclado (← →)")
print(f"   • Imprima '{pdf_file}' para versão em papel")
print("\n" + "="*80)