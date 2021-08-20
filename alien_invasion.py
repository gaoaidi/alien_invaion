import sys
import pygame
from pygame.display import update
from settings import Settings
from ships import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """管理游戏资源和行为的类"""

    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()
        self.settings=Settings()

        self.screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        self.settings.screen_height=self.screen.get_rect().height
        self.settings.screen_width=self.screen.get_rect().width
        pygame.display.set_caption("Alien Invasion")
        
        self.ship=Ship(self)
        self.bullets=pygame.sprite.Group()
        self.aliens=pygame.sprite.Group()
        self._create_fleet()
        # 设置背景色
        self.bg_color=self.settings.bg_color
    def run_game(self):
        """开始游戏的主循环"""
        while True:
            self._check_events()
            self.ship.update()
            self._update_bullets()
            self._update_aliens()
            self._update_screen()

    def _create_fleet(self):
        """创建外星人群"""
        alien=Alien(self)
        alien_width,alien_height=alien.rect.size
        availbale_space_x=self.settings.screen_width-(2*alien_width)
        number_aliens_x=availbale_space_x//(2*alien_width)

        ship_height=self.ship.rect.height
        availbale_space_y=(self.settings.screen_height-
            (3*alien_height)-ship_height)
        number_rows=availbale_space_y//(2*ship_height)
        # 创建外星人群
        for row_number in range(number_rows-3):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number,row_number)

    def _create_alien(self, alien_number, row_number):
        alien=Alien(self)
        alien_width,alien_height=alien.rect.size
        alien.x=alien_width+2*alien_width*alien_number
        alien.rect.x=alien.x
        alien.rect.y=alien_height+2*alien_height*row_number
        self.aliens.add(alien)

    def _check_events(self):
        # 监视键盘和鼠标事件
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                sys.exit()
            elif event.type==pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type==pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self, event):
        if event.key==pygame.K_RIGHT:
            self.ship.moving_right=True
        if event.key==pygame.K_LEFT:
            self.ship.moving_left=True
        if event.key==pygame.K_SPACE:
            self._fire_bullet()
        if event.key==pygame.K_q:
            sys.exit()

    def _check_keyup_events(self, event):
        if event.key==pygame.K_RIGHT:
            self.ship.moving_right=False
        if event.key==pygame.K_LEFT:
            self.ship.moving_left=False
    
    def _fire_bullet(self):
        # 创建一个子弹，并将其加入编组bullets中
        if len(self.bullets)<self.settings.bullet_allow:
            new_bullet=Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        # 更新子弹位置并删除消失的子弹
        self.bullets.update()
        for bullet in self.bullets.copy():
                if bullet.rect.bottom<=0:
                    self.bullets.remove(bullet)
        # 检查是否有子弹击中了外星人
        #   如果是，就删除相应的子弹和外星人
        collisions=pygame.sprite.groupcollide(
            self.bullets,self.aliens,True,True)

    def _update_aliens(self):
        """更新外星人群中所有外星人的位置"""
        self._check_fleet_edges()
        self.aliens.update()

    def _check_fleet_edges(self):
        """有外星人到达边缘时采取相应的措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """将整群外星人下移，并改变它们的方向"""
        for alien in self.aliens.sprites():
            alien.rect.y+=self.settings.fleet_drop_speed
        self.settings.fleet_direction*=-1

    def _update_screen(self):
        # 每次循环时都重绘屏幕
        self.screen.fill(self.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        # 让最近绘制的屏幕可见
        pygame.display.update()

if __name__=="__main__":
    # 创建游戏实例并运行游戏
    ai=AlienInvasion()
    ai.run_game()