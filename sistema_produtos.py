"""
Sistema de Gerenciamento de Produtos - Loja fictícia
Disciplina: Programação Python
Banco de dados: SQLite (arquivo loja.db)
"""

import os
import sqlite3

# O banco fica na mesma pasta do script, assim os dados persistem
# independente de onde o programa for executado.
PASTA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BANCO = os.path.join(PASTA, "loja.db")



def conectar():
    """Abre a conexão com o banco loja.db (cria o arquivo se não existir)."""
    return sqlite3.connect(CAMINHO_BANCO)


def criar_tabela(conexao):
    """Cria a tabela produtos automaticamente, caso ainda não exista."""
    cursor = conexao.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            nome       TEXT    NOT NULL,
            categoria  TEXT    NOT NULL,
            preco      REAL    NOT NULL,
            quantidade INTEGER NOT NULL
        )
        """
    )
    conexao.commit()



def ler_texto(mensagem):
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("Campo obrigatório. Tente novamente.")


def ler_preco(mensagem):
    while True:
        try:
            valor = float(input(mensagem).strip().replace(",", "."))
            if valor < 0:
                print("O preço não pode ser negativo.")
                continue
            return valor
        except ValueError:
            print("Valor inválido. Digite um número, por exemplo: 19.90")


def ler_inteiro(mensagem, minimo=0):
    while True:
        try:
            valor = int(input(mensagem).strip())
            if valor < minimo:
                print(f"O valor deve ser maior ou igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("Valor inválido. Digite um número inteiro.")


def formatar_reais(valor):
    """Formata um número no padrão brasileiro: R$ 1.234,56"""
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def exibir_produtos(produtos):
    """Mostra uma lista de produtos em formato de tabela."""
    print()
    print(f"{'ID':<5}{'Nome':<25}{'Categoria':<18}{'Preço':>14}{'Qtd':>6}")
    print("-" * 68)
    for id_, nome, categoria, preco, quantidade in produtos:
        print(
            f"{id_:<5}{nome[:24]:<25}{categoria[:17]:<18}"
            f"{formatar_reais(preco):>14}{quantidade:>6}"
        )
    print("-" * 68)



def cadastrar_produto(conexao):
    print("\n--- Cadastrar produto ---")
    nome = ler_texto("Nome: ")
    categoria = ler_texto("Categoria: ")
    preco = ler_preco("Preço (R$): ")
    quantidade = ler_inteiro("Quantidade em estoque: ")

    cursor = conexao.cursor()
    # Os "?" são parâmetros: evitam SQL Injection.
    cursor.execute(
        "INSERT INTO produtos (nome, categoria, preco, quantidade) "
        "VALUES (?, ?, ?, ?)",
        (nome, categoria, preco, quantidade),
    )
    conexao.commit()
    print(f"\nProduto '{nome}' cadastrado com sucesso! (ID {cursor.lastrowid})")


def listar_produtos(conexao):
    print("\n--- Lista de produtos ---")
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id, nome, categoria, preco, quantidade FROM produtos ORDER BY id"
    )
    produtos = cursor.fetchall()

    if not produtos:
        print("Nenhum produto cadastrado.")
        return
    exibir_produtos(produtos)


def pesquisar_produto(conexao):
    print("\n--- Pesquisar produto pelo nome ---")
    termo = ler_texto("Digite o nome (ou parte dele): ")

    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id, nome, categoria, preco, quantidade FROM produtos "
        "WHERE nome LIKE ? ORDER BY nome",
        (f"%{termo}%",),
    )
    produtos = cursor.fetchall()

    if not produtos:
        print(f"Nenhum produto encontrado com o nome '{termo}'.")
        return
    exibir_produtos(produtos)


def produto_existe(conexao, id_produto):
    cursor = conexao.cursor()
    cursor.execute("SELECT 1 FROM produtos WHERE id = ?", (id_produto,))
    return cursor.fetchone() is not None


def atualizar_produto(conexao):
    print("\n--- Atualizar produto ---")
    id_produto = ler_inteiro("ID do produto: ", minimo=1)

    if not produto_existe(conexao, id_produto):
        print(f"Produto com ID {id_produto} não encontrado.")
        return

    print("O que deseja atualizar?")
    print("  1 - Preço")
    print("  2 - Quantidade")
    opcao = input("Escolha: ").strip()

    cursor = conexao.cursor()
    if opcao == "1":
        novo_preco = ler_preco("Novo preço (R$): ")
        cursor.execute(
            "UPDATE produtos SET preco = ? WHERE id = ?", (novo_preco, id_produto)
        )
    elif opcao == "2":
        nova_qtd = ler_inteiro("Nova quantidade: ")
        cursor.execute(
            "UPDATE produtos SET quantidade = ? WHERE id = ?", (nova_qtd, id_produto)
        )
    else:
        print("Opção inválida. Nada foi alterado.")
        return

    conexao.commit()
    print("\nProduto atualizado com sucesso!")


def excluir_produto(conexao):
    print("\n--- Excluir produto ---")
    id_produto = ler_inteiro("ID do produto: ", minimo=1)

    if not produto_existe(conexao, id_produto):
        print(f"Produto com ID {id_produto} não encontrado.")
        return

    confirmacao = input(f"Confirma a exclusão do produto {id_produto}? (s/n): ")
    if confirmacao.strip().lower() != "s":
        print("Exclusão cancelada.")
        return

    cursor = conexao.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
    conexao.commit()
    print("\nProduto excluído com sucesso!")


def valor_total_estoque(conexao):
    print("\n--- Valor total do estoque ---")
    cursor = conexao.cursor()
    cursor.execute("SELECT SUM(preco * quantidade) FROM produtos")
    total = cursor.fetchone()[0] or 0
    print(f"Valor total do estoque: {formatar_reais(total)}")



def exibir_menu():
    print("\n" + "=" * 40)
    print("   SISTEMA DE GERENCIAMENTO DE PRODUTOS")
    print("=" * 40)
    print("1 - Cadastrar produto")
    print("2 - Listar todos os produtos")
    print("3 - Pesquisar produto pelo nome")
    print("4 - Atualizar preço ou quantidade")
    print("5 - Excluir produto")
    print("6 - Exibir valor total do estoque")
    print("0 - Sair")
    print("=" * 40)


def main():
    conexao = conectar()
    try:
        criar_tabela(conexao)

        acoes = {
            "1": cadastrar_produto,
            "2": listar_produtos,
            "3": pesquisar_produto,
            "4": atualizar_produto,
            "5": excluir_produto,
            "6": valor_total_estoque,
        }

        while True:
            exibir_menu()
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "0":
                print("\nEncerrando o sistema. Até logo!")
                break
            elif opcao in acoes:
                acoes[opcao](conexao)
            else:
                print("\nOpção inválida. Escolha um número do menu.")
    except KeyboardInterrupt:
        print("\n\nPrograma interrompido pelo usuário.")
    finally:
        # Garante que a conexão seja sempre fechada ao encerrar.
        conexao.close()


if __name__ == "__main__":
    main()
