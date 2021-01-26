import datetime
import pyautogui
import time
import pyperclip
import keyboard
import requests
from lib.image.compare import Compare
from lib.image.process import Process
from lib.image.recognize import Recognize
from lib.vk.api import Api
from lib.vk.auth import Auth
import winsound
import re


def main():
    
    def sound():
        try:
            winsound.PlaySound("sound.mp3", winsound.SND_ASYNC | winsound.SND_ALIAS)
        except:
            print('can`t find sound file for notification! Please, put it in the same directory with name "sound.mp3"')

    def set_clipboard(string: str):
        pyperclip.copy(string)

    # insert your login and password
    login = ''
    password = ''

    hotkey = 'F2'  # your hotkey

    group_id = -190337559 # insert group id here

    auth = Auth()
    print('authorize vk account...')
    token = auth.get_token(login=login, password=password)
    print('authorized')

    api = Api(token)
    http = requests.session()

    comp = Compare()
    print('loading font...')
    comp.load_font()
    print('script is activated')
    proc = Process()
    recog = Recognize(process=proc, compare=comp)
    lastId = 0
    lock = False

    def check():
        nonlocal lock
        nonlocal group_id
        nonlocal lastId
        if not lock:
            lock = True
            now = datetime.datetime.now()
            current_time = (now.hour, now.minute)
            old_time = time.time()
            print('getting last post...')
            posts = api.get_posts(group_id, 1)
            last_post = posts[0] if 'is_pinned' not in posts[0] else posts[1]
            attachments = False
            if last_post['id'] != lastId:
                try:
                    attachments = last_post['attachments']
                except:
                    attachments = False
                if not attachments or 'photo' not in attachments[0]:
                    print('There is post, but where is picture?')
                    lastId = last_post['id']
                else:
                    symb = ''
                    chsymb = ''
                    text = last_post['text']
                    image_obj = attachments[0]['photo']
                    image_url = image_obj['sizes'][-1]['url']
                    image_bytes = http.get(image_url).content
                    image = recog.create_image(image_bytes)
                    try:
                        old_time = time.time()
                        ar = re.findall(r'([0123456789-]+[+-/*]\d+=.) \(напиши цифру вместо "."\)', text)
                        ar2 = re.findall(r'Напиши "(.)" вместо "(.)"', text)
                        if ar:
                            symb = ar[0][-1]
                            if '+' in ar[0] and '+' != ar[0][-1] :
                                a = int(ar[0].split('+')[0])
                                b = int(ar[0].split('+')[1].split('=')[0])
                                chsymb = str(a+b)
                            elif '/' in ar[0] and '/' != ar[0][-1]:
                                a = int(ar[0].split('/')[0])
                                b = int(ar[0].split('/')[1].split('=')[0])
                                chsymb = str(a/b)
                            elif '*' in ar[0] and '*' != ar[0][-1]:
                                a = int(ar[0].split('*')[0])
                                b = int(ar[0].split('*')[1].split('=')[0])
                                chsymb = str(a*b)
                            elif '-' in ar[0] and '-' != ar[0][-1] :
                                if '-' != ar[0][0]:
                                    a = int(ar[0].split('-')[0])
                                    b = int(ar[0].split('-')[1].split('=')[0])
                                    chsymb = str(a-b)
                                else:
                                    a = int(ar[0].split('-')[1])
                                    b = int(ar[0].split('-')[2].split('=')[0])
                                    chsymb = str(a-b)
                        elif ar2:
                            chsymb, symb = ar2[0]
                        else:
                            symb = text[text.find('"') + 1]
                            chsymb = recog.get_num(image)
                            if len(str(chsymb)) > 1:
                                if re.match('^[7]*[^7][7]*$', chsymb):
                                    chsymb = chsymb.replace('7', '')
                                else:
                                    chsymb = '7'
                        code = recog.get_code(image)
                        code = code.replace(symb, chsymb)
                        print(f'recognise took {round(time.time() - old_time, 1)} sec')
                        print('code:', code)
                        print("Символ '{0}' изменен на '{1}'".format(symb, chsymb))
                        set_clipboard(code)
                        sound()
                        pyautogui.press('f1')
                        lastId = last_post['id']
                    except Exception as e:
                        print('something went wrong. Maybe it`s not voucher?')
                        print(e)
                        lastId = last_post['id']
            lock = False

    #keyboard.add_hotkey(hotkey, check)
    print('Запущен цикл проверки поста, интервал: 0.1 секунд')
    while True:
        check()
        time.sleep(0)


if __name__ == "__main__":
    main()
