import sys
import pygame
from pygame.display import update
from time import sleep

from settings import Settings
from ships import Ship
from bullet import Bullet
from alien import Alien
from game_start import GameStats
from button import Buttom
from scoreboard import Scoreboard

class AlienInvasion:
    """管理游戏资源和行为的类"""

    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()
        self.settings=Settings()
        # 创建屏幕
        # self.screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        # self.settings.screen_height=self.screen.get_rect().height
        # self.settings.screen_width=self.screen.get_rect().width
        self.screen=pygame.display.set_mode(
            (self.settings.screen_width,self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")
        # 创建储存游戏统计信息的实例，并创建计分牌
        self.stats=GameStats(self)
        self.sb=Scoreboard(self)
        # 创建飞船子弹外星人
        self.ship=Ship(self)
        self.bullets=pygame.sprite.Group()
        self.aliens=pygame.sprite.Group()
        self._create_fleet()
        # 创建play按钮
        self.play_buttom=Buttom(self,"Play")
        # 设置背景色
        self.bg_color=self.settings.bg_color

    def run_game(self):
        """开始游戏的主循环"""
        while True:
            self._check_events()

            if self.stats.game_active:
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
            elif event.type==pygame.MOUSEBUTTONDOWN:
                mouse_pos=pygame.mouse.get_pos()
                self._check_play_buttom(mouse_pos)

    def _check_keydown_events(self, event):
        if event.key==pygame.K_RIGHT:
            self.ship.moving_right=True
        if event.key==pygame.K_LEFT:
            self.ship.moving_left=True
        if event.key==pygame.K_SPACE:
            self._fire_bullet()
        if event.key==pygame.K_q:
            sys.exit()
        if event.key==pygame.K_p:
            self._start_game()

    def _check_keyup_events(self, event):
        if event.key==pygame.K_RIGHT:
            self.ship.moving_right=False
        if event.key==pygame.K_LEFT:
            self.ship.moving_left=False
    
    def _check_play_buttom(self,mouse_pos):
        """在玩家点击play按钮时开始新游戏"""
        buttom_clicked=self.play_buttom.rect.collidepoint(mouse_pos)
        if buttom_clicked and not self.stats.game_active:
            self._start_game()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

    def _start_game(self):
        # 重置游戏统计信息
        self.stats.reset_stats()
        self.stats.game_active=True
            # 清空余下的外星人和子弹
        self.aliens.empty()
        self.bullets.empty()
            # 创建一群新的外星人并让飞船居中
        self._create_fleet()
        self.ship.center_ship()
            # 隐藏光标
        pygame.mouse.set_visible(False)

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
        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        # 检查是否有子弹击中了外星人
        #   如果是，就删除相应的子弹和外星人
        collisions=pygame.sprite.groupcollide(
            self.bullets,self.aliens,True,True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score+=self.settings.alien_point*len(aliens)
                self.sb.prep_score()
                self.sb.check_high_score()
        if not self.aliens:
            # 删除现有的子弹并创建一群外星人
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            # 提高等级
            self.stats.level+=1
            self.sb.prep_level()

    def _update_aliens(self):
        """更新外星人群中所有外星人的位置"""
        self._check_fleet_edges()
        self.aliens.update()
        # 检查是否有外星人撞到了飞船
        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            self._ship_hit()
        # 检查是否有外星人到达了屏幕底端
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """检查是否有外星人到达了屏幕底端"""
        screen_rect=self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom>=screen_rect.bottom:
                # 像飞船被撞一样处理
                self._ship_hit()
                break

    def _ship_hit(self):
        if self.stats.ship_left>0:
            """响应飞船被外星人撞到"""
            self.stats.ship_left-=1
            self.sb.prep_ships()

            self.aliens.empty()
            self.bullets.empty()

            self._create_fleet()
            self.ship.center_ship()

            # 暂停
            sleep(0.5)
        else:
            self.stats.game_active=False
            pygame.mouse.set_visible(True)

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
        # 显示得分
        self.sb.show_score()
        # 如果游戏处于非活动状态，就绘制play按钮
        if not self.stats.game_active:
            self.play_buttom.draw_buttom()
        # 让最近绘制的屏幕可见
        pygame.display.update()

if __name__=="__main__":
    # 创建游戏实例并运行游戏
    ai=AlienInvasion()
    screen=ai.screen.get_rect()
    ai.run_game()