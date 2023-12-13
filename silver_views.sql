CREATE TABLE jk33033_homework.silver_views
WITH (
        format = 'PARQUET',
        parquet_compression = 'SNAPPY',
        external_location = 's3://ceu-jo-kudo-wikidata/datalake/views_silver/'
) AS SELECT article, views, ranks, date FROM jk33033_homework.bronze_views