import mysql.connector
from werkzeug.security import check_password_hash
from config import * # importando as variáveis do config.py


# Função para se conectar ao Banco de Dados SQL
def conectar():
    conexao = mysql.connector.connect(
        host=HOST,   # variável do config.py
        user=USER,   # variável do config.py
        password=PASSWORD,   # variável do config.py
        database=DATABASE   # variável do config.py
    )
    if conexao.is_connected():
        print("Conexão com BD OK!")
    
    return conexao

# Função para listar todas as postagens
def listar_post():
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True) # Função que vai executar oq for preciso no Banco de Dados. Ex: "Copilot"
            # Corrigido: p.* sem espaço e nome da tabela de usuários conforme script (usuarios)
            cursor.execute("SELECT p.*, u.user, u.foto FROM post p INNER JOIN usuarios u ON u.idUsuario = p.idUsuario ORDER BY p.idPost DESC")
            return cursor.fetchall()
    except mysql.connector.Error as erro:
        print(f"ERRO DE BD! Erro: {erro}")
        return [] # Lista Vazia
   
# Função para listar todos os usuários
def listar_usuarios():
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True) # Função que vai executar oq for preciso no Banco de Dados. Ex: "Copilot"
            # Usar o nome correto da tabela conforme scriptBD.sql
            cursor.execute("SELECT * FROM usuarios")
            return cursor.fetchall()
    except mysql.connector.Error as erro:
        print(f"ERRO DE BD! Erro: {erro}")
        return [] # Lista Vazia


def adicionar_post(titulo, conteudo, idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "INSERT INTO post (titulo, conteudo, idUsuario) VALUES (%s, %s, %s)"
            cursor.execute(sql, (titulo, conteudo, idUsuario))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BD! Erro: {erro}")
        return False

def adicionar_usuario(nome, user, senha_hash):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "INSERT INTO usuarios (nome, user, senha) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nome, user, senha_hash))
            conexao.commit()
            return True  # ⚠️ Retorna apenas True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BD! Erro: {erro}")
        return False  # ⚠️ Retorna apenas False
    
def verificar_usuario(user, senha):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "SELECT * FROM usuarios WHERE user= %s"
            cursor.execute(sql, (user,))
            usuario_encontrado = cursor.fetchone()
            if usuario_encontrado:
                if usuario_encontrado['senha'] == 'nulo1234':
                    return True, usuario_encontrado
                
                # ⚠️ NOVO: Checa se o usuário está ativo
                if usuario_encontrado['ativo'] == 0:
                    return False, "Conta suspensa" # Retorna sinal de erro
                    
                if check_password_hash(usuario_encontrado['senha'], senha):
                    return True, usuario_encontrado
            return False, None
    except mysql.connector.Error as erro:
        print(f"ERRO DE BD! Erro: {erro}")
        return False, None
    
def excluir_usuario(idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            # ⚠️ Importante: Lembre-se de deletar os posts do usuário primeiro
            # ou configurar o ON DELETE CASCADE na sua tabela 'post'.
            # Se não fizer isso, o MySQL pode impedir a exclusão por chave estrangeira.
            
            # 1. Exclui posts do usuário (para evitar erro de chave estrangeira)
            sql_delete_posts = "DELETE FROM post WHERE idUsuario = %s"
            cursor.execute(sql_delete_posts, (idUsuario,))
            
            # 2. Exclui o usuário
            sql_delete_user = "DELETE FROM usuarios WHERE idUsuario = %s"
            cursor.execute(sql_delete_user, (idUsuario,))
            
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BD ao excluir usuário! Erro: {erro}")
        return False
    
def alternar_status_usuario(idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            # Alterna o valor de 'ativo' (1 para 0, 0 para 1)
            sql = "UPDATE usuarios SET ativo = NOT ativo WHERE idUsuario = %s"
            cursor.execute(sql, (idUsuario,))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BD! Erro ao alternar status: {erro}")
        return False
    
def atualizar_post(titulo, conteudo, idPost):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "UPDATE post SET titulo=%s, conteudo=%s WHERE idPost = %s"
            cursor.execute(sql, (titulo, conteudo, idPost))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"Erro de BD: {erro}")
        print("Erro ao atualizar post!")
        return False
    
def resetar_senha(idUsuario, nova_senha_hash):
    """Reseta a senha do usuário e marca que precisa trocar senha."""
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            # SQL para atualizar senha e marcar que precisa trocar
            sql = "UPDATE usuarios SET senha = %s, precisa_trocar_senha = 1 WHERE idUsuario = %s"
            cursor.execute(sql, (nova_senha_hash, idUsuario))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BD! Erro ao resetar senha: {erro}")
        return False

def atualizar_senha_usuario(idUsuario, nova_senha_hash):
    """Atualiza a senha do usuário e libera o acesso (remove flag precisa_trocar_senha)."""
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "UPDATE usuarios SET senha = %s, precisa_trocar_senha = 0 WHERE idUsuario = %s"
            cursor.execute(sql, (nova_senha_hash, idUsuario))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BD! Erro ao atualizar senha: {erro}")
        return False

def editar_perfil(nome, user, nome_foto, idUsuario):
    """Atualiza os dados do perfil do usuário."""
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "UPDATE usuarios SET nome = %s, user = %s, foto = %s WHERE idUsuario = %s"
            cursor.execute(sql, (nome, user, nome_foto, idUsuario))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BD! Erro ao atualizar perfil: {erro}")
        return False