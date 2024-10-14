import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime



def conectar_banco():
    conn = sqlite3.connect('estoque.db')
    return conn

def carregar_dados(pesquisa=""):
    conn = conectar_banco()
    query = "SELECT * FROM produto"
    if pesquisa:
        query += f" WHERE pro_nome LIKE '%{pesquisa}%'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

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


def home():
    st.subheader("Selecione os Produtos")
    pesquisa_col, button_col = st.columns([3, 1])
    with pesquisa_col:
        pesquisa = st.text_input("Pesquisa", "", key="pesquisa")

    with button_col:
        if st.button("Pesquisar"):
            xx = 0

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
                key=f"quantidade_{index}",
                index=1
            )
        with col5:
            if st.button("Adicionar ao carrinho", key=f"add_{index}"):
                adicionar_ao_carrinho(row['pro_cod'], row['pro_nome'], quantidade, row['pro_valorvenda'])
                st.toast(f"Adicionado ao carrinho: {row['pro_nome']}")





def enviar_email(gmail_user, gmail_password, to_email, subject, body, filename=None):
    # Configurações do servidor SMTP
    smtp_host = 'smtp.gmail.com'
    smtp_port = 587
    from_email = gmail_user

    # Criar a mensagem
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Adicionar o corpo do e-mail
    msg.attach(MIMEText(body, 'plain'))

    # (Opcional) Anexar um arquivo ao e-mail
    if filename:
        try:
            attachment = open(filename, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={filename}')
            msg.attach(part)
        except Exception as e:
            print(f"Falha ao anexar o arquivo: {e}")
            return

    # Enviar o e-mail
    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(gmail_user, gmail_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        st.toast("E-mail enviado com sucesso!")
    except Exception as e:
        st.toast(f"Falha ao enviar o e-mail: {e}")


def gerar_corpo_email(nome, email, whatsapp):
    if 'carrinho' not in st.session_state or len(st.session_state['carrinho']) == 0:
        return "Carrinho vazio!"

    corpo = (f"Nome: {nome}\n\n"
             f"E-mail: {email}\n\n"
             f"WhatsApp: {whatsapp}\n\n\n"
             f"Resumo do Pedido:\n\n")



    total = 0

    for item in st.session_state['carrinho']:
        subtotal = item['quantidade'] * item['pro_valorvenda']
        total += subtotal
        corpo += (f"Produto: {item['pro_nome']}   \n"
                  f"Quantidade: {item['quantidade']}   \n"
                  f"Preço Unitário: R$ {item['pro_valorvenda']:.2f} \n\n"
                  f"Subtotal: R$ {subtotal:.2f}\n\n")

    corpo += f"Total do Pedido: R$ {total:.2f}"
    return corpo

def gerar_numero_pedido():
    agora = datetime.now()
    numero_pedido = agora.strftime("%d%m%y%H%M")  # Formato: ddMMyyHHmm
    return numero_pedido

def pag1():
    st.subheader("Confira os dados de seu pedido")

    if 'carrinho' not in st.session_state or len(st.session_state['carrinho']) == 0:
        st.warning("Carrinho vazio!")
    else:
        # Exibe os itens do carrinho
        total = 0

        for index, item in enumerate(st.session_state['carrinho']):
            col1, col2, col3, col4 ,col5 = st.columns([2, 2, 2, 2, 2])
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
            with col5:
                if st.button('Excluir', key=f"excluir_{index}"):
                    st.session_state['carrinho'].pop(index)
                    st.rerun()







        st.write(f"**Total: R$ {total:.2f}**")




def pag2():
    st.subheader("Envie seu pedido")
    nome = st.text_input("Nome")
    email = st.text_input("E-mail")
    whatsapp = st.text_input("WhatsApp")

    if st.button("Enviar"):
        ped = gerar_numero_pedido()
        corpo = gerar_corpo_email(nome, email, whatsapp)
        gmail_user = 'fivestarshdw@gmail.com'
        gmail_password = 'o w e l y t y g l c g s p j k x'
        to_email = 'felipedssilva@hotmail.com'

        subject = 'pedido numero ' + ped
        body = ''
        filename = None  # Defina None se não quiser anexar arquivo

        # Chamando a função
        enviar_email(gmail_user, gmail_password, to_email, subject, corpo, filename)


def main():

    Home = st.Page(home,title="Fazer Pedido")
    Pag1 = st.Page(pag1,title="Revisar Pedido")
    Pag2 = st.Page(pag2,title="Enviar Pedido")
    pg = st.navigation([Home,Pag1,Pag2])
    carrinho =1
    pg.run()

if __name__ == "__main__":
    main()

