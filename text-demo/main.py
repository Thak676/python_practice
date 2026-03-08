import pygame
from pygame.locals import *
import sys

def main():
    pygame.init()    # Pygameを初期化
    screen = pygame.display.set_mode((400, 300))    # 画面を作成
    pygame.display.set_caption("S.C.MAGI")    # タイトルを作成

    #STEP1.フォントの用意  
    font1 = pygame.font.SysFont("notosanscjkjp", 50)
    font2 = pygame.font.SysFont(None, 50)
    
    #STEP2.テキストの設定
    text1 = font1.render("警告", True, (255,0,0))
    text2 = font2.render("EMERGENCY", True, (255,0,0))
    
    running = True
    #メインループ
    while running:
        screen.fill((0,0,0))  #画面を黒で塗りつぶす
    
        # STEP3.テキストを描画
        screen.blit(text1, (40,30))
        screen.blit(text2, (80,180))
        
        pygame.display.update() #描画処理を実行
        
        for event in pygame.event.get():
            if event.type == QUIT:  # 終了イベント
                running = False
                pygame.quit()  #pygameのウィンドウを閉じる
                sys.exit() #システム終了
                
     
if __name__=="__main__":
    main()
