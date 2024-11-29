#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import rev2

UsageText = '''
  制約の最適化レベル K = 0, 1, 2, 3 （2が最も制約生成に時間がかかる）

  使用方法
    $ python3 rev-tetro.py [ --opt K ]
      例：
      h*wの領域にペントミノピースを敷き詰める制約
      MinBoardは存在しない
      $ python3 rev-pento.py 6 > revJ6.pb
  '''

################################################################################
## N=1 のときの盤面の情報
##
##     i行j列のマス(i,j) where i>=0 and j>=0 を列挙して表現
##     0
##     0   0
##     0 0 0
##
##MinBoard = {(0, 0), (0, 1), (0, 2), (1, 2), (2, 1), (2, 2)}
##python3 rev-pento.py 6 10
#scp -r rev-tetro.py oguri@atlas.trs.css.i.nagoya-u.ac.jp: /home/fs5/common/DB/project/sharpsat/tools/git
#scp -r varscore_2.txt oguri@atlas.trs.css.i.nagoya-u.ac.jp:/home/fs5/common/DB/project/sharpsat/tools/git/tetromino

## gpmcコマンド例 ./../gpmc-1.1.1/bin/gpmc -mode=2 -ppverb=1 -varscore="varscore_2.txt" rev-pento-size6*10-opt3-3-gpmc.cnf >> res-varscore-rev-pento-size6*10-opt3-3-gpmc.txt  &
## ./../gpmc-1.1.1/bin/gpmc -mode=2 -ppverb=1 -varscore="varscore_2.txt" -ddnnf -nnfout="nnf-7col.txt" rev-pento-size6*10-opt3-leftpverb-Lnodup-7col-3-gpmc.cnf >> res-leftpverb-Lnodup-7col.txt &
## napsコマンド例 ./naps-1.02b2 -A -pos rev-pento2-size6*10-opt3-ptn2.pb  >> naps-opt1.txt &
## cnf化コマンド例 ./bin/pb2cnf.sh rev-pento-size6*10-opt3-leftpverb-Lnodup.pb rev-pento2-size6*10-opt2-ptn2.pb
#rev-pento2-size6*10-opt2-ptn2-3-gpmc.cnf
## gpmcコマンド例 ./../gpmc-1.1.1/bin/gpmc -mode=2 -ppverb=1 -varscore="varscore_1.txt" rev-pento-size6*10-opt3-test-3-gpmc.cnf >> left_pvars_vs1.txt  &
##
##pathcount COUNTER=/home/fs5/common/DB/project/icgca/pathcount/graphpathcounter/bin/pathcount
##gpmc_no_inisat_mindeg = /home/fs5/common/DB/project/icgca/gpmc_no_inisat_mindeg
##gpmc_no_presat = /home/fs5/common/DB/project/icgca/gpmc_no_presat
################################################################################
##
## タイルの情報（使用するピースを登録）
## P1:
##     0
##     0   0
##     0 0 0
##
## (type, cell list) のリスト。ここで、長方形は type=0 とすること。
##   １以上の type はカラーで結果表示されることになる
PrimTilePat = [

        (0, {(0,0),(2,1),(1,1),(1,2),(1,0)}), \
        (1, {(0,0),(0,1),(0,2),(0,3),(1,3)}), \
        (2, {(0,0),(0,1),(1,1),(1,2),(1,3)}), \
        (3, {(0,0),(0,1),(1,0),(1,1),(0,2)}), \
        (4, {(0,0),(0,1),(0,2),(0,3),(1,2)}), \
        (5, {(0,0),(1,0),(1,1),(1,2),(2,2)}), \
        (6, {(0,0),(1,0),(2,0),(1,1),(1,2)}), \
        (7, {(0,0),(0,1),(1,1),(2,0),(2,1)}), \
        (8, {(0,0),(0,1),(0,2),(1,2),(2,2)}), \
        (9, {(0,0),(0,1),(1,1),(1,2),(2,2)}), \
        (10, {(0,0),(0,1),(0,2),(0,3),(0,4)}), \
        (11, {(0,1),(1,0),(1,1),(1,2),(2,1)}), \

        ]

## メイン関数
if __name__ == "__main__":
    rev2.gen_reptile(PrimTilePat, UsageText)
