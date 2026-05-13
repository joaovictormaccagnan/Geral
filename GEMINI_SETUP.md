# 🚀 Configurar Google Gemini API - Guia Rápido

## ✅ Passo 1: Obter Chave API Grátis

1. Acesse: **https://ai.google.dev/**
2. Clique em **"Get API Key"** (parte superior direita)
3. Selecione **"Create API key in new project"**
4. Copie sua chave (formato: `AIza...`)

## ✅ Passo 2: Configurar no Arquivo `.env`

Abra o arquivo `.env` na pasta principal:

```
# 🔑 Google Gemini API Key
GEMINI_API_KEY=AIza_sua_chave_aqui
```

**Cole sua chave** onde está `AIza_sua_chave_aqui`

## ✅ Passo 3: Salvar e Reiniciar

1. Salve o arquivo `.env`
2. Reinicie o servidor FastAPI:
   ```bash
   uvicorn api_maison:app --reload
   ```

## 🎯 Pronto!

O chatbot vai:
1. ✅ Tentar usar **Google Gemini IA** automaticamente
2. ✅ Se o limite grátis acabar, **volta para IA local** automaticamente
3. ✅ Sem erro, sem queda de serviço!

---

## 📊 Limite Grátis do Gemini

- **15 requisições por minuto** - Grátis
- **1 milhão de tokens por dia** - Grátis
- Depois disso, volta para IA local automaticamente

---

## 🔍 Verificar Status

Para ver qual IA está sendo usada, no console aparecerá:
- ✅ `✅ Google Gemini IA configurado com sucesso!` - Gemini ativo
- ⚠️ `⚠️ GEMINI_API_KEY não configurada. Usando IA local.` - Gemini inativo

---

## 🆘 Solucionar Problemas

### "GEMINI_API_KEY não configurada"
- Verifique se o arquivo `.env` existe na raiz do projeto
- Verifique se a chave foi colada corretamente
- Não use aspas: `AIza_chave` (não `"AIza_chave"`)

### "Invalid API key"
- Copie a chave novamente de https://ai.google.dev/
- Certifique-se de que não há espaços extras

### "Quota exceeded"
- Limite grátis atingido
- Não se preocupe! O chatbot **volta para IA local automaticamente**
- Pode fazer upgrade na Google Cloud Console se quiser

---

**Desenvolvido com ❤️ para Maison Café**
