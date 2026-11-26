# Guia: perfil do GitHub estilo "terminal pro"

## Estrutura do projeto

```
fevillalon/                  <- repositório com o MESMO nome do seu usuário
├── README.md                <- o que aparece no seu perfil
├── assets/
│   └── avatar.png           <- sua foto (vira o avatar e o retrato ASCII)
├── scripts/
│   └── generate.py          <- gera os 5 cards SVG com seus dados reais
├── generated/               <- criada automaticamente pelo workflow
└── .github/workflows/
    └── update-profile.yml   <- atualiza os cards a cada 6 horas
```

## Passo a passo

### 1. Criar o repositório especial
1. Acesse https://github.com/new
2. **Repository name:** `fevillalon` (igual ao seu usuário, senão não funciona)
3. Marque **Public** e **Add a README file** → **Create repository**
4. Você verá a mensagem "You found a secret repository" — está certo.

### 2. Subir os arquivos
Pelo navegador (mais simples): em **Add file → Upload files**, arraste a pasta com
`README.md`, `scripts/` e `.github/` (a pasta `.github` pode ficar oculta no seu
explorador; ative "mostrar arquivos ocultos"). Faça o commit na branch `main`.

Ou pelo terminal:
```bash
git clone https://github.com/fevillalon/fevillalon.git
cd fevillalon
# copie os arquivos do kit para cá
git add .
git commit -m "feat: novo perfil"
git push
```

### 3. Adicionar sua foto
Coloque uma foto **quadrada, de rosto, com bom contraste** em `assets/avatar.png`
(ou `.jpg`). Ela é usada no círculo do topo e convertida em arte ASCII no terminal.
Se o retrato ASCII ficar "negativo", mude `INVERT_ASCII = True` em `scripts/generate.py`.

### 4. Permitir o workflow commitar
Repositório → **Settings → Actions → General → Workflow permissions** →
**Read and write permissions** → Save.

### 5. Rodar a primeira vez
Aba **Actions → Update profile cards → Run workflow**. Em ~1 minuto a pasta
`generated/` aparece com os 5 SVGs e o perfil já fica pronto.

### 6. (Opcional) Contribuições com mais precisão
O token padrão já mostra contribuições públicas. Para contar também as privadas:
1. Settings (da sua conta) → Developer settings → Personal access tokens →
   **Fine-grained** → gere um com leitura de metadados
2. No repositório: Settings → Secrets and variables → Actions → **New repository secret**
   com o nome `PROFILE_TOKEN`
3. Ative em Perfil → Settings → "Include private contributions on my profile".

### 7. Fixar projetos (pin)
No seu perfil → **Customize your pins** → escolha os 3–6 melhores repositórios.

## Personalização
Tudo fica no bloco `CONFIG` no topo de `scripts/generate.py`: nome, cargo, status,
botões do topo, tamanho do ASCII, número de projetos e linguagens.
Para testar localmente sem internet: `pip install pillow` e `python scripts/generate.py --demo`.

## Como deixar o perfil realmente profissional

**O visual chama atenção; o conteúdo convence.** Alguns pontos para você:

- **Os números são reais, então faça-os crescer.** Os cards puxam dados da API do
  GitHub: nada é falso. Commits frequentes e repositórios bem feitos enchem os cards
  naturalmente. (Na imagem de referência, 1 repo e 6 contribuições também aparecem
  como estão. Isso é bom: honesto.)
- **Linguagens condizentes com você.** O card "Language Stack" é calculado dos seus
  repositórios. Com seus projetos em Python e C, ele vai mostrar Python e C. Não
  copie "TypeScript/React/Next.js" só pela estética.
- **Suba 3 projetos bem acabados** (mais vale 3 bons do que 20 soltos). Sugestões
  para o seu nível:
  1. Sistema CRUD em Python (SQLite ou arquivos) com README e prints
  2. Estruturas de dados em C (lista encadeada, pilha, fila) com Makefile e testes
  3. Automação/script útil do seu dia a dia (organizador de arquivos, bot, scraper)
- **README de cada projeto:** descrição, como instalar/rodar, tecnologias, prints,
  próximos passos. Use `.gitignore`, licença (MIT) e commits claros
  (`feat:`, `fix:`, `docs:`).
- **Descrição em cada repositório** (aparece no card "Projects") e tópicos
  (`python`, `c`, `data-structures`).
- Preencha **bio, localização e link do LinkedIn** no perfil e troque os
  placeholders de LinkedIn/e-mail no final do `README.md`.
- Ative o **2FA** e use uma foto de perfil nítida.
