from linebot.models import ButtonsTemplate
from linebot.models import MessageTemplateAction
from linebot.models import PostbackTemplateAction
from linebot.models import TemplateSendMessage
from linebot.models import URITemplateAction

imgbuttons = [{
    "id":"example",
    "payload": TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url='https://example.com/image.jpg',
            title='Menu',
            text='Please select',
            actions=[
                PostbackTemplateAction(
                    label='postback',
                    text='postback text',
                    data='action=buy&itemid=1'
                ),
                MessageTemplateAction(
                    label='message',
                    text='message text'
                ),
                URITemplateAction(
                    label='uri',
                    uri='http://example.com/'
                )
            ]
        )
    )
},{
    "id":"bjpay_register",
    "payload": TemplateSendMessage(
        alt_text='Register BJPAY',
        template=ButtonsTemplate(
            thumbnail_image_url='https://bangjoni.com/v2/carousel/greetings/bjpay.png',
            title='Register BJPAY',
            text='Buat BJPAY biar kamu gampang transaksinya',
            actions=[
                MessageTemplateAction(
                    label='Register',
                    text='bjpay register'
                )
            ]
        )
    )
}]

def compose_link_message(alt_text, thumbnail_url, title, description, label, uri):
    return TemplateSendMessage(
        alt_text=alt_text,
        template=ButtonsTemplate(
            thumbnail_image_url=thumbnail_url,
            title=title,
            text=description,
            actions=[
                URITemplateAction(label=label, uri=uri)
            ]
        ))