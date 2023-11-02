"""
title:
Blobデータから回答を生成するプロトタイプ

contents:
BlobからDBデータをDLして同データを元に回答を生成する

"""
import os
import sys

sys.path.append(os.path.abspath("prototype"))
from prototype_base import PrototypeBase
#from azure.storage.blob import BlobServiceClient

class PrototypeSample(PrototypeBase):

    @PrototypeBase.processing_structure
    def run(self, params):
        """
        プロトタイプ実行

        Returns:
        プロンプトへのAI回答

        """
        # connection_string = "DefaultEndpointsProtocol=https;AccountName=mzbotstorage;AccountKey=55enF2UEzMTFtjn9mpg9TPvSgNpWgULSLkj0U3ErPYZhjwoNnQQoRoW6JzszuHO31h+sz0P2XaZ8+ASt0rOc+Q==;EndpointSuffix=core.windows.net"  # Azure Portal から取得する
        # container_name = "root"
        # blob_name = "DB/chroma.sqlite3"
        # download_path = "./DB/chroma.sqlite3"

        # blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        # blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        # directory = os.path.dirname(download_path)
        # if not os.path.exists(directory):
        #     os.makedirs(directory)
        # with open(download_path, "wb") as download_file:
        #     download_file.write(blob_client.download_blob().readall())

if __name__ == "__main__":
    PrototypeSample().run()
