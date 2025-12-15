SECRET_KEY = "Bl0gJ0!@o"     # senha secreta para sessão e outras coisas
USUARIO_ADMIN = "adm"        # senha do adm (alterar para uma mais segura
SENHA_ADMIN = "adm"          # senha do adm (alterar para uma mais segura

# Variável de controle de ambiente, poderá ser "local" ou "produção"
ambiente = "local"

if ambiente == "local":
	# ------ INFORMAÇÕES DO SEU BLOG LOCAL, DEIXE COMO ESTÁ
	HOST = "localhost"
	USER = "root"
	PASSWORD = "senai"
	DATABASE = "blog_joao"
elif ambiente == "produção":
	# ------ INFORMAÇÕES VINDAS DO DATABASE DO PYTHON ANYWHERE
	HOST =  "link python anywhere"
	USER = "user python anywhere"
	PASSWORD = "senha database python anywhere"
	DATABASE = "nome do database python anywhere"