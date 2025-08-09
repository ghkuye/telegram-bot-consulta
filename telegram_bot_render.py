#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Telegram para Consulta de Dados de Pessoas - Versão Render
Este bot permite consultar informações de pessoas em um banco de dados SQLite.
Adaptado para funcionar no Render.
"""

import logging
import sqlite3
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token do bot (deve ser definido como variável de ambiente)
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Nome do arquivo do banco de dados
DB_FILE = 'pessoas.db'

class PessoasBot:
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados com dados de exemplo"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Criar tabela se não existir
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pessoas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE NOT NULL,
                email TEXT,
                telefone TEXT,
                endereco TEXT,
                cidade TEXT,
                estado TEXT,
                data_nascimento TEXT,
                profissao TEXT
            )
        ''')
        
        # Inserir dados de exemplo se a tabela estiver vazia
        cursor.execute('SELECT COUNT(*) FROM pessoas')
        if cursor.fetchone()[0] == 0:
            dados_exemplo = [
                ('João Silva', '123.456.789-00', 'joao@email.com', '(11) 99999-1111', 'Rua A, 123', 'São Paulo', 'SP', '1990-01-15', 'Engenheiro'),
                ('Maria Santos', '987.654.321-00', 'maria@email.com', '(11) 88888-2222', 'Rua B, 456', 'Rio de Janeiro', 'RJ', '1985-05-20', 'Médica'),
                ('Pedro Oliveira', '456.789.123-00', 'pedro@email.com', '(11) 77777-3333', 'Rua C, 789', 'Belo Horizonte', 'MG', '1992-12-10', 'Professor'),
                ('Ana Costa', '321.654.987-00', 'ana@email.com', '(11) 66666-4444', 'Rua D, 321', 'Salvador', 'BA', '1988-08-25', 'Advogada'),
                ('Carlos Ferreira', '789.123.456-00', 'carlos@email.com', '(11) 55555-5555', 'Rua E, 654', 'Fortaleza', 'CE', '1995-03-30', 'Programador')
            ]
            
            cursor.executemany('''
                INSERT INTO pessoas (nome, cpf, email, telefone, endereco, cidade, estado, data_nascimento, profissao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', dados_exemplo)
        
        conn.commit()
        conn.close()
        logger.info("Banco de dados inicializado com sucesso")
    
    def buscar_pessoa_por_cpf(self, cpf):
        """Busca uma pessoa pelo CPF"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM pessoas WHERE cpf = ?', (cpf,))
        resultado = cursor.fetchone()
        
        conn.close()
        return resultado
    
    def buscar_pessoa_por_nome(self, nome):
        """Busca pessoas pelo nome (busca parcial)"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM pessoas WHERE nome LIKE ?', (f'%{nome}%',))
        resultados = cursor.fetchall()
        
        conn.close()
        return resultados
    
    def listar_todas_pessoas(self):
        """Lista todas as pessoas do banco de dados"""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM pessoas ORDER BY nome')
        resultados = cursor.fetchall()
        
        conn.close()
        return resultados
    
    def formatar_pessoa(self, pessoa):
        """Formata os dados de uma pessoa para exibição"""
        if not pessoa:
            return "Pessoa não encontrada."
        
        return f"""
👤 **{pessoa[1]}**
📄 CPF: {pessoa[2]}
📧 Email: {pessoa[3]}
📞 Telefone: {pessoa[4]}
🏠 Endereço: {pessoa[5]}
🏙️ Cidade: {pessoa[6]} - {pessoa[7]}
🎂 Data de Nascimento: {pessoa[8]}
💼 Profissão: {pessoa[9]}
        """.strip()

# Instância global do bot
bot_instance = PessoasBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Mensagem de boas-vindas"""
    keyboard = [
        [InlineKeyboardButton("📋 Listar Todas", callback_data='listar_todas')],
        [InlineKeyboardButton("🔍 Buscar por Nome", callback_data='buscar_nome')],
        [InlineKeyboardButton("📄 Buscar por CPF", callback_data='buscar_cpf')],
        [InlineKeyboardButton("ℹ️ Ajuda", callback_data='ajuda')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    mensagem = """
🤖 **Bot de Consulta de Dados de Pessoas**

Olá! Eu sou um bot que pode ajudá-lo a consultar informações de pessoas em nosso banco de dados.

**Comandos disponíveis:**
• /start - Mostra este menu
• /listar - Lista todas as pessoas
• /ajuda - Mostra informações de ajuda

**Como usar:**
• Use os botões abaixo para navegar
• Ou digite diretamente o nome ou CPF da pessoa que deseja buscar

Escolha uma opção:
    """.strip()
    
    await update.message.reply_text(mensagem, reply_markup=reply_markup, parse_mode='Markdown')

async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ajuda - Informações de ajuda"""
    mensagem = """
ℹ️ **Ajuda - Bot de Consulta de Dados**

**Como usar o bot:**

1️⃣ **Buscar por Nome:**
   • Digite o nome da pessoa (busca parcial)
   • Exemplo: "João" ou "Silva"

2️⃣ **Buscar por CPF:**
   • Digite o CPF completo com ou sem formatação
   • Exemplo: "123.456.789-00" ou "12345678900"

3️⃣ **Listar Todas:**
   • Use o comando /listar ou o botão correspondente

**Comandos:**
• /start - Menu principal
• /listar - Lista todas as pessoas
• /ajuda - Esta mensagem de ajuda

**Dicas:**
• A busca por nome não diferencia maiúsculas/minúsculas
• Você pode buscar por parte do nome
• O CPF pode ser digitado com ou sem formatação

🌐 **Bot hospedado no Render**
    """.strip()
    
    await update.message.reply_text(mensagem, parse_mode='Markdown')

async def listar_pessoas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /listar - Lista todas as pessoas"""
    pessoas = bot_instance.listar_todas_pessoas()
    
    if not pessoas:
        await update.message.reply_text("❌ Nenhuma pessoa encontrada no banco de dados.")
        return
    
    mensagem = "📋 **Lista de Todas as Pessoas:**\n\n"
    
    for pessoa in pessoas:
        mensagem += f"👤 {pessoa[1]} - CPF: {pessoa[2]}\n"
    
    mensagem += f"\n📊 Total: {len(pessoas)} pessoa(s) encontrada(s)"
    
    if len(mensagem) > 4096:  # Limite do Telegram
        # Dividir em múltiplas mensagens se necessário
        partes = [mensagem[i:i+4000] for i in range(0, len(mensagem), 4000)]
        for parte in partes:
            await update.message.reply_text(parte, parse_mode='Markdown')
    else:
        await update.message.reply_text(mensagem, parse_mode='Markdown')

async def processar_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa mensagens de texto do usuário"""
    texto = update.message.text.strip()
    
    # Verificar se é um CPF (números com ou sem formatação)
    cpf_limpo = ''.join(filter(str.isdigit, texto))
    
    if len(cpf_limpo) == 11:
        # Buscar por CPF
        pessoa = bot_instance.buscar_pessoa_por_cpf(texto)
        if pessoa:
            mensagem = "🔍 **Resultado da busca por CPF:**\n\n"
            mensagem += bot_instance.formatar_pessoa(pessoa)
        else:
            mensagem = f"❌ Nenhuma pessoa encontrada com o CPF: {texto}"
    else:
        # Buscar por nome
        pessoas = bot_instance.buscar_pessoa_por_nome(texto)
        if pessoas:
            if len(pessoas) == 1:
                mensagem = "🔍 **Resultado da busca por nome:**\n\n"
                mensagem += bot_instance.formatar_pessoa(pessoas[0])
            else:
                mensagem = f"🔍 **{len(pessoas)} pessoa(s) encontrada(s) com o nome '{texto}':**\n\n"
                for pessoa in pessoas:
                    mensagem += f"👤 {pessoa[1]} - CPF: {pessoa[2]}\n"
                mensagem += "\n💡 Digite o CPF para ver detalhes completos."
        else:
            mensagem = f"❌ Nenhuma pessoa encontrada com o nome: {texto}"
    
    await update.message.reply_text(mensagem, parse_mode='Markdown')

async def processar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa callbacks dos botões inline"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'listar_todas':
        pessoas = bot_instance.listar_todas_pessoas()
        
        if not pessoas:
            await query.edit_message_text("❌ Nenhuma pessoa encontrada no banco de dados.")
            return
        
        mensagem = "📋 **Lista de Todas as Pessoas:**\n\n"
        
        for pessoa in pessoas:
            mensagem += f"👤 {pessoa[1]} - CPF: {pessoa[2]}\n"
        
        mensagem += f"\n📊 Total: {len(pessoas)} pessoa(s) encontrada(s)"
        
        await query.edit_message_text(mensagem, parse_mode='Markdown')
    
    elif query.data == 'buscar_nome':
        await query.edit_message_text(
            "🔍 **Buscar por Nome**\n\n"
            "Digite o nome da pessoa que deseja buscar.\n"
            "Você pode digitar o nome completo ou apenas parte dele.\n\n"
            "Exemplo: João, Silva, Maria Santos"
        )
    
    elif query.data == 'buscar_cpf':
        await query.edit_message_text(
            "📄 **Buscar por CPF**\n\n"
            "Digite o CPF da pessoa que deseja buscar.\n"
            "Pode ser com ou sem formatação.\n\n"
            "Exemplos:\n"
            "• 123.456.789-00\n"
            "• 12345678900"
        )
    
    elif query.data == 'ajuda':
        await ajuda(query, context)

def main():
    """Função principal do bot"""
    # Verificar se o token foi configurado
    if not BOT_TOKEN:
        logger.error("Token do bot não configurado! Configure a variável de ambiente TELEGRAM_BOT_TOKEN")
        return
    
    # Criar aplicação
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Adicionar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ajuda", ajuda))
    application.add_handler(CommandHandler("listar", listar_pessoas))
    application.add_handler(CallbackQueryHandler(processar_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, processar_mensagem))
    
    # Iniciar o bot
    logger.info("Bot iniciado com sucesso no Render!")
    
    # Para Render, usar webhook ou polling dependendo da configuração
    port = int(os.environ.get('PORT', 8080))
    
    # Se estiver em produção no Render, usar webhook
    if os.environ.get('RENDER'):
        # Configurar webhook (requer URL do Render)
        webhook_url = os.environ.get('WEBHOOK_URL')
        if webhook_url:
            application.run_webhook(
                listen="0.0.0.0",
                port=port,
                webhook_url=webhook_url
            )
        else:
            logger.warning("WEBHOOK_URL não configurada, usando polling")
            application.run_polling()
    else:
        # Desenvolvimento local
        application.run_polling()

if __name__ == '__main__':
    main()
