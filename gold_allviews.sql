CREATE TABLE jk33033_homework.gold_allviews
WITH (
        format = 'PARQUET',
        parquet_compression = 'SNAPPY',
        external_location = 's3://ceu-jo-kudo-wikidata/datalake/gold_allviews/'
) AS SELECT 
    article,
    SUM(views) AS total_top_view,
    MIN(ranks) AS top_rank,
    COUNT(DISTINCT date) AS ranked_days
FROM 
    jk33033_homework.bronze_views
GROUP BY 
    article
ORDER BY 
    total_top_view DESC