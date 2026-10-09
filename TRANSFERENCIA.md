# Meu Plantão: documento de transferência

Este documento é para quem vai assumir o projeto. Ele explica o que o sistema faz, onde cada coisa fica e como passar a titularidade do GitHub e do Firebase.

- **Criadora:** Pollyana Silveira (coordenação de vendas, Almeida Carneiro)
- **Site no ar:** https://pollyanasilveira.github.io/meu-plantao/
- **Código:** https://github.com/PollyanaSilveira/meu-plantao
- **Banco e logins:** Firebase, projeto `meuplantaoalmeidacarneir-f8326`

## 1. O que é

O Meu Plantão organiza a escala de plantões dos corretores parceiros no **Stand de Vendas – Shopping Jequitibá** (Itabuna).

Há três tipos de acesso:

| Perfil | Como entra | O que faz |
|---|---|---|
| **Coordenação** | E-mail e senha | Faz quase tudo: <br>• gera os horários do mês a partir de um padrão editável; <br>• libera dias por imobiliária e por corretor; <br>• abre e fecha a escala de cada mês; <br>• cadastra corretores e gestores; <br>• acompanha o check-in; <br>• tira relatórios em PDF. |
| **Gestor de imobiliária** | E-mail e senha. Pede acesso em "Cadastre-se" e a coordenação aprova, ou a coordenação já cadastra. | Distribui os plantões entre os corretores da imobiliária dele, só nos dias que a coordenação liberou. Também ativa e desativa os corretores dele mês a mês. |
| **Corretor** | Nome + imobiliária + ano de nascimento, sem senha | Faz quatro coisas: <br>• escolhe horários livres nos dias liberados para ele (quem escolher primeiro fica com o horário); <br>• inclui os plantões no calendário do celular (.ics); <br>• faz check-in e check-out pela localização; <br>• lê as Orientações do Plantão. |

**Corretor sem senha.** O corretor não tem senha própria. Ao ser cadastrado, o sistema cria por baixo uma conta Firebase com e-mail e senha internos. Esses dados ficam guardados em `credenciais`, coleção que só a coordenação lê. O documento `logins/{imobiliária--nome--ano}` aponta para essa conta.

## 2. Arquivos

| Arquivo | Para que serve |
|---|---|
| `index.html` | O aplicativo inteiro, em um arquivo só (HTML + CSS + JavaScript, sem framework e sem etapa de build). |
| `firebase-config.js` | Configuração pública do projeto Firebase. Não é senha. Quem protege os dados são as regras. |
| `firestore.rules` | Regras de segurança do banco. **Precisam ser coladas e publicadas no console do Firebase** sempre que mudarem. |
| `logo-almeida-carneiro.svg` | Logo usada no app e nos PDFs. |
| `LEIA-ME.md` | Passo a passo original para montar o projeto do zero. |
| `.git/` | Histórico completo das mudanças (72 commits). |

## 3. Como funciona por dentro

### Bibliotecas e publicação

- **Firebase JS SDK 10.12.2.** É carregado direto do `gstatic.com`. Usa Authentication (e-mail/senha) e Cloud Firestore.
- **Segunda instância do Firebase (`"cadastro"`).** Serve para a coordenação criar contas de corretor sem sair da própria sessão.
- **Hospedagem no GitHub Pages**, a partir da branch `main`, pasta raiz. Cada `git push` publica uma nova versão em 1 ou 2 minutos.

### Coleções do Firestore

| Coleção | Conteúdo |
|---|---|
| `admins/{uid}` | Contas da coordenação. |
| `gestoresImob/{uid}` | Gestores de imobiliária: `{nome, email, imob}`. |
| `solicitacoes/{uid}` | Pedidos de acesso de gestor, aguardando aprovação. |
| `perfis/{uid}` | Cadastro do corretor: nome, imobiliária, ano, `inativos` (lista de meses `AAAA-MM` em que está desativado). |
| `logins/{id}` | Login do corretor. Só aceita leitura direta, nunca listagem. |
| `credenciais/{uid}` | Credenciais internas do corretor. Só a coordenação lê. |
| `vagas/{id}` | Cada horário (sem nomes): data, início, fim, mês, restrições, `corretorId`, check-in e check-out. |
| `privado/{id}` | Nome de quem está em cada horário e observações. Só a coordenação lê. |
| `liberacoes/{uid_AAAA-MM}` | Dias liberados para cada corretor no mês, limite de escolhas e horários escolhidos. |
| `liberacoesImob/{imob_AAAA-MM}` | Dias liberados para cada imobiliária no mês (usado pelos gestores). |
| `publico/imobiliarias`, `publico/distribui` | Lista de imobiliárias e as que estão no modo "Gestor distribui". Leitura pública. |
| `config/geral` | Ajustes gerais, explicados abaixo. |

O documento `config/geral` guarda:

- `abertos`: meses com a escala em aberto.
- `padrao`: horários padrão, com os turnos salvos como texto `"10:00-14:00"`. O Firestore não aceita lista dentro de lista.
- `orientacoes`: texto das Orientações do Plantão.
- `stand`: localização do stand, como `{lat, lng, raio}`.
- `tolerancia`, `feriados`, `desistir`.

As regras em `firestore.rules` garantem que:

- o corretor só pega horário livre, num dia liberado para ele, com a escala do mês aberta;
- o check-in usa a hora do servidor;
- o gestor só mexe nos corretores e nos dias da imobiliária dele.

## 4. Como transferir a titularidade

Faça na ordem. A Pollyana só deve sair do projeto depois que o novo responsável testar o acesso.

### 4.1 GitHub (código e site)

1. A Pollyana abre https://github.com/PollyanaSilveira/meu-plantao/settings.
2. Desce até **Danger Zone → Transfer ownership**.
3. Digita o usuário do GitHub do novo responsável (ou a organização da empresa) e confirma.
4. O novo dono aceita a transferência pelo e-mail que o GitHub enviar.
5. Em **Settings → Pages**, ele confirma que a publicação está em `main`, pasta `/ (root)`.

**Atenção: o endereço do site muda.** Ele passa a ser `https://NOVO-USUARIO.github.io/meu-plantao/`. O GitHub não redireciona o site antigo. Por isso:

- **Firebase:** adicione o novo domínio em **Authentication → Configurações → Domínios autorizados**. Sem isso, ninguém consegue entrar.
- **Corretores e gestores:** avise o novo link a todos.
- **Endereço que não muda:** se quiser um endereço fixo, configure um domínio próprio em Settings → Pages → Custom domain. Exemplo: `plantao.almeidacarneiro.com.br`.

### 4.2 Firebase (banco de dados e logins)

1. A Pollyana abre https://console.firebase.google.com/project/meuplantaoalmeidacarneir-f8326/settings/iam.
2. Clica em **Adicionar membro**, coloca o e-mail Google do novo responsável e escolhe o papel **Proprietário (Owner)**.
3. O novo responsável aceita o convite e confere se consegue abrir Authentication, Firestore e Regras.
4. Só depois disso, se for o caso, ele remove a Pollyana da lista.

Se o projeto Firebase estiver em plano pago (Blaze), a conta de faturamento também precisa ser transferida. No plano gratuito (Spark), não há nada a fazer.

### 4.3 Acesso de coordenação dentro do app

O acesso de coordenação é separado do dono do Firebase. Para o novo responsável virar coordenação no app:

1. No console do Firebase, em **Authentication → Usuários**, crie um usuário com o e-mail dele. Ou deixe que ele crie a própria senha pelo "Esqueci a senha".
2. Copie o **UID** desse usuário.
3. Em **Firestore → admins**, crie um documento com esse UID como ID. O conteúdo pode ser `{ "email": "..." }`.

## 5. Como fazer mudanças

```bash
git clone https://github.com/NOVO-USUARIO/meu-plantao.git
cd meu-plantao
python3 -m http.server 8765
```

1. Abra http://localhost:8765. O app conversa com o Firebase de verdade, mesmo rodando localmente.
2. Edite o `index.html`.
3. Faça `git commit` e `git push` para publicar.
4. Se mudar o `firestore.rules`, cole o novo conteúdo em **Firestore → Regras → Publicar**.

O GitHub Pages guarda a página em cache por cerca de 10 minutos. Para ver na hora, use Cmd+Shift+R (ou Ctrl+Shift+R).

## 6. Pendências conhecidas

- **Regras do Firebase:** conferir se a versão atual do `firestore.rules` foi publicada no console.
- **Localização do stand:** em Ajustes, a coordenada salva aponta para o mar. Corrija com a coordenada real do Shopping Jequitibá, senão o check-in por localização não confere.
- **Corretores sem ano de nascimento:** alguns ainda estão sem ano, e sem ele o corretor não consegue entrar.
- **Novembro:** liberar os dias das imobiliárias e abrir o mês em Ajustes.
- **Arquivo de importação:** o `seed-outubro.json` (escala de outubro, usada na primeira importação) não vai neste pacote porque tem nomes de corretores. Os dados já estão no Firebase.
