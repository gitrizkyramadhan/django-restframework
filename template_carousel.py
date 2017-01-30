from linebot.models import CarouselColumn
from linebot.models import CarouselTemplate
from linebot.models import MessageTemplateAction
from linebot.models import PostbackTemplateAction
from linebot.models import TemplateSendMessage
from linebot.models import URITemplateAction

carousels = [{
    "id" : "example",
    "payload" : TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://example.com/item1.jpg',
                    title='Transportasi & Travel',
                    text='blah',
                    actions=[
                        MessageTemplateAction(
                            label='Pesawat',
                            text='pesawat'
                        ),
                        MessageTemplateAction(
                            label='Uber',
                            text='uber'
                        ),
                        URITemplateAction(
                            label='',
                            uri='http://example.com/1'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://example.com/item2.jpg',
                    title='BJPay',
                    text='blah',
                    actions=[
                        PostbackTemplateAction(
                            label='postback2',
                            text='postback text2',
                            data='action=buy&itemid=2'
                        ),
                        MessageTemplateAction(
                            label='message2',
                            text='message text2'
                        ),
                        URITemplateAction(
                            label='uri2',
                            uri='http://example.com/2'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://example.com/item2.jpg',
                    title='Pulsa',
                    text='blah',
                    actions=[
                        PostbackTemplateAction(
                            label='postback3',
                            text='postback text3',
                            data='action=buy&itemid=3'
                        ),
                        MessageTemplateAction(
                            label='message3',
                            text='message text3'
                        ),
                        URITemplateAction(
                            label='uri3',
                            uri='http://example.com/2'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://example.com/item2.jpg',
                    title='Info',
                    text='blah',
                    actions=[
                        PostbackTemplateAction(
                            label='postback4',
                            text='postback text4',
                            data='action=buy&itemid=4'
                        ),
                        MessageTemplateAction(
                            label='message4',
                            text='message text4'
                        ),
                        URITemplateAction(
                            label='uri4',
                            uri='http://example.com/2'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://example.com/item2.jpg',
                    title='Others',
                    text='blah',
                    actions=[
                        PostbackTemplateAction(
                            label='postback5',
                            text='postback text5',
                            data='action=buy&itemid=2'
                        ),
                        MessageTemplateAction(
                            label='message5',
                            text='message text5'
                        ),
                        URITemplateAction(
                            label='uri5',
                            uri='http://example.com/2'
                        )
                    ]
                )
            ]
        )
    )
},{
"id" : "greetings",
    "payload" : TemplateSendMessage(
        alt_text='Greetings',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://bangjoni.com/v2/carousel/greetings/travel.png',
                    title='Transportasi & Travel',
                    text='buat yg suka travelling',
                    actions=[
                        MessageTemplateAction(
                            label='Pesawat',
                            text='pesawat'
                        ),
                        MessageTemplateAction(
                            label='Xtrans',
                            text='xtrans'
                        ),
                        MessageTemplateAction(
                            label='Lainnya',
                            text='transportasi lainnya'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://bangjoni.com/v2/carousel/greetings/bjpay.png',
                    title='BJPay',
                    text='carousel buat BJPAY',
                    actions=[
                        MessageTemplateAction(
                            label='Top Up',
                            text='top up bjpay'
                        ),
                        MessageTemplateAction(
                            label='Registrasi',
                            text='byjpay register'
                        ),
                        MessageTemplateAction(
                            label='Cek Saldo',
                            text='saldo'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://bangjoni.com/v2/carousel/greetings/pulsa.png',
                    title='Pulsa',
                    text='deskripsi pulsa',
                    actions=[
                        MessageTemplateAction(
                            label='Pulsa',
                            text='pulsa'
                        ),
                        MessageTemplateAction(
                            label='Token Listrik',
                            text='token'
                        ),
                        MessageTemplateAction(
                            label='Kuota Data',
                            text='pulsa data'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://bangjoni.com/v2/carousel/greetings/info.png',
                    title='Info',
                    text='blah',
                    actions=[
                        MessageTemplateAction(
                            label='Cuaca',
                            text='cuaca'
                        ),
                        MessageTemplateAction(
                            label='Tol',
                            text='tol'
                        ),
                        MessageTemplateAction(
                            label='Lainnya',
                            text='info lainnya'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://bangjoni.com/v2/carousel/greetings/other.png',
                    title='Others',
                    text='blah',
                    actions=[
                        MessageTemplateAction(
                            label='Matahari Mall',
                            text='matahari mall'
                        ),
                        MessageTemplateAction(
                            label='Lovidovi',
                            text='lovidovi'
                        ),
                        MessageTemplateAction(
                            label='Polka',
                            text='polka'
                        )
                    ]
                )
            ]
        )
    )
},{
    "id" : "transport_other",
    "payload" : TemplateSendMessage(
        alt_text='Other transportation',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://example.com/item1.jpg',
                    title='Kereta',
                    text='tut...tut..tuuutt..',
                    actions=[
                        MessageTemplateAction(
                            label='Pesan',
                            text='pesan'
                        ),
                        MessageTemplateAction(
                            label='Cek Booking',
                            text='cek booking'
                        )
                    ]
                )
            ]
        )
    )
},{
    "id" : "info_other",
    "payload" : TemplateSendMessage(
        alt_text='Other transportation',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://example.com/item1.jpg',
                    title='Translator',
                    text='Monsieur?',
                    actions=[
                        MessageTemplateAction(
                            label='Mulai',
                            text='translator'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://example.com/item1.jpg',
                    title='Zomato',
                    text='Nyam..',
                    actions=[
                        MessageTemplateAction(
                            label='Cari',
                            text='zomato'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://example.com/item1.jpg',
                    title='Reminder',
                    text='Mau diingetin?',
                    actions=[
                        MessageTemplateAction(
                            label='Mau!',
                            text='ingetin'
                        )
                    ]
                )
            ]
        )
    )
}]

def composeCarousel(alt_text, columns):
    carousel_columns = []
    for column in columns:
        actions = []
        for action in column['actions']:
            if action['type'] == 'postback':
                actions.append(PostbackTemplateAction(label=action['label'], text=action['text'], data=action['data']))
            elif action['type'] == 'message':
                actions.append(MessageTemplateAction(label=action['label'], text=action['text']))
            elif action['type'] == 'uri':
                actions.append(URITemplateAction(label=action['label'], uri=action['uri']))
        col = CarouselColumn(thumbnail_image_url=column['thumbnail_image_url'], title=column['title'], text=column['text'], actions=actions)
        carousel_columns.append(col)
    template = TemplateSendMessage(alt_text=alt_text, template=CarouselColumn(columns=carousel_columns))
    return template