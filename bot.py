import json
import requests
#from requests_toolbelt import MultipartEncoder


class Bot(object):
    def __init__(self):
        self.base_url = "https://api.line.me/v1/events"

    def send_link_message(self, recipient_id, message1, message2, message3, link_url, previewImageUrl):
        payload = {
                    'to':[recipient_id],
                    'toChannel':1341301715,
                    'eventType':'137299299800026303',
                    'content':{
                                   'templateId':'payment_kartu_kredit_tiketux',
                                   'previewUrl': previewImageUrl,
                                   'textParams':{
                                                    'templatetext': message1
                                                },
                                   'subTextParams':{
                                                    'subtext': message2
                                                },
                                   'linkTextParams':{
                                                    'linktext': message3
                                                },
                                   'aLinkUriParams':{
                                                    'alu_p':'foo'
                                                },
                                   'iLinkUriParams':{
                                                    'ilu_p':'bar'
                                                },
                                   'linkUriParams':{
                                                    'weburl': link_url
                                                   }
                              }
                  }	              
        return self._send_payload(payload)


    def send_images_text(self, recipient_id, image_url, image_url_thumbnail, message):
        payload = {
                    'to':[recipient_id],
                    'toChannel':1383378250,
                    'eventType':'140177271400161403',
                    'content':{
                                'messageNotified': 0,
                                'messages': [
                                               {
                                                   'contentType': 1,
                                                   'text': message
                                               },
                                               {
                                                   'contentType': 2,
                                                   'originalContentUrl': image_url,
                                                   'previewImageUrl': image_url_thumbnail
                                               }
                                            ]
                              }
                  }	              
        return self._send_payload(payload)		

    def send_message(self, recipient_id, message):
        payload = {
                    'to':[recipient_id],
                    'toChannel':1383378250,
                    'eventType':'138311608800106203',
                    'content':{
                                 'contentType':1,
                                 'toType':1,
                                 'text': message
                              }
                  }	              
        return self._send_payload(payload)
		
	

    def _send_payload(self, payload):
        #result = requests.post(self.base_url, json=payload).json()
        #result = requests.post(self.base_url, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'X-Line-ChannelID': '1474966219', 'X-Line-ChannelSecret': '8b1939d2a3e0b43eeb144405a19a4152', 'X-Line-Trusted-User-With-ACL': 'u046be05c81c5a02fc2f056c8b08e25a1'})
        #result = requests.post(self.base_url, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'X-LINE-ChannelToken': 'Wo5lZ0Dq0zy5Qr7b9kFG0ZaAantipK1zhKv70ghoPQ+GMcSqufV97jxhOV8MGwth5WsoPw5Rw5N5YyNK2wY64un6VMPiQgrowuMpvej/e6UHeOX6o/5CIkz4YaXed3bsnwaNIQFPjtojpFtrq+nkta18BSl7lGXPAT9HRw/DX2c='})		
		print "kirim pesan cuy"
		result = requests.post(self.base_url, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'X-LINE-ChannelToken': 'wc0Gldamr7gGN3DN56fvee0MJoRbEHwgwgGwhUfvocf6Ot6wd/DWFlFP2PzVEji+5WsoPw5Rw5N5YyNK2wY64un6VMPiQgrowuMpvej/e6Vj1y7+wixSoo5IbRVwjvMI6C/2k8IzhLwMh5QCMm6uKq18BSl7lGXPAT9HRw/DX2c='})		
		print result
		print result.content
		return result.content
		
    def send_payload_new(self, payload):
        #result = requests.post(self.base_url, json=payload).json()
        #result = requests.post(self.base_url, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'X-Line-ChannelID': '1474966219', 'X-Line-ChannelSecret': '8b1939d2a3e0b43eeb144405a19a4152', 'X-Line-Trusted-User-With-ACL': 'u046be05c81c5a02fc2f056c8b08e25a1'})
        #result = requests.post(self.base_url, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'X-LINE-ChannelToken': 'Wo5lZ0Dq0zy5Qr7b9kFG0ZaAantipK1zhKv70ghoPQ+GMcSqufV97jxhOV8MGwth5WsoPw5Rw5N5YyNK2wY64un6VMPiQgrowuMpvej/e6UHeOX6o/5CIkz4YaXed3bsnwaNIQFPjtojpFtrq+nkta18BSl7lGXPAT9HRw/DX2c='})		
		print "kirim pesan cuy"
		result = requests.post(self.base_url, data=json.dumps(payload), headers={'Content-Type': 'application/json', 'X-LINE-ChannelToken': 'wc0Gldamr7gGN3DN56fvee0MJoRbEHwgwgGwhUfvocf6Ot6wd/DWFlFP2PzVEji+5WsoPw5Rw5N5YyNK2wY64un6VMPiQgrowuMpvej/e6Vj1y7+wixSoo5IbRVwjvMI6C/2k8IzhLwMh5QCMm6uKq18BSl7lGXPAT9HRw/DX2c='})		
		print result
		print result.content
		return result.content
		
    def send_images(self, recipient_id, image_url, image_url_thumbnail):
        payload = {
                    'to':[recipient_id],
                    'toChannel':1383378250,
                    'eventType':'138311608800106203',
                    'content':{
                        'contentType':2,
                        'toType':1,
                        'originalContentUrl': image_url,
                        'previewImageUrl': image_url_thumbnail
                              }
                  }
        return self._send_payload(payload)        

    def set_markup(self):
        markup_json = {
                    'scenes': {
                       'scene1': {
                          'listeners': [
                              {
                                 'type': 'touch',
                                 'action': 'action0',
                                 'params': [0, 0, 520, 1040]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action1',
                                 'params': [520, 0, 520, 1040]
                              }
                           ],
                         'draws': [
                              {
                                 'h': 701,
                                 'w': 1040,
                                 'y': 0,
                                 'x': 0,
                                 'image': 'image1'
                              }
                          ]
                      }
                   },
                   'actions': {
                      'action1': {
                         'params': {
                            'linkUri': 'https://www.bangjoni.com'
                         },
                         'type': 'web'
                      },
                      'action0': {
                        'params': {
                            'text': 'Hello World'
                        },
                        'type': 'sendMessage',
                        'text' : 'Hello World Again'
                      }
                  },
                  'images': {
                      'image1': {
                          'h': 701,
                          'w': 1040,
                          'y': 0,
                          'x': 0
                       }
                  },
                  'canvas': {
                      'height': 701,
                      'width': 1040,
                      'initialScene': 'scene1'
                  }
        }
        return markup_json
		
    def send_rich_message(self, recipient_id, image_url, alt_text):
        markup_json = json.dumps(self.set_markup())
        payload = {
                    'to':[recipient_id],
                    'toChannel':1383378250,
                    'eventType':'138311608800106203',
                    'content':{
                                 'contentType':12,
                                 'toType':1,
                                 'contentMetadata': {
								    'SPEC_REV':'1',
                                    'DOWNLOAD_URL': image_url,
                                    'ALT_TEXT': alt_text,
                                    'MARKUP_JSON': markup_json
								 
								 
								 
								 }
								 
                              }
                  }	  
        return self._send_payload(payload) 				

		
    def set_markup_payment_jatis(self):
        markup_json = {
                    'scenes': {
                       'scene1': {
                          'listeners': [
                              {
                                 'type': 'touch',
                                 'action': 'action0',
                                 'params': [0, 0, 344, 230]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action1',
                                 'params': [344, 0, 692, 230]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action2',
                                 'params': [692, 0, 1040, 230]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action3',
                                 'params': [0, 230, 344, 500]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action4',
                                 'params': [344, 230, 692, 500]
                              },		
                              {
                                 'type': 'touch',
                                 'action': 'action5',
                                 'params': [692, 230, 1040, 500]
                              }								  
                           ],
                         'draws': [
                              {
                                 'h': 466,
                                 'w': 1040,
                                 'y': 0,
                                 'x': 0,
                                 'image': 'image1'
                              }
                          ]
                      }
                   },
                   'actions': {
                      'action0': {
                        'params': {
                            'text': 'atm'
                        },
                        'type': 'sendMessage',
                        'text' : 'atm'
                      },
                      'action1': {
                        'params': {
                            'text': 'kartu kredit'
                        },
                        'type': 'sendMessage',
                        'text' : 'kartu kredit'
                      },
                      'action2': {
                        'params': {
                            'text': 'kartu kredit'
                        },
                        'type': 'sendMessage',
                        'text' : 'kartu kredit'
                      },
                      'action3': {
                        'params': {
                            'text': 'mandiri ecash'
                        },
                        'type': 'sendMessage',
                        'text' : 'mandiri ecash'
                      },
                      'action4': {
                        'params': {
                            'text': 'doku wallet'
                        },
                        'type': 'sendMessage',
                        'text' : 'doku wallet'
                      },					  
                      'action5': {
                        'params': {
                            'text': 'alfamidi lawson dandan'
                        },
                        'type': 'sendMessage',
                        'text' : 'alfamidi lawson dandan'
                      }					  
                  },
                  'images': {
                      'image1': {
                          'h': 466,
                          'w': 1040,
                          'y': 0,
                          'x': 0
                       }
                  },
                  'canvas': {
                      'height': 466,
                      'width': 1040,
                      'initialScene': 'scene1'
                  }
        }
        return markup_json
		

    def send_rich_message_payment_jatis_text(self, recipient_id, image_url, alt_text, message):
        markup_json = json.dumps(self.set_markup_payment_jatis())	
        payload = {
                    'to':[recipient_id],
                    'toChannel':1383378250,
                    'eventType':'140177271400161403',
                    'content':{
                                'messageNotified': 0,
                                'messages': [
                                               {
                                                   'contentType': 1,
                                                   'text': message
                                               },
                                               {
                                                   'contentType':12,
                                                   'toType':1,
                                                   'contentMetadata': {
								                       'SPEC_REV':'1',
                                                       'DOWNLOAD_URL': image_url,
                                                       'ALT_TEXT': alt_text,
                                                       'MARKUP_JSON': markup_json

								                   }               
                                               }
                                            ]
                              }
                  }	              
        return self._send_payload(payload)				

    def set_markup_pulsa_hp(self):
        markup_json = {
                    'scenes': {
                       'scene1': {
                          'listeners': [
                              {
                                 'type': 'touch',
                                 'action': 'action0',
                                 'params': [0, 0, 346, 350]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action1',
                                 'params': [346, 0, 693, 350]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action2',
                                 'params': [693, 0, 1040, 350]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action3',
                                 'params': [0, 350, 346, 701]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action4',
                                 'params': [346, 350, 693, 701]
                              },		
                              {
                                 'type': 'touch',
                                 'action': 'action5',
                                 'params': [693, 350, 1040, 701]
                              }
                           ],
                         'draws': [
                              {
                                 'h': 701,
                                 'w': 1040,
                                 'y': 0,
                                 'x': 0,
                                 'image': 'image1'
                              }
                          ]
                      }
                   },
                   'actions': {
                      'action0': {
                        'params': {
                            'text': 'lima ribu'
                        },
                        'type': 'sendMessage',
                        'text' : 'lima ribu'
                      },
                      'action1': {
                        'params': {
                            'text': 'sepuluh ribu'
                        },
                        'type': 'sendMessage',
                        'text' : 'sepuluh ribu'
                      },
                      'action2': {
                        'params': {
                            'text': 'dua puluh ribu'
                        },
                        'type': 'sendMessage',
                        'text' : 'dua puluh ribu'
                      },
                      'action3': {
                        'params': {
                            'text': 'dua puluh lima ribu'
                        },
                        'type': 'sendMessage',
                        'text' : 'dua puluh lima ribu'
                      },
                      'action4': {
                        'params': {
                            'text': 'lima puluh ribu'
                        },
                        'type': 'sendMessage',
                        'text' : 'lima puluh ribu'
                      },
                      'action5': {
                        'params': {
                            'text': 'seratus ribu'
                        },
                        'type': 'sendMessage',
                        'text' : 'seratus ribu'
                      }

                  },
                  'images': {
                      'image1': {
                         'h': 701,
                          'w': 1040,
                          'y': 0,
                          'x': 0
                       }
                  },
                  'canvas': {
                      'height': 701,
                      'width': 1040,
                      'initialScene': 'scene1'
                  }
        }
        return markup_json

    def send_rich_message_pulsa_hp_text(self, recipient_id, image_url, alt_text, message):
        markup_json = json.dumps(self.set_markup_pulsa_hp())	
        payload = {
                    'to':[recipient_id],
                    'toChannel':1383378250,
                    'eventType':'140177271400161403',
                    'content':{
                                'messageNotified': 0,
                                'messages': [
                                               {
                                                   'contentType': 1,
                                                   'text': message
                                               },
                                               {
                                                   'contentType':12,
                                                   'toType':1,
                                                   'contentMetadata': {
								                       'SPEC_REV':'1',
                                                       'DOWNLOAD_URL': image_url,
                                                       'ALT_TEXT': alt_text,
                                                       'MARKUP_JSON': markup_json

								                   }               
                                               }
                                            ]
                              }
                  }	              
	print "pulsa"
	hasil = self.send_payload_new(payload)
	print hasil
        return hasil			
		
    def set_markup_token_pln(self):
        markup_json = {
                    'scenes': {
                       'scene1': {
                          'listeners': [
                              {
                                 'type': 'touch',
                                 'action': 'action0',
                                 'params': [0, 0, 345, 235]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action1',
                                 'params': [345, 0, 692, 235]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action2',
                                 'params': [692, 0, 1040, 235]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action3',
                                 'params': [0, 235, 345, 467]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action4',
                                 'params': [345, 235, 692, 467]
                              },		
                              {
                                 'type': 'touch',
                                 'action': 'action5',
                                 'params': [692, 235, 1040, 467]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action6',
                                 'params': [0, 467, 345, 701]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action7',
                                 'params': [345, 467, 692, 701]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action8',
                                 'params': [692, 467, 1040, 701]
                              }								  
                           ],
                         'draws': [
                              {
                                 'h': 701,
                                 'w': 1040,
                                 'y': 0,
                                 'x': 0,
                                 'image': 'image1'
                              }
                          ]
                      }
                   },
                   'actions': {
                      'action0': {
                        'params': {
                            'text': 'dua puluh'
                        },
                        'type': 'sendMessage',
                        'text' : 'dua puluh'
                      },
                      'action1': {
                        'params': {
                            'text': 'lima puluh'
                        },
                        'type': 'sendMessage',
                        'text' : 'lima puluh'
                      },
                      'action2': {
                        'params': {
                            'text': 'seratus'
                        },
                        'type': 'sendMessage',
                        'text' : 'seratus'
                      },
                      'action3': {
                        'params': {
                            'text': 'dua ratus'
                        },
                        'type': 'sendMessage',
                        'text' : 'dua ratus'
                      },
                      'action4': {
                        'params': {
                            'text': 'lima ratus'
                        },
                        'type': 'sendMessage',
                        'text' : 'lima ratus'
                      },
                      'action5': {
                        'params': {
                            'text': 'sejuta'
                        },
                        'type': 'sendMessage',
                        'text' : 'sejuta'
                      },
                      'action6': {
                        'params': {
                            'text': 'lima juta'
                        },
                        'type': 'sendMessage',
                        'text' : 'lima juta'
                      },
                      'action7': {
                        'params': {
                            'text': 'sepuluh juta'
                        },
                        'type': 'sendMessage',
                        'text' : 'sepuluh juta'
                      },
                      'action8': {
                        'params': {
                            'text': 'lima puluh juta'
                        },
                        'type': 'sendMessage',
                        'text' : 'lima puluh juta'
                      }							  
                  },
                  'images': {
                      'image1': {
                          'h': 701,
                          'w': 1040,
                          'y': 0,
                          'x': 0
                       }
                  },
                  'canvas': {
                      'height': 701,
                      'width': 1040,
                      'initialScene': 'scene1'
                  }
        }
        return markup_json

    def send_rich_message_token_pln_text(self, recipient_id, image_url, alt_text, message):
        markup_json = json.dumps(self.set_markup_token_pln())	
        payload = {
                    'to':[recipient_id],
                    'toChannel':1383378250,
                    'eventType':'140177271400161403',
                    'content':{
                                'messageNotified': 0,
                                'messages': [
                                               {
                                                   'contentType': 1,
                                                   'text': message
                                               },
                                               {
                                                   'contentType':12,
                                                   'toType':1,
                                                   'contentMetadata': {
								                       'SPEC_REV':'1',
                                                       'DOWNLOAD_URL': image_url,
                                                       'ALT_TEXT': alt_text,
                                                       'MARKUP_JSON': markup_json

								                   }               
                                               }
                                            ]
                              }
                  }	              
        return self._send_payload(payload)	


		
    def set_markup_payment_tiketdotcom(self):
        markup_json = {
                    'scenes': {
                       'scene1': {
                          'listeners': [
                              {
                                 'type': 'touch',
                                 'action': 'action0',
                                 'params': [0, 0, 346, 230]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action1',
                                 'params': [346, 0, 692, 230]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action2',
                                 'params': [692, 0, 1040, 230]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action3',
                                 'params': [0, 230, 346, 466]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action4',
                                 'params': [346, 230, 692, 466]
                              },	
                              {
                                 'type': 'touch',
                                 'action': 'action5',
                                 'params': [692, 230, 1040, 466]
                              }								  
                           ],
                         'draws': [
                              {
                                 'h': 466,
                                 'w': 1040,
                                 'y': 0,
                                 'x': 0,
                                 'image': 'image1'
                              }
                          ]
                      }
                   },
                   'actions': {
                      'action0': {
                        'params': {
                            'text': 'atm'
                        },
                        'type': 'sendMessage',
                        'text' : 'atm'
                      },
                      'action1': {
                        'params': {
                            'text': 'mandiri clickpay'
                        },
                        'type': 'sendMessage',
                        'text' : 'mandiri clickpay'
                      },
                      'action2': {
                        'params': {
                            'text': 'cimb clicks'
                        },
                        'type': 'sendMessage',
                        'text' : 'cimb clicks'
                      },
                      'action3': {
                        'params': {
                            'text': 'kartu kredit'
                        },
                        'type': 'sendMessage',
                        'text' : 'kartu kredit'
                      },
                      'action4': {
                        'params': {
                            'text': 'kartu kredit'
                        },
                        'type': 'sendMessage',
                        'text' : 'kartu kredit'
                      },	
                      'action5': {
                        'params': {
                            'text': 'bca klikpay'
                        },
                        'type': 'sendMessage',
                        'text' : 'bca klikpay'
                      }					  
                  },
                  'images': {
                      'image1': {
                          'h': 466,
                          'w': 1040,
                          'y': 0,
                          'x': 0
                       }
                  },
                  'canvas': {
                      'height': 500,
                      'width': 1040,
                      'initialScene': 'scene1'
                  }
        }
        return markup_json
		
    def send_rich_message_payment_tiketdotcom(self, recipient_id, image_url, alt_text):
        markup_json = json.dumps(self.set_markup_payment_tiketdotcom())
        payload = {
                    'to':[recipient_id],
                    'toChannel':1383378250,
                    'eventType':'138311608800106203',
                    'content':{
                                 'contentType':12,
                                 'toType':1,
                                 'contentMetadata': {
								    'SPEC_REV':'1',
                                    'DOWNLOAD_URL': image_url,
                                    'ALT_TEXT': alt_text,
                                    'MARKUP_JSON': markup_json
								 
								 
								 
								 }
								 
                              }
                  }	  
        return self._send_payload(payload) 		

    def send_rich_message_payment_tiketdotcom_text(self, recipient_id, image_url, alt_text, message):
        markup_json = json.dumps(self.set_markup_payment_tiketdotcom())	
        payload = {
                    'to':[recipient_id],
                    'toChannel':1383378250,
                    'eventType':'140177271400161403',
                    'content':{
                                'messageNotified': 0,
                                'messages': [
                                               {
                                                   'contentType': 1,
                                                   'text': message
                                               },
                                               {
                                                   'contentType':12,
                                                   'toType':1,
                                                   'contentMetadata': {
								                       'SPEC_REV':'1',
                                                       'DOWNLOAD_URL': image_url,
                                                       'ALT_TEXT': alt_text,
                                                       'MARKUP_JSON': markup_json

								                   }               
                                               }
                                            ]
                              }
                  }	              
        return self._send_payload(payload)				

    def set_markup_payment_tiketux(self):
        markup_json = {
                    'scenes': {
                       'scene1': {
                          'listeners': [
                              {
                                 'type': 'touch',
                                 'action': 'action0',
                                 'params': [0, 0, 347, 232]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action1',
                                 'params': [347, 0, 692, 232]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action2',
                                 'params': [692, 0, 1040, 232]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action3',
                                 'params': [0, 232, 347, 463]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action4',
                                 'params': [347, 232, 692, 463]
                              },		
                              {
                                 'type': 'touch',
                                 'action': 'action5',
                                 'params': [692, 232, 1040, 463]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action6',
                                 'params': [0, 463, 347, 701]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action7',
                                 'params': [347, 463, 692, 701]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action8',
                                 'params': [692, 463, 1040, 701]
                              }								  
                           ],
                         'draws': [
                              {
                                 'h': 701,
                                 'w': 1040,
                                 'y': 0,
                                 'x': 0,
                                 'image': 'image1'
                              }
                          ]
                      }
                   },
                   'actions': {
                      'action0': {
                        'params': {
                            'text': 'atm'
                        },
                        'type': 'sendMessage',
                        'text' : 'atm'
                      },
                      'action1': {
                        'params': {
                            'text': 'kartu kredit'
                        },
                        'type': 'sendMessage',
                        'text' : 'kartu kredit'
                      },
                      'action2': {
                        'params': {
                            'text': 'cimb clicks'
                        },
                        'type': 'sendMessage',
                        'text' : 'cimb clicks'
                      },
                      'action3': {
                        'params': {
                            'text': 'mandiri ecash'
                        },
                        'type': 'sendMessage',
                        'text' : 'mandiri ecash'
                      },
                      'action4': {
                        'params': {
                            'text': 'mandiri clickpay'
                        },
                        'type': 'sendMessage',
                        'text' : 'mandiri clickpay'
                      },		
                      'action5': {
                        'params': {
                            'text': 'bca klikpay'
                        },
                        'type': 'sendMessage',
                        'text' : 'bca klikpay'
                      },
                      'action6': {
                        'params': {
                            'text': 'tcash'
                        },
                        'type': 'sendMessage',
                        'text' : 'tcash'
                      },
                      'action7': {
                        'params': {
                            'text': 'xl tunai'
                        },
                        'type': 'sendMessage',
                        'text' : 'xl tunai'
                      },
                      'action8': {
                        'params': {
                            'text': 'indomaret'
                        },
                        'type': 'sendMessage',
                        'text' : 'indomaret'
                      }						  
                  },
                  'images': {
                      'image1': {
                          'h': 701,
                          'w': 1040,
                          'y': 0,
                          'x': 0
                       }
                  },
                  'canvas': {
                      'height': 701,
                      'width': 1040,
                      'initialScene': 'scene1'
                  }
        }
        return markup_json
		
    def send_rich_message_payment_tiketux(self, recipient_id, image_url, alt_text):
        markup_json = json.dumps(self.set_markup_payment_tiketux())
        payload = {
                    'to':[recipient_id],
                    'toChannel':1383378250,
                    'eventType':'138311608800106203',
                    'content':{
                                 'contentType':12,
                                 'toType':1,
                                 'contentMetadata': {
								    'SPEC_REV':'1',
                                    'DOWNLOAD_URL': image_url,
                                    'ALT_TEXT': alt_text,
                                    'MARKUP_JSON': markup_json
								 
								 
								 
								 }
								 
                              }
                  }	  
        return self._send_payload(payload) 						 
				 
    def send_rich_message_payment_tiketux_text(self, recipient_id, image_url, alt_text, message):
        markup_json = json.dumps(self.set_markup_payment_tiketux())	
        payload = {
                    'to':[recipient_id],
                    'toChannel':1383378250,
                    'eventType':'140177271400161403',
                    'content':{
                                'messageNotified': 0,
                                'messages': [
                                               {
                                                   'contentType': 1,
                                                   'text': message
                                               },
                                               {
                                                   'contentType':12,
                                                   'toType':1,
                                                   'contentMetadata': {
								                       'SPEC_REV':'1',
                                                       'DOWNLOAD_URL': image_url,
                                                       'ALT_TEXT': alt_text,
                                                       'MARKUP_JSON': markup_json

								                   }               
                                               }
                                            ]
                              }
                  }	              
        return self._send_payload(payload)	
		
		
		
    def set_markup_greeting(self):
        markup_json = {
                    'scenes': {
                       'scene1': {
                          'listeners': [
                              {
                                 'type': 'touch',
                                 'action': 'action0',
                                 'params': [0, 0, 345, 238]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action1',
                                 'params': [345, 0, 690, 238]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action2',
                                 'params': [690, 0, 1040, 238]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action3',
                                 'params': [0, 238, 345, 470]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action4',
                                 'params': [345, 238, 690, 470]
                              },		
                              {
                                 'type': 'touch',
                                 'action': 'action5',
                                 'params': [690, 238, 1040, 470]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action6',
                                 'params': [0, 470, 345, 700]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action7',
                                 'params': [345, 470, 690, 700]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action8',
                                 'params': [690, 470, 1040, 700]
                              },		
                              {
                                 'type': 'touch',
                                 'action': 'action9',
                                 'params': [0, 700, 345, 937]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action10',
                                 'params': [345, 700, 690, 937]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action11',
                                 'params': [690, 700, 1040, 937]
                              }								  
                           ],
                         'draws': [
                              {
                                 'h': 937,
                                 'w': 1040,
                                 'y': 0,
                                 'x': 0,
                                 'image': 'image1'
                              }
                          ]
                      }
                   },
                   'actions': {
                      'action0': {
                        'params': {
                            'text': 'pesawat'
                        },
                        'type': 'sendMessage',
                        'text' : 'pesawat'
                      },
                      'action1': {
                        'params': {
                            'text': 'kereta api'
                        },
                        'type': 'sendMessage',
                        'text' : 'kereta api'
                      },
                      'action2': {
                        'params': {
                            'text': 'xtrans'
                        },
                        'type': 'sendMessage',
                        'text' : 'xtrans'
                      },
                      'action3': {
                        'params': {
                            'text': 'uber'
                        },
                        'type': 'sendMessage',
                        'text' : 'uber'
                      },
                      'action4': {
                        'params': {
                            'text': 'info restoran'
                        },
                        'type': 'sendMessage',
                        'text' : 'info restoran'
                      },		
                      'action5': {
                        'params': {
                            'text': 'jalan tol'
                        },
                        'type': 'sendMessage',
                        'text' : 'jalan tol'
                      },
                      'action6': {
                        'params': {
                            'text': 'cuaca'
                        },
                        'type': 'sendMessage',
                        'text' : 'cuaca'
                      },
                      'action7': {
                        'params': {
                            'text': 'ingetin'
                        },
                        'type': 'sendMessage',
                        'text' : 'ingetin'
                      },
                      'action8': {
                        'params': {
                            'text': 'token pln'
                        },
                        'type': 'sendMessage',
                        'text' : 'token pln'
                      },
                      'action9': {
                        'params': {
                            'text': 'pulsa'
                        },
                        'type': 'sendMessage',
                        'text' : 'pulsa'
                      },
                      'action10': {
                        'params': {
                            'text': 'terjemahin'
                        },
                        'type': 'sendMessage',
                        'text' : 'terjemahin'
                      },
                      'action11': {
                        'params': {
                            'text': 'bantuan'
                        },
                        'type': 'sendMessage',
                        'text' : 'bantuan'
                      }							  
                  },
                  'images': {
                      'image1': {
                          'h': 937,
                          'w': 1040,
                          'y': 0,
                          'x': 0
                       }
                  },
                  'canvas': {
                      'height': 937,
                      'width': 1040,
                      'initialScene': 'scene1'
                  }
        }
        return markup_json
		
    def send_rich_message_greeting(self, recipient_id, image_url, alt_text):
        markup_json = json.dumps(self.set_markup_greeting())
        payload = {
                    'to':[recipient_id],
                    'toChannel':1383378250,
                    'eventType':'138311608800106203',
                    'content':{
                                 'contentType':12,
                                 'toType':1,
                                 'contentMetadata': {
								    'SPEC_REV':'1',
                                    'DOWNLOAD_URL': image_url,
                                    'ALT_TEXT': alt_text,
                                    'MARKUP_JSON': markup_json
								 
								 
								 
								 }
								 
                              }
                  }	  
        return self._send_payload(payload) 						 
				 
    def send_rich_message_greeting_text(self, recipient_id, image_url, alt_text, message):
        markup_json = json.dumps(self.set_markup_greeting())	
        payload = {
                    'to':[recipient_id],
                    'toChannel':1383378250,
                    'eventType':'140177271400161403',
                    'content':{
                                'messageNotified': 0,
                                'messages': [
                                               {
                                                   'contentType': 1,
                                                   'text': message
                                               },
                                               {
                                                   'contentType':12,
                                                   'toType':1,
                                                   'contentMetadata': {
								                       'SPEC_REV':'1',
                                                       'DOWNLOAD_URL': image_url,
                                                       'ALT_TEXT': alt_text,
                                                       'MARKUP_JSON': markup_json

								                   }               
                                               }
                                            ]
                              }
                  }	              
        return self._send_payload(payload)			

    def send_image(self, recipient_id, image_path):
        '''
            This sends an image to the specified recipient.
            Input:
              recipient_id: recipient id to send to
              image_path: path to image to be sent
            Output:
              Response from API as <dict>
        '''
        payload = {
            'recipient': json.dumps(
                {
                    'id': recipient_id
                }
            ),
            'message': json.dumps(
                {
                    'attachment': {
                        'type': 'image',
                        'payload': {}
                    }
                }
            ),
            'filedata': (image_path, open(image_path, 'rb'))
        }
        multipart_data = MultipartEncoder(payload)
        multipart_header = {
            'Content-Type': multipart_data.content_type
        }
        return requests.post(self.base_url, data=multipart_data, headers=multipart_header).json()

    def set_markup_dwp_discount(self):
        markup_json = {
                    'scenes': {
                       'scene1': {
                          'listeners': [
                              {
                                 'type': 'touch',
                                 'action': 'action0',
                                 'params': [0, 0, 520, 344]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action1',
                                 'params': [520, 0, 1040, 344]
                              }
                           ],
                         'draws': [
                              {
                                 'h': 344,
                                 'w': 1040,
                                 'y': 0,
                                 'x': 0,
                                 'image': 'image1'
                              }
                          ]
                      }
                   },
                   'actions': {
                      'action0': {
                        'params': {
                            'text': 'buy 5 get 1 free'
                        },
                        'type': 'sendMessage',
                        'text' : 'buy 5 get 1 free'
                      },
                      'action1': {
                        'params': {
                            'text': 'buy 1 disc 15'
                        },
                        'type': 'sendMessage',
                        'text' : 'buy 1 disc 15'
                      }
                  },
                  'images': {
                      'image1': {
                          'h': 344,
                          'w': 1040,
                          'y': 0,
                          'x': 0
                       }
                  },
                  'canvas': {
                      'height': 344,
                      'width': 1040,
                      'initialScene': 'scene1'
                  }
        }
        return markup_json

    def send_rich_message_dwp_discount(self, recipient_id, image_url, alt_text):
            markup_json = json.dumps(self.set_markup_dwp_discount())
            payload = {
                'to': [recipient_id],
                'toChannel': 1383378250,
                'eventType': '138311608800106203',
                'content': {
                    'contentType': 12,
                    'toType': 1,
                    'contentMetadata': {
                        'SPEC_REV': '1',
                        'DOWNLOAD_URL': "http://bangjoni.com/dwp_images/dwp_disc",
                        'ALT_TEXT': "DWP Discount",
                        'MARKUP_JSON': markup_json
                    }
                }
            }
            return self._send_payload(payload)

    def set_markup_dwp_tickets(self):
        markup_json = {
                    'scenes': {
                       'scene1': {
                          'listeners': [
                              {
                                 'type': 'touch',
                                 'action': 'action0',
                                 'params': [0, 0, 344, 343]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action1',
                                 'params': [344, 0, 692, 343]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action2',
                                 'params': [692, 0, 1040, 343]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action3',
                                 'params': [0, 343, 344, 500]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action4',
                                 'params': [344, 343, 692, 500]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action5',
                                 'params': [692, 343, 1040, 500]
                              }
                           ],
                         'draws': [
                              {
                                 'h': 687,
                                 'w': 1040,
                                 'y': 0,
                                 'x': 0,
                                 'image': 'image1'
                              }
                          ]
                      }
                   },
                   'actions': {
                      'action0': {
                        'params': {
                            'text': 'vip day 1'
                        },
                        'type': 'sendMessage',
                        'text' : 'vip day 1'
                      },
                      'action1': {
                        'params': {
                            'text': 'vip day 2'
                        },
                        'type': 'sendMessage',
                        'text' : 'vip day 2'
                      },
                      'action2': {
                        'params': {
                            'text': 'vip 2 day'
                        },
                        'type': 'sendMessage',
                        'text' : 'vip 2 day'
                      },
                      'action3': {
                        'params': {
                            'text': 'general day 1'
                        },
                        'type': 'sendMessage',
                        'text' : 'general day 1'
                      },
                      'action4': {
                        'params': {
                            'text': 'general day 2'
                        },
                        'type': 'sendMessage',
                        'text' : 'general day 2'
                      },
                      'action5': {
                        'params': {
                            'text': 'general 2 day'
                        },
                        'type': 'sendMessage',
                        'text' : 'general 2 day'
                      }
                  },
                  'images': {
                      'image1': {
                          'h': 687,
                          'w': 1040,
                          'y': 0,
                          'x': 0
                       }
                  },
                  'canvas': {
                      'height': 687,
                      'width': 1040,
                      'initialScene': 'scene1'
                  }
        }
        return markup_json

    def send_rich_message_dwp_tickets(self, recipient_id, image_url, alt_text):
            markup_json = json.dumps(self.set_markup_dwp_tickets())
            payload = {
                'to': [recipient_id],
                'toChannel': 1383378250,
                'eventType': '138311608800106203',
                'content': {
                    'contentType': 12,
                    'toType': 1,
                    'contentMetadata': {
                        'SPEC_REV': '1',
                        'DOWNLOAD_URL': image_url,
                        'ALT_TEXT': alt_text,
                        'MARKUP_JSON': markup_json

                    }

                }
            }
            return self._send_payload(payload)

			
######

    def set_markup_bjpay_register(self):
        markup_json = {
                    'scenes': {
                       'scene1': {
                          'listeners': [
                              {
                                 'type': 'touch',
                                 'action': 'action0',
                                 'params': [0, 0, 1040, 466]
                              }

                           ],
                         'draws': [
                              {
                                 'h': 466,
                                 'w': 1040,
                                 'y': 0,
                                 'x': 0,
                                 'image': 'image1'
                              }
                          ]
                      }
                   },
                   'actions': {
                      'action0': {
                        'params': {
                            'text': 'bjpay register'
                        },
                        'type': 'sendMessage',
                        'text' : 'bjpay register'
                      }

                  },
                  'images': {
                      'image1': {
                          'h': 466,
                          'w': 1040,
                          'y': 0,
                          'x': 0
                       }
                  },
                  'canvas': {
                      'height': 466,
                      'width': 1040,
                      'initialScene': 'scene1'
                  }
        }
        return markup_json
		
    def send_rich_message_bjpay_register(self, recipient_id, image_url, alt_text):
        markup_json = json.dumps(self.set_markup_bjpay_register())
        payload = {
                    'to':[recipient_id],
                    'toChannel':1383378250,
                    'eventType':'138311608800106203',
                    'content':{
                                 'contentType':12,
                                 'toType':1,
                                 'contentMetadata': {
								    'SPEC_REV':'1',
                                    'DOWNLOAD_URL': image_url,
                                    'ALT_TEXT': alt_text,
                                    'MARKUP_JSON': markup_json
								 
								 
								 
								 }
								 
                              }
                  }	  
        return self._send_payload(payload) 						 
				 
    def send_rich_message_bjpay_register_text(self, recipient_id, image_url, alt_text, message):
        markup_json = json.dumps(self.set_markup_bjpay_register())	
        payload = {
                    'to':[recipient_id],
                    'toChannel':1383378250,
                    'eventType':'140177271400161403',
                    'content':{
                                'messageNotified': 0,
                                'messages': [
                                               {
                                                   'contentType': 1,
                                                   'text': message
                                               },
                                               {
                                                   'contentType':12,
                                                   'toType':1,
                                                   'contentMetadata': {
								                       'SPEC_REV':'1',
                                                       'DOWNLOAD_URL': image_url,
                                                       'ALT_TEXT': alt_text,
                                                       'MARKUP_JSON': markup_json

								                   }               
                                               }
                                            ]
                              }
                  }	              
        return self._send_payload(payload)				
		
		
    def set_markup_bjpay_deposit(self):
        markup_json = {
                    'scenes': {
                       'scene1': {
                          'listeners': [
                              {
                                 'type': 'touch',
                                 'action': 'action0',
                                 'params': [0, 0, 346, 466]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action1',
                                 'params': [346, 0, 693, 466]
                              },
                              {
                                 'type': 'touch',
                                 'action': 'action2',
                                 'params': [693, 0, 1040, 466]
                              }
                           ],
                         'draws': [
                              {
                                 'h': 466,
                                 'w': 1040,
                                 'y': 0,
                                 'x': 0,
                                 'image': 'image1'
                              }
                          ]
                      }
                   },
                   'actions': {
                      'action0': {
                        'params': {
                            'text': 'va permata'
                        },
                        'type': 'sendMessage',
                        'text' : 'va permata'
                      },
                      'action1': {
                        'params': {
                            'text': 'transfer mandiri'
                        },
                        'type': 'sendMessage',
                        'text' : 'transfer mandiri'
                      },
                      'action2': {
                        'params': {
                            'text': 'transfer bca'
                        },
                        'type': 'sendMessage',
                        'text' : 'transfer bca'
                      }
                  },
                  'images': {
                      'image1': {
                          'h': 466,
                          'w': 1040,
                          'y': 0,
                          'x': 0
                       }
                  },
                  'canvas': {
                      'height': 466,
                      'width': 1040,
                      'initialScene': 'scene1'
                  }
        }
        return markup_json
		
    def send_rich_message_bjpay_deposit(self, recipient_id, image_url, alt_text):
        markup_json = json.dumps(self.set_markup_bjpay_deposit())
        payload = {
                    'to':[recipient_id],
                    'toChannel':1383378250,
                    'eventType':'138311608800106203',
                    'content':{
                                 'contentType':12,
                                 'toType':1,
                                 'contentMetadata': {
								    'SPEC_REV':'1',
                                    'DOWNLOAD_URL': image_url,
                                    'ALT_TEXT': alt_text,
                                    'MARKUP_JSON': markup_json
								 
								 
								 
								 }
								 
                              }
                  }	  
        return self._send_payload(payload) 						 
				 
    def send_rich_message_bjpay_deposit_text(self, recipient_id, image_url, alt_text, message):
        markup_json = json.dumps(self.set_markup_bjpay_deposit())	
        payload = {
                    'to':[recipient_id],
                    'toChannel':1383378250,
                    'eventType':'140177271400161403',
                    'content':{
                                'messageNotified': 0,
                                'messages': [
                                               {
                                                   'contentType': 1,
                                                   'text': message
                                               },
                                               {
                                                   'contentType':12,
                                                   'toType':1,
                                                   'contentMetadata': {
								                       'SPEC_REV':'1',
                                                       'DOWNLOAD_URL': image_url,
                                                       'ALT_TEXT': alt_text,
                                                       'MARKUP_JSON': markup_json

								                   }               
                                               }
                                            ]
                              }
                  }	              
        return self._send_payload(payload)			