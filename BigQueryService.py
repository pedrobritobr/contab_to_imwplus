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

    def read_inflow(self):
        try:
            query = f"""
            SELECT
                FORMAT_TIMESTAMP('%d/%m/%Y', date) AS data,
                inflow_code as plano_conta,
                description as titulo,
                FORMAT('%0.2f', amount) AS valor
            FROM
                `{self.inflow_table}`
            WHERE
                EXTRACT(MONTH FROM date) = EXTRACT(MONTH FROM DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH))
                AND removed IS NOT TRUE
            ORDER BY
                date
            """

            result = self.query_table(query, [])
        except Exception as error:
            raise Exception(error)
        
        if not result:
            raise NoDataFoundException()
        return result

    def read_outflow(self):
        try:
            query = f"""
            SELECT
                FORMAT_TIMESTAMP('%d/%m/%Y', date) AS data,
                outflow_code as plano_conta,
                description as titulo,
                FORMAT('%0.2f', amount) AS valor
            FROM
                `{self.outflow_table}`
            WHERE
                EXTRACT(MONTH FROM date) = EXTRACT(MONTH FROM DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH))
                AND removed IS NOT TRUE
            ORDER BY
                date
            """
            result = self.query_table(query, [])
        except Exception as error:
            raise Exception(error)
        
        if not result:
            raise NoDataFoundException()
        return result
