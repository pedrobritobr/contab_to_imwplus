from google.cloud import bigquery
from flask import current_app

class NoDataFoundException(Exception):
    def __init__(self):
        super().__init__()

class BigQueryService:
    def __init__(self):
        config = current_app.config
        GCP_CREDS = config.get('GCP_CREDS')
        TABLE_AMBIENT = config.get('TABLE_AMBIENT')
        DATASET_ID = config.get('DATASET_ID')
        PROJECT_ID = config.get('PROJECT_ID')

        self.client = bigquery.Client(credentials=GCP_CREDS, project=PROJECT_ID)
        self.dataset_id = f"{PROJECT_ID}.{DATASET_ID}"
        self.table_ambient = TABLE_AMBIENT

        self.inflow_table = f"{self.dataset_id}.imw_inflow_{self.table_ambient}"
        self.outflow_table = f"{self.dataset_id}.imw_outflow_{self.table_ambient}"

    def query_table(self, query, query_parameters = []):
        try:
            job_config = bigquery.QueryJobConfig(
                query_parameters=query_parameters
            )
            query_job = self.client.query(query, job_config=job_config)
            result = query_job.result()
            return [dict(row) for row in result]
        except Exception as error:
            raise Exception(f"Failed to query table. {error}")

    def get_transactions_from_month_query(self, transaction_type, transactions_month):
        transaction_map = {
            "inflow": {
                "table": self.inflow_table,
                "column": "inflow_code"
            },
            "outflow": {
                "table": self.outflow_table,
                "column": "outflow_code"
            }
        }

        return f"""
        SELECT
            FORMAT_TIMESTAMP('%d/%m/%Y', date) AS data,
            {transaction_map[transaction_type]["column"]} as plano_conta,
            description as titulo,
            COALESCE(payment_method, 'cash') AS payment_method,
            REPLACE(FORMAT('%.2f', amount), '.', ',') AS valor
        FROM
            `{transaction_map[transaction_type]["table"]}`
        WHERE
            DATE(DATE_TRUNC(date, MONTH)) = PARSE_DATE("%Y-%m", "{transactions_month}")
            AND removed IS NOT TRUE
        """

    def get_transactions(self, transactions):
        try:
            transactions_type = transactions.get("type")
            transactions_month = transactions.get("month")

            if transactions_type not in ["inflow", "outflow", "all"]:
                raise ValueError("Invalid transactions type")

            inflow_query = self.get_transactions_from_month_query("inflow", transactions_month)
            outflow_query = self.get_transactions_from_month_query("outflow", transactions_month)

            queries = {
                "all": f"{inflow_query} UNION ALL {outflow_query} ORDER BY data",
                "inflow": inflow_query,
                "outflow": outflow_query
            }

            query = queries.get(transactions_type)
            result = self.query_table(query, [])

        except Exception as error:
            raise Exception(error)

        if not result:
            raise NoDataFoundException()

        return result
