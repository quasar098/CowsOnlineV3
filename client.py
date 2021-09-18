import _thread
import os
from random import randint as rand
from random import choice
from numpy import clip as clamp
from numpy import sin, cos
from pygameinfo import *
from time import sleep as wait
from json import loads, dumps
import socket

fps = 75
tick = 0
width = 1280
height = 720
pygame.init()
pyclock = pygame.time.Clock()
screen = pygame.display.set_mode([width, height])
pygame.display.set_caption('Cows Online (v3) by quasar098')
font = pygame.font.SysFont('Calibri', 40)
pygameinfofont = pygame.font.SysFont('Arial', 20)
cardstorage = {'nullcard': pygame.image.load('nullcard.png').convert_alpha()}  # path: img
screenstage = 'menu'

connecting = False
istypingname = False
istypingip = False
isselectingcard = False
name = ''
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
online = False
CardSendData = {}
updatethedata = False
other_data = {}
raw_data = {}
viewing_deck = name


def getsurf(path_, size=None):
    # noinspection PyBroadException
    try:
        if not cardstorage.__contains__(path_):  # not registered
            cardstorage[path_] = pygame.image.load(path_).convert_alpha()
        if size is not None:
            surf__ = pygame.transform.scale(cardstorage[path_], size)
        else:
            surf__ = cardstorage[path_]
        return surf__.copy()
    except Exception:
        return cardstorage['nullcard']


def getpath(name_):
    if GetCardPath.__contains__(name_):
        return GetCardPath[name_]
    else:
        return 'nullcard'


savedtext = {}


def gametext(text, color=(0, 0, 0), font_=font):
    text: str
    color: (int or float, int or float, int or float)
    if not savedtext.__contains__(text+str(color)):
        savedtext[text+str(color)] = font_.render(text, True, color)
    return savedtext[text+str(color)]


def is_hover(mouse_loc, loc1, loc2):
    if loc1[0] < mouse_loc[0] < loc2[0]:
        if loc1[1] < mouse_loc[1] < loc2[1]:
            return True
    return False


class Card:
    def __init__(self, nameofcard, loc=(width/2-83, 10), id1=None, enteranim=0):
        if nameofcard == '.random':
            nameofcard = getrandomcard()
        self.name = nameofcard
        self.loc = loc
        if id1 is None:
            id1 = str(rand(0, 999999)) + 'abcdef'[rand(0, 5)]
        self.id = id1
        self.counter = 0
        # animations
        self.handanim = 0
        self.enteranim = enteranim
        self.exitanim = 0
        self.exitanimgoto = 0

    def draw(self, hidehand=False):
        if self.handanim > 0:
            if hidehand:
                return
        cardpath_ = getpath(self.name)
        _surf = getsurf(cardpath_)
        _surf = pygame.transform.scale(_surf, (166, 216))
        anim = self.handanim
        outrect = self.get_rect()
        if self.id in Hand:
            self.handanim = (self.handanim*4 + 5)/5
        else:
            self.handanim = (self.handanim*4-2)/5
        # noinspection PyShadowingNames
        x = self.loc[0]
        self.enteranim /= 1.1
        self.exitanim = (self.exitanim*8+self.exitanimgoto)/9
        grab = 0
        if self.id == grab_id:
            grab = 10
        grabcolour = (clamp(-cos(tick/fps*4+x/500)*90+140, 50, 255), clamp(-sin(tick/fps*4+x/500)*90+140, 50, 255),
                      clamp(cos(tick/fps*4+x/500)*90+140, 50, 255))
        grabrect = (outrect[0]-anim-grab, outrect[1]-anim-self.enteranim-self.exitanim-grab, 167+anim*2, 217+anim*2)
        pygame.draw.rect(screen, grabcolour,
                         grabrect,
                         border_radius=17)
        screen.blit(_surf, (self.loc[0]-grab, self.loc[1]-self.enteranim-self.exitanim-grab))
        if self.counter != 0:  # display counter
            counterloc = (self.loc[0]-grab+83, self.loc[1]-self.enteranim-self.exitanim-grab+216)
            squaresurface = pygame.Surface((35, 45)).convert_alpha()
            pygame.draw.rect(squaresurface, (20, 20, 20, 120), (0, 0, 35, 45))
            screen.blit(squaresurface, squaresurface.get_rect(midbottom=counterloc))
            countertextloc = squaresurface.get_rect(midbottom=counterloc).center
            screen.blit(gametext(str(card.counter), (255, 255, 255)),
                        gametext(str(card.counter), (255, 255, 255)).get_rect(center=countertextloc))

    def get_rect(self):
        return self.loc[0], self.loc[1], self.loc[0]+166, self.loc[1]+216

    def unpack(self, box):
        self.name = box['name']
        self.loc = box['loc']
        self.id = box['id']
        self.handanim = box['handanim']
        self.exitanim = box['exitanim']
        self.enteranim = box['enteranim']
        self.counter = box['counter']
        return self

    def pack(self):
        return {'name': self.name, 'loc': self.loc, 'id': self.id, 'handanim': self.handanim, 'exitanim': self.exitanim, 'enteranim': self.enteranim,
                'counter': self.counter}


rarities = {}
shufflerandom = []
with open('cardrarities.txt', 'r') as file:
    for rarity in file.read().split('\n'):
        beforestring = ''
        afterstring = ''
        after = False
        for letter in rarity:
            if after:
                afterstring += letter
            else:
                if letter == '=':
                    after = True
                else:
                    beforestring += letter
        if not afterstring.isnumeric():
            continue
        afterstring = int(afterstring)
        rarities[beforestring] = afterstring
for rarity in rarities:
    for i in range(rarities[rarity]):
        shufflerandom.append(rarity)
shufflerandom.reverse()


def getrandomcard():
    return choice(shufflerandom)


ip = ""


def connect_thread():
    global connecting
    global online
    global screenstage
    global s
    add_info_text('Attempting to connect to server...', pygameinfofont, fps)
    connecting = True
    wait(0.1)
    try:
        int_ip = ip
        if int_ip == 'localhost':
            int_ip = "127.0.0.1"
        elif int_ip == 'dev':
            int_ip = '192.168.1.13'
        s.connect((int_ip, 25565))
        screenstage = 'play'
        add_info_text('Connection Succesful', pygameinfofont, fps)
        online = True
    except WindowsError as errno:
        online = False
        if errno.errno == 10061:
            add_info_text('(Server Offline)', pygameinfofont, fps)
        add_info_text('Connection Failed', pygameinfofont, fps)
    finally:
        connecting = False


def packet_thread():
    global CardSendData
    global raw_data
    while True:
        if not online:
            wait(1/fps)
        else:
            # noinspection PyShadowingNames
            CardSendData = [card.pack() for card in CardsInField if card not in Hand]
            # noinspection PyShadowingNames
            for currency in CurrenciesAmount:
                # noinspection PyUnresolvedReferences
                CurrenciesAmount[currency] = int(CurrenciesAmount[currency])
            s.sendall(bytes(dumps({'currencies': CurrenciesAmount, 'field': CardSendData, 'name': name}), encoding='utf8'))
            raw_data = loads(s.recv(65536))
            while True:
                wait(0.25/fps)
                if updatethedata:
                    break


GetCardPath = {}
Hand = [str(rand(1, 28914)), str(rand(1, 28914)), str(rand(1, 28914)), str(rand(1, 28914))]
CardsInField = [Card('farmland', (10, 200), Hand[0]),
                Card('dairycow', (200, 200), Hand[1]),
                Card('dairycow', (390, 200), Hand[2]),
                Card('.random', (580, 200), Hand[3])]
for cardpath in os.listdir('images'):  # add cards path
    cardname = cardpath[:-4]
    GetCardPath[cardname] = 'images\\' + cardpath
GetCurrencyPath = {}
CurrenciesAmount = {}
for currencypath in os.listdir('currencies'):  # add currencies
    currencyname = currencypath[:-4]
    GetCurrencyPath[currencyname] = 'currencies\\' + currencypath
    CurrenciesAmount[currencyname] = 0

grab_id = 'none'
grab_offset = (0, 0)

drawaddrect = (width-100, 20, 80, 25)
specificdrawaddrect = (width-126, 20, 25, 25)
changefieldviewingrect = (25, 25, 25, 25)
buttoncolour = 255
findoffset = 0
gotooffset = 0

_thread.start_new_thread(packet_thread, ())

running = True
while running:
    if viewing_deck not in other_data:
        viewing_deck = name
    if screenstage == 'play':
        mouseLoc = pygame.mouse.get_pos()
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # drag card
                    foundcard = False
                    if viewing_deck == name:
                        reverseddeck = CardsInField.copy()
                        reverseddeck.reverse()
                        for card in reverseddeck:
                            cardloc1 = card.get_rect()[:-2]
                            cardloc2 = card.get_rect()[2:]
                            if is_hover(mouseLoc, cardloc1, cardloc2):
                                if card.exitanimgoto == 0:
                                    foundcard = True
                                    grab_id = card.id
                                    grab_offset = (mouseLoc[0]-cardloc1[0], mouseLoc[1]-cardloc1[1])
                                    CardsInField.remove(card)
                                    CardsInField.append(card)
                                    break
                        if not foundcard:
                            if is_hover(mouseLoc, (drawaddrect[0], drawaddrect[1]), (drawaddrect[2]+drawaddrect[0], drawaddrect[3]+drawaddrect[1])):  # add card
                                if len(CardsInField) <= 31:
                                    newcard = Card('.random', enteranim=600)
                                    CardsInField.append(newcard)
                                    Hand.append(newcard.id)
                                else:
                                    add_info_text('Too many cards!', pygameinfofont, fps)
                                foundcard = True
                        spec = specificdrawaddrect
                        if isselectingcard:
                            if not foundcard:
                                if is_hover(mouseLoc, (spec[0], spec[1]+35), (83+spec[0], spec[1]+216+35)):  # add specific card select card part
                                    scrollpart = -int((findoffset-1-(mouseLoc[1]+spec[1]+35))/108)-3
                                    cardpath = list(GetCardPath.values())[divmod(-scrollpart+len(GetCardPath), len(GetCardPath))[1]]
                                    newcard = Card(cardpath[7:-4], enteranim=600)
                                    CardsInField.append(newcard)
                                    Hand.append(newcard.id)
                                    foundcard = True
                        if not foundcard:
                            if is_hover(mouseLoc, (spec[0], spec[1]), (spec[0]+spec[2], spec[1]+spec[3])):  # add specific card check for click
                                isselectingcard = True
                                foundcard = True
                        if not is_hover(mouseLoc, (spec[0], spec[1]), (spec[0]+spec[2], spec[1]+spec[3])):
                            isselectingcard = False
                    if not foundcard:  # check for change viewing_deck
                        count = -1
                        for player in other_data:
                            count += 1
                            if player == viewing_deck:
                                rect = changefieldviewingrect
                                if is_hover(mouseLoc, (rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3])):
                                    viewing_deck = list(other_data.copy().values())[divmod(count+1, len(other_data))[1]]['name']
                                    foundcard = True
                                    add_info_text(f"Now viewing {viewing_deck}'s field", pygameinfofont, fps)
                                elif is_hover(mouseLoc, (rect[0]+200, rect[1]), (rect[0]+rect[2]+200, rect[1]+rect[3])):
                                    viewing_deck = list(other_data.copy().values())[divmod(count-1, len(other_data))[1]]['name']
                                    foundcard = True
                                    add_info_text(f"Now viewing {viewing_deck}'s field", pygameinfofont, fps)
                                break
                if event.button == 3:  # put in hand
                    if viewing_deck == name:
                        reverseddeck = CardsInField.copy()
                        reverseddeck.reverse()
                        for card in reverseddeck:
                            cardloc1 = card.get_rect()[:-2]
                            cardloc2 = card.get_rect()[2:]
                            if is_hover(mouseLoc, cardloc1, cardloc2):
                                if Hand.__contains__(card.id):
                                    Hand.remove(card.id)
                                else:
                                    Hand.append(card.id)
                                break
                if event.button == 4 or event.button == 5:  # change currency value
                    count = -1
                    foundcard = False
                    if viewing_deck == name:
                        for currency in GetCurrencyPath:
                            count += 1
                            path = GetCurrencyPath[currency]
                            surf = pygame.transform.scale(getsurf(path), (125, 175))
                            surfrect = surf.get_rect(bottomright=(width-count*(surf.get_width()+10)-10, height-35))
                            if is_hover(mouseLoc, surfrect.topleft, surfrect.bottomright):
                                foundcard = True
                                if viewing_deck == name:
                                    # noinspection PyUnresolvedReferences
                                    CurrenciesAmount[currency] = clamp(CurrenciesAmount[currency] + int(-(event.button-4.5)*2), 0, 100)
                    if viewing_deck == name:
                        if not foundcard:
                            reverseddeck = CardsInField.copy()
                            reverseddeck.reverse()
                            for card in reverseddeck:
                                cardloc1 = card.get_rect()[:-2]
                                cardloc2 = card.get_rect()[2:]
                                if is_hover(mouseLoc, cardloc1, cardloc2):
                                    card.counter += int(-(event.button-4.5)*2)
                                    foundcard = True
                                    break
                        if not foundcard:
                            spec = specificdrawaddrect
                            if is_hover(mouseLoc, (spec[0], spec[1]+35), (83+spec[0], spec[1]+216+35)):
                                gotooffset += int(-(event.button-4.5)*2)*108/2
                                foundcard = True
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    grab_id = 'none'
            if event.type == pygame.KEYDOWN:
                if viewing_deck == name:
                    if event.key == pygame.K_BACKSPACE:
                        reverseddeck = CardsInField.copy()
                        reverseddeck.reverse()
                        for card in reverseddeck:
                            cardloc1 = card.get_rect()[:-2]
                            cardloc2 = card.get_rect()[2:]
                            if is_hover(mouseLoc, cardloc1, cardloc2):
                                if card.exitanimgoto == 0:
                                    card.exitanimgoto = card.loc[1]+246
                                    break

        # change viewingdeck boxes
        rect = changefieldviewingrect
        # boxx1
        if viewing_deck == name:
            pygame.draw.rect(screen, (255, 255, 255), (rect[0]-1, rect[1]-1, rect[2]+2+200, rect[3]+2))
            pygame.draw.rect(screen, (0, 0, 0), (rect[0], rect[1], rect[2]+200, rect[3]))
        else:
            pygame.draw.rect(screen, (0, 0, 0), (rect[0]-1, rect[1]-1, rect[2]+2+200, rect[3]+2))
            pygame.draw.rect(screen, (255, 255, 255), (rect[0], rect[1], rect[2]+200, rect[3]))

        # lef boxx1
        pygame.draw.rect(screen, (0, 0, 0), (rect[0]-1, rect[1]-1, rect[2]+2, rect[3]+2))
        pygame.draw.rect(screen, (255, 255, 255), rect)
        changefieldviewlefttext = gametext('<', (0, 0, 0))
        screen.blit(changefieldviewlefttext, changefieldviewlefttext.get_rect(center=(37.5, 37.5)))
        xfact = 200
        pygame.draw.rect(screen, (0, 0, 0), (rect[0]-1+xfact, rect[1]-1, rect[2]+2, rect[3]+2))
        pygame.draw.rect(screen, (255, 255, 255), (rect[0]+xfact, rect[1], rect[2], rect[3]))
        changefieldviewrighttext = gametext('>', (0, 0, 0))
        screen.blit(changefieldviewrighttext, changefieldviewrighttext.get_rect(center=(37.5+xfact, 37.5)))
        if viewing_deck == name:
            viewingdecktext = gametext("Your Field", (0, 255, 200), pygameinfofont)
        else:
            viewingdecktext = gametext(f"{viewing_deck}'s Field", (0, 0, 0), pygameinfofont)
        screen.blit(viewingdecktext, viewingdecktext.get_rect(center=(37.5+xfact/2, 37.5)))

        if viewing_deck == name:
            # draw add button
            spec = specificdrawaddrect
            pygame.draw.rect(screen, (0, 0, 0), drawaddrect)
            pygame.draw.rect(screen, (0, 0, 0), specificdrawaddrect)
            pygame.draw.rect(screen, (buttoncolour, buttoncolour, buttoncolour), (drawaddrect[0]+1, drawaddrect[1]+1, drawaddrect[2]-2, drawaddrect[3]-2))
            pygame.draw.rect(screen, (buttoncolour, buttoncolour, buttoncolour),
                             (spec[0]+1, spec[1]+1, spec[2]-2, spec[3]-2))
            screen.blit(font.render('+', True, (0, 0, 0)), (drawaddrect[0]+28, drawaddrect[1]-6))
            # noinspection PyTypeChecker
            # also draws the triangle used in specific draw
            for x in range(0, 2):
                for y in range(0, 2):
                    pygame.draw.aalines(screen, (0, 0, 0), False, ((spec[0]+4-x, spec[1]+4-y), (spec[0]+spec[2]-4-x, spec[1]+4-y),
                                                                   ((spec[0]*2+spec[2])/2-x, spec[1]+spec[3]-4-y), (spec[0]+4-x, spec[1]+4-y)))

        if viewing_deck == name:
            # selecting specific card
            if isselectingcard:
                gotooffset = clamp(gotooffset, -len(GetCardPath)*108, -108*2)
                findoffset = (findoffset*4+gotooffset)/5
                findoffset = clamp(findoffset, -len(GetCardPath)*108, 0)
                surf = pygame.transform.chop(getsurf(list(GetCardPath.values())[int(findoffset/108)+2], size=(83, 108)), (0, 0, 0, divmod(-findoffset, 108)[1]))
                surf2 = getsurf(list(GetCardPath.values())[int(findoffset/108)+1], size=(83, 108))
                surf3 = pygame.transform.chop(getsurf(list(GetCardPath.values())[int(findoffset/108)], size=(83, 108)), (0, divmod(-findoffset, 108)[1], 0, 1000))
                spec = specificdrawaddrect
                pygame.draw.rect(screen, (0, 0, 0), (spec[0], spec[1]+35, 83, 216))
                screen.blit(surf, (spec[0], spec[1]+spec[3]+10))
                screen.blit(surf2, (spec[0], spec[1]+spec[3]+surf.get_rect()[1]+surf.get_rect()[3]+10))
                screen.blit(surf3, (spec[0], spec[1]+spec[3]+surf.get_rect()[1]+surf.get_rect()[3]+118))

        if viewing_deck == name:
            # draw currencies
            count = 0
            for currency in GetCurrencyPath:
                path = GetCurrencyPath[currency]
                surf = pygame.transform.scale(getsurf(path), (125, 175))
                fontsurf = gametext(str(CurrenciesAmount[currency]), (0, 0, 0))
                screen.blit(fontsurf, surf.get_rect(bottomright=(width-count*(surf.get_width()+10)+40, height+140)))
                screen.blit(surf, surf.get_rect(bottomright=(width-count*(surf.get_width()+10)-10, height-35)))
                count += 1
            for card in CardsInField:  # draw cards
                if card.id == grab_id:
                    card.loc = (mouseLoc[0]-grab_offset[0], mouseLoc[1]-grab_offset[1])
                    cardrect = card.get_rect()
                    pygame.draw.rect(screen, (50, 50, 50), (cardrect[0], cardrect[1]-card.exitanim-card.enteranim, 166, 216), border_radius=14)
                card.draw()
                if card.loc[1]-card.exitanim < -220:
                    CardsInField.remove(card)
                    if Hand.__contains__(card.id):
                        Hand.remove(card.id)
        else:
            # draw currencies [others]
            count = 0
            for currency in other_data[viewing_deck]['currencies']:
                path = GetCurrencyPath[currency]
                surf = pygame.transform.scale(getsurf(path), (125, 175))
                fontsurf = gametext(str(other_data[viewing_deck]['currencies'][currency]), (0, 0, 0))
                screen.blit(fontsurf, surf.get_rect(bottomright=(width-count*(surf.get_width()+10)+40, height+140)))
                screen.blit(surf, surf.get_rect(bottomright=(width-count*(surf.get_width()+10)-10, height-35)))
                count += 1
            for card in other_data[viewing_deck]['field']:  # draw cards [others]
                if card.id == grab_id:
                    card.loc = (mouseLoc[0]-grab_offset[0], mouseLoc[1]-grab_offset[1])
                    cardrect = card.get_rect()
                    pygame.draw.rect(screen, (50, 50, 50), (cardrect[0], cardrect[1]-card.exitanim-card.enteranim, 166, 216), border_radius=14)
                card.draw(True)

        info_put(screen)

        if updatethedata:
            other_data = raw_data.copy()
            # noinspection PyShadowingNames
            for player in other_data:
                # noinspection PyShadowingNames
                other_data[player]['field'] = [Card('nullcard').unpack(card) for
                                               card in other_data[player]['field'] if type(other_data[player]['field']) != Card]
        pygame.display.update()
        updatethedata = True
        pyclock.tick(fps)
        tick += 1

    elif screenstage == 'menu':  # MENU
        mouseLoc = pygame.mouse.get_pos()
        joinrect = (width/2-100, height/2+125, 200, 30)
        namerect = (width/2-100, height/2+200, 200, 30)
        nameloc = (namerect[0], namerect[1], namerect[2], namerect[3])
        iprect = (width/2-100, height/2+(125+200)/2, 200, 30)
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if is_hover(mouseLoc, (joinrect[0], joinrect[1]), (joinrect[2]+joinrect[0], joinrect[1]+joinrect[3])):
                        if not connecting:
                            if len(name) > 2:
                                if len(ip) > 2:
                                    connecting = True
                                    _thread.start_new_thread(connect_thread, ())
                                else:
                                    if len(ip) == 0:
                                        add_info_text('enter ip address pls', pygameinfofont, fps)
                                    else:
                                        add_info_text('try entering long ip', pygameinfofont, fps)
                            else:
                                add_info_text('longer name please', pygameinfofont, fps)
                            # pressing connect to server!
                    if not istypingname:
                        if is_hover(mouseLoc, (namerect[0], namerect[1]), (namerect[0]+namerect[2], namerect[1]+namerect[3])):
                            istypingname = True
                    else:
                        istypingname = False
                    if not istypingip:
                        if is_hover(mouseLoc, (iprect[0], iprect[1]), (iprect[2]+iprect[0], iprect[1]+iprect[3])):
                            istypingip = True
                    else:
                        istypingip = False

            if event.type == pygame.KEYDOWN:
                if istypingname:
                    if event.unicode in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzw1234567890_':
                        if len(name) <= 15:
                            name += event.unicode
                    if event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                elif istypingip:
                    if event.unicode in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzw1234567890.-':
                        if len(ip) <= 20:
                            ip += event.unicode
                    if event.key == pygame.K_BACKSPACE:
                        ip = ip[:-1]

        info_put(screen)

        logo = pygame.image.load('logo.png')
        logorect = logo.get_rect(center=(width/2, 250))
        screen.blit(logo, logorect)

        # noinspection PyTypeChecker
        pygame.draw.rect(screen, (50, 240, 90), joinrect)
        screen.blit(pygameinfofont.render('join server', True, (0, 0, 0)), joinrect)

        if istypingname:
            # noinspection PyTypeChecker
            pygame.draw.rect(screen, (120, 50, 240), nameloc)
        else:
            # noinspection PyTypeChecker
            pygame.draw.rect(screen, (190, 160, 240), nameloc)

        if istypingip:  # ip thing
            # noinspection PyTypeChecker
            pygame.draw.rect(screen, (50, 80, 240), iprect)
        else:
            # noinspection PyTypeChecker
            pygame.draw.rect(screen, (150, 180, 240), iprect)

        if istypingname:
            screen.blit(pygameinfofont.render(name, True, (0, 0, 0)), nameloc)
        else:
            if len(name) != 0:
                screen.blit(pygameinfofont.render(name, True, (0, 0, 0)), nameloc)
            else:
                screen.blit(pygameinfofont.render('please input name', True, (0, 0, 0)), namerect)

        if istypingip:
            screen.blit(pygameinfofont.render(ip, True, (0, 0, 0)), iprect)
        else:
            if len(ip) != 0:
                screen.blit(pygameinfofont.render(ip, True, (0, 0, 0)), iprect)
            else:
                screen.blit(pygameinfofont.render('input ip here', True, (0, 0, 0)), iprect)

        pyclock.tick(fps)
        pygame.display.update()
pygame.quit()
