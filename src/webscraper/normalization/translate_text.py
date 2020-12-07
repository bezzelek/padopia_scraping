import os

from google.cloud import translate_v2 as translate


class Translate:

    def __init__(self):
        self.translate_client = self.translate_client

    def start_client_translate(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'src/resonant-forge-294511-25f7c1fc6d0f.json'
        client = translate.Client()
        return client

    def translate_text(self, text, source_lang):
        request = self.translate_client.translate(
            values=text,
            target_language='en',
            source_language=source_lang,
            format_='html',

        )
        result = request['translatedText']
        return result
