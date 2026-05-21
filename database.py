"""
🗄️ DATABASE - Maison Café Chatbot
Gerencia conexão MySQL e operações de histórico de conversas
"""

import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional

try:
    import mysql.connector
    from mysql.connector import Error
    MYSQL_DISPONIVEL = True
except ImportError:
    MYSQL_DISPONIVEL = False
    print("⚠️  mysql-connector-python não instalado.")
    print("   Execute: pip install mysql-connector-python")


# ============================================================
# CONFIGURAÇÃO — altere conforme seu ambiente
# ============================================================
DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "database": os.getenv("DB_NAME",     "maison_cafe"),
    "user":     os.getenv("DB_USER",     "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "charset":  "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
}

# SQL para criar as tabelas (executado automaticamente na 1ª vez)
SQL_CRIAR_TABELAS = """
CREATE TABLE IF NOT EXISTS sessions (
    id          VARCHAR(36)  PRIMARY KEY,
    usuario_id  VARCHAR(255) NOT NULL DEFAULT 'guest',
    criado_em   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP  DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_usuario (usuario_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS messages (
    id          INT          AUTO_INCREMENT PRIMARY KEY,
    session_id  VARCHAR(36)  NOT NULL,
    role        ENUM('user','assistant') NOT NULL,
    content     TEXT         NOT NULL,
    modo_ia     VARCHAR(100) DEFAULT NULL,
    criado_em   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE,
    FULLTEXT KEY ft_content (content),
    INDEX idx_session (session_id),
    INDEX idx_criado (criado_em)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""


class Database:
    """Gerenciador do banco de dados MySQL para o chatbot"""

    def __init__(self):
        self.conn = None
        self.disponivel = False

        if not MYSQL_DISPONIVEL:
            return

        self._conectar()

    # ----------------------------------------------------------
    # Conexão
    # ----------------------------------------------------------

    def _conectar(self):
        """Estabelece conexão com o MySQL"""
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            if self.conn.is_connected():
                self.disponivel = True
                print(f"✅ MySQL conectado! Banco: {DB_CONFIG['database']}")
                self._criar_tabelas()
        except Error as e:
            print(f"⚠️  Não foi possível conectar ao MySQL: {e}")
            print("   O chatbot funcionará normalmente sem salvar histórico.")
            self.disponivel = False

    def _garantir_conexao(self):
        """Reconecta se a conexão cair"""
        if not self.disponivel:
            return False
        try:
            if not self.conn.is_connected():
                self.conn.reconnect(attempts=3, delay=1)
            return True
        except Error:
            self.disponivel = False
            return False

    def _criar_tabelas(self):
        """Cria as tabelas caso ainda não existam"""
        try:
            cursor = self.conn.cursor()
            for sql in SQL_CRIAR_TABELAS.strip().split(";"):
                sql = sql.strip()
                if sql:
                    cursor.execute(sql)
            self.conn.commit()
            cursor.close()
        except Error as e:
            print(f"⚠️  Erro ao criar tabelas: {e}")

    # ----------------------------------------------------------
    # Sessions
    # ----------------------------------------------------------

    def criar_session(self, usuario_id: str = "guest") -> str:
        """Cria uma nova sessão e retorna o session_id"""
        session_id = str(uuid.uuid4())

        if not self._garantir_conexao():
            return session_id  # retorna ID mesmo sem salvar

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO sessions (id, usuario_id) VALUES (%s, %s)",
                (session_id, usuario_id)
            )
            self.conn.commit()
            cursor.close()
        except Error as e:
            print(f"⚠️  Erro ao criar sessão: {e}")

        return session_id

    # ----------------------------------------------------------
    # Mensagens
    # ----------------------------------------------------------

    def salvar_mensagem(
        self,
        session_id: str,
        role: str,
        content: str,
        modo_ia: str = None
    ) -> bool:
        """Salva uma mensagem no banco. Retorna True se salvou com sucesso."""
        if not self._garantir_conexao():
            return False

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT INTO messages (session_id, role, content, modo_ia)
                   VALUES (%s, %s, %s, %s)""",
                (session_id, role, content, modo_ia)
            )
            self.conn.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"⚠️  Erro ao salvar mensagem: {e}")
            return False

    def buscar_contexto_relevante(
        self,
        mensagem: str,
        limite: int = 5
    ) -> List[Dict]:
        """
        Busca mensagens anteriores relevantes usando FULLTEXT search.
        Retorna lista de dicts com 'role' e 'content'.
        """
        if not self._garantir_conexao():
            return []

        try:
            cursor = self.conn.cursor(dictionary=True)

            # Busca fulltext nas mensagens mais relevantes
            cursor.execute(
                """
                SELECT role, content,
                       MATCH(content) AGAINST (%s IN NATURAL LANGUAGE MODE) AS relevancia
                FROM messages
                WHERE MATCH(content) AGAINST (%s IN NATURAL LANGUAGE MODE)
                  AND role IN ('user', 'assistant')
                ORDER BY relevancia DESC
                LIMIT %s
                """,
                (mensagem, mensagem, limite)
            )
            rows = cursor.fetchall()
            cursor.close()

            return [{"role": r["role"], "content": r["content"]} for r in rows]

        except Error as e:
            print(f"⚠️  Erro na busca de contexto: {e}")
            return []

    def buscar_historico_sessao(
        self,
        session_id: str,
        limite: int = 20
    ) -> List[Dict]:
        """Retorna as últimas N mensagens de uma sessão específica."""
        if not self._garantir_conexao():
            return []

        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(
                """SELECT role, content, criado_em
                   FROM messages
                   WHERE session_id = %s
                   ORDER BY criado_em DESC
                   LIMIT %s""",
                (session_id, limite)
            )
            rows = cursor.fetchall()
            cursor.close()
            # Retorna em ordem cronológica
            return list(reversed(rows))
        except Error as e:
            print(f"⚠️  Erro ao buscar histórico: {e}")
            return []

    # ----------------------------------------------------------
    # Estatísticas (bônus)
    # ----------------------------------------------------------

    def estatisticas(self) -> Dict:
        """Retorna estatísticas básicas do banco."""
        if not self._garantir_conexao():
            return {}

        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) AS total FROM sessions")
            total_sessions = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) AS total FROM messages")
            total_msgs = cursor.fetchone()["total"]

            cursor.execute(
                "SELECT COUNT(*) AS total FROM messages WHERE role = 'user'"
            )
            perguntas = cursor.fetchone()["total"]

            cursor.close()
            return {
                "total_sessoes": total_sessions,
                "total_mensagens": total_msgs,
                "total_perguntas": perguntas,
            }
        except Error as e:
            print(f"⚠️  Erro ao buscar estatísticas: {e}")
            return {}

    def fechar(self):
        """Fecha a conexão com o banco."""
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("🔒 Conexão MySQL encerrada.")


# Instância global — importada pelo chatbot_ia.py
db = Database()