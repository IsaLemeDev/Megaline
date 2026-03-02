import pandas as pd
import seaborn as sns
import numpy as np
import math as mt
import matplotlib.pyplot as plt
from scipy import stats

megaline_calls = pd.read_csv('/datasets/megaline_calls.csv')
megaline_plans = pd.read_csv('/datasets/megaline_plans.csv')
megaline_messages = pd.read_csv('/datasets/megaline_messages.csv')
megaline_users = pd.read_csv('/datasets/megaline_users.csv')
megaline_internet = pd.read_csv('/datasets/megaline_internet.csv')

megaline_plans['plan_name'] = megaline_plans['plan_name'].str.capitalize()
megaline_plans['usd_per_gb'] = megaline_plans['usd_per_gb'].astype(float)
megaline_plans['usd_monthly_pay'] = megaline_plans['usd_monthly_pay'].astype(float)

megaline_plans['gb_per_month_included'] = megaline_plans ['mb_per_month_included'] / 1024 

megaline_users['churn_date'] = megaline_users['churn_date'].fillna('Em uso')
print(megaline_users['churn_date'].head(20))
print()
print(megaline_users.duplicated().sum())

megaline_calls['duration'] = np.ceil(megaline_calls['duration']).astype(int)
print(megaline_calls['duration'])

megaline_calls['call_date'] = pd.to_datetime(megaline_calls['call_date'])
megaline_calls['month'] = megaline_calls['call_date'].dt.month
megaline_calls['year'] = megaline_calls['call_date'].dt.year

megaline_messages['message_date'] = pd.to_datetime(megaline_messages['message_date'])
megaline_messages['month'] = megaline_messages['message_date'].dt.month
megaline_messages['year'] = megaline_messages['message_date'].dt.year

megaline_internet['mb_used'] = np.ceil(megaline_internet['mb_used']).astype(int)
megaline_internet.rename(columns={'mb_used': 'gb_used'}, inplace=True)

megaline_internet['session_date'] = pd.to_datetime(megaline_internet['session_date'])
megaline_internet['month'] = megaline_internet['session_date'].dt.month
megaline_internet['year'] = megaline_internet['session_date'].dt.year

megaline_calls['call_date'] = pd.to_datetime(megaline_calls['call_date'])
megaline_calls['month'] = megaline_calls['call_date'].dt.month
chamadas_realizada = megaline_calls.groupby(['user_id', 'month'])['id'].count()
print(chamadas_realizada.head(20))

minutos_gastos = megaline_calls.groupby(['user_id', 'month'])['duration'].sum()
mensagens_enviadas = megaline_messages.groupby(['user_id', 'month'])['id'].count()
trafego_internet = megaline_internet.groupby(['user_id', 'month'])['gb_used'].sum()
trafego_internet = trafego_internet / 1024

dados_agregados = pd.DataFrame({
    'chamadas': chamadas_realizada,
    'minutos': minutos_gastos,
    'mensagens': mensagens_enviadas,
    'gb_usados': trafego_internet

}).fillna(0)

dados_agregados = dados_agregados.reset_index()
dados_agregados = dados_agregados.merge(
    megaline_users[['user_id', 'plan']], 
    on='user_id', 
    how='left'
)

def calcular_receita(row):
    if row['plan'] == 'surf':
        receita = 20.0
        if row['minutos'] > 500:
            receita += (row['minutos'] - 500) * 0.03
        if row['mensagens'] > 50:
            receita += (row['mensagens'] - 50) * 0.03
        if row['gb_usados'] > 15:
            gb_excesso = (row['gb_usados'] - 15)
            receita += gb_excesso * 10
    else:
        receita = 70.0
        if row['minutos'] > 3000:
            receita += (row['minutos'] - 3000) * 0.01
        if row ['mensagens'] > 1000:
            receita += (row['mensagens'] - 1000) * 0.01
        if row['gb_usados'] > 30:
            gb_excesso = (row['gb_usados'] - 30)
            receita += gb_excesso * 7
    return receita


dados_agregados['receita'] = dados_agregados.apply(calcular_receita, axis=1)
print(dados_agregados.head(21))

megaline_calls['call_date'] = pd.to_datetime(megaline_calls['call_date'])
megaline_calls['month'] = megaline_calls['call_date'].dt.month
chamadas_por_plano = pd.merge(
    megaline_calls,
    megaline_users[['user_id','plan']],
    on='user_id',
    how='left'
)
duracao_media = chamadas_por_plano.groupby(['plan','month'])['duration'].mean().reset_index()
plt.figure(figsize=(5,3))
surf_data = duracao_media[duracao_media['plan'] == 'surf']
ultimate_data = duracao_media[duracao_media['plan'] == 'ultimate']
width = 0.35
x = surf_data['month']
plt.bar(x - width/2, surf_data['duration'], width, label='Surf', color='skyblue', alpha=0.8)
plt.bar(ultimate_data['month'] + width/2, ultimate_data['duration'], width, label='Ultimate', color='orange', alpha=0.8)

plt.title('Duração Média das Chamadas por Plano e Mês', fontsize=10)
plt.xlabel('Mês', fontsize=10)
plt.ylabel('Duração Média (minutos)', fontsize=10)
plt.legend(loc='lower left', fontsize=5)

minutos_por_usuario_mes = megaline_calls.groupby(['user_id','month'])['duration'].sum().reset_index()

minutos_com_plano = pd.merge(
    minutos_por_usuario_mes,
    megaline_users[['user_id', 'plan']],
    on='user_id',
    how='left'
)

print("Dados preparados:")
print(minutos_com_plano.head())
print(f"\nTotal de registros: {len(minutos_com_plano)}")

plt.figure(figsize=(12, 6))

surf_minutos = minutos_com_plano[minutos_com_plano['plan'] == 'surf']['duration']
ultimate_minutos = minutos_com_plano[minutos_com_plano['plan'] == 'ultimate']['duration']

plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 6))

plt.hist(surf_minutos, bins=30, alpha=0.6, label='Surf', color='purple', edgecolor='black')
plt.hist(ultimate_minutos, bins=30, alpha=0.6, label='Ultimate', color='yellow', edgecolor='black')

plt.title('Comparação da Distribuição de Minutos por Plano')
plt.xlabel('Minutos por mês')
plt.ylabel('Frequência')
plt.legend(fontsize=14)
plt.grid(True, alpha=0.3)
plt.show()

print('*****PLANO SURF*****')
media_surf = minutos_surf.mean()
variancia_surf = minutos_surf.var()
print(f'A média é: {media_surf:.2f}') 
print(f'A variância é: {variancia_surf:.2f}')
print()
print('*****PLANO ULTIMATE*****')
media_ultimate = minutos_ultimate.mean()
variancia_ultimate = minutos_ultimate.var()
print(f'A média é: {media_ultimate:.2f}')
print(f'A variância é: {variancia_ultimate:.2f}')

plt.figure(figsize=(10,6))
sns.boxplot(data=dados_agregados, x='plan', y='minutos')

plt.title('Distribuição da Duração Mensal das Chamadas por Plano', fontsize=12)
plt.xlabel('Plano', fontsize=12)
plt.ylabel('Minutos por Mês',fontsize=12)
plt.grid(True, alpha=0.5)

plt.show()

mensagens_por_usuario_mes = megaline_messages.groupby(['user_id','month'])['id'].count().reset_index()

mensagens_por_plano = pd.merge(
    mensagens_por_usuario_mes,
    megaline_users[['user_id', 'plan']],
    on='user_id',
    how='left'
)

print("Dados preparados:")
print(mensagens_por_plano.head(5))
print(f"\nTotal de registros: {len(mensagens_por_plano)}")

plt.figure(figsize=(8, 4))
plt.hist(mensagens_surf, bins=30, alpha=0.7, label='Surf', color='purple', edgecolor='black')
plt.hist(mensagens_ultimate, bins=30, alpha=0.7, label='Ultimate', color='yellow', edgecolor='black')
plt.title('Distribuição de Mensagens Enviadas por Mês', fontsize=14)
plt.xlabel('Mensagens por Mês', fontsize=12)
plt.ylabel('Frequência', fontsize=12)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.show()

trafego_por_usuario_plano = megaline_internet.groupby(['user_id'])['gb_used'].sum().reset_index()

trafego_por_plano = pd.merge(
    trafego_por_usuario_plano,
    megaline_users[['user_id','plan']],
    on='user_id',
    how='left'
)

print('Dados preparados: ')
print(trafego_por_plano.head(5))
print(f"\nTotal de registros: {len(trafego_por_plano)}")

internet_surf = trafego_por_plano[trafego_por_plano['plan']== 'surf']['gb_used']
internet_ultimate = trafego_por_plano[trafego_por_plano['plan']== 'ultimate']['gb_used']

print(f"Usuários Surf: {len(internet_surf)}")
print(f"Usuários Ultimate: {len(internet_ultimate)}")

plt.figure(figsize=(8, 4))
plt.hist(internet_surf, bins=30, alpha=0.7, label='Surf', color='purple', edgecolor='black')
plt.hist(internet_ultimate, bins=30, alpha=0.7, label='Ultimate', color='yellow', edgecolor='black')
plt.title('Tráfego de Internet Consumido pelos Usuários por Plano', fontsize=14)
plt.xlabel('Planos', fontsize=12)
plt.ylabel('Consumo', fontsize=12)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.show()

print('*****PLANO SURF*****')
media_surf = mensagens_surf.mean()
variancia_surf = mensagens_surf.var()
print(f'A média é: {media_surf:.2f}') 
print(f'A variância é: {variancia_surf:.2f}')
print()
print('*****PLANO ULTIMATE*****')
media_ultimate = mensagens_ultimate.mean()
variancia_ultimate = mensagens_ultimate.var()
print(f'A média é: {media_ultimate:.2f}')
print(f'A variância é: {variancia_ultimate:.2f}')

plt.figure(figsize=(10,6))
sns.boxplot(data=dados_agregados, x='plan', y='mensagens')

plt.title('Distribuição de Mensagens enviadas por Plano', fontsize=12)
plt.xlabel('Plano', fontsize=12)
plt.ylabel('Mensagens por Mês',fontsize=12)
plt.grid(True, alpha=0.5)

plt.show()

megaline_internet['month'] = megaline_internet['session_date'].dt.month
trafego_por_usuario_mes = megaline_internet.groupby(['user_id','month'])['gb_used'].sum().reset_index()

trafego_por_mes = pd.merge(
    trafego_por_usuario_mes,
    megaline_users[['user_id', 'plan']],
    on='user_id',
    how='left'
)

print("Dados preparados:")
print(trafego_por_mes.head())
print(f"\nTotal de registros: {len(trafego_por_mes)}")

internet_surf = trafego_por_mes[trafego_por_mes['plan'] == 'surf']['gb_used']
internet_ultimate = trafego_por_mes[trafego_por_mes['plan'] == 'ultimate']['gb_used']

print(f"Usuários Surf: {len(internet_surf)}")
print(f"Usuários Ultimate: {len(internet_ultimate)}")

plt.figure(figsize=(8, 4))
plt.hist(internet_surf, bins=30, alpha=0.7, label='Surf', color='purple', edgecolor='black')
plt.hist(internet_ultimate, bins=30, alpha=0.7, label='Ultimate', color='yellow', edgecolor='black')
plt.title('Tráfego de Internet Consumido pelos Usuários por Mês', fontsize=14)
plt.xlabel('Consumo de Internet GB', fontsize=12)
plt.ylabel('Frequencia', fontsize=12)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.show()

plt.figure(figsize=(10, 6))
sns.boxplot(data=trafego_por_mes, x='plan', y='gb_used')
plt.title('Distribuição do Tráfego de Internet por Mês', fontsize=14)
plt.xlabel('Plano', fontsize=12)
plt.ylabel('Tráfego de Internet (GB por mês)', fontsize=12)
plt.grid(True, alpha=0.3)
plt.show()

print('*****PLANO SURF*****')
media_surf = surf_minutos.mean()
variancia_surf = surf_minutos.var()
print(f'Média: {media_surf:.2f} gb')
print(f'Variância: {variancia_surf:.2f}')

print()

print('*****PLANO ULTIMATE*****')
media_ultimate = ultimate_minutos.mean()
variancia_ultimate = ultimate_minutos.var()
print(f'Média: {media_ultimate:.2f} gb')
print(f'Variância: {variancia_ultimate:.2f}')

receitas_surf = dados_agregados[dados_agregados['plan'] == 'surf']['receita']
receitas_ultimate = dados_agregados[dados_agregados['plan'] == 'ultimate']['receita']

print(f"Usuários Surf: {len(receitas_surf)}")
print(f"Usuários Ultimate: {len(receitas_ultimate)}")

plt.figure(figsize=(12, 6))
plt.hist(receitas_surf, bins=30, alpha=0.6, label='Surf', color='skyblue', edgecolor='black')
plt.hist(receitas_ultimate, bins=30, alpha=0.6, label='Ultimate', color='orange', edgecolor='black')
plt.title('Distribuição das Receitas Mensais por Plano', fontsize=14)
plt.xlabel('Receita Mensal (USD)', fontsize=12)
plt.ylabel('Frequência', fontsize=12)
plt.legend(fontsize=12)
plt.grid(True, alpha=0.3)
plt.show()

print('*****PLANO SURF*****')
media_surf = receitas_surf.mean()
variancia_surf = receitas_surf.var()
print(f'Média: ${media_surf:.2f}')
print(f'Variância: {variancia_surf:.2f}')
print()
print('*****PLANO ULTIMATE*****')
media_ultimate = receitas_ultimate.mean()
variancia_ultimate = receitas_ultimate.var()
print(f'Média: ${media_ultimate:.2f}')
print(f'Variância: {variancia_ultimate:.2f}')

alpha = 0.05

statistic, p_value = stats.ttest_ind(receitas_ultimate, receitas_surf)

print("Teste de hipóteses")
print(f"Estatística do teste: {statistic:.4f}")
print(f"Valor p: {p_value:.10f}")
print(f"Nível de significância: {alpha}")
print()
if p_value < alpha:
    print("Resultado: Rejeitamos a hipótese nula")
    print("Conclusão: Há evidência estatística de que as receitas médias são diferentes")
else:
    print("Resultado: Não rejeitamos a hipótese nula")
    print("Conclusão: Não há evidência estatística suficiente para afirmar que as receitas médias são diferentes")

alpha = 0.05

usuarios_ny_nj = megaline_users[megaline_users['city'].str.contains('NY-NJ', na=False)]
outras_regioes = megaline_users[~megaline_users['city'].str.contains('NY-NJ', na=False)]

receitas_ny_nj = dados_agregados[dados_agregados['user_id'].isin(usuarios_ny_nj['user_id'])]['receita']
receitas_outras = dados_agregados[dados_agregados['user_id'].isin(outras_regioes['user_id'])]['receita']

statistic, p_value = stats.ttest_ind(receitas_ny_nj, receitas_outras)

print("Teste de hipóteses")
print(f"Estatística do teste: {statistic:.4f}")
print(f"Valor p: {p_value:.10f}")
print(f"Nível de significância: {alpha}")
print()
if p_value < alpha:
    print("Resultado: Rejeitamos a hipótese nula")
    print("Conclusão: Há evidência estatística de que as receitas médias são diferentes")
else:
    print("Resultado: Não rejeitamos a hipótese nula")
    print("Conclusão: Não há evidência estatística suficiente para afirmar que as receitas médias são diferentes")

# Conclusão geral do projeto: De maneira geral, os dados indicam que embora os planos Surf e Ultimate apresentem comportamentos semelhantes, o Ultimate se destaca por gerar maior receita e apresentar um consumo médio maior em chamadas e uso de internet. A linha mediana mais alta para o plano Ultimate mostra que seus usuários realizam mais ligações. Apesar do plano Surf possuir mais usuários, o Ultimate demonstra mais receitas mensais fixas. Então, concluo que o Ultimate representa usuários mais ativos, enquanto o Surf concentra mais numero de usuários.
