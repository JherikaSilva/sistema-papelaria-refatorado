# 📦 Sistema de Gestão – Amor de Papelaria

> Sistema desenvolvido para apoio à gestão de estoque da empresa **Amor de Papelaria**, com foco em organização, controle e evolução para ambiente de produção.

---

## 🧠 Sobre o Projeto

Este projeto consiste no desenvolvimento e evolução de um sistema de gestão para a empresa **Amor de Papelaria**, com o objetivo de organizar e otimizar o controle de produtos e estoque.

Inicialmente criado em ambiente acadêmico, o sistema está sendo refatorado para atender requisitos reais de produção, incluindo persistência de dados, segurança e disponibilidade online.

A proposta é transformar uma aplicação local em um sistema robusto, escalável e preparado para uso contínuo em um contexto empresarial.

---

## 🏢 Contexto do Negócio

A **Amor de Papelaria** atua no segmento de papelaria e demanda organização eficiente de produtos, controle de estoque e praticidade no gerenciamento de informações.

Este sistema foi desenvolvido para atender essas necessidades, proporcionando:

* Maior controle operacional
* Redução de erros manuais
* Centralização das informações
* Otimização de processos internos

---

## 🚀 Funcionalidades

* 📋 Cadastro de produtos
* 📦 Controle de estoque
* 🧾 Gestão de dados da aplicação
* ⚙️ Interface administrativa via Django
* 📥 Importação em massa de produtos (CSV/Excel) *(em desenvolvimento)*

---

## 🛠️ Tecnologias Utilizadas

* Python
* Django
* PostgreSQL *(planejado para produção)*
* Pandas
* HTML / CSS
* Git e GitHub

---

## ⚙️ Melhorias Implementadas

* Refatoração da estrutura do projeto
* Organização do código para ambiente profissional
* Preparação para deploy em nuvem
* Configuração para banco de dados persistente
* Implementação de boas práticas de versionamento

---

## 🔐 Persistência e Segurança dos Dados

O sistema está sendo preparado para utilização de banco de dados em nuvem, garantindo:

* Persistência de dados
* Redução do risco de perda de informações
* Maior confiabilidade no armazenamento
* Independência de máquina local

---

## 💾 Estratégia de Backup

Para garantir a integridade dos dados, o projeto contempla:

* Backup automático em nuvem *(planejado)*
* Exportação manual de dados (SQL/CSV)
* Armazenamento externo (HD/pendrive)
* Redundância de informações

---

## 📦 Como Executar o Projeto

### 🔹 1. Clonar o repositório

```bash
git clone https://github.com/JherikaSilva/sistema-papelaria-refatorado
```

---

### 🔹 2. Acessar a pasta do projeto

```bash
cd papelaria-app
```

---

### 🔹 3. Criar ambiente virtual

```bash
python -m venv .venv
```

---

### 🔹 4. Ativar ambiente virtual

#### Windows:

```bash
.venv\Scripts\activate
```

#### Linux/Mac:

```bash
source .venv/bin/activate
```

---

### 🔹 5. Instalar dependências

```bash
pip install -r requirements.txt
```

---

### 🔹 6. Aplicar migrações

```bash
python manage.py migrate
```

---

### 🔹 7. Executar o servidor

```bash
python manage.py runserver
```

---

## 🌐 Acesso ao Sistema

Após iniciar o servidor, acesse:

http://127.0.0.1:8000/

---

## 🎯 Objetivo do Projeto

Desenvolver uma aplicação web funcional para gestão de estoque, aplicando conceitos de desenvolvimento backend e preparando o sistema para uso real em ambiente empresarial.

O projeto também tem como foco a evolução técnica dos desenvolvedores, utilizando ferramentas e práticas adotadas no mercado.

---

## 📌 Próximas Implementações

* Deploy em ambiente de nuvem (Render ou Railway)
* Integração completa com PostgreSQL
* Backup automatizado
* Sistema completo de importação via planilhas
* Melhorias na interface e usabilidade

---

## ⚠️ Observação

Este projeto foi baseado em uma estrutura previamente existente, sendo reorganizado e aprimorado com foco em qualidade, escalabilidade e uso profissional.

---

## 👩‍💻👨‍💻 Autores

Desenvolvido por:

* **Jherika Pereira da Silva**
* **Miguel Gonçalves Viana**

---


