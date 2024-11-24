#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import itertools

import diamond
import time

UsageText = '''
  ダイヤモンドパズル
  制約の最適化レベル K = 0, 1, 2 （2が最も制約生成に時間がかかる）

  使用方法
    $ python3 dmd.py [--opt K]
      例：
      ダイヤモンドパズルの制約 dmd-opt1.pb を生成．
      $ python3 dmd.py
  '''

################################################################################
## N=1 のときの盤面の情報
##
##     i行j列のマス(i,j) where i>=0 and j>=0 を列挙して表現
##     0   0
##     0 0 0 0
##

################################################################################
##
## タイルの情報（使用するピースを登録）
## P1:
##     0   0
##     0 0 0 0
##
## (type, cell list) のリスト。ここで、長方形は type=0 とすること。
##   １以上の type はカラーで結果表示されることになる
primTilePat = {
    diamond.Tile({(0, 0), (1, 0), (1, 1), (1, 2), (2, 0)}, 1), \
    diamond.Tile({(0, 1), (0, 3), (1, 0), (1, 1), (1, 2)}, 2), \
    diamond.Tile({(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)}, 3), \
    diamond.Tile({(0, 0), (0, 3), (1, 0), (1, 1), (1, 2)}, 4), \
    diamond.Tile({(0, 3), (1, 1), (1, 2), (1, 3), (2, 0)}, 5), \
    diamond.Tile({(0, 2), (1, 0), (1, 1), (1, 2), (2, 0)}, 6), \
    diamond.Tile({(0, 4), (1, 2), (1, 3), (2, 1), (3, 0)}, 7), \
    diamond.Tile({(0, 4), (1, 3), (2, 2), (3, 0), (3, 1)}, 8), \
    diamond.Tile({(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)}, 9), \
    diamond.Tile({(0, 1), (0, 2), (1, 2), (2, 0), (2, 1)}, 10), \
    diamond.Tile({(0, 3), (1, 1), (1, 2), (2, 0), (2, 1)}, 11), \
    diamond.Tile({(0, 2), (1, 2), (2, 1), (3, 0), (4, 0)}, 12), \
    diamond.Tile({(0, 3), (1, 2), (2, 0), (2, 1), (3, 1)}, 13), \
    diamond.Tile({(0, 1), (0, 2), (1, 1), (1, 2), (2, 0)}, 14), \
    diamond.Tile({(0, 0), (1, 0), (1, 1), (2, 0), (3, 0)}, 15), \
    diamond.Tile({(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)}, 16), \
    diamond.Tile({(0, 0), (0, 1), (0, 2), (1, 1), (2, 0)}, 17), \
    diamond.Tile({(0, 0), (1, 0), (1, 2), (2, 0), (2, 1)}, 18), \
    diamond.Tile({(0, 0), (0, 1), (1, 0), (2, 0), (3, 0)}, 19), \
    diamond.Tile({(0, 3), (1, 3), (2, 1), (2, 2), (3, 0)}, 20), \
    diamond.Tile({(0, 3), (1, 1), (1, 2), (2, 0), (2, 2)}, 21), \
    diamond.Tile({(0, 3), (0, 4), (1, 1), (1, 2), (2, 0)}, 22), \
 \
    }

# print("{}".format(PrimTilePat))

# x座標：横１０列, y座標：右下６０度１１行
Board = diamond.Tile(set(itertools.product(range(0,10), range(0,11))))
'''
0 0 0 0 0 0 0 0 0 0 
 0 0 0 0 0 0 0 0 0 0 
  0 0 0 0 0 0 0 0 0 0 
   0 0 0 0 0 0 0 0 0 0 
    0 0 0 0 0 0 0 0 0 0 
     0 0 0 0 0 0 0 0 0 0 
      0 0 0 0 0 0 0 0 0 0 
       0 0 0 0 0 0 0 0 0 0 
        0 0 0 0 0 0 0 0 0 0 
         0 0 0 0 0 0 0 0 0 0 
          0 0 0 0 0 0 0 0 0 0 
'''
# print("{}".format(Board.prettyHex()))

    # primTilePatのタイルの向きを洗い出して tilePatに入れる
#    for tile in primTilePat:
#        print("'{}'  ".format(tile.pretty()), end='\n')

x_tilePat = {pat.flipHex() for pat in primTilePat} | primTilePat
r_tilePat = {pat.rotateHex_60() for pat in x_tilePat}
rr_tilePat = {pat.rotateHex_60() for pat in r_tilePat}

xrrr_tilePat = x_tilePat | r_tilePat | rr_tilePat
rot180_tilePat = {pat.rotateHex_180() for pat in xrrr_tilePat}
tilePat = rot180_tilePat | xrrr_tilePat

# for pat in tilePat:
#     if pat.type == 11:
#         print("{}".format(pat.prettyHex()))

## メイン関数
if __name__ == "__main__":

    # 計測開始
    start_time = time.time()
    
#    for tile in PrimTilePat:
#        print("{}".format(tile.prettyHex()))
    diamond.gen_tiling_constraints(tilePat, Board, UsageText)

    # 計測終了
    end_time = time.time()

    # 結果表示
    print(f"Execution time: {end_time - start_time:.6f} seconds")
