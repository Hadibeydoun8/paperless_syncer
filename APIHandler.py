import requests
import json
import sqlite3
from sqlite3 import Error


class APIHandler:
    def __init__(self, token, api_url, config_path):
        self.needed_tag_ids = []
        self.update_config_counter = 0
        self.conn = None
        self.token = token
        self.api_url = api_url
        self.auth_header = {"Authorization": f"Token {token}"}
        self.tags_to_path = {}
        self.needed_tags = []
        self.files_to_download = []
        self.db_file = f'{config_path}/written_files.db'
        self._update_config()
        self._create_connection()
        self._create_table()

    def update(self):
        for tag_id in self.needed_tag_ids:
            self.update_config_counter += 1
            if self.update_config_counter == 100:
                self._update_config()
                self.update_config_counter = 0
            self._get_files_to_download_for_tag_id(tag_id)
            self._remove_already_downloaded_ids()
            self._download_files(tag_id)

    def _get_files_to_download_for_tag_id(self, tag_id):
        response = requests.get(f'{self.api_url}/documents/?tags__id={tag_id}', headers=self.auth_header)
        for i in response.json()['results']:
            self.files_to_download.append(i['id'])

    def _get_slug_to_tag_id_dict(self):
        tag_json = requests.get(f'{self.api_url}/tags/', headers=self.auth_header)
        tag_json = tag_json.json()['results']
        con_dict = {}
        for i in tag_json:
            con_dict[i['slug']] = i['id']
        return con_dict

    def _convert_name_to_id(self, tags_as_dict: dict) -> [int]:
        con_dict = self._get_slug_to_tag_id_dict()
        temp_id_to_path = {}
        ids = []
        for key in tags_as_dict:
            ids.append(con_dict[key])
            for _key in self.tags_to_path:
                if _key == key:
                    temp_id_to_path[con_dict[key]] = self.tags_to_path[key]
        self.needed_tag_ids = ids
        self.tag_id_to_path = temp_id_to_path

    def _create_connection(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
            print(sqlite3.version)
        except Error as e:
            print(e)

    def _create_table(self):
        try:
            c = self.conn.cursor()
            result = c.execute("""
            CREATE TABLE IF NOT EXISTS downloaded_files (
                id integer NOT NULL
            )
            """)
            print(result)
        except Error as e:
            print(e)

    def _id_in_database(self, id_to_check):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM downloaded_files WHERE id=?", (id_to_check,))
        rows = cur.fetchall()

        if len(rows) == 0:
            return False
        return True

    def _insert_id_to_database(self, id_to_insert):
        sql = ''' INSERT INTO downloaded_files(id)
                  VALUES(?)'''
        cur = self.conn.cursor()
        cur.execute(sql, (id_to_insert,))
        self.conn.commit()

    def _remove_already_downloaded_ids(self):
        temp = self.files_to_download.copy()
        for current_id in self.files_to_download:
            if self._id_in_database(current_id):
                temp.remove(current_id)
        self.files_to_download = temp

    def _get_file_name(self, _id):
        response = requests.get(f'{self.api_url}/documents/{_id}/', headers=self.auth_header)
        return response.json()["archived_file_name"].replace(' ', "_")

    def _download_files(self, tag_id):
        download_dir = self.tag_id_to_path[tag_id]
        for _id in self.files_to_download:
            response = requests.get(f'{self.api_url}/documents/{_id}/download/', headers=self.auth_header,
                                    allow_redirects=True)
            file_dir = f"{download_dir}/{self._get_file_name(_id)}".encode('ascii', 'ignore').decode('ascii')
            with open(file_dir, 'wb') as outfile:
                outfile.write(response.content)
            print(f"Downloaded file: {file_dir}")
            self._insert_id_to_database(_id)

    def _update_config(self):
        with open('/config/config.json', 'r') as j:
            self.tags_to_path = json.load(j)['downloadable_tags']
            self._convert_name_to_id(self.tags_to_path)
