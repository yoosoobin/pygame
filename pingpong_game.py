'''
과제 번호 : 03
문제 내용 : 미니탁구
'''

import pygame
import sys
import random

SCREEN = pygame.display.set_mode((822,457))

class Paddle(pygame.sprite.Sprite):
    def __init__(self,gamer,filename):
        super().__init__()

        self.image = pygame.image.load(filename).convert_alpha()
        self.image = pygame.transform.scale(self.image, (20,100))
        self.rect = self.image.get_rect()
        self.rect.x = (SCREEN.get_width() - self.rect.width)if gamer != 'blue' else 0
        self.rect.centery = random.randint(0, SCREEN.get_height() - self.rect.height)
        # (self.rect.x, self.rect.y) : 패들 이미지의 좌측 상단점
        self.dy = 2




    def paddle_down(self):
        self.rect.y += self.dy
        if self.rect.bottom >= SCREEN.get_height():
            self.rect.bottom = SCREEN.get_height()

    def paddle_up(self):
        self.rect.y -= self.dy
        if self.rect.top <=0:
            self.rect.top = 0



class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('ball.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (15, 15))
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN.get_width()//2
        self.rect.centery = SCREEN.get_height()//2




    def prepare_ball(self,player):
        self.rect.centerx = SCREEN.get_width()//2
        min_y = int(SCREEN.get_height()*0.2)
        max_y = int(SCREEN.get_height()*0.8)
        self.rect.centery = random.randint(min_y, max_y)


        if player== 0:
            self.dx = 2
        else:
            self.dx = -2

        self.dy = random.choice([-1, 1])


    def bounce_wall(self,wall_grp):
        t = pygame.sprite.spritecollide(self, wall_grp, False)
        if len(t) >0:
            pygame.mixer.Sound('wall_beep.ogg').play()
            self.dy *= -1
            return True
        else:
            return False

    def bounce_paddle(self, paddle_grp):
        paddle = pygame.sprite.spritecollide(self, paddle_grp, False)
        if len(paddle) >0:
            self.dx *= -1
            ratio = 0.6*2*(self.rect.centery == paddle[0].rect.centery)/paddle[0].rect.height
            self.dy = self.dy + int(self.dy * ratio)

            pygame.mixer.Sound('paddle_beep.ogg').play()
            return True
        else:
            return False



    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy


class Wall(pygame.sprite.Sprite):
    def __init__(self,position):
        super().__init__()

        self.image = pygame.Surface((SCREEN.get_width(),1)).convert()
        self.rect = self.image.get_rect().move(0,0)
        self.rect.y = SCREEN.get_height() if position == 'bottom' else 0


class ScoreBoard(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.score = {'blue':0, 'red':0}
        self.font = pygame.font.SysFont(None, 48)

        self.image = self.font.render(f'{self.score["blue"]} : {self.score["red"]}', True, 'white')

        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN.get_width()//2
        self.rect.y = 5

    def update_score(self):
        self.text = f'{self.score["blue"]} : {self.score["red"]}'
        self.image = self.font.render(self.text, True, pygame.Color('white'))


class Message(pygame.sprite.Sprite):
     def __init__(self,msg):
         super().__init__()

         font = pygame.font.SysFont(None, 50)
         #message = 'Press any key to continue'
         self.image = font.render(msg, True, pygame.Color('white'))
         self.rect = self.image.get_rect()

         self.rect.centerx = SCREEN.get_width() // 2
         self.rect.centery = SCREEN.get_height() // 2







class PingPong:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('미니 탁구')
        self.background = pygame.Surface(SCREEN.get_size())
        self.background.fill(pygame.Color('black'))
        pygame.draw.line(self.background, pygame.Color('gray'), (SCREEN.get_width() // 2, 0),
                         (SCREEN.get_width() // 2, SCREEN.get_height()))
        pygame.draw.rect(self.background, pygame.Color('white'),
                         (0, 0, SCREEN.get_width(), SCREEN.get_height()), width=10)
        SCREEN.blit(self.background, (0, 0))
        self.fps = 100
        self.paddle = {'blue': Paddle('blue', 'blue.png'),
                       'red': Paddle('red', 'red.png')}
        self.wall = {'top': Wall('top'), 'bottom': Wall('bottom')}
        self.ball = Ball()
        self.score_board = ScoreBoard()
        self.message = Message('press any key to continue')
        self.message_blue = Message('Blue Win!')
        self.message_red = Message('Red Win!')
        self.sp_grps = {'paddle':pygame.sprite.Group(self.paddle['blue'], self.paddle['red']),
                        'wall': pygame.sprite.Group(self.wall['top'], self.wall['bottom']),
                        'ball':pygame.sprite.Group(self.ball),
                        'scoreboard':pygame.sprite.Group(self.score_board),
                        'message':pygame.sprite.Group(self.message)}

        self.clock = pygame.time.Clock()

    def render(self):
        for name in self.sp_grps:
            self.sp_grps[name].clear(SCREEN, self.background)
            self.sp_grps[name].update()
            self.sp_grps[name].draw(SCREEN)

            pygame.display.flip()


    def show_message(self):
        self.render()






    def do_serve(self):
        offence = sum(self.score_board.score.values())//5 #5점마다 서브권 교체
        self.ball.prepare_ball(offence%2)
        self.show_message()
        self.fps += 10  # 점점 속도가 빨라짐 (교수님..말씀하신게 이게 맞는지는 잘 모르겠지만..빨라집니다!!..ㅎㅎ)

        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                self.sp_grps['message'].remove(self.message)
                break


    def is_ball_alive(self):
        flag = True
        if self.ball.rect.x <0:                 #red wins
            pygame.mixer.Sound('dying_ball.mp3').play()
            self.score_board.score['red'] +=1
            self.score_board.update_score()
            flag=False
        elif self.ball.rect.right > SCREEN.get_width():             #blue wins
            pygame.mixer.Sound('dying_ball.mp3').play()
            self.score_board.score['blue'] +=1
            self.score_board.update_score()
            flag = False

        return flag

    def game_loop(self):

        self.do_serve()
        while True:
            self.clock.tick(self.fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)

            pressed_key = pygame.key.get_pressed()
            if pressed_key[pygame.K_q]:
                self.paddle['blue'].paddle_up()
            elif pressed_key[pygame.K_a]:
                self.paddle['blue'].paddle_down()
            elif pressed_key[pygame.K_p]:
                self.paddle['red'].paddle_up()
            elif pressed_key[pygame.K_l]:
                self.paddle['red'].paddle_down()


            if self.is_ball_alive():
                self.ball.bounce_paddle(self.sp_grps['paddle'])
                self.ball.bounce_wall(self.sp_grps['wall'])

            else:
                self.do_serve()

            if self.score_board.score['blue'] == 2 :
                self.sp_grps['ball'].remove(self.ball)
                self.sp_grps['message'] = pygame.sprite.Group(self.message_blue)
                self.show_message()
                pygame.mixer.Sound('start.mp3').play()
                event = pygame.event.wait()
                if event.type == pygame.KEYDOWN:
                    game=PingPong()
                    game.game_loop()



            elif self.score_board.score['red'] == 2 :
                self.sp_grps['ball'].remove(self.ball)
                self.sp_grps['message'] = pygame.sprite.Group(self.message_red)
                self.show_message()
                pygame.mixer.Sound('start.mp3').play()
                event = pygame.event.wait()
                if event.type == pygame.KEYDOWN:
                    game = PingPong()
                    game.game_loop()


            else:
                pass



            self.render()






if __name__ == '__main__':
    game = PingPong()
    game.game_loop()
