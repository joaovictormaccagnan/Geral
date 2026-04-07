
-- Maison Café 

-- Cria o banco de dados e as tabelas necessárias

-- Criar banco de dados se não existir
CREATE DATABASE IF NOT EXISTS maison_cafe;
USE maison_cafe;

-- ============================================
-- Tabela de Usuários
-- ============================================
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Tabela de Pedidos
-- ============================================
CREATE TABLE IF NOT EXISTS pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(100),
    itens JSON NOT NULL,
    pagamento VARCHAR(20) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario) REFERENCES usuarios(usuario) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- Inserir usuário de teste (OPCIONAL)
-- ============================================
-- Senha: senha123 (criptografada com bcrypt)
INSERT INTO usuarios (usuario, senha, email) VALUES 
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmGEJiq', 'admin@maison.com')
ON DUPLICATE KEY UPDATE usuario=usuario;

-- ============================================
-- Criar índices para performance
-- ============================================
CREATE INDEX idx_usuario ON usuarios(usuario);
CREATE INDEX idx_pedidos_usuario ON pedidos(usuario);
CREATE INDEX idx_pedidos_data ON pedidos(criado_em);

-- Script finalizado!

