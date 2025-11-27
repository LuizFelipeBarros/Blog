CREATE DATABASE blog_luiz;

    USE blog_luiz;

    CREATE TABLE usuarios ( 
        idUsuario INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
        nome VARCHAR(50) NOT NULL,
        user VARCHAR(15) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE,
        senha VARCHAR(255) NOT NULL,
        foto VARCHAR(300),
        dataCadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ativo BOOLEAN NOT NULL DEFAULT 1
    );
    CREATE TABLE post(
        idPost INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
        titulo VARCHAR(50) NOT NULL,
        conteudo TEXT NOT NULL,
        dataPost TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        idUsuario INT,
        FOREIGN KEY (idUsuario) REFERENCES usuarios(idUsuario)
        ON DELETE CASCADE
        
    );
    -- Cadastrar um usuário de teste:
    INSERT INTO usuarios (nome, user, senha) VALUES ("Teste","Teste","Teste");

    --Para zerar a tabela POST:
    TRUNCATE post;


    ALTER TABLE usuarios ADD ativo BOOLEAN NOT NULL DEFAULT 1;
    ALTER TABLE usuarios ADD precisa_trocar_senha BOOLEAN NOT NULL DEFAULT 0;

    UPDATE usuarios SET foto = 'jp_user.jfif' WHERE user = 'jp';
    UPDATE usuarios SET foto = 'user_vini.png' WHERE user = 'vini';
    UPDATE usuarios SET foto = 'em_mannoel_userv2.png' WHERE user = 'em_mannoel';
    UPDATE usuarios SET foto = 'John_user.jfif' WHERE user = 'john_67_monster';

    CREATE VIEW vw_total_posts AS SELECT
    COUNT(*) AS total_posts
    FROM post p JOIN usuarios u ON p.idUsuario = u.idUsuario
    WHERE u.ativo = 1;

    CREATE VIEW vw_usuarios AS SELECT
    COUNT(*) AS total_usuarios
    FROM usuarios
    WHERE ativo = 1;