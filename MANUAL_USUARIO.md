# 📖 Manual do Usuário - SILVESS

Bem-vindo ao **SILVESS** - Sistema de Gestão de Restaurantes!

Este manual irá guiá-lo através de todas as funcionalidades do sistema.

## 🔐 1. Acesso ao Sistema

### 1.1 Login

1. Acesse a URL do sistema
2. Digite seu **e-mail** e **senha**
3. Clique em **Entrar**

**Credenciais padrão do administrador:**
- Email: `admin@silvess.com`
- Senha: `admin123`

⚠️ **Importante**: Altere a senha padrão após o primeiro acesso!

### 1.2 Recuperar Senha

(Funcionalidade a ser implementada)

## 📊 2. Dashboard

O Dashboard é a tela inicial do sistema e apresenta:

### Indicadores Principais
- **Total de Ingredientes**: Quantidade de ingredientes cadastrados
- **Estoque Baixo**: Ingredientes abaixo do estoque mínimo
- **Fichas Técnicas**: Total de pratos cadastrados
- **Vendas Hoje**: Valor total de vendas do dia

### Navegação
Use o menu lateral para acessar as diferentes funcionalidades.

## 📦 3. Gestão de Ingredientes

### 3.1 Cadastrar Ingrediente

1. Clique em **Ingredientes** no menu lateral
2. Clique em **Novo Ingrediente**
3. Preencha os campos:
   - **Nome**: Nome do ingrediente
   - **Unidade de Medida**: kg, litro, unidade, etc.
   - **Custo Unitário**: Preço por unidade
   - **Estoque Atual**: Quantidade em estoque
   - **Estoque Mínimo**: Alerta quando atingir este valor
   - **Fornecedor**: Nome do fornecedor (opcional)
4. Clique em **Salvar**

### 3.2 Atualizar Estoque

**Entrada de Mercadoria:**
1. Localize o ingrediente
2. Clique no botão de **Editar**
3. Selecione **Entrada**
4. Informe a quantidade
5. Adicione observação (opcional)
6. Clique em **Salvar**

**Saída de Mercadoria:**
- Mesmo processo, mas selecione **Saída**

### 3.3 Alertas de Estoque

Ingredientes com estoque abaixo do mínimo aparecem com badge **vermelho** e são destacados no dashboard.

## 🍽️ 4. Fichas Técnicas

As fichas técnicas são o coração do sistema. Elas contêm todas as informações sobre os pratos.

### 4.1 Criar Ficha Técnica

1. Clique em **Fichas Técnicas** no menu
2. Clique em **Nova Ficha Técnica**
3. Preencha as **Informações Básicas**:
   - Nome do Prato
   - Categoria (Entrada, Prato Principal, etc.)
   - Descrição
   - Número de Porções
   - Tempo de Preparo (minutos)
   - Validade (horas)
   - Modo de Preparo

### 4.2 Adicionar Ingredientes com Gramatura

Esta é a parte mais importante!

1. Na seção **Ingredientes e Gramatura**:
2. Selecione um **Ingrediente** da lista
3. Informe a **Quantidade em Gramas**
   - Exemplo: 500g de farinha, 200g de açúcar
4. Clique em **Adicionar**
5. Repita para todos os ingredientes do prato

**Dica**: Seja preciso nas gramaturas para cálculo correto de custos!

### 4.3 Cálculo Automático de Custos

O sistema calcula automaticamente:
- **Custo Total**: Soma de todos os ingredientes
- **Custo por Porção**: Custo total ÷ número de porções
- **Preço Sugerido**: Baseado em 100% de margem

### 4.4 Definir Preço de Venda

1. Veja o **Preço Sugerido** calculado
2. Ajuste o **Preço de Venda** conforme sua estratégia
3. O sistema mostra a **Margem de Lucro** automaticamente
4. Clique em **Salvar Ficha Técnica**

### 4.5 Visualizar Ficha

- Clique no ícone de **olho** para ver todos os detalhes
- Veja ingredientes, custos, modo de preparo, etc.

## 📋 5. Inventário

O inventário permite controlar e corrigir divergências no estoque.

### 5.1 Gerar Inventário

1. Clique em **Inventário** no menu
2. Selecione a **Data** (geralmente final do mês)
3. Clique em **Gerar Novo**
4. O sistema cria automaticamente um inventário com todos os ingredientes

### 5.2 Realizar Contagem Física

1. Com o inventário aberto:
2. Para cada ingrediente:
   - Veja a **Quantidade no Sistema**
   - Digite a **Quantidade Física** (contada fisicamente)
   - O sistema calcula a **Diferença** automaticamente
3. Adicione **Observações** se necessário
4. Clique em **Salvar** para cada item

### 5.3 Corrigir Divergências

Quando há diferença entre sistema e físico:

1. Revise a contagem
2. Adicione observação explicando (quebra, perda, etc.)
3. Marque **Ajustar Estoque do Sistema**
4. Clique em **Salvar**

O estoque do sistema será atualizado automaticamente!

### 5.4 Fechar Inventário

Após conferir todos os itens:

1. Clique em **Fechar Inventário**
2. Confirme a ação
3. O inventário fica **somente leitura**

⚠️ **Importante**: Após fechado, não é possível editar!

### 5.5 Reabrir Inventário

Se precisar fazer correções:

1. Clique em **Reabrir**
2. Faça as correções necessárias
3. Feche novamente quando terminar

## 📱 6. Cardápio Digital

### 6.1 Criar Cardápio

1. Clique em **Cardápios** no menu
2. Clique em **Novo Cardápio**
3. Preencha:
   - **Nome**: Ex: "Cardápio de Verão"
   - **Data**: Data de vigência
   - **Descrição**: Descrição opcional
4. Selecione os **Pratos** (segure Ctrl para múltiplos)
5. Clique em **Salvar Cardápio**

### 6.2 Gerenciar Disponibilidade

Durante o dia, você pode marcar pratos como indisponíveis:

1. Abra o cardápio
2. Use o **toggle** ao lado de cada prato
3. Verde = Disponível
4. Cinza = Indisponível

Os clientes verão a atualização em tempo real!

## 🏷️ 7. Mesas e QR Codes

### 7.1 Cadastrar Mesas

1. Clique em **Mesas & QR Codes**
2. Clique em **Nova Mesa**
3. Informe:
   - **Número da Mesa**
   - **Cardápio Associado** (opcional)
4. Clique em **Criar Mesa**

### 7.2 Gerar QR Code

1. Localize a mesa
2. Clique em **Ver QR Code**
3. O QR Code é gerado automaticamente
4. Clique em **Imprimir**
5. Coloque o QR Code impresso na mesa

### 7.3 Como Funciona

1. Cliente escaneia o QR Code com o celular
2. Abre o cardápio digital automaticamente
3. Vê todos os pratos disponíveis
4. Pratos indisponíveis aparecem marcados

**Vantagens:**
- Sem necessidade de cardápio físico
- Atualização em tempo real
- Higiênico e moderno
- Economia de impressão

## 💰 8. Vendas

### 8.1 Registrar Venda

1. Clique em **Vendas** no menu
2. Clique em **Registrar Venda**
3. Selecione os pratos vendidos
4. Informe as quantidades
5. O sistema:
   - Calcula o valor total
   - Baixa ingredientes do estoque automaticamente
   - Registra a venda

### 8.2 Visualizar Vendas

- Veja todas as vendas do dia
- Filtre por período
- Veja valor total e quantidade

## 📊 9. Relatórios

### 9.1 Relatório de Vendas

1. Clique em **Relatórios**
2. Selecione **Relatório de Vendas**
3. Escolha o período
4. Clique em **Gerar**

**Informações:**
- Total de vendas
- Pratos mais vendidos
- Faturamento por período
- Margem de lucro

### 9.2 Relatório de Estoque

1. Selecione **Relatório de Estoque**
2. Clique em **Gerar**

**Informações:**
- Valor total do estoque
- Ingredientes em falta
- Movimentações recentes
- Custo médio

## 🔧 10. Configurações

### 10.1 Alterar Senha

1. Clique no seu nome (canto inferior esquerdo)
2. Selecione **Alterar Senha**
3. Digite a senha atual
4. Digite a nova senha
5. Confirme a nova senha
6. Clique em **Salvar**

### 10.2 Gerenciar Usuários

(Funcionalidade disponível apenas para administradores)

1. Acesse **Configurações** > **Usuários**
2. Adicione novos usuários
3. Defina perfis de acesso:
   - **Admin**: Acesso total
   - **Usuário**: Acesso limitado

## 💡 11. Dicas e Boas Práticas

### Gestão de Estoque
- ✅ Faça inventário mensalmente
- ✅ Mantenha estoque mínimo atualizado
- ✅ Registre todas as movimentações
- ✅ Revise alertas de estoque baixo diariamente

### Fichas Técnicas
- ✅ Seja preciso nas gramaturas
- ✅ Atualize custos regularmente
- ✅ Revise margens de lucro mensalmente
- ✅ Documente o modo de preparo detalhadamente

### Cardápio Digital
- ✅ Atualize disponibilidade em tempo real
- ✅ Troque QR codes danificados imediatamente
- ✅ Mantenha cardápios atualizados
- ✅ Use fotos atrativas dos pratos (futuro)

### Inventário
- ✅ Faça no final do mês
- ✅ Conte fisicamente com cuidado
- ✅ Documente divergências
- ✅ Feche após conferência completa

## ❓ 12. Perguntas Frequentes

### Como calcular o preço de venda?

O sistema sugere 100% de margem, mas você pode ajustar conforme:
- Concorrência
- Posicionamento do restaurante
- Complexidade do prato
- Demanda

### O que fazer quando ingrediente está em falta?

1. Marque o prato como **indisponível** no cardápio
2. Faça pedido ao fornecedor
3. Registre entrada quando chegar
4. Marque o prato como **disponível** novamente

### Como corrigir erro no inventário?

Se o inventário está **aberto**:
- Edite diretamente

Se está **fechado**:
- Clique em **Reabrir**
- Faça as correções
- Feche novamente

### Posso ter múltiplos cardápios?

Sim! Você pode criar:
- Cardápio do almoço
- Cardápio do jantar
- Cardápio de fim de semana
- Cardápio especial

Basta criar cardápios diferentes e associar às mesas.

## 📞 13. Suporte

### Problemas Técnicos

Se encontrar algum problema:
1. Verifique sua conexão com a internet
2. Atualize a página (F5)
3. Limpe o cache do navegador
4. Entre em contato com o suporte

### Contato

- Email: suporte@silvess.com
- GitHub: [Issues](https://github.com/seu-usuario/silvess/issues)

## 🎓 14. Treinamento

### Novo Funcionário

Para treinar um novo funcionário:

1. **Dia 1**: Login, Dashboard, Navegação
2. **Dia 2**: Ingredientes e Estoque
3. **Dia 3**: Fichas Técnicas
4. **Dia 4**: Cardápio e QR Codes
5. **Dia 5**: Vendas e Relatórios

### Vídeos Tutoriais

(Em desenvolvimento)

## ✅ 15. Checklist Diário

Use este checklist para operação diária:

**Manhã:**
- [ ] Fazer login no sistema
- [ ] Verificar alertas de estoque baixo
- [ ] Atualizar disponibilidade de pratos
- [ ] Revisar cardápio do dia

**Durante o Dia:**
- [ ] Registrar vendas
- [ ] Atualizar disponibilidade conforme necessário
- [ ] Registrar entradas de mercadoria

**Final do Dia:**
- [ ] Conferir vendas do dia
- [ ] Verificar estoque crítico
- [ ] Planejar compras do dia seguinte

**Final do Mês:**
- [ ] Gerar inventário
- [ ] Realizar contagem física
- [ ] Ajustar divergências
- [ ] Fechar inventário
- [ ] Gerar relatórios mensais

---

## 🎉 Parabéns!

Você está pronto para usar o SILVESS!

Este sistema foi desenvolvido para facilitar a gestão do seu restaurante. Use todas as funcionalidades e veja sua operação se tornar mais eficiente e lucrativa.

**Bom trabalho! 🍽️**

---

**SILVESS** - Sistema de Gestão de Restaurantes
© 2024 - Todos os direitos reservados
