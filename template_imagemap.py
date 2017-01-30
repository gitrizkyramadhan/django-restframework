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
    },{
        "id":"pulsa",
        "payload": ImagemapSendMessage(
            base_url='https://www.bangjoni.com/line_images/pulsa_hp1',
                alt_text='Rich Menu Pulsa',
                base_size=BaseSize(height=701, width=1040),
                actions=[
                    MessageImagemapAction(
                        text='lima ribu',
                        area=ImagemapArea(
                            x=0, y=0, width=346, height=350
                        )
                    ),
                    MessageImagemapAction(
                        text='sepuluh ribu',
                        area=ImagemapArea(
                            x=346, y=0, width=693, height=350
                        )
                    ),
                    MessageImagemapAction(
                        text='dua puluh ribu',
                        area=ImagemapArea(
                            x=693, y=0, width=1040, height=350
                        )
                    ),
                    MessageImagemapAction(
                        text='dua puluh lima ribu',
                        area=ImagemapArea(
                            x=0, y=350, width=346, height=701
                        )
                    ),
                    MessageImagemapAction(
                        text='lima puluh ribu',
                        area=ImagemapArea(
                            x=346, y=350, width=693, height=701
                        )
                    ),
                    MessageImagemapAction(
                        text='seratus ribu',
                        area=ImagemapArea(
                            x=693, y=350, width=1040, height=701
                        )
                    )
                ]
            )
    },{
        "id":"bjpay_register",
        "payload": ImagemapSendMessage(
            base_url='https://www.bangjoni.com/line_images/bjpay_register2',
                alt_text='Rich Menu BJPay Register',
                base_size=BaseSize(height=466, width=1040),
                actions=[
                    MessageImagemapAction(
                        text='bjpay register',
                        area=ImagemapArea(
                            x=0, y=0, width=1040, height=466
                        )
                    )
                ]
            )
    },{
        "id":"bjpay_register",
        "payload": ImagemapSendMessage(
            base_url='https://www.bangjoni.com/line_images/bjpay_deposit',
                alt_text='Rich Menu BJPay Deposit',
                base_size=BaseSize(height=701, width=1040),
                actions=[
                    MessageImagemapAction(
                        text='va permata',
                        area=ImagemapArea(
                            x=0, y=0, width=346, height=466
                        )
                    ),
                    MessageImagemapAction(
                        text='transfer mandiri',
                        area=ImagemapArea(
                            x=346, y=0, width=693, height=466
                        )
                    ),
                    MessageImagemapAction(
                        text='transfer bca',
                        area=ImagemapArea(
                            x=693, y=0, width=1040, height=466
                        )
                    )
                ]
            )
    }
]