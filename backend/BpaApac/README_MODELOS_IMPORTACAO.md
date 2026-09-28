## Modelos BPA/APAC

Arquivos gerados para distribuicao as unidades:

- `MODELO_APAC_IMPORTACAO.xlsx`
- `MODELO_BPA_IMPORTACAO.xlsx`

Esses modelos seguem exatamente o que o importador do modulo `BpaApac` espera hoje.

## Regras do APAC

- O arquivo deve ser `.xlsx` ou `.xls`.
- A aba `CORPO` precisa existir com esse nome exato.
- A aba `PROCEDIMENTOS` precisa existir com esse nome exato.
- Nas duas abas, os cabecalhos devem ficar exatamente na linha `4`.
- As 3 primeiras linhas podem conter instrucoes e nao devem ser removidas no modelo.

### Colunas obrigatorias na aba `CORPO`

- `apa_num`
- `apa_codprinc`
- `apa_nomepcnte`
- `apa_datanascim`

### Colunas obrigatorias na aba `PROCEDIMENTOS`

- `pap_num`
- `pap_codproc`
- `pap_qtdprod`

## Regras do BPA

- O arquivo deve ser `.xlsx`, `.xls` ou `.txt`.
- No modelo Excel, a aba principal precisa se chamar exatamente `bpa original`.
- Os cabecalhos precisam ficar exatamente na linha `1`.

### Colunas obrigatorias na aba `bpa original`

- `prd-nmpac`
- `prd-dtnasc`
- `prd-pa`
- `prd-qt`

## Padrao de preenchimento

- Datas: usar `YYYYMMDD`
- Procedimentos: usar codigo sem mascara, preferencialmente com 10 digitos
- Quantidade: informar apenas numero
- Numero da APAC: o mesmo valor da aba `CORPO` deve aparecer na aba `PROCEDIMENTOS`
- Nome do paciente e data de nascimento devem bater entre APAC e BPA para o cruzamento funcionar

## Objetivo do cruzamento

O processador usa o APAC para identificar pacientes OCI e os procedimentos que devem ser abatidos do BPA, gerando o arquivo `BPA tratado`.

## Observacao

Se as unidades alterarem:

- nome das abas
- linha dos cabecalhos
- nome das colunas obrigatorias

o importador pode rejeitar o arquivo.
