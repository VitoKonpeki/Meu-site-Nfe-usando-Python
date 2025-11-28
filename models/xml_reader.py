import xml.etree.ElementTree as ET

ns = {"nfe": "http://www.portalfiscal.inf.br/nfe"}

def ler_nf(caminho):
    """
    Lê uma nota fiscal XML e retorna:
    - tipo ("COMPRA" ou "VENDA")
    - data (usa dFab)
    - lista de produtos
    """

    tree = ET.parse(caminho)
    root = tree.getroot()

    # Se vier envelopado como <nfeProc>, pegamos o <NFe>
    nfe = root.find(".//nfe:NFe", ns)
    if nfe is None:
        nfe = root

    # Tipo da NF
    ide = nfe.find(".//nfe:ide", ns)
    tpNF = ide.find("nfe:tpNF", ns).text.strip()
    tipo = "VENDA" if tpNF == "1" else "COMPRA"

    # --- DATA: agora buscando *dFab* ---
    # dFab fica dentro do produto → rastro
# --- DATA: agora buscando *dFab* corretamente ---
    data = None
    dFab_tag = nfe.find(".//nfe:prod/nfe:rastro/nfe:dFab", ns)

    if dFab_tag is None:
        data = None
    else:
        data = dFab_tag.text

    # Produtos
    produtos = []
    for det in nfe.findall(".//nfe:det", ns):
        prod = det.find("nfe:prod", ns)
        if prod is None:
            continue

        nome = prod.find("nfe:xProd", ns).text
        quantidade = float(prod.find("nfe:qCom", ns).text)
        valor_total = float(prod.find("nfe:vProd", ns).text)

        produtos.append({
            "produto": nome,
            "quantidade": quantidade,
            "valor_total": valor_total
        })

    return tipo, data, produtos