"""
title:
Blobデータから回答を生成するプロトタイプ

contents:
BlobからDBデータをDLして同データを元に回答を生成する

"""
import os

from prototype_base import PrototypeBase
from azure.storage.blob import BlobServiceClient

class Prototype(PrototypeBase):

    @PrototypeBase.processing_structure
    def run(params : PrototypeBase.Params):
        """
        プロトタイプ

        Args:
        入力パラメータ群
        Returns:
        プロンプトに対するAIの回答
        """
        connection_string = "DefaultEndpointsProtocol=https;AccountName=mzbotstorage;AccountKey=55enF2UEzMTFtjn9mpg9TPvSgNpWgULSLkj0U3ErPYZhjwoNnQQoRoW6JzszuHO31h+sz0P2XaZ8+ASt0rOc+Q==;EndpointSuffix=core.windows.net"
        container_name = "root"
        blob_name = params.config["db_path"]
        download_path = "./DB/chroma.sqlite3"

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        directory = "DB"
        
        print(blob_client)
        if not os.path.exists("DB"):
            os.makedirs(directory)
        with open(download_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

if __name__ == "__main__":
    Prototype().run()
