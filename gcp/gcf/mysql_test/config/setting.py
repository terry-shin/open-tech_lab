import os
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from google.cloud import secretmanager

CRAWLER_ENV = os.environ.get('CRAWLER_ENV', 'local')
DB_PASS = os.environ.get('DB_PASS', 'local')


def get_db_pass():
    client = secretmanager.SecretManagerServiceClient()

    name = client.secret_version_path("GCPプロジェクト", "dev-db-pass",  "latest")
    print(name)
    check_name = "projects/GCPプロジェクト/secrets/dev-db-pass/versions/latest"
    response = client.access_secret_version(request={"name": f"{check_name}"})
    print(f"TEST:{response.payload.data.decode('UTF-8')}")

    return(response.payload.data.decode('UTF-8'))


# DB接続 & クエリ追加
# Cloud SQL設定
connection_name = f"{GCPプロジェクト}:asia-northeast1:{CRAWLER_ENV}-master"
db_user = "crawler_user"
db_pass = get_db_pass()
db_name = "master"
driver_name = 'mysql+pymysql'
query_string = dict({"unix_socket": "/cloudsql/{}".format(connection_name)})

ENGINE = create_engine(
  sqlalchemy.engine.url.URL(
      drivername=driver_name,
      username=db_user,
      password=db_pass,
      database=db_name,
      query=query_string,
  ),
  encoding='utf-8',
  pool_size=5,
  max_overflow=2,
  pool_timeout=30,
  pool_recycle=1800,
  echo=False
)

# DBに対してORM操作するときに利用
# Sessionを通じて操作を行う
session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)
)

# 各modelで利用
# classとDBをMapping
Base = declarative_base()
Base.query = session.query_property()

print("db session:success")
