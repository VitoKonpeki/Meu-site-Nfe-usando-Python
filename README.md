README - Sistema de Gestão Financeira e de Estoque com NF-e em XML
1. Descrição Geral
  Este projeto é um sistema completo para importação, leitura, organização e análise de Notas
  Fiscais Eletrônicas (NF-e) em formato XML.
  Ele atualiza automaticamente o estoque, gera relatórios financeiros e estatísticos, e fornece
  uma interface web simples e intuitiva desenvolvida em Python com Flask.

2. Objetivo do Projeto
  O objetivo é criar um sistema capaz de:
  • Importar NF-e em XML (entradas e saídas);
  • Extrair e organizar dados de produtos, valores, clientes e fornecedores;
  • Atualizar automaticamente o estoque;
  • Gerar relatórios financeiros, de estoque e movimentações;
  • Oferecer uma interface web para interação com o usuário.

3. Integrantes do Grupo
  • Vitor Henrique de Sousa
  • Amália Pereira Camandona
  • Gustavo Wellyngton Souza Silva

4. Tecnologias Utilizadas
  • Python 3.12
  • Flask
  • Flask-Paginate
  • Pandas
  • xml.etree.ElementTree
  • glob, os, re, string
  • HTML, CSS

5. Instalação do Ambiente – Linux
  ● 1. Verifique o Python:
  python3 --version
  ● 2. Instale Python e pip:
  sudo apt install python3 python3-pip
  ● 3. Atualize o pip:
  python3 -m pip install --upgrade pip
  ● 4. Instale as dependências:
  python3 -m pip install flask flask-paginate pandas
  ● 5. Execute o sistema no VSCode.

6. Instalação do Ambiente - Windows
  1. Baixe o Python no site oficial.
  2. Marque "Add Python to PATH".
  3. Atualize o pip:
  python -m pip install --upgrade pip

7. Instale Flask, Flask-Paginate e Pandas:
  python -m pip install flask flask-paginate pandas
  7. Como Executar o Sistema
  1. Abra o VSCode
  2. Clique em File → Open Folder
  3. Selecione a pasta do projeto
  4. Execute o arquivo main.py
  5. Abra o link exibido no terminal:
  http://127.0.0.1:5000
8. Funcionalidades do Sistema
  Após o login, o usuário terá acesso às seguintes funções:
  • Importação de NF-e
  Permite carregar arquivos XML e extrair dados automaticamente.
  • Relatórios
  Gera relatórios financeiros, estatísticos e gráficos.
  • Saldo de Estoque
  Mostra entradas, saídas e saldo final dos produtos.
  • Login e Senha
  Validação de usuário, permitindo autenticação segura.

9. Estrutura do Projeto
  • main.py — Arquivo principal
  • templates/ — Páginas HTML
  • static/ — CSS e imagens
  • arquivos_xml/ — Pasta para os XML importados
  • bancoDeDadosOG.py — Lógica de banco de dados

10. Licença
  Projeto licenciado pela FATEC Tatuí, sob orientação do professor Bruno Miranda.

11. Agradecimentos
  Agradecemos a Deus por ter nos dado forças até aqui, à FATEC de Tatuí pela oportunidade
  desse projeto e ao professor Bruno Miranda, orientador do curso.
