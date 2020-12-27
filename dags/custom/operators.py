from airflow.hooks.postgres_hook import PostgresHook
from airflow.hoos.S3_hook import S3Hook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class S3ToRedshiftOperator(BaseOperator):

    template_fields = ["_s3_prefix"]

    @apply_defaults
    def __init__(self, redshift_conn_id, aws_conn_id, table, schema, s3_bucket, s3_prefix="{{ ds }}.json", **kwargs):
        super(S3ToRedshiftOperator, self).__init__(**kwargs)
        self._redshift_conn_id = redshift_conn_id
        self._aws_conn_id = aws_conn_id
        self._table = table
        self._schema = schema
        self._s3_bucket = s3_bucket 
        self._s3_prefix = s3_prefix

    def execute(self, context):
        self.hook = PostgresHook(postgres_conn_id=self._redshift_conn_id)
        conn = self.hook.get_conn()
        cursor = conn.cursor()
        self.s3 = S3Hook(aws_conn_id=self._aws_conn_id)
        credentials = self.s3.get_credentials()

        copy_statement = """
            COPY {schema}.{table}
            FROM 's3://{s3_bucket}/{s3_prefix}'
            with credentials
            'aws_access_key_id={access_key};aws_secret_access_key={secret_key}'
            DATEFORMAT 'auto'
            CSV DELIMITER ',';
        """.format(schema=self._schema, table=self._table, s3_bucket=self._s3_bucket,
        s3_prefix=self._s3_prefix, access_key=credentials.access_key, 
        secret_key=credentials.secret_key)

        cursor.execute(copy_statement)
        cursor.close()
        conn.commit()
