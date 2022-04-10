
import pymysql

from easy_automation.utils.yaml_loader import YamlLoader
from easy_automation.utils.custom_logging import Logs

log = Logs(log_name="mysql")


class EasyMysql:
    _DATABASE = {}

    def __init__(self, database):
        if database not in self._DATABASE.keys():
            connect = _MysqlConnector(database)
            log.debug(f"connected mysql database {database}")
            self._DATABASE[database] = connect
        self.db = self._DATABASE[database]

    def select_one(self, sql):
        log.debug(f"execute sql: {sql}")
        return self.db.select_one(sql)

    def select_all(self, sql):
        log.debug(f"execute sql: {sql}")
        return self.db.select_all(sql)

    @classmethod
    def close_all_connect(cls):
        for conn in cls._DATABASE.values():
            conn.close()


class _MysqlConnector:
    """
    db_conf.yml file can not be modify filename or path, please use default config
    """
    mysql_conf = YamlLoader("db_conf.yml")

    def __init__(self, database):
        host = self.mysql_conf.data.mysql.host
        port = self.mysql_conf.data.mysql.port
        user = self.mysql_conf.data.mysql.user
        password = self.mysql_conf.data.mysql.password
        self.db = pymysql.connect(host=host, port=port, user=user, password=password, database=database, autocommit=True)
        self._connect = "{} connector".format(database)

    def select_one(self, sql):
        with self.db.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(sql)
            return cur.fetchone()

    def select_all(self, sql):
        with self.db.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()

    def close(self):
        log.debug(f"{self._connect} connect close")
        self.db.close()