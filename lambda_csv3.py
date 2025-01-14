import json
import csv
import os
from pathlib import Path
from typing import Dict, List, Optional, Union


def carregar_json(json_str: str) -> Dict:
    """
    Converte uma string JSON em um dicionário Python.
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Erro ao carregar JSON: {e}")


def obter_maior_parcela(parcelas: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Retorna a maior parcela com base no número da parcela.
    """
    return max(parcelas, key=lambda x: int(x["num_parcela"]))


def obter_maior_saldo(valores: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Retorna o maior saldo com base no valor do saldo.
    """
    return max(valores, key=lambda x: float(x["valor_saldo_devedor"]))


def obter_historico_atual(historicos: Union[List[Dict], Dict]) -> Optional[str]:
    """
    Retorna a data de referência do histórico marcado como "hist_atual": "true".
    """
    if isinstance(historicos, dict):
        historicos = [historicos]

    historico_atual = next((h for h in historicos if h.get("hist_atual") == "true"), None)
    return historico_atual["data_referencia"] if historico_atual else ""


def criar_diretorio(caminho: Path) -> None:
    """
    Cria o diretório se ele não existir.
    """
    if not caminho.exists():
        caminho.mkdir(parents=True, exist_ok=True)


def escrever_csv(nome_arquivo: Path, contratos: List[Dict]) -> None:
    """
    Escreve os dados dos contratos em um arquivo CSV, gerando uma linha para cada pagamento ou amortização.
    """
    with nome_arquivo.open(mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=";")

        # Cabeçalho
        writer.writerow([
            "DATA_PRO", "SIGLA", "CPRODLIM", "NUM_CTRT" "COD_PROD_FINN", "COD_PRDO_CPIT_JRNM", "COD_SITU_COPO_CNTR"
            "COD_COPO_FINN", "COD_FORM_EFET_COPO", "COD_FSCR_OPCR", "COD_MOTI_ISEN_COPO_FINN", "COD_REGM_CPIT_JRNM",
            "COD_REGR_APRO_REACT_OPCR", "COD_SITU_OPCR", "COD_TIPO_COPO_FINN", "COD_TIPO_EFET_COPO_FINN",
            "COD_TIPO_PARP_PESS_OPCR", "DAT_BAIX_OPCR", "DAT_CNTC_COPO_FINN", "DAT_CNTC_OPCR", "DAT_DTVR_ULTI_ATUI_OPCR",
            "DAT_INICIO_ATIVO", "DAT_MDOO_ATIVO", "DATA_VALOR"
        ])

        for contrato in contratos:
            maior_parcela = obter_maior_parcela(contrato["parcelas"])
            maior_saldo = obter_maior_saldo(contrato["dados_historicos_saldo_devedor"])
            data_hist_atual = obter_historico_atual(contrato.get("dados_historicos_marcacao_contrato", []))

            pagamentos = contrato.get("pagamentos_realizados", [])
            amortizacoes = contrato.get("amortizacoes", [])

            eventos = [
                          ("Pagamento", p["data_pagamento"], p["valor_pago"]) for p in pagamentos
                      ] + [
                          ("Amortização", a["data_amortizacao"], a["valor_amortizado"]) for a in amortizacoes
                      ]

            for taxa in contrato.get("dados_historicos_taxa", []):
                data_referencia_taxa = taxa.get("data_referencia", "")
                for valor in contrato.get("dados_historicos_valor", []):
                    data_referencia_valor = valor.get("data_referencia", "")

                    # Inclui a lógica de eventos
                    if not eventos:
                        eventos.append(("", "", ""))  # Garante que o contrato apareça no CSV

                    regime_apropriacao = contrato["dados_da_operacao"]["regime_apropriacao"]
                    if regime_apropriacao == "Competencia":
                        regime_apropriacao = "00001"
                    else:
                        regime_apropriacao = "     ".ljust(5)

                    motivo_baixa_contrato = contrato["dados_da_operacao"]["motivo_baixa_contrato"]
                    # Mapeamento dos códigos
                    motivos = {
                        "1": "00001",
                        "5": "00001",
                        "2": "00002",
                        "3": "00002",
                        "4": "00003",
                    }

                    # Obtém o valor correspondente, se existir, senão mantém o original
                    motivo_baixa_contrato = motivos.get(motivo_baixa_contrato, motivo_baixa_contrato)

                    cod_tipo_copo_finn = "00000"
                    cod_copo_finn = "00001"
                    cod_situ_copo_cntr = "00001"
                    cod_form_efet_copo = "00002"
                    cod_moti_isen_copo_finn = "00002"
                    cod_regm_cpit_jrnm = "00001"
                    cod_tipo_efet_copo_finn = "00001"
                    codi_tipo_parp_pess_opcr = "00002"

                    for cod_fscr_opcr in contrato.get("dados_historicos_marcacao_contrato", []):
                        marcacao_contrato = {
                            "1": "00010", "2": "XXXXX", "3": "00072"
                        }.get(cod_fscr_opcr.get("marcacao", ""), "")
                        for tipo, data, valor in eventos:
                            writer.writerow([
                                contrato["data_hora-processamento_dados"][:10],
                                contrato["sigla"],
                                contrato["dados_do_produto"]["cprodlin"],
                                contrato["cod_contrato"],
                                contrato["dados_do_produto"]["cprodlin"],
                                # contrato["dados_do_produto"]["cod_produto_operacioanl_v9"],
                                cod_situ_copo_cntr,
                                cod_copo_finn,
                                cod_form_efet_copo,
                                marcacao_contrato,
                                cod_moti_isen_copo_finn,
                                cod_regm_cpit_jrnm,
                                regime_apropriacao,
                                motivo_baixa_contrato,
                                cod_tipo_copo_finn,
                                cod_tipo_efet_copo_finn,
                                codi_tipo_parp_pess_opcr,
                                contrato["dados_da_operacao"]["data_implantacao"],
                                contrato["dados_da_operacao"]["data_liquidacao"],
                                contrato["dados_da_operacao"]["data_ulitma_atualizacao"],
                                contrato.get("dados_historicos_marcacao_contrato", [{}])[0].get("data_referencia", ""),
                                data_referencia_taxa,  # Adiciona data de referência da taxa
                                data_referencia_valor  # Adiciona data de referência do valor
                            ])

                            
def main():
    """
    Função principal que carrega o JSON, processa os contratos e gera um CSV.
    """
    json_str = '''
    {
  "dados": {
    "contratos": [
      {
        "dados_historicos_marcacao_contrato": [
          {
            "marcacao": "1",
            "data_referencia": "2024-04-28",
            "hist_atual": "false"
          },
          {
            "marcacao": "2",
            "data_referencia": "2024-05-02",
            "hist_atual": "false"
          },
        {
            "marcacao": "3",
            "data_referencia": "2024-06-02",
            "hist_atual": "true"
          }
        ],
        "dados_historicos_taxa": [
          {
            "tipo": "1",
            "data_referencia": "2024-03-28",
            "taxa_pre_nominal": "6.79",
            "taxa_pre_efetiva": "7.00",
            "indexador_correcao": "1",
            "base_indexador_correcao": "1",
            "indexador_taxa": "1",
            "base_indexador_taxa": "1",
            "prog_indexador_taxa": "1",
            "perc_indexador_taxa": "100.00",
            "hist_atual": "false"
          },
          {
            "tipo": "2",
            "data_referencia": "2024-04-28",
            "taxa_pre_nominal": "6.79",
            "taxa_pre_efetiva": "7.00",
            "indexador_correcao": "1",
            "base_indexador_correcao": "1",
            "indexador_taxa": "1",
            "base_indexador_taxa": "1",
            "prog_indexador_taxa": "1",
            "perc_indexador_taxa": "100.00",
            "hist_atual": "false"
          },
          {
            "tipo": "3",
            "data_referencia": "2024-05-28",
            "taxa_pre_nominal": "6.79",
            "taxa_pre_efetiva": "7.00",
            "indexador_correcao": "1",
            "base_indexador_correcao": "1",
            "indexador_taxa": "1",
            "base_indexador_taxa": "1",
            "prog_indexador_taxa": "1",
            "perc_indexador_taxa": "100.00",
            "hist_atual": "false"
          }
        ],
        "dados_historicos_valor": [
          {
            "tipo": "3",
            "data_referencia": "2024-05-28",
            "data_ocorrencia_incorporacao": "",
            "valor_incorporado_parcelas": "0.00",
            "dias_atraso": "1"
          }
        ],
        "dados_historicos_alteracao_produto": [
          {
            "tipo": "3",
            "data_referencia": "2024-05-28",
            "cprodlin": "70321",
            "hist_atual": "true"
          }
        ],
        "parcelas": [
          {
            "num_parcela": "1",
            "data_vencimento": "2024-03-28",
            "data_ocorrencia_incorporacao": "2024-04-28",
            "valor_incorporacao_parcelas": "70321",
            "dias_atraso": "0"
          },
          {
            "num_parcela": "2",
            "data_vencimento": "2024-04-28",
            "data_ocorrencia_incorporacao": "2024-05-28",
            "valor_incorporacao_parcelas": "70321",
            "dias_atraso": "0"
          },
          {
            "num_parcela": "3",
            "data_vencimento": "2024-05-28",
            "data_ocorrencia_incorporacao": "2024-06-28",
            "valor_incorporacao_parcelas": "70321",
            "dias_atraso": "0"
          }
        ],
        "dados_historicos_saldo_devedor": [
          {
            "data_referencia": "2024-03-28",
            "valor_saldo_devedor": "5674.48"
          },
          {
            "data_referencia": "2024-04-28",
            "valor_saldo_devedor": "1024.00"
          },
          {
            "data_referencia": "2024-05-28",
            "valor_saldo_devedor": "3600.00"
          }
        ],
        "cod_contrato": "1111",
        "sigla": "OD",
        "data_hora-processamento_dados": "2024-06-28 17:20:15",
        "dados_do_produto": {
          "cprodlin": "70321",
          "cod_produto_operacioanl_v9": "0",
          "cod_produto_financeiro_v9": "0"
        },
        "dados_da_operacao": {
          "data_da_assinatura": "2008-01-18",
          "data_implantacao": "2008-01-04",
          "valor_financ_total": "0.00",
          "regime_apropriacao": "Competencia",
          "motivo_baixa_contrato": "1",
          "data_liquidacao": "2024-06-28",
          "data_ulitma_atualizacao": "2024-08-28"
        }
      },
      {
        "dados_historicos_marcacao_contrato": [
          {
            "marcacao": "1",
            "data_referencia": "2024-04-28",
            "hist_atual": "false"
          },
          {
            "marcacao": "1",
            "data_referencia": "2024-05-02",
            "hist_atual": "true"
          }
        ],
        "dados_historicos_taxa": [
          {
            "tipo": "1",
            "data_referencia": "2024-03-28",
            "taxa_pre_nominal": "6.79",
            "taxa_pre_efetiva": "7.00",
            "indexador_correcao": "1",
            "base_indexador_correcao": "1",
            "indexador_taxa": "1",
            "base_indexador_taxa": "1",
            "prog_indexador_taxa": "1",
            "perc_indexador_taxa": "100.00",
            "hist_atual": "false"
          },
          {
            "tipo": "2",
            "data_referencia": "2024-04-28",
            "taxa_pre_nominal": "6.79",
            "taxa_pre_efetiva": "7.00",
            "indexador_correcao": "1",
            "base_indexador_correcao": "1",
            "indexador_taxa": "1",
            "base_indexador_taxa": "1",
            "prog_indexador_taxa": "1",
            "perc_indexador_taxa": "100.00",
            "hist_atual": "false"
          },
          {
            "tipo": "3",
            "data_referencia": "2024-05-28",
            "taxa_pre_nominal": "6.79",
            "taxa_pre_efetiva": "7.00",
            "indexador_correcao": "1",
            "base_indexador_correcao": "1",
            "indexador_taxa": "1",
            "base_indexador_taxa": "1",
            "prog_indexador_taxa": "1",
            "perc_indexador_taxa": "100.00",
            "hist_atual": "false"
          }
        ],
        "dados_historicos_valor": [
          {
            "tipo": "3",
            "data_referencia": "2024-05-28",
            "data_ocorrencia_incorporacao": "",
            "valor_incorporado_parcelas": "0.00",
            "dias_atraso": "1"
          }
        ],
        "dados_historicos_alteracao_produto": [
          {
            "tipo": "3",
            "data_referencia": "2024-05-28",
            "cprodlin": "70321",
            "hist_atual": "true"
          }
        ],
        "parcelas": [
          {
            "num_parcela": "1",
            "data_vencimento": "2024-03-28",
            "data_ocorrencia_incorporacao": "2024-04-28",
            "valor_incorporacao_parcelas": "70321",
            "dias_atraso": "0"
          },
          {
            "num_parcela": "2",
            "data_vencimento": "2024-04-28",
            "data_ocorrencia_incorporacao": "2024-05-28",
            "valor_incorporacao_parcelas": "70321",
            "dias_atraso": "0"
          },
          {
            "num_parcela": "3",
            "data_vencimento": "2024-05-28",
            "data_ocorrencia_incorporacao": "2024-06-28",
            "valor_incorporacao_parcelas": "70321",
            "dias_atraso": "0"
          }
        ],
        "dados_historicos_saldo_devedor": [
          {
            "data_referencia": "2024-03-28",
            "valor_saldo_devedor": "5674.48"
          },
          {
            "data_referencia": "2024-04-28",
            "valor_saldo_devedor": "1024.00"
          },
          {
            "data_referencia": "2024-05-28",
            "valor_saldo_devedor": "3600.00"
          }
        ],
        "cod_contrato": "2222",
        "sigla": "OD",
        "data_hora-processamento_dados": "2024-07-28 17:20:15",
        "dados_do_produto": {
          "cprodlin": "70314",
          "cod_produto_operacioanl_v9": "0",
          "cod_produto_financeiro_v9": "0"
        },
        "dados_da_operacao": {
          "data_da_assinatura": "2011-01-18",
          "data_implantacao": "2011-01-04",
          "valor_financ_total": "0.00",
          "regime_apropriacao": "Competencia",
          "motivo_baixa_contrato": "1",
          "data_liquidacao": "2024-03-28",
          "data_ulitma_atualizacao": "2024-07-28"

        }
      }
    ]
  }
}

    '''  # Substitua pelo JSON completo

    # Carregar JSON
    dados = carregar_json(json_str)

    # Nome do arquivo CSV
    arquivo_csv = "contratos.csv"

    # Obter lista de contratos
    contratos = dados["dados"]["contratos"]

    # Caminho onde você quer salvar o arquivo (diretório temp_dir no Windows)
    temp_dir = r"C:\Users\Rafael\Documents\lambda\lambda-python"

    # Verificar se o diretório existe, se não, criar
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Caminho completo para o arquivo CSV
    csv_file_path = os.path.join(temp_dir, "contratos.csv")

    # Gerar CSV
    escrever_csv(Path(csv_file_path), contratos)

    print(f"Arquivo CSV criado em: {csv_file_path}")


# Executar script apenas se chamado diretamente
if __name__ == "__main__":
    main()
