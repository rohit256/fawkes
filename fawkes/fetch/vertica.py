import json
import vertica_python

default_vertica_connection_config = {
    "host": "",
    "port": 5433,
    "user": "",
    "password": "",
    "database": "",
    # autogenerated session label by default,
    "session_label": "fawkes",
    # default throw error on invalid UTF-8 results
    "unicode_error": "strict",
    # SSL is disabled by default
    "ssl": True,
    # autocommit is off by default
    "autocommit": False,
    # using server-side prepared statements is disabled by default
    "use_prepared_statements": False,
    # connection timeout is not enabled by default
    # 5 seconds timeout for a socket operation (Establishing a TCP connection or read/write operation)
    "connection_timeout": 5
}

def fetch(review_channel):
    conn_info = {
        **default_vertica_connection_config,
        **review_channel.vertica_connection_config.to_dict(),
    }
    reviews = []
    with vertica_python.connect(**conn_info) as connection:
        cur = connection.cursor('dict')
        cur.execute(review_channel.query)
        reviews = cur.fetchall()
    return json.loads(json.dumps(reviews, indent=4, sort_keys=True, default=str))
