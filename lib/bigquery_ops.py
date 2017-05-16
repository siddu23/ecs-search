from google.cloud import bigquery

def create_dataset(dataset_name='search'):
    """create new dataset
    search will have a new dataset
    """
    bigquery_client = bigquery.Client()
    dataset = bigquery_client.dataset(dataset_name)
    dataset.create()
    print('Dataset {} created.'.format(dataset.name))


def create_table(dataset_name='search', table_name='user_activity'):
    """Creates a simple table in the given dataset.

    If no project is specified, then the currently active project is used.
    """
    bigquery_client = bigquery.Client()
    dataset = bigquery_client.dataset(dataset_name)

    if not dataset.exists():
        print('Dataset {} does not exist.'.format(dataset_name))
        return

    table = dataset.table(table_name)

    # Set the table schema
    table.schema = (
        bigquery.SchemaField('lang', 'STRING'),
        bigquery.SchemaField('userid', 'STRING'),
        bigquery.SchemaField('platform', 'STRING'),
        bigquery.SchemaField('keyword', 'STRING'),
        bigquery.SchemaField('activity_dt','DATETIME'),
    )

    table.create()

    print('Created table {} in dataset {}.'.format(table_name, dataset_name))


def list_rows(dataset_name='search', table_name='user_activity'):
    """Prints rows in the given table.

    Will print 25 rows at most for brevity as tables can contain large amounts
    of rows.

    If no project is specified, then the currently active project is used.
    """
    bigquery_client = bigquery.Client()
    dataset = bigquery_client.dataset(dataset_name)
    table = dataset.table(table_name)

    if not table.exists():
        print('Table {}:{} does not exist.'.format(dataset_name, table_name))
        return

    # Reload the table so that the schema is available.
    table.reload()

    # Load at most 25 results. You can change the max_results argument to load
    # more rows from BigQuery, but note that this can take some time. It's
    # preferred to use a query.
    rows = list(table.fetch_data(max_results=25))

    # Use format to create a simple table.
    format_string = '{!s:<16} ' * len(table.schema)

    # Print schema field names
    field_names = [field.name for field in table.schema]
    print(format_string.format(*field_names))

    for row in rows:
        print(format_string.format(*row))


def stream_data(dataset_name, table_name, json_data):
    bigquery_client = bigquery.Client()
    dataset = bigquery_client.dataset(dataset_name)
    table = dataset.table(table_name)

    # Reload the table to get the schema.
    table.reload()

    rows = [json_data]
    errors = table.insert_data(rows)

    if errors:
        return False
    return True
