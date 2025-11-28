from flask import Flask, render_template, request, redirect, url_for, send_file, session
from models.estoque import gerar_relatorio_entrada_saida
import os
import re
from datetime import datetime
import glob
import xml.etree.ElementTree as ET
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from models.estoque import gerar_relatorio_entrada_saida, carregar_estoque
# Definindo o namespace
ns = 'http://www.portalfiscal.inf.br/nfe'

# Módulos internos
from models.estoque import atualizar_estoque, carregar_estoque
from models.xml_reader import ler_nf
from models.financeiro import calcular_financas
from flask_paginate import Pagination, get_page_args
from models.usuarios import criar_usuario, login_usuario
from validate_email import validate_email
import string
from models.db import init_db
init_db()

# Módulos internos
from models.estoque import atualizar_estoque, carregar_estoque
from models.xml_reader import ler_nf
from models.financeiro import calcular_financas

app = Flask(__name__, static_folder="Static", template_folder="templates")
app.secret_key = "vitorelegal"
dados_usuarios = {}

# FUNÇÕES AUXILIARES
def verificar_senha_user(senha):
    return (
        any(c.isdigit() for c in senha) and
        any(c.isalpha() for c in senha) and
        any(c in string.punctuation for c in senha) and
        any(c.isupper() for c in senha)
    )



# LOGIN / CADASTRO
from models.usuarios import criar_usuario

@app.route("/", methods=["GET", "POST"])
def cadastro_user():
    mensagem = ""

    if request.method == "POST":
        nome = request.form["email"]
        senha = request.form["Password"]

        if len(nome) > 250:
            mensagem = "O nome não pode ter mais de 20 caracteres."
        elif len(senha) < 6:
            mensagem = "A senha precisa ter ao menos 6 caracteres."
        elif not verificar_senha_user(senha):
            mensagem = "A senha deve ter número, letra, símbolo e letra maiúscula."
        elif criar_usuario(nome, senha) == "email_existe":
            mensagem = "Este usuário já existe."
        elif criar_usuario(nome, senha) == "email_sem_acesso":
            mensagem = "Voce não tem permissão de acesso"
        else:
            return redirect(url_for("login_conta_existente"))

    return render_template("cadastro.html", mensagem=mensagem)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("cadastro_user"))


from models.usuarios import login_usuario

@app.route("/login_conta_existente", methods=["GET", "POST"])
def login_conta_existente():
    mensagem = ""
    if request.method == "POST":
        nome = request.form["email"]
        senha = request.form["Password"]

        resultado = login_usuario(nome, senha)

        if not resultado:
            mensagem = "Usuário ou senha incorretos."
        else:
            session["usuario_id"] = resultado["id"]
            session["nivel"] = resultado["nivel"]
            print(session)
            return redirect(url_for("homepage"))

    return render_template("login.html", mensagem=mensagem)



@app.route("/homepage")
def homepage():
    return render_template("homepage.html")



# IMPORTAÇÃO DE NOTAS + ATUALIZAÇÃO DE ESTOQUE
@app.route("/importar_arquivo")
def importar_arquivo():
    return render_template("importarNovaNota.html", mensagem="")


@app.route("/upload_notas", methods=["POST"])
def upload_notas():
    pasta = "Notas_fiscais_xml1"
    os.makedirs(pasta, exist_ok=True)

    arquivo = request.files.get("arquivo_xml")

    if not arquivo:
        return render_template("importarNovaNota.html", mensagem="Nenhum arquivo enviado!")

    if not arquivo.filename.endswith(".xml"):
        return render_template("importarNovaNota.html", mensagem="Envie apenas XML.")

    caminho = os.path.join(pasta, arquivo.filename)
    arquivo.save(caminho)

    tipo, data, produtos = ler_nf(caminho)
    for p in produtos:
        atualizar_estoque(p["produto"], p["quantidade"], tipo)

    return render_template("importarNovaNota.html", mensagem="Nota importada com sucesso!")



# LISTAR NOTAS IMPORTADAS
@app.route("/importarNotas")
def importar_notas():
    dados = []
    pasta = "Notas_fiscais_xml1"
    ns = {"nfe": "http://www.portalfiscal.inf.br/nfe"}

    arquivos = glob.glob(f"{pasta}/**/*.xml", recursive=True)

    def extrair_num(c):
        nome = os.path.basename(c)
        nums = re.findall(r"\d+", nome)
        return int(nums[0]) if nums else 0

    arquivos = sorted(arquivos, key=extrair_num)

    for caminho in arquivos:
        tree = ET.parse(caminho)
        root = tree.getroot()

        emit = root.find(".//nfe:emit", ns)

        nome = emit.find("nfe:xNome", ns).text
        cnpj = emit.find("nfe:CNPJ", ns).text

        for p in root.findall(".//nfe:prod", ns):
            dados.append({
                "Arquivo": os.path.basename(caminho),
                "Nome": nome,
                "CNPJ": cnpj,
                "prod": p.find("nfe:xProd", ns).text
            })

    page, per_page, offset = get_page_args()
    per_page = 10

    dados_paginados = dados[offset:offset + per_page]

    pagination = Pagination(page=page, per_page=per_page,
                            total=len(dados), css_framework="bootstrap4")

    return render_template("importarNotas.html", dados=dados_paginados,
                           pagination=pagination)

ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

import xml.etree.ElementTree as ET
from datetime import datetime
import matplotlib.pyplot as plt
import glob
import collections
import matplotlib.dates as mdates

# Definindo o namespace
ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

def gerar_grafico(pasta="Notas_fiscais_xml1", grafico_path="static/grafico_relatorio.png",
                  figsize=(6.99, 6), dpi=150, aggregate_by_date=True):
    datas_compras = []
    datas_vendas = []
    quantidades_compras = []
    quantidades_vendas = []

    arquivos = glob.glob(f"{pasta}/**/*.xml", recursive=True)

    for arquivo in arquivos:
        tree = ET.parse(arquivo)
        root = tree.getroot()

        tp_elem = root.find('.//nfe:tpNF', ns)
        if tp_elem is None:
            continue
        tp = tp_elem.text  # '0' compra, '1' venda

        for p in root.findall('.//nfe:det', ns):
            quantidade_elem = p.find('.//nfe:prod/nfe:qCom', ns)
            if quantidade_elem is None:
                continue

            try:
                quantidade = float(quantidade_elem.text)
            except (ValueError, TypeError):
                continue

            dFab_elem = p.find('.//nfe:prod/nfe:rastro/nfe:dFab', ns)
            if dFab_elem is None or not dFab_elem.text:
                continue

            try:
                dt = datetime.strptime(dFab_elem.text, "%Y-%m-%d").date()  # usar date para agrupar por dia
            except ValueError:
                continue

            if tp == '0':
                datas_compras.append(dt)
                quantidades_compras.append(quantidade)
            else:
                datas_vendas.append(dt)
                quantidades_vendas.append(quantidade)

    # Função auxiliar para agregar (somar) quantidades por data (reduz pontos)
    def aggregate(dates, amounts):
        if not dates:
            return [], []
        agg = collections.defaultdict(float)
        for d, a in zip(dates, amounts):
            agg[d] += a
        items = sorted(agg.items())
        xs, ys = zip(*items)
        # converter datas de volta para datetime para o matplotlib
        xs = [datetime.combine(x, datetime.min.time()) for x in xs]
        return xs, ys

    # ordenar e (opcional) agregar
    if aggregate_by_date:
        datas_compras, quantidades_compras = aggregate(datas_compras, quantidades_compras)
        datas_vendas, quantidades_vendas = aggregate(datas_vendas, quantidades_vendas)
    else:
        compras_ordenadas = sorted(zip(datas_compras, quantidades_compras))
        vendas_ordenadas = sorted(zip(datas_vendas, quantidades_vendas))
        if compras_ordenadas:
            datas_compras, quantidades_compras = zip(*compras_ordenadas)
            datas_compras = [datetime.combine(d, datetime.min.time()) for d in datas_compras]
        if vendas_ordenadas:
            datas_vendas, quantidades_vendas = zip(*vendas_ordenadas)
            datas_vendas = [datetime.combine(d, datetime.min.time()) for d in datas_vendas]

    # Criar gráfico maior e mais nítido
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=figsize, dpi=dpi)

    # Plot com linhas finas e marcadores pequenos
    if datas_compras:
        ax1.plot(datas_compras, quantidades_compras, marker='o', linestyle='-', linewidth=1, markersize=4, alpha=0.9)
    ax1.set_title("Notas de Compra (tpNF=0)")
    ax1.set_ylabel('Quantidade de Compra')
    ax1.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.6)

    if datas_vendas:
        ax2.plot(datas_vendas, quantidades_vendas, marker='o', linestyle='-', linewidth=1, markersize=4, alpha=0.9)
    ax2.set_title("Notas de Venda (tpNF=1)")
    ax2.set_ylabel('Quantidade de Venda')
    ax2.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.6)

    # Formatação do eixo X: locator automático + formatter conciso (menos poluição)
    import locale

    # Definir idioma para meses em PT-BR
    try:
        locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
    except:
        locale.setlocale(locale.LC_TIME, 'pt_BR')

    ax2.xaxis.set_major_locator(mdates.MonthLocator())              # coloca 1 tick por mês
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b'))       # exibe abreviação (Ago, Set...)

    # Ajustes visuais
    plt.xlabel("Data de Fabricação (dFab)")
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=30, ha='right')
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.25)

    # Salvar com margens cortadas
    plt.savefig(grafico_path, bbox_inches='tight')
    plt.close()

    return grafico_path

from models.estoque import zerar_estoque
from models.estoque import zerar_notas  # <<<< adicionado

@app.route("/zerar_estoque")
def zerar():
    zerar_estoque()
    return redirect(url_for("homepage"))

# rota nova: zera arquivos de notas fiscais (XML) e mostra mensagem
@app.route("/zerar_notas")
def zerar_notas_route():
    removidos = zerar_notas()
    mensagem = f"{removidos} notas fiscais removidas." if removidos else "Nenhuma nota encontrada."
    # exibe a mesma tela de importação com mensagem
    return render_template("importarNovaNota.html", mensagem=mensagem)


# RELATÓRIOS: FINANCEIRO + GRÁFICO + HISTÓRICO
@app.route("/relatorios")
def relatorios():
    # Chama a função para gerar o gráfico
    grafico_path = gerar_grafico()

    total_compras, total_vendas, saldo, historico = calcular_financas()
    return render_template(
        "relatorios.html",
        total_compras=total_compras,
        total_vendas=total_vendas,
        saldo=saldo,
        historico=historico,
        grafico=grafico_path  # Passa o caminho do gráfico para o template
    )

# ESTOQUE
@app.route("/estoque", endpoint="ver_estoque")
def ver_estoque():
    estoque = carregar_estoque()
    return render_template("estoque.html", estoque=estoque)

@app.route("/estoque", endpoint="estoque")
def ver_estoque():
    estoque = carregar_estoque()
    return render_template("estoque.html", estoque=estoque)



# Exibir relatório de entradas/saídas
@app.route("/relatorio_entrada_saida")
def relatorio_entrada_saida():
    relatorio, total_entradas, total_saidas = gerar_relatorio_entrada_saida()
    return render_template("relatorio_entrada_saida.html",
                           relatorio=relatorio,
                           total_entradas=total_entradas,
                           total_saidas=total_saidas)

# Exibir histórico de um produto
@app.route("/historico/<path:produto>")
def historico(produto):
    estoque = carregar_estoque()
    historico = estoque.get(produto, {}).get("historico", [])
    return render_template("historico_produto.html", produto=produto, historico=historico)

# Função simples para gerar gráfico por produto (entradas x saídas)
def gerar_grafico_estoque(path_png=None):
    estoque = carregar_estoque()
    produtos = list(estoque.keys())
    entradas = [estoque[p].get("entradas", 0) for p in produtos]
    saidas = [estoque[p].get("saidas", 0) for p in produtos]

    if not produtos:
        return None

    x = range(len(produtos))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5), dpi=120)
    ax.bar([i - width/2 for i in x], entradas, width=width, label='Entradas', color='#4CAF50')
    ax.bar([i + width/2 for i in x], saidas, width=width, label='Saídas', color='#F44336')
    ax.set_xticks(list(x))
    ax.set_xticklabels(produtos, rotation=45, ha='right')
    ax.set_ylabel('Quantidade')
    ax.set_title('Entradas e Saídas por Produto')
    ax.legend()
    plt.tight_layout()

    if path_png:
        fig.savefig(path_png)
        plt.close(fig)
        return path_png
    else:
        import io
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)
        return buf

# Dashboard que exibe gráfico salvo em Static/
@app.route("/dashboard_estoque")
def dashboard_estoque():
    grafico_nome = "grafico_estoque.png"
    grafico_path = os.path.join(app.static_folder, grafico_nome)
    gerar_grafico_estoque(grafico_path)
    return render_template("dashboard_estoque.html", grafico_url=url_for('static', filename=grafico_nome))




# RUN
@app.route("/routes")
def listar_rotas():
    lines = []
    for rule in app.url_map.iter_rules():
        methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
        lines.append(f"{rule.rule}  -> {methods}")
    return "<br>".join(lines)

if __name__ == "__main__":
    app.run(debug=True)
