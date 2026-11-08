# Etapa 1: escolha do nicho e ROI estimado

Data: 08/11/2026 · Verba simulada: R$1.000 em Instagram Ads · 5.000 campanhas simuladas por nicho

## Recomendação

**Nicho vencedor: sono do bebê**, para mães de bebês de 0 a 2 anos, com um guia + planner de rotina de sono. Foi o único nicho que deu lucro na maioria das simulações, e lucra mais a **R$37** do que a R$47.

Os números abaixo dizem respeito ao **primeiro teste de R$1.000**, com tráfego frio e página nova. É a pior fase de qualquer funil; depois de otimizar criativos e página, o custo por venda costuma cair.

## Ranking dos 6 nichos

| # | Nicho | Preço | Vendas (faixa 80%) | Conversão da página | ROAS | Lucro mediano | Chance de lucro | Nota |
|---|---|---|---|---|---|---|---|---|
| 1 | Sono do bebê | R$37 | 15 a 71 (34) | 6,2% | 1,72 | **+R$394** | **70%** | 6,96 |
| 2 | Adestramento de cães | R$37 | 13 a 60 (29) | 4,2% | 1,42 | +R$139 | 59% | 5,89 |
| 3 | Cardápio semanal na airfryer | R$37 | 9 a 43 (20) | 2,7% | 0,98 | -R$205 | 35% | 5,48 |
| 4 | Controle da ansiedade | R$37 | 6 a 33 (16) | 3,5% | 0,74 | -R$411 | 19% | 4,61 |
| 5 | Sair das dívidas | R$37 | 5 a 28 (13) | 3,5% | 0,62 | -R$505 | 12% | 4,35 |
| 6 | IA para o trabalho | R$37 | 4 a 25 (11) | 2,2% | 0,57 | -R$556 | 10% | 4,13 |

A R$47, o sono do bebê fica em 12 a 53 vendas (mediana 26), ROAS 1,54, lucro mediano de R$257 e 64% de chance de lucro.

ROAS = faturamento ÷ verba. Lucro = faturamento − reembolsos − taxas da Kiwify − R$1.000. A nota junta 50% simulação (ROI e chance de lucro) e 50% critérios de mercado (demanda, concorrência, risco de bloqueio no Meta, potencial de escala, chance de vender o segundo produto).

### O que se espera dos R$1.000 no nicho vencedor (R$37)

- **Cenário pessimista (10% piores):** cerca de 15 vendas, prejuízo de uns R$390. O dinheiro vira aprendizado sobre criativo e público.
- **Cenário realista (mediana):** cerca de 34 vendas, R$1.720 de faturamento, uns R$390 de lucro (ROI de ~39%).
- **Cenário otimista (10% melhores):** 70 vendas ou mais, lucro acima de R$1.900.

## Por que o sono do bebê ganhou

1. **Dor urgente e diária.** Mãe que não dorme compra na hora; é o perfil de compra por impulso mais forte entre os seis.
2. **Público barato e fácil de achar no Instagram.** Mães de bebês são muito ativas na plataforma e o Meta segmenta bem esse público.
3. **Risco baixo de bloqueio.** Não envolve promessa de dinheiro, peso ou saúde mental, que são os temas que mais reprovam anúncios.
4. **Escada de produtos natural.** Depois do sono vêm introdução alimentar, desfralde, birras e rotina, ou seja, o segundo produto já está desenhado.
5. **Order bump forte.** "Pack de áudios de ruído branco e canções de ninar" a R$19 tem alta adesão.

Cuidado obrigatório: o produto deve falar de rotina e hábitos, nunca de diagnóstico ou tratamento, e precisa citar fontes confiáveis (por exemplo, Sociedade Brasileira de Pediatria). Se você tiver formação em saúde, isso vira autoridade e aumenta muito a conversão.

## Por que os outros ficaram atrás

- **Adestramento de cães:** bom segundo lugar e reserva caso o primeiro não funcione. Público apaixonado e CPM barato, mas a dor é menos urgente.
- **Cardápio airfryer:** público enorme e cliques baratos, mas compra menos por impulso a esse preço; funciona melhor como order bump de outro produto.
- **Ansiedade:** demanda altíssima, porém o Meta trata saúde mental como tema sensível (anúncios reprovados e restrição de segmentação), e o público desconfia de promessa.
- **Dívidas:** quem está endividado hesita em gastar R$37 com infoproduto; conversão baixa e anúncios de finanças passam por revisão mais rígida.
- **IA para o trabalho:** mercado saturado de "packs de prompts" gratuitos e baratos, o que derruba a conversão.

## Como a simulação funciona

O código está em [`simulador/`](../simulador). Para cada nicho, ele roda 5.000 campanhas de R$1.000:

1. Sorteia as incertezas do mercado: CPM (R$12 a R$48 conforme o nicho), taxa de clique, qualidade do criativo, adesão ao order bump e ao upsell, e reembolsos.
2. Desconta os ~12,15% de impostos que o Meta cobra desde janeiro de 2026 (de R$1.000 pagos, ~R$891 viram anúncio).
3. Gera **uma persona sintética para cada visitante** da página, com nível de dor, confiança em infoproduto, impulso de compra e quanto aceitaria pagar, e decide com um modelo de probabilidade se ela compra.
4. Calcula faturamento, reembolso, taxa da Kiwify (8,99% + R$2,49 por venda) e lucro.

Para rodar de novo ou mudar premissas: `python simulador/simulador.py --precos 37 47 50`, editando `simulador/nichos.json`.

### Limites honestos

- As premissas de CPM e clique vêm de projeções públicas de 2026 (CPM de infoproduto entre R$28 e R$60, CPC entre R$3,20 e R$8,00), não de dados medidos. Não existe benchmark oficial confiável para o Brasil.
- O comportamento das personas é um modelo calibrado para conversões típicas de página de vendas de ticket baixo (1,5% a 6%). Ele compara nichos entre si de forma consistente, mas não garante o número absoluto.
- **O passo mais importante é recalibrar com dados reais:** depois dos primeiros R$100 a R$150 de anúncio, troco CPM, CTR e conversão pelos números verdadeiros e a projeção dos R$1.000 fica muito mais precisa.

### Sobre IAs de "pessoas sintéticas"

Existem serviços comerciais que simulam consumidores com IA, como Synthetic Users e Aaru. São pagos, focados em pesquisa qualitativa em inglês e não trazem dados de custo de anúncio no Brasil, então não respondem à pergunta de ROI melhor do que este simulador. O próximo passo possível é acrescentar entrevistas com personas geradas por IA (via API do Claude) para testar headline, promessa e preço da página antes de lançar.

## Próximo passo

Com o nicho aprovado: definir nome da marca e do produto, e montar o conteúdo completo do guia (Etapa 2).

## Fontes

- [Estatísticas de custo do Meta Ads no Brasil em 2026 (Vini Ensina)](https://viniensina.com.br/estatisticas-meta-ads-brasil-2026/)
- [Benchmark de CPM no Brasil em 2026 por nicho (Trafius)](https://trafius.com.br/blog/benchmark-de-cpm-no-brasil-em-2026-por-nicho)
- [CPC médio no Meta Ads em 2026 por segmento (Trafius)](https://trafius.com.br/blog/cpc-medio-no-meta-ads-em-2026-por-segmento)
- [Produtos para vender na Kiwify (Tactus)](https://tactus.com.br/produtos-para-vender-na-kiwify/amp/)
- [Produtos mais vendidos na Kiwify (HeroSpark)](https://herospark.com/blog/produtos-mais-vendidos-na-kiwify)
- [Produtos mais vendidos na Kiwify (JivoChat)](https://www.jivochat.com.br/blog/ecommerce/produtos-mais-vendidos-kiwify.html)
- [Ferramentas de usuários sintéticos (AIMultiple)](https://research.aimultiple.com/synthetic-users)
