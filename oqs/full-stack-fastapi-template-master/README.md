# Autenticação Pós-Quântica (PQC) no Full Stack FastAPI Template com liboqs

Este projeto estende o **Full Stack FastAPI Template** com um mecanismo de **autenticação reforçada por criptografia pós-quântica (Post-Quantum Cryptography – PQC)**, utilizando a biblioteca **liboqs (Open Quantum Safe)**. A proposta não é substituir os mecanismos tradicionais do template, mas **complementá-los**, criando um modelo híbrido no qual operações sensíveis exigem tanto autenticação clássica (JWT) quanto uma sessão criptográfica pós-quântica estabelecida dinamicamente.

A implementação foi pensada para ser didática, modular e compatível com a arquitetura original do template, permitindo sua análise acadêmica e futura evolução.

---

## Motivação e papel da liboqs

A **liboqs** fornece implementações de algoritmos criptográficos resistentes a ataques de computadores quânticos, como **Kyber** (KEM) e **Dilithium** (assinaturas digitais), ambos selecionados pelo NIST como padrões pós-quânticos. Esses algoritmos são projetados para resistir a ataques que quebrariam esquemas clássicos amplamente usados hoje, como RSA e ECC.

No contexto deste projeto, a liboqs é utilizada **no nível da aplicação**, e não apenas na camada de transporte (TLS). Isso permite a construção de protocolos próprios de autenticação e autorização que permanecem seguros mesmo em um cenário futuro onde adversários possuam computadores quânticos capazes de executar algoritmos como o de Shor.

---

## Visão geral do fluxo de autenticação implementado

O fluxo completo pode ser observado no script `backend/example_pqc_client.py`, que atua como um cliente de demonstração. Esse fluxo combina **JWT tradicional** com um **handshake pós-quântico baseado em KEM**, criando uma sessão adicional exigida para operações críticas.

O processo ocorre da seguinte forma:

Primeiro, o cliente realiza o login normalmente, utilizando email e senha. Esse passo é idêntico ao do Full Stack FastAPI Template original. O backend valida as credenciais e retorna um **JWT**, que continua sendo necessário para autenticação básica e controle de acesso.

Em seguida, o cliente consulta a API para listar os algoritmos pós-quânticos disponíveis. Esse endpoint retorna informações sobre os KEMs suportados pelo servidor, como nome do algoritmo e nível de segurança NIST. No exemplo, o algoritmo padrão utilizado é o **Kyber512**.

Após isso, inicia-se o **handshake pós-quântico**. O cliente solicita ao servidor a inicialização do handshake, informando o algoritmo desejado. O servidor então gera um par de chaves KEM e retorna ao cliente um identificador de handshake junto com a **chave pública pós-quântica**, codificada em Base64.

Com essa chave pública, o cliente utiliza a liboqs localmente para encapsular um segredo compartilhado. Esse processo gera dois artefatos: um **ciphertext**, que pode ser enviado ao servidor, e um **shared secret**, que nunca trafega pela rede. O ciphertext é então enviado ao servidor para completar o handshake.

O servidor, ao receber o ciphertext, realiza a operação de desencapsulamento com sua chave privada, obtendo o mesmo segredo compartilhado que o cliente. A partir desse ponto, o backend cria uma **sessão PQC**, associada ao usuário autenticado, com tempo de expiração definido. Essa sessão é identificada por um `session_id`.

---

## Sessão PQC e proteção de operações críticas

A sessão pós-quântica criada durante o handshake não substitui o JWT. Em vez disso, ela atua como um **segundo fator criptográfico**, exigido apenas para operações sensíveis.

No exemplo fornecido, a troca de senha do usuário é tratada como uma operação crítica. Para executá-la, o cliente deve enviar dois elementos simultaneamente:

* O JWT tradicional no header `Authorization`
* O identificador da sessão PQC no header `X-PQC-Session`

Se o cliente tentar executar essa operação sem uma sessão PQC válida, o servidor rejeita a requisição com erro **403 Forbidden**, mesmo que o JWT seja válido. Isso demonstra que o sistema exige explicitamente a autenticação pós-quântica para determinadas ações.

Esse modelo cria uma separação clara entre:

* Autenticação clássica (identidade do usuário)
* Estabelecimento de confiança criptográfica pós-quântica (sessão PQC)

---

## Papel do cliente PQC de exemplo

O script `example_pqc_client.py` foi incluído como uma ferramenta de demonstração e validação do sistema. Ele executa automaticamente todo o fluxo descrito, incluindo:

* Login JWT tradicional
* Descoberta de algoritmos pós-quânticos disponíveis
* Handshake PQC completo usando Kyber
* Execução de uma operação protegida
* Demonstração de falha ao tentar a mesma operação sem sessão PQC
* Consulta de estatísticas internas de sessões PQC ativas e handshakes pendentes

Esse cliente evidencia que a liboqs não está sendo usada apenas como dependência teórica, mas como parte efetiva de um protocolo de autenticação híbrido.

---

## Impacto no Full Stack FastAPI Template

Um aspecto central desta implementação é que **nenhuma funcionalidade original do template foi removida ou modificada de forma destrutiva**. O login, JWT, modelos de usuário, banco de dados e permissões continuam funcionando exatamente como antes.

As extensões introduzidas são opcionais e isoladas. Caso o cliente não utilize os endpoints PQC, o sistema se comporta como o Full Stack FastAPI Template padrão. Isso garante compatibilidade retroativa e facilita a adoção gradual de criptografia pós-quântica.

Além disso, a solução foi projetada para coexistir com TLS (inclusive TLS híbrido pós-quântico), reforçando a segurança tanto no transporte quanto na lógica de aplicação.

---

## Considerações finais

Esta implementação demonstra, de forma prática, como **criptografia pós-quântica pode ser integrada a uma aplicação web moderna** sem comprometer sua arquitetura ou simplicidade. O uso de KEMs para criar sessões criptográficas adicionais oferece um caminho viável para proteger operações críticas contra adversários quânticos futuros.

O projeto possui caráter **experimental e educacional**, sendo indicado para pesquisas, provas de conceito e estudos acadêmicos. Ainda assim, ele segue princípios sólidos de engenharia de software e segurança, alinhados às recomendações do NIST e do projeto Open Quantum Safe.

