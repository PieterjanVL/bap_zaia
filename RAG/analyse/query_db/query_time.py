import pandas as pd
import matplotlib.pyplot as plt
def get_average_df(df):
    return df.groupby('neighbors')['time_in_sec'].mean().round(2).reset_index()

df_chroma_384 = get_average_df(pd.read_csv('chroma-query-time-384.csv'))
df_chroma_768 = get_average_df(pd.read_csv('chroma-query-time-768.csv'))

df_qdrant_384 = get_average_df(pd.read_csv('qdrant-query-time-384.csv'))
df_qdrant_768 = get_average_df(pd.read_csv('qdrant-query-time-768.csv'))

df_pinecone_384 = get_average_df(pd.read_csv('pinecone-query-time-384.csv'))
df_pinecone_768 = get_average_df(pd.read_csv('pinecone-query-time-768.csv'))

print(df_chroma_384)
print(df_chroma_768)

print("--------------------------------------------")

print(df_qdrant_384)
print(df_qdrant_768)

def get_average_384_df():
    plt.figure(figsize=(10, 6))
    plt.plot(df_chroma_384['neighbors'], df_chroma_384['time_in_sec'], marker='o', label='chroma 384')
    plt.plot(df_qdrant_384['neighbors'], df_qdrant_384['time_in_sec'], marker='o', label='qdrant 384')
    plt.plot(df_pinecone_384['neighbors'], df_pinecone_384['time_in_sec'], marker='o', label='pinecone 384')

    plt.xlabel('Aantal Neighbors')
    plt.ylabel('Gemmidelde tijd nodig in Seconden')
    plt.title('Vergelijking van het uitvoeren van één query met verschillende aantallen\n'
    'dichtstbijzijnde neighbors in een vectordatabase met een dimensie van 384.')
    plt.legend()

    plt.show()

def get_average_768_df():
    plt.figure(figsize=(10, 6))
    plt.plot(df_chroma_768['neighbors'], df_chroma_768['time_in_sec'], marker='o', label='chroma 768')
    plt.plot(df_qdrant_768['neighbors'], df_qdrant_768['time_in_sec'], marker='o', label='qdrant 768')
    plt.plot(df_pinecone_768['neighbors'], df_pinecone_768['time_in_sec'], marker='o', label='pinecone 768')

    plt.xlabel('Aantal Neighbors')
    plt.ylabel('Gemmidelde tijd nodig in Seconden')
    plt.title('Vergelijking van het uitvoeren van één query met verschillende aantallen\n'
              'dichtstbijzijnde neighbors in een vectordatabase met een dimensie van 768.')
    plt.legend()

    plt.show()


get_average_768_df()