import os

SOLR_URL = "http://ip-172-31-16-221.ap-southeast-1.compute.internal:8983/solr"
PRATILIPI_SERVICE_URL = "{}/{}".format(os.environ['API_END_POINT'], "pratilipis")
AUTHOR_SERVICE_URL = "{}/{}".format(os.environ['API_END_POINT'], "authors")
REDIS_URL = "ecs-search.e6ocw5.0001.apse1.cache.amazonaws.com"
REDIS_PORT = 8080
REDIS_DB = 9
TOP_SEARCH_LIMIT = 10
TOP_SEARCH_AGE_IN_MIN = 3600

if os.environ["STAGE"] == "gamma":
    SOLR_URL = "http://ip-172-31-0-99.ap-southeast-1.compute.internal:8983/solr"
    REDIS_URL = "ecs-search-001.cpzshl.0001.apse1.cache.amazonaws.com"
elif os.environ["STAGE"] == "prod":
    SOLR_URL = "http://ip-172-31-0-99.ap-southeast-1.compute.internal:8983/solr"
    REDIS_URL = "ecs-search-001.cpzshl.0001.apse1.cache.amazonaws.com"
elif os.environ["STAGE"] == "devo":
    SOLR_URL = "http://ip-172-31-16-221.ap-southeast-1.compute.internal:8983/solr"
    REDIS_URL = "ecs-search.e6ocw5.0001.apse1.cache.amazonaws.com"
elif os.environ["STAGE"] == "local":
    SOLR_URL = "http://localhost:8983/solr"
    REDIS_URL = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 9
