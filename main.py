from flask import Flask, render_template, request, redirect, url_for, session, flash
from myproject.banco import criar_tabela_usuarios, adicionar_usuario, conectar_db, criar_tabela_acessos, middleware_registrar_acesso, registrar_acesso
import os
import re
from datetime import datetime
app = Flask(__name__)
app.secret_key = '123'

LOG_PATTERN = re.compile(
    r'(?P<data>\d{4}-\d{2}-\d{2}) '
    r'(?P<hora>\d{2}:\d{2}:\d{2}\.\d+) - '
    r'User (?P<usuario>\w+):'
)


criar_tabela_usuarios()
criar_tabela_acessos()

@app.route('/')
def index():
    return redirect(url_for('login'))

#pegando as informações de login from main.py
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['password']
        if senha == '123':
            session['usuario_logado'] = username
            flash('Bem-vindo!', 'success')
            return redirect(url_for('cadastro'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/usuarios')  # ← path da rota
def listar_usuarios():
    print("rota de usuários acessada com sucesso!")
    usuario = session.get('usuario_logado')
    if usuario is None:
        flash("Você precisa estar logado!", "warning")
        return redirect(url_for('login'))
    
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if 'usuario_logado' not in session:
        flash('Faça login primeiro para acessar o cadastro.', 'warning')
        return redirect(url_for('login'))
    
    usuario_salvo = None
   
    if request.method == 'POST':
        nome = request.form['nome']
        username = request.form['username']
        matricula = request.form['matricula']
        cpf = request.form['cpf']
        telefone = request.form['telefone']
        setor = request.form['setor']

        try:
            adicionar_usuario(nome, username, matricula, cpf, telefone, setor)
            flash('Usuário cadastrado com sucesso!', 'success')
    
        except ValueError as e:
            flash(str(e), 'erro')
            return render_template('cadastro.html', form_data=request.form)
        except Exception as e:
            flash('Erro', 'erro')
            #adicionar
            
    return render_template('cadastro.html', usuario_salvo=usuario_salvo)

@app.before_request
def before_request():
    usuario = session.get('usuario_logado')
    if usuario and request.endpoint != 'static':
        registrar_acesso(usuario)

#tentando salvar os dados de usuário logado p/ depois retornar os dados da tela usuario
@app.route('/consultas', methods = ['GET'])
@middleware_registrar_acesso
def consultas():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT usuario, data_hora FROM acessos ORDER BY data_hora DESC")
    acessos = cursor.fetchall()
    conn.close()
    return render_template('consultas.html', acessos=acessos) 


#Acessando o arquivo TXT
#formatando data, hora e user

@app.route('/exibir_arquivo')
def exibir_arquivo():
    try:
        caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'access_log.txt')
        
        # Filtros da URL
        filtro_data = request.args.get('data')
        filtro_usuario = request.args.get('usuario')
        
        linhas_filtradas = []
        todas_datas = set()
        todos_usuarios = set()
        ultima_data=None
        
        with open(caminho, "r", encoding='latin-1') as arquivo:
            for linha in arquivo:
                # Extrai dados da linha
                match = LOG_PATTERN.search(linha)
                if match:
                    data = match.group('data')
                    usuario = match.group('usuario')
                    
                    # Armazena para os dropdowns
                    todas_datas.add(data)
                    todos_usuarios.add(usuario)
                    
                    # Aplica filtros
                    if filtro_data and filtro_data != data:
                        continue
                    if filtro_usuario and filtro_usuario != usuario:
                        continue
                    #inserindo quebra de linh para formatar a visualização!
                    if ultima_data is not None and data != ultima_data:
                        linhas_filtradas.append("")

                    linhas_filtradas.append(linha.strip())
                    ultima_data = data
        conteudo_formatado = "<br>".join(linhas_filtradas)
                      
        return render_template("exibir_arquivo.html", 
                            conteudo=conteudo_formatado,
                            erro=None,
                            datas=sorted(todas_datas, reverse=True),
                            usuarios=sorted(todos_usuarios),
                            filtros={
                                'data': filtro_data,
                                'usuario': filtro_usuario
                            })
    
    except Exception as e:
        return render_template("exibir_arquivo.html",
                            conteudo=None,
                            erro=str(e),
                            datas=[],
                            usuarios=[]), 500
 

#arquivo TXT fim

@app.route('/consultas', methods=['GET'])
def consultas():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM acessos")
    consultas_data = cursor.fetchall()
    conn.close()
    return render_template('consultas.html', consultas=consultas_data)

@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)