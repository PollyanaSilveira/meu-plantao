# Meu Plantão: como colocar no ar

O site fica no **GitHub Pages**, que é gratuito. Os logins e a escala ficam no **Firebase**, do Google, que também é gratuito para este uso. Faça os passos na ordem. Leva uns 20 minutos.

## 1. Criar o projeto no Firebase
1. Acesse https://console.firebase.google.com e entre com sua conta Google.
2. Clique em **Criar um projeto**, dê o nome `meu-plantao` e desative o Google Analytics (não é necessário).

## 2. Registrar o site e copiar a configuração
1. Na página do projeto, clique no ícone **</>** (Web).
2. Dê o apelido `Meu Plantão`, deixe o Hosting desmarcado e clique em **Registrar app**.
3. Vai aparecer um bloco `const firebaseConfig = { apiKey: ..., ... }`.
4. Copie os valores para o arquivo **`firebase-config.js`** desta pasta, no lugar de cada `COLE_AQUI`. Esses dados não são senha e podem ficar visíveis no site.

## 3. Ativar o login
1. No menu lateral, abra **Criação → Authentication** e clique em **Vamos começar**.
2. Em **Método de login**, ative **E-mail/senha** (só a primeira opção) e salve.

## 4. Criar o banco de dados e as regras de segurança
1. No menu lateral, abra **Criação → Firestore Database** e clique em **Criar banco de dados**.
2. Escolha a região **southamerica-east1 (São Paulo)** e depois o **modo de produção**.
3. Abra a aba **Regras**, apague o que estiver lá e cole todo o conteúdo do arquivo **`firestore.rules`**.
4. Clique em **Publicar**.

## 5. Publicar no GitHub
1. Em https://github.com/new, crie um repositório **público** chamado `meu-plantao`.
2. Na página do repositório, clique em **Add file → Upload files** e envie:
   `index.html`, `firebase-config.js` e `seed-outubro.json`.
3. Clique em **Commit changes**.
4. Abra **Settings → Pages**. Em *Branch*, escolha `main` e a pasta `/ (root)`, e clique em **Save**.
5. Em 1 ou 2 minutos, o site fica no ar em `https://SEU-USUARIO.github.io/meu-plantao/`.

## 6. Autorizar o endereço do site no Firebase
1. No Firebase, abra **Authentication → Configurações → Domínios autorizados**.
2. Clique em **Adicionar domínio** e digite `SEU-USUARIO.github.io`.

## 7. Primeiro acesso do gestor (faça logo depois de publicar)
1. Abra o site e clique em **Acesso do gestor → Primeira vez? Criar acesso de gestor**.
2. Use seu e-mail e uma senha. Depois disso, o sistema não aceita novas contas de gestor.
3. Em **Horários**, clique em **Importar outubro/2026** para trazer a escala que já existia.

## Uso no dia a dia
- **Corretores:** cadastre cada um com nome, imobiliária e ano de nascimento. Também dá para colar uma lista de vários de uma vez.
- **Horários:** no começo de cada mês, crie os horários com os dias e turnos.
- **Liberar horários:** escolha os dias de cada corretor e quantos plantões ele pode pegar. Quem não tiver dia liberado vê que não está liberado no mês.
- **O corretor:** entra com nome, imobiliária e ano de nascimento, e escolhe entre os dias dele. Quem escolhe primeiro fica com o horário, e o horário some para os outros.
- **Ajustes:** abre ou fecha a escala (Escala em aberto / Escala fechada), define se o corretor pode desistir e guarda o aviso para os corretores, os feriados e as imobiliárias.

## Atualizar o site depois
Para trocar um arquivo, envie de novo por **Add file → Upload files** no GitHub. Os dados (corretores, escala) ficam no Firebase e não se perdem.
