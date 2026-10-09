# Meu Plantão: manual com o prompt do projeto

Este manual tem o **prompt completo** do Meu Plantão: tudo o que o sistema faz, as regras de negócio e as decisões de visual, escrito para uma IA (como o Claude) entender o projeto de uma vez.

## Como usar

**Para dar manutenção ou criar algo novo.**

1. Abra o Claude Code na pasta do projeto, onde estão o `index.html` e o `firestore.rules`.
2. Cole o prompt da seção abaixo.
3. Na mesma mensagem, peça o que você quer. Por exemplo: “Leia o prompt acima e o código. Quero adicionar um aviso por WhatsApp quando o corretor escolher um horário.”

**Para recriar o sistema do zero**, cole o prompt e peça: “Construa este sistema seguindo a especificação.” O passo a passo de Firebase e GitHub está no `LEIA-ME.md`.

**Para entender a transferência de titularidade**, veja o `TRANSFERENCIA.md`.

> **Regra combinada com a coordenação:** pedidos de mudança visual não alteram funcionalidade, regra de negócio, banco de dados, rotas nem fontes, a menos que isso seja autorizado. Teste antes de publicar e confira também no celular.

---

## PROMPT (copie daqui até o fim)

Você vai trabalhar no **Meu Plantão**, aplicativo web da **Almeida Carneiro** (incorporadora de alto padrão, Itabuna/BA). Ele organiza a escala de plantões dos corretores parceiros no **Stand de Vendas – Shopping Jequitibá**. A dona do produto é a coordenação de vendas.

### 1. Tecnologia e estrutura

- **O app inteiro está em um arquivo, `index.html`.**
  - É HTML, CSS e JavaScript puro (ES module), sem framework e sem etapa de build.
  - O estado fica em variáveis globais.
  - `render()` refaz o `innerHTML` de `#root` a cada mudança.
  - Cliques passam por delegação com `data-act`, e formulários usam `data-form`.
  - O que a pessoa digita é preservado em `drafts{}` entre um render e outro.
- **Firebase JS SDK 10.12.2**, carregado do `gstatic.com`.
  - Usa Authentication (e-mail/senha) e Cloud Firestore com `onSnapshot` (tempo real).
  - Uma segunda instância do app, chamada `"cadastro"`, cria contas sem tirar a coordenação da sessão.
- **Configuração e regras.** A configuração pública fica em `firebase-config.js`. As regras de segurança ficam em `firestore.rules` e precisam ser publicadas manualmente no console do Firebase.
- **Hospedagem no GitHub Pages**, branch `main`, pasta raiz. O cache é de cerca de 10 minutos.
- **O sistema tem que funcionar bem no computador e no celular.**
  - No computador, as telas da coordenação ocupam a largura toda.
  - No celular, tudo fica enquadrado, sem rolagem lateral.
- **Textos em português do Brasil**, curtos e sem jargão técnico.

### 2. Perfis de acesso

1. **Coordenação.** Entra com e-mail e senha e tem controle total. Uma conta é coordenação quando existe o documento `admins/{uid}`.
2. **Gestor de imobiliária.** Entra com e-mail e senha. A conta nasce de um destes dois jeitos:
   - **Pedido do próprio gestor:** ele usa "Cadastre-se" na tela de entrada, informando nome, e-mail, senha e imobiliária. O pedido vai para `solicitacoes`, e a coordenação aprova ou recusa na aba Corretores. Enquanto o pedido não é aprovado, ele vê "Cadastro em análise".
   - **Cadastro pela coordenação:** a coordenação cria a conta direto.

   O gestor fica registrado em `gestoresImob/{uid}`, com `{nome, email, imob}`.
3. **Corretor.** Entra com **nome + imobiliária + ano de nascimento**, sem senha.
   - Esse login não pode ser trocado pelo corretor.
   - Só a coordenação cadastra corretores.
   - Por baixo, cada corretor tem uma conta Firebase com e-mail e senha internos. Esses dados ficam em `credenciais/{uid}`, coleção que só a coordenação lê.
   - O documento `logins/{imobiliária--nome--ano}` aponta para essa conta. Ele aceita leitura direta, nunca listagem.

**Tela de entrada.**

- Fundo azul-marinho, com a logo da Almeida Carneiro.
- Título "Meu Plantão" em DM Serif Display itálico, com o slogan "Em alto padrão".
- A pessoa escolhe "Acesse:" **Corretor** ou **Imobiliária**. O acesso da coordenação fica em um link discreto.
- Ao clicar em Entrar, aparece por 5 segundos a mensagem "Seja bem-vindo(a)", seguida do primeiro nome do corretor. Para gestores, a mensagem sai sem nome.

### 3. Coordenação: abas

As abas aparecem nesta ordem: **Check-in · Escala · 1. Horários · 2. Liberar horários · 3. Relatórios · Corretores · Ajustes**.

Toda tela tem um seletor de mês (‹ mês ›). As seções longas podem ser recolhidas, e o sistema lembra quais estavam abertas pelo `localStorage`.

#### 3.1 Horários padrão e geração do mês (aba 1)

Existe um **padrão editável**, guardado em `config/geral.padrao`. Ele é formado por grupos de dias. Cada grupo tem os dias da semana, os turnos e quem pode escolher, e pode valer também para feriados.

Padrão inicial:
  - **Terça, quinta e sábado:** 10h–14h, 14h–17h e 17h–20h. Só a imobiliária TORRE escolhe.
  - **Segunda, quarta e sexta:** 10h–15h e 15h–20h. Todas as imobiliárias escolhem.
  - **Domingo e feriados:** 14h–20h.

**Formato no banco.** Os turnos são salvos como texto `"10:00-14:00"`, porque o Firestore não aceita lista dentro de lista.

**Quem pode escolher** cada grupo segue esta lógica:

| O que está marcado | Como o horário é gravado |
|---|---|
| Nenhuma imobiliária, ou todas | Qualquer imobiliária |
| Uma imobiliária | `restrito` = essa imobiliária |
| Várias imobiliárias | `excetoImob` = as que ficaram desmarcadas |

O texto na tela acompanha: "Só TORRE" ou "Todas, exceto TORRE". Clicar de novo desmarca, e "Todas as imobiliárias" alterna entre marcar e desmarcar todas.

**Gerar para:** a coordenação escolhe cada mês individualmente. O sistema cria os horários que faltam a partir de hoje, sem duplicar os que já existem.

**Horários avulsos:** servem para dias ou turnos fora do padrão. Também é possível editar ou excluir um horário específico na aba Escala.

**Feriados:** ficam numa lista em Ajustes e seguem o grupo marcado como "feriados".

#### 3.2 Liberar horários (aba 2)

- **Liberar em grupo:** por imobiliária. Os dias já vêm pré-marcados conforme o que foi definido na etapa 1. Por exemplo: ao clicar em SOLO, aparecem todos os dias exceto os que são só da TORRE.
- **Liberar por corretor:** dias específicos e um limite de quantos plantões ele pode pegar no mês.
- **Gravação no banco:**
  - Liberação por corretor: `liberacoes/{uid_AAAA-MM}`, com `{uid, mes, dias[], limite, escolhidas[]}`.
  - Liberação por imobiliária: `liberacoesImob/{imob_AAAA-MM}`, com `{imob, mes, dias[]}`.
- **Imobiliárias no modo "Gestor distribui":** a liberação em grupo grava só a liberação da imobiliária, para o gestor dela.
- **Prazo:** o padrão é liberar o mês seguinte a partir do dia 24. A coordenação pode liberar antes, inclusive para testes.

#### 3.3 Escala

- Mostra o calendário do mês e uma lista com quem está em cada horário. Os nomes ficam em `privado/{id}`, que só a coordenação lê.
- A coordenação pode colocar, trocar ou tirar um corretor, reservar um horário para uma imobiliária, editar o local ou as observações e excluir.

#### 3.4 Abrir ou fechar a escala

É feito **por mês**, em Ajustes, e fica em `config/geral.abertos`, uma lista de meses `AAAA-MM`. Os rótulos são "Escala em aberto" e "Escala fechada".

A configuração antiga, `aberta` (um valor só para todos os meses), continua aceita como alternativa.

#### 3.5 Corretores

**Lista.**

- Agrupada por imobiliária. Cada grupo mostra quantos corretores tem e quantos estão ativos no mês.
- Cada corretor tem **um único interruptor "Ativo / Desativado" por mês**, gravado no campo `inativos[]` do perfil.
- Corretor sem ano de nascimento ainda não consegue entrar.
- Dá para editar ou remover cada corretor.

**Cadastro de corretor.**

- Fica numa faixa verde-clara com ícone de pessoa.
- Campos: nome, imobiliária, ano de nascimento e a caixa "Ativo".
- Há a opção "Cadastrar vários de uma vez", com um corretor por linha no formato `nome; imobiliária; ano; ativo`.

**Gestores de imobiliária.**

- Lista sem bordas. Cada imobiliária tem um interruptor "Gestor distribui", com o efeito explicado na seção 4.
- Ao lado aparecem "Corretores escolhem" ou "Gestor distribui", o nome e e-mail do gestor e o botão "Remover", que pede confirmação.
- O cadastro de gestor segue o mesmo modelo da faixa verde.

**Pedidos de acesso:** os pedidos de gestores aparecem para a coordenação aprovar ou recusar.

#### 3.6 Check-in

- A visão é por imobiliária e por dia: presença, atraso, falta e horas cumpridas.
- A tolerância de atraso é configurável. O padrão é 10 minutos.
- A coordenação pode ajustar o check-in manualmente.

#### 3.7 Relatórios (aba 3)

Há quatro tipos:

- Escala do mês
- Resumo por corretor
- Horários livres
- Presença (check-in)

Os filtros são imobiliária e corretor.

- **Na tela:** aparecem só os filtros e os totais (plantões e horas). **Não mostre a tabela detalhada na tela.**
- **No PDF:** os detalhes saem no botão **Baixar PDF**, com a logo redonda da Almeida Carneiro.

#### 3.8 Ajustes

- Escala em aberto ou fechada, por mês.
- Se o corretor pode desistir de um plantão (`desistir`).
- Feriados.
- Imobiliárias: cadastro e nomes. A cor de cada uma é atribuída pelo sistema.
- Localização do stand: `stand {lat, lng, raio}`. Coordenadas fora do Brasil são recusadas com aviso.
- Tolerância de atraso.
- Texto das **Orientações do Plantão**.

### 4. Gestor de imobiliária

As abas são: **Distribuir horários · Calendário · Meus corretores · Check-in**.

- **O que ele faz:**
  - distribui os horários da imobiliária dele entre os corretores dela;
  - vê os plantões que já são dos corretores dele;
  - troca ou tira esses corretores a qualquer momento.
- **Limite:** só preenche horários livres **nos dias que a coordenação liberou** para a imobiliária, em `liberacoesImob`. A coordenação libera primeiro, depois o gestor distribui.
- **Corretores:** ativa ou desativa os corretores dele mês a mês, alterando só o campo `inativos`.
- **Modo "Gestor distribui" ligado** (`publico/distribui.imobs`):
  - só o gestor escolhe os horários da imobiliária;
  - os corretores dela veem a aba Calendário bloqueada, com um aviso;
  - **quando a coordenação libera um corretor individualmente**, o aviso some e esse corretor volta a escolher sozinho.
  - O aviso aparece só na aba Calendário, não na Visão geral.

### 5. Corretor

As abas são: **Visão geral · Check-in · Horários · Calendário**.

**Visão geral.**

- Saudação com o primeiro nome e os próximos plantões.
- Botão "Incluir no Calendário", que gera um arquivo `.ics` para o iPhone ou Android.
- Um card discreto avisando quando o mês seguinte estiver disponível, a partir do dia 24.
- As **Orientações do Plantão** em seções que abrem e fecham: Maquete, Registro de atendimento (no CVCRM, mídia "Stand do Shopping"), Check-in, Organização do espaço e Vestimenta.

**Horários.**

- Mostra só os dias liberados para ele, num calendário verde.
- **Quem escolhe primeiro fica com o horário.** A gravação é feita em transação, então o horário trava na hora para os outros.
- Respeita o limite de plantões do mês.
- **O corretor nunca vê nomes de outros corretores.** Ele só vê se um horário está livre ou se é dele.

**Calendário.** Só para visualizar. Mostra os próprios plantões, com cores para próximo, concluído e com check-in. O status de plantão passado se chama "Concluído".

**Check-in e check-out.**

- Usam a localização do celular, comparada com o raio do stand.
- Valem uma vez cada, com a hora do servidor (`request.time`).
- Quando há 2 corretores no mesmo plantão, só um faz check-in.

**Visual.**

- Tema claro por padrão.
- Há um **modo noturno** opcional, em azul-marinho, que fica guardado no aparelho (`mp-tema`).
- A tela de entrada é sempre azul-marinho.

### 6. Banco de dados (Firestore)

| Coleção | Conteúdo |
|---|---|
| `admins/{uid}` | Contas da coordenação. |
| `gestoresImob/{uid}` | Gestores de imobiliária. |
| `solicitacoes/{uid}` | Pedidos de acesso de gestor: `{nome, email, imob, criadoEm}`. |
| `perfis/{uid}` | Corretor: `{nome, parceiro, key, ano, inativos[], plantao, criadoEm}`. |
| `logins/{id}` | `{email, senha, uid}`. Leitura direta (`get`), nunca listagem. |
| `credenciais/{uid}` | Credenciais internas. Só a coordenação lê. |
| `vagas/{id}` | Um horário: `{mes, data, ini, fim, restrito, excetoImob[], excetoCor[], local, obs, aberta, corretorId, escolhidoEm, checkin{em,dist,prec}, checkout{…}}`. Sem nomes. |
| `privado/{id}` | Nome de quem está no horário, notas e imobiliária responsável. Só a coordenação lê. |
| `liberacoes/{uid_AAAA-MM}` | Dias, limite e horários escolhidos pelo corretor. |
| `liberacoesImob/{imob_AAAA-MM}` | Dias liberados para a imobiliária. |
| `publico/imobiliarias`, `publico/distribui` | Leitura pública, usados na tela de entrada e no modo do gestor. |
| `config/geral` | `abertos[]`, `padrao`, `orientacoes`, `stand`, `tolerancia`, `feriados`, `desistir`. |

**As regras do `firestore.rules` são a fonte da verdade da segurança.** Não afrouxe nenhuma regra sem necessidade. Resumo do que elas garantem:

- **Corretor escolhendo horário:** precisa ter perfil, a escala do mês precisa estar aberta e ele precisa estar ativo no mês. A imobiliária dele e ele próprio não podem estar excluídos, o horário precisa estar livre e o dia liberado para ele. Ele só altera `corretorId` e `escolhidoEm`, e a escolha precisa constar em `escolhidas` dentro do limite.
- **Desistir:** só se `desistir` estiver ligado e a escala do mês aberta.
- **Check-in e check-out:** só o dono do plantão, uma vez cada, com a hora do servidor.
- **Gestor:** só mexe em plantões dos corretores dele, ou em horários livres da imobiliária dele nos dias de `liberacoesImob`.

### 7. Identidade visual

**Cores.**

| Uso | Cor |
|---|---|
| Azul-marinho | `#0B1B36` (marca `#091A35`) |
| Azul claro | `#7AA8D4` |
| Fundo | `#F7F8FA` |
| Texto | `#18263D` |
| Texto secundário | `#667085` |
| Linhas | `#E3E7ED` |
| Verde de confirmação | `#2E8B68` |
| Verde claro | `#E5F2EC` |

Cada imobiliária tem uma cor própria, que aparece como uma bolinha ao lado do nome.

**Fontes.**

- Source Sans 3 para o texto.
- Outfit para números e títulos de tela.
- DM Serif Display itálico para "Meu Plantão" e para a saudação.

**Estilo:** minimalista e limpo, sem bordas desnecessárias, com ícones de traço fino e botões principais em azul-marinho. Evite fundos azuis inesperados.

**Logo:** wordmark da Almeida Carneiro (`logo-almeida-carneiro.svg`) e o símbolo redondo, usado no PDF e nas boas-vindas.

### 8. Como trabalhar neste projeto

- Leia o `index.html` antes de mudar qualquer coisa. Siga o estilo existente: funções `viewX()` que devolvem HTML em texto, `esc()` em todo texto vindo de usuário e `run()` para gravações com aviso de sucesso ou erro.
- Mudança visual não altera regra de negócio, banco, rotas nem fontes sem autorização.
- Teste localmente com `python3 -m http.server 8765`, no tamanho do computador e do celular (375 px), antes de publicar.
- Se as regras mudarem, avise que é preciso colar o `firestore.rules` no console do Firebase e clicar em Publicar.
- Nunca coloque senhas reais, dados pessoais de corretores ou links privados no repositório, que é público.
