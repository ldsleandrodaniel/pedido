import sqlite3
import pandas as pd
import streamlit as st
from PIL import Image
import io

#rodar com python -m streamlit run pedido.py

carrinho = []

# Função para conectar ao banco de dados
def conectar_banco():
    conn = sqlite3.connect('estoque.db')
    return conn

# Função para carregar os dados dos produtos
def carregar_dados(pesquisa=""):
    conn = conectar_banco()
    query = "SELECT * FROM produto"
    if pesquisa:
        query += f" WHERE pro_nome LIKE '%{pesquisa}%'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Função para exibir a página de produtos
def pagina_produtos():
    st.title("Five Stars Hardware - Pedidos")
    # Barra de pesquisa
    pesquisa_col, button_col = st.columns([3, 1])
    with pesquisa_col:
        pesquisa = st.text_input("Pesquisa", "", key="pesquisa")

    with button_col:
        if st.button("Pesquisar"):
            xx=0

    # Carregar e exibir os produtos
    dados_produtos = carregar_dados(pesquisa)
    for index, row in dados_produtos.iterrows():
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])  # Ajuste as colunas
        with col1:
            st.write(row['pro_nome'])
        with col2:
            st.write(f"R$ {row['pro_valorvenda']:.2f}")
        with col3:
            img_data = row['pro_foto']
            if img_data:
                img = Image.open(io.BytesIO(img_data))
                img.thumbnail((100, 100))  # Miniatura
                st.image(img)
            else:
                st.write("Sem imagem")
        with col4:
            quantidade = st.selectbox(
                "Quantidade",
                options=range(int(row['pro_qtde']) + 1),
                key=f"quantidade_{index}"
            )
        with col5:
            if st.button("Adicionar ao carrinho", key=f"add_{index}"):
                adicionar_ao_carrinho(row['pro_cod'], row['pro_nome'], quantidade, row['pro_valorvenda'])
                st.success(f"Adicionado ao carrinho: {row['pro_nome']}")

# Função para adicionar item ao carrinho
def adicionar_ao_carrinho(pro_cod, pro_nome, quantidade, pro_valorvenda):
    if 'carrinho' not in st.session_state:
        st.session_state['carrinho'] = []

        # Adiciona o item ao carrinho na sessão
    st.session_state['carrinho'].append({
        'pro_cod': pro_cod,
        'pro_nome': pro_nome,
        'quantidade': quantidade,
        'pro_valorvenda': pro_valorvenda
    })

# Função para exibir a página do carrinho
def pagina_carrinho():
    st.title("Carrinho de Compras")

    if 'carrinho' not in st.session_state or len(st.session_state['carrinho']) == 0:
        st.warning("Carrinho vazio!")
    else:
        # Exibe os itens do carrinho
        total = 0
        for item in st.session_state['carrinho']:
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            with col1:
                st.write(item['pro_nome'])
            with col2:
                st.write(f"Quantidade: {item['quantidade']}")
            with col3:
                st.write(f"Preço Unitário: R$ {item['pro_valorvenda']:.2f}")
            with col4:
                subtotal = item['quantidade'] * item['pro_valorvenda']
                total += subtotal
                st.write(f"Subtotal: R$ {subtotal:.2f}")

        st.write(f"**Total: R$ {total:.2f}**")
        # Botão para enviar pedido
        if st.button("Enviar Pedido"):
            st.success("Pedido enviado com sucesso!")
            st.session_state['carrinho'].clear()  # Limpa o carrinho após enviar o pedido
# Função principal para criar o layout com navegação
def main():
    # Barra lateral para navegação entre páginas
    pagina = st.sidebar.selectbox("Navegação", ["Produtos", "Carrinho"])

    # Navega entre as páginas
    if pagina == "Produtos":
        pagina_produtos()
    elif pagina == "Carrinho":
        pagina_carrinho()

if __name__ == "__main__":
    main()