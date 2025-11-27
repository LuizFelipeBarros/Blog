from flask import Flask, render_template, request, redirect, flash, session
from db import *
import mysql.connector
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Carregar variáveis do arquivo .env
load_dotenv()

# Acessar as variáveis do .env
SECRET_KEY = os.getenv('SECRET_KEY')
USUARIO_ADMIN = os.getenv('USUARIO_ADMIN')
SENHA_ADMIN = os.getenv('SENHA_ADMIN')

# Inicializar Flask
app = Flask(__name__)
app.secret_key = SECRET_KEY

#Configurar pasta de upload
app.config['UPLOAD_FOLDER'] = "static/uploads/"


# -------------------- ROTAS --------------------

# Página inicial
@app.route('/')
def index():
    postagens = listar_post()
    return render_template('index.html', postagens=postagens)


# Criar novo post
@app.route('/novopost', methods=['GET', 'POST'])
def novopost():
    if request.method == 'GET':
        return redirect('/')
    else:
        titulo = request.form.get('titulo').strip()
        conteudo = request.form.get('conteudo').strip()
        idUsuario = session['idUsuario']  # por enquanto fixo

        if not titulo or not conteudo:
            flash("Preencha todos os campos!")
            return redirect('/')

        post = adicionar_post(titulo, conteudo, idUsuario)
        if post:
            flash("Post realizado com sucesso!")
        else:
            flash("ERRO! Falha ao postar!")
        return redirect('/')


# Editar post
@app.route('/editarpost/<int:idPost>', methods=['GET', 'POST'])
def editarpost(idPost):
    if 'usuario' not in session and 'admin' not in session:
        return redirect('/')
    
    with conectar() as conexao:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(f"SELECT idUsuario FROM post WHERE idPost = {idPost}")
        autor = cursor.fetchone()
        if not autor or autor['idUsuario'] != session['idUsuario']:
            print("Tentativa de edição inválida!")
            return redirect('/')

    if request.method == 'GET':
        try:
            with conectar() as conexao:
                cursor = conexao.cursor(dictionary=True)
                cursor.execute("SELECT * FROM post WHERE idPost = %s", (idPost,))
                post = cursor.fetchone()
                postagens = listar_post()
                return render_template('index.html', postagens=postagens, post=post)
        except mysql.connector.Error as erro:
            print(f"Erro de BD: {erro}")
            flash("Erro ao carregar post!")
            return redirect('/')

    elif request.method == 'POST':
        titulo = request.form.get('titulo').strip()
        conteudo = request.form.get('conteudo').strip()

        if not titulo or not conteudo:
            flash("Preencha todos os campos!")
            return redirect(f'/editarpost/{idPost}')

        sucesso = atualizar_post(titulo, conteudo, idPost)

        if sucesso:
            flash("Post alterado com sucesso!")
        else:
            flash("Falha ao alterar post! Tente mais tarde.")
        return redirect('/')        

# Excluir post
@app.route('/excluirpost/<int:idPost>')
def deletepost(idPost):
    if not session:
        print("Usuário não autorizado acessando rota excluir.")
        return redirect('/')

    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            if "admin" not in session:
                cursor.execute(f"SELECT idUsuario FROM post WHERE idPost = {idPost}")
                autor_post = cursor.fetchone()

                if not autor_post or autor_post['idUsuario'] != session.get('idUsuario'):
                    print("Tentativa de exclusão inválida!")
                    return redirect('/')

            cursor.execute(f"DELETE FROM post WHERE idPost = {idPost}")
            conexao.commit()
            flash("Post excluído com sucesso!")

            if 'admin' in session:
                return redirect('/dashboard')
            else:
                return redirect('/')

    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BD! Erro: {erro}")
        flash("Ops! Tente mais tarde!")
        return redirect('/')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        usuario = request.form['usuario'].lower().strip()
        senha = request.form['senha'].strip()

        if not usuario or not senha:
            flash("Preencha todos os campos!")
            return redirect('/login')


       # 1° Primeiro verificamos se o usuário é o ADMIN
        if usuario == USUARIO_ADMIN and senha == SENHA_ADMIN:
            session['admin'] = True
            print("Session admin set to True.")
            flash("Login bem-sucedido!")
            return redirect('/dashboard')
        
        # 2° Verificar se é um usuário cadastrado
        resultado, usuario_encontrado = verificar_usuario(usuario, senha)
        if resultado:
            session['idUsuario'] = usuario_encontrado['idUsuario']
            session['usuario'] = usuario_encontrado['user']
            flash("Login bem-sucedido!")
            
            # Se o usuário precisa trocar senha, redireciona para página de mudança
            if usuario_encontrado['precisa_trocar_senha'] == 1:
                return redirect('/mudarsenha')
            
            return redirect('/')
        # 3° Nenhum usuário ou ADMIN foram encontrados
        else:
            # A função verificar_usuario pode retornar uma mensagem (ex: "Conta suspensa")
            if isinstance(usuario_encontrado, str) and usuario_encontrado:
                flash(usuario_encontrado)
            else:
                flash("Usuário ou senha incorretos!")
            return redirect('/login')



def totais():
    """Retorna tupla (total_posts, total_usuarios) usando as views do banco.

    As views esperadas no banco são `vw_total_posts` e `vw_usuarios`.
    Retorna duas tuplas (cada uma é o resultado de fetchone) ou (None, None) em erro.
    """
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            # view criada no scriptBD.sql: vw_total_posts e vw_usuarios
            try:
                cursor.execute("SELECT total_posts FROM vw_total_posts")
                total_posts = cursor.fetchone()
            except mysql.connector.Error:
                # fallback para nome alternativo
                cursor.execute("SELECT * FROM vw_total_posts")
                total_posts = cursor.fetchone()

            try:
                cursor.execute("SELECT total_usuarios FROM vw_usuarios")
                total_usuarios = cursor.fetchone()
            except mysql.connector.Error:
                cursor.execute("SELECT * FROM vw_usuarios")
                total_usuarios = cursor.fetchone()

            return total_posts, total_usuarios
    except mysql.connector.Error as erro:
        print(f"ERRO DE BD! Erro: {erro}")
        return None, None


# Dashboard do admin
@app.route('/dashboard')
def dashboard():
    if not session or 'admin' not in session:
        flash("Acesso negado! Faça login.")
        return redirect('/login')
    
    usuarios = listar_usuarios()
    postagens = listar_post()
    totais_posts, total_usuarios = totais()
    return render_template('dashboard.html', usuarios=usuarios, postagens=postagens, totais_posts=totais_posts, total_usuarios=total_usuarios)


# Logout
@app.route('/logout')
def logout():
    # Armazenar a mensagem antes de limpar a sessão (flash usa session)
    flash("Logout realizado com sucesso!", 'short')
    session.clear()
    return redirect('/')


# Rota para cadastro de usuários
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'GET':
        return render_template('cadastro.html')
    elif request.method == 'POST':
        nome = request.form.get('nome').strip()
        usuario = request.form.get('user').lower().strip()
        senha = request.form.get('senha').strip()

        if not nome or not usuario or not senha:
            flash("Preencha todos os campos!")
            return redirect('/cadastro')

        senha_hash = generate_password_hash(senha)

        # ⚠️ CORREÇÃO: Remove o unpacking (resultado, erro)
        resultado = adicionar_usuario(nome, usuario, senha_hash)
        
        if resultado:
            flash("Usuário cadastrado com sucesso!")
            return redirect('/login')
        else:
            flash("Erro ao cadastrar usuário!")
            return redirect('/cadastro')


# Rota para excluir usuário (somente admin)
@app.route('/excluirusuario/<int:idUsuario>')
def excluirusuario(idUsuario):
    # 1. VERIFICAÇÃO DE AUTORIZAÇÃO (SOMENTE ADMIN)
    if 'admin' not in session:
        flash("Acesso negado. Apenas administradores podem excluir usuários.")
        return redirect('/')

    # 2. IMPEDE ADMIN DE EXCLUIR A SI MESMO (opcional, mas recomendado)
    if idUsuario == session.get('idUsuario'):
        flash("Você não pode excluir sua própria conta de administrador aqui.")
        return redirect('/dashboard')

    # 3. CHAMADA À FUNÇÃO DE EXCLUSÃO
    if excluir_usuario(idUsuario):
        flash(f"Usuário com ID {idUsuario} e todos os seus posts foram excluídos com sucesso.")
    else:
        flash(f"Erro ao excluir o usuário com ID {idUsuario}.")
    
    return redirect('/dashboard')


# Rota para banir/ativar usuário (somente admin)
@app.route('/banirusuario/<int:idUsuario>')
def banirusuario(idUsuario):
    # 1. VERIFICAÇÃO DE AUTORIZAÇÃO (SOMENTE ADMIN)
    if 'admin' not in session:
        flash("Acesso negado. Apenas administradores podem alterar status de usuários.")
        return redirect('/')

    # 2. IMPEDE ADMIN DE BANIR A SI MESMO
    if idUsuario == session.get('idUsuario'):
        flash("Você não pode alterar seu próprio status.")
        return redirect('/dashboard')

    # 3. CHAMADA À FUNÇÃO DE ALTERNÂNCIA DE STATUS
    if alternar_status_usuario(idUsuario):
        flash("Status do usuário alterado com sucesso!")
    else:
        flash("Erro ao alterar status do usuário.")
    
    return redirect('/dashboard')

@app.route('/resetarsenha/<int:idUsuario>')
def resetarsenha(idUsuario):
    # 1. VERIFICAÇÃO DE AUTORIZAÇÃO (SOMENTE ADMIN)
    if 'admin' not in session:
        flash("Acesso negado. Apenas administradores podem resetar senhas.")
        return redirect('/')

    # 2. IMPEDE ADMIN DE ALTERAR A PRÓPRIA SENHA POR ESTA ROTA
    if idUsuario == session.get('idUsuario'):
        flash("Você não pode resetar sua própria senha por aqui.")
        return redirect('/dashboard')
        
    # 3. GERA HASH DA NOVA SENHA
    nova_senha_texto = "nulo1234"  # <--- NOVA SENHA TEMPORÁRIA
    nova_senha_hash = generate_password_hash(nova_senha_texto)

    # 4. CHAMADA À FUNÇÃO DE RESETAR SENHA (marca precisa_trocar_senha = 1)
    if resetar_senha(idUsuario, nova_senha_hash):
        flash(f"Senha do usuário ID {idUsuario} resetada. Usuário deverá trocar ao próximo login.", "success")
    else:
        flash("Erro ao resetar senha do usuário.", "error")
    
    return redirect('/dashboard')


@app.route('/mudarsenha', methods=['GET', 'POST'])
def mudarsenha():
    # Verificação: Usuário precisa estar logado
    if 'usuario' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect('/login')
    
    if request.method == 'GET':
        return render_template('nova_senha.html')
    
    elif request.method == 'POST':
        nova_senha = request.form.get('senha', '').strip()
        confirmacao = request.form.get('confirmacao', '').strip()
        
        # Validações
        if not nova_senha or not confirmacao:
            flash("Preencha todos os campos!")
            return redirect('/mudarsenha')
        
        if nova_senha != confirmacao:
            flash("As senhas não correspondem!")
            return redirect('/mudarsenha')
        
        if len(nova_senha) < 4:
            flash("A senha deve ter pelo menos 4 caracteres!")
            return redirect('/mudarsenha')
        
        # Atualizar senha no banco
        nova_senha_hash = generate_password_hash(nova_senha)
        idUsuario = session.get('idUsuario')
        
        if atualizar_senha_usuario(idUsuario, nova_senha_hash):
            flash("Senha atualizada com sucesso! Bem-vindo ao Blog!", "success")
            return redirect('/')
        else:
            flash("Erro ao atualizar senha. Tente novamente.", "error")
            return redirect('/mudarsenha')

# Rota do perfil
@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if 'usuario' not in session:
        flash("Você precisa estar logado para acessar esta página.")
        return redirect('/login')
    
    if request.method == 'GET':
        listas_usuarios = listar_usuarios()
        usuario = None
        for u in listas_usuarios:
            if u['idUsuario'] == session['idUsuario']:
                usuario = u 
                break

        return render_template('perfil.html', nome=usuario['nome'], usuario=usuario['user'], foto=usuario['foto'])
    
    if request.method == 'POST':
        nome = request.form.get('nome').strip()
        user = request.form.get('user').strip()
        foto = request.files.get('foto')
        idUsuario = session['idUsuario']
        nome_foto = None
        
        if not nome or not user:
            flash("Preencha todos os campos !!!")
            return redirect('/perfil')
        if foto:
            if foto.filename == '':
                flash("Arquivo inválido ou não selecionado!!!")
                return redirect('/perfil')
            extensao = foto.filename.rsplit('.', 1)[-1].lower()
            if extensao not in ['png', 'jpg', 'webp', 'jfif']:
                flash("Extensão de arquivo não permitida!!!")
                return redirect('/perfil')
            if len(foto.read()) > 2  * 1024  * 1024: # o primeiro número ai é o tamanho da img em mega
                flash("Arquivo acima do tamanho permitido!!!")
                return redirect('/perfil')
            
            foto.seek(0)
            nome_foto = f"{idUsuario}.{extensao}"
        
        # Se não houver foto, coloca essa padrão ai
        if not nome_foto:
            nome_foto = "imgnull.png"

        sucesso = editar_perfil(nome, user, nome_foto, idUsuario)
        if sucesso:
            if foto:
                foto.save(f"static/uploads/{nome_foto}")
            flash("Dados alterados com sucesso!!!")
        else:
            flash("Error ao alterar os dados!!!")

        return redirect('/perfil')

    
    
# ERRO 404 - Pagina não encontrada
@app.errorhandler(404)
def page_not_found(error):
    return render_template ('erro404.html'), 404

# ERRO 500 - Erro interno do servidor
@app.errorhandler(500)
def internal_error(error):
    return render_template ('erro500.html'), 500

# Iniciar servidor
if __name__ == '__main__':
    app.run(debug=True)
