import os
from models.xml_reader import ler_nf

def calcular_financas(pasta="Notas_fiscais_xml1"):
    """
    Lê todas as notas e calcula:
    - total de compras
    - total de vendas
    - saldo (vendas - compras)
    - histórico detalhado
    """
    total_compras = 0
    total_vendas = 0
    historico = []

    for arquivo in os.listdir(pasta):
        if arquivo.endswith(".xml"):
            caminho = os.path.join(pasta, arquivo)

            tipo, data, produtos = ler_nf(caminho)
            subtotal = sum(p["valor_total"] for p in produtos)

            historico.append({
                "arquivo": arquivo,
                "tipo": tipo,
                "data": data,
                "valor": subtotal
            })

            if tipo == "COMPRA":
                total_compras += subtotal
            else:
                total_vendas += subtotal

    saldo = total_vendas - total_compras
    return total_compras, total_vendas, saldo, historico
