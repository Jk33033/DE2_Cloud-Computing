CREATE EXTERNAL TABLE
jk33033_homework.bronze_views (
    article STRING,
    views INT,
    ranks INT,
    date DATE,
    retrieved_at TIMESTAMP) 
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://ceu-jo-kudo-wikidata/datalake/views/';