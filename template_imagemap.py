from linebot.models import BaseSize
from linebot.models import ImagemapArea
from linebot.models import ImagemapSendMessage
from linebot.models import MessageImagemapAction
from linebot.models import URIImagemapAction

imagemaps = [
    {
        "id":"example",
        "payload": ImagemapSendMessage(
            base_url='https://example.com/base',
                alt_text='this is an imagemap',
                base_size=BaseSize(height=1040, width=1040),
                actions=[
                    URIImagemapAction(
                        link_uri='https://example.com/',
                        area=ImagemapArea(
                            x=0, y=0, width=520, height=1040
                        )
                    ),
                    MessageImagemapAction(
                        text='hello',
                        area=ImagemapArea(
                            x=520, y=0, width=520, height=1040
                        )
                    )
                ]
            )
    }
]