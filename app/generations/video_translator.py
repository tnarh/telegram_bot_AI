import asyncio
import time

import requests

from config import HEIGEN_AI_TOKEN, BASE_DIR


class VideoTranslator:

    def __init__(self):
        self.__url = "https://api.heygen.com/v2/video_translate"
        self.__headers = {
            "accept": "application/json",
            "x-api-key": HEIGEN_AI_TOKEN
        }


    def get_list_languages(self):
        url = self.__url + "/target_languages"
        response = requests.get(url, headers=self.__headers)
        return response.text


    @classmethod
    def _upload_video(cls, path_to_file: str):
        """

        :param path_to_file: Max File Size: 100 MB | Resolution: <2K
        :return:
        """
        url = "https://upload.heygen.com/v1/asset"
        with open(path_to_file, "rb") as file:
            resp = requests.post(url,
                                 data=file,
                                 headers={
                                     "Content-Type": "video/mp4",
                                     "x-api-key": HEIGEN_AI_TOKEN
                                 }
                                 )
            print(resp.json())
            return resp.json()

    def translate_video(self, video_url: str, language: str):
        """

        :param video_url:
        :param language:
        :return:
        """
        headers = self.__headers | {"Content-Type": "application/json"}
        print(headers)
        payload = {
            "video_url": video_url,
            "output_language": language,
            "title": "New Video"
            # "translate_audio_only": True
        }

        response = requests.post(self.__url, json=payload, headers=headers)
        return response.text





    def download_video(self, video_id: str):
        import requests

        url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"

        headers = {
            "accept": "application/json",
            "x-api-key": HEIGEN_AI_TOKEN
        }

        response = requests.get(url, headers=headers)

        print(response.text)








if __name__ == '__main__':
    videotr = VideoTranslator()
    # print(videotr.get_list_languages())
    # print(videotr.translate_video('https://resource2.heygen.ai/video/b544a3c38536441eb74ecda7fb3f5279/original', 'English'))
    # VideoTranslator._upload_video(f'{BASE_DIR}/app/data/media/promo.mp4')
    print(videotr.download_video('2ef9c685c32b4051874b28fede13161e'))



# 2ef9c685c32b4051874b28fede13161e
# {'code': 100, 'data': {'id': '215ed4646e1240298392e14ddc90617c', 'name': '215ed4646e1240298392e14ddc90617c', 'file_type': 'video', 'folder_id': '', 'meta': None, 'created_ts': 1725385306, 'url': 'https://resource2.heygen.ai/video/215ed4646e1240298392e14ddc90617c/original'}, 'msg': None, 'message': None}