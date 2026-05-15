import json
import os
import glob

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQ_ESTOQUE = os.path.join(BASE_DIR, "estoque.json")


def gerar_relatorio_entrada_saida():
    estoque = carregar_estoque()

    relatorio = []
    total_entradas = 0 
    total_saidas = 0

    for produto, dados in estoque.items():
        # usar .get para tolerância a dados antigos
        entradas = dados.get("entradas", 0)
        saidas = dados.get("saidas", 0)
        saldo = dados.get("quantidade", 0)
        relatorio.append({
            "produto": produto,
            "entradas": entradas,
            "saidas": saidas,
            "saldo": saldo
        })

        total_entradas += entradas
        total_saidas += saidas

    return relatorio, total_entradas, total_saidas


def carregar_estoque():
    if not os.path.exists(ARQ_ESTOQUE):
        return {}
    with open(ARQ_ESTOQUE, "r", encoding="utf8") as f:
        data = json.load(f)

    # garantir compatibilidade: adicionar campos que possam faltar (migração)
    for produto, dados in data.items():
        dados.setdefault("quantidade", 0)
        dados.setdefault("entradas", 0)
        dados.setdefault("saidas", 0)
        dados.setdefault("historico", [])

    return data


def salvar_estoque(estoque):
    with open(ARQ_ESTOQUE, "w", encoding="utf8") as f:
        json.dump(estoque, f, indent=4, ensure_ascii=False)


from datetime import datetime

def atualizar_estoque(produto, quantidade, tipo):
    estoque = carregar_estoque()

    if produto not in estoque:
        estoque[produto] = {
            "quantidade": 0,
            "entradas": 0,
            "saidas": 0,
            "historico": []     # <<<<<< ADICIONE ISTO
        }

    registro = {
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "tipo": tipo,
        "quantidade": quantidade
    }
    estoque[produto]["historico"].append(registro)

    if tipo == "COMPRA" or tipo == "0":
        estoque[produto]["quantidade"] += quantidade
        estoque[produto]["entradas"] += quantidade
    elif tipo == "VENDA" or tipo == "1":
        estoque[produto]["quantidade"] -= quantidade
        estoque[produto]["saidas"] += quantidade

    salvar_estoque(estoque)


def zerar_estoque():
    salvar_estoque({})


# nova função: remove arquivos XML em Notas_fiscais_xml1 (retorna contagem)
def zerar_notas(pasta="Notas_fiscais_xml1"):
    if not os.path.isdir(pasta):
        return 0
    arquivos = glob.glob(os.path.join(pasta, "**", "*.xml"), recursive=True)
    removidos = 0
    for a in arquivos:
        try:
            os.remove(a)
            removidos += 1
        except Exception:
            pass
    return removidos
