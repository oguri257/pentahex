##
## 正方形ベースの Rep-tile の Pseudo Boolean 制約生成ライブラリ
##
## 特定の問題に特化した制約生成プログラムは以下のようにする
##-----------------------------------------------------------------------------
## imprt rev					# このファイルをインポート
##
## UsageText ="ヘルプコメントをここに書く"   #(省略可)
##
## MinBoard = {(x1, y1), .... , (xn, yn)}	# サイズ１の枠の座標を書く
## #  例 MinBoard = {(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)}
##
## PrimTilePat = [ (1, MinBoard) ]		# タイルの定義（通常はサイズ１の枠を使う）
##						# 第１要素はタイルのタイプで
##						# 生成される制約変数の P?(xxxxx) の？に使われる
## ## メイン関数
## if __name__ == "__main__":
##     rev.gen_tiling_constraints(MinBoard, PrimTilePat, UsageText)
##-----------------------------------------------------------------------------

import sys
import os
import shutil
import time
import argparse
import textwrap
import re
from functools import total_ordering

##
## 配置領域（の設定関数）:
# pat の部分のみTrueに変更する
def setDomain(D, pat):
    for (x, y) in pat.cells:
        D[x][y] = True

# convert 0 1  .. 9 10 11 12 .. into 0 1 .. 9 a b c ..
def toSingleChar(n):
    return str(n) if n <= 9 else chr(ord('a')+n-10)

################################################################################
################################################################################

##
## Tileクラス: ボードに埋め込まれたタイル
##
@total_ordering
class Tile(object):
    def __init__(self, cells, type=0):
        super().__init__()
        self.cells = cells
        self.sortedCells = sorted(list(cells))
        self.size = len(cells)
        self.type = type

        setX = {x for (x, y) in cells}
        setY = {y for (x, y) in cells}
        if self.size > 0:
            self.xmin = min(setX)
            self.xmax = max(setX)
            self.ymin = min(setY)
            self.ymax = max(setY)
        else:
            self.xmin = 0
            self.xmax = -1
            self.ymin = 0
            self.ymax = -1
        self.borders = set()
        for (x,y) in cells:
            for i in range(x-1,x+2,2):
                if not (i, y) in cells:
                    self.borders.add((i, y))
            for j in range(y-1,y+2,2):
                if not (x,j) in cells:
                    self.borders.add((x, j))
            for i in {-1, 1}:
                if not (x+i,y-i) in cells:
                    self.borders.add((x+i, y-i))
                if not (x-i,y+i) in cells:
                    self.borders.add((x-i, y+i))

    def __str__(self):
        return "P{}[{}]".format(self.type, ','.join(["(" + str(x) + "," + str(y) + ")" for (x, y) in sorted(self.cells)]))

    def toVariable(self, M = 0):
        return "P{}[{}]".format(self.type, ','.join(["(" + str(x) + "," + str(y) + ")" for (x, y) in sorted(self.cells)]))
#        return "P{}({})".format(self.type, ','.join([str(p) for p in sorted([y * M + x + 1 for (x, y) in self.cells])]))

    def prettyHex(self):
        resStr = ""
        n = 0
#        print("xrange={}, yrange={}".format(range(self.xmin, self.xmax+1), range(self.ymin, self.ymax+1)))
        for y in range(self.ymin, self.ymax+1):
            for x in range(self.xmin, self.xmax+1):
#                print("({},{})".format(x,y))
                resStr += toSingleChar(self.type) if ((x,y) in self.cells) else " "
                resStr += " "
            n += 1
            resStr += "{}{}".format("\n", " "*n)
        return resStr

    def xlen(self):
        return (self.xmax - self.xmin + 1)

    def ylen(self):
        return (self.ymax - self.ymin + 1)

    # p =(x,y) の位置を占めるか？
    def contains(self, p):
        return (p in self.cells)

    def isnormalized(self):
        return (self.xmin == 0 and self.ymin == 0)

    def isoverlap(self, other):
        if not isinstance(other, Tile):
            return false
        return (not (self.cells.isdisjoint(other.cells)))

    # create normalized new Tile
    def normalize(self):
        #        if(self.isnormalized()):
        #            return
        xshift = -self.xmin
        yshift = -self.ymin
        return Tile({(x + xshift, y + yshift) for (x, y) in self.cells}, self.type)

    # (x',y') := (x+y, -y)
    def flipHex(self):
        return Tile({(x+y, -y) for (x, y) in self.cells}, self.type).normalize()

    # (x', y') := (-y, x+y)
    def rotateHex_60(self):
        return Tile({(-y, x+y) for (x, y) in self.cells}, self.type).normalize()

    # (x', y') := (-y, x+y)
    def rotateHex_180(self):
        return Tile({(-x, -y) for (x, y) in self.cells}, self.type).normalize()

    def __eq__(self, other):
        if not isinstance(other, Tile):
            return False
        return self.type == other.type and self.cells == other.cells

    def __lt__(self, other):
        if not isinstance(other, Tile):
            return NotImplemented
        return self.sortedCells < other.sortedCells

    def __hash__(self):
        return hash(tuple(self.cells))

##
## PB等式出力用の関数
##
#   1 P0(1,3,4) 1 P0(1,2,3) ...
def printLinEx(out, exp, M):
    for (coeff, tile) in exp:
        print("{} {}".format(coeff, tile.toVariable(M)), end=' ', file=out)

def printConstr(out, exp, M, Op, num):
    if exp != set():
        printLinEx(out, exp, M)
        print("{} {};".format(Op, num), file=out)

def tilesToExp(tileSet, coeff=1):
    res = set()
    for t in tileSet:
        res.add((coeff, t))
    return res

##
## コマンドラインオプション
##
def get_args(UsageText):
    if UsageText == "":
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter)
    else:
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=textwrap.dedent(UsageText))
    '''
    parser.add_argument("N", type=int, help="problem size")  # 問題サイズ
    parser.add_argument("--nOC", type=str, help="constraints on rectangle pieces: NOC is >n, >=n, =n, <n or <=n")  # 長方形ピースの使用数の条件
    parser.add_argument("--nOCsimp", action="store_true", help="prefer simple constraints on number of pieces withtout assuming rectangles")
    parser.add_argument("--frm", type=int, help="generates PB files for every rectangle pieces >= n")
    parser.add_argument("--to", type=int, help="generates PB files for every rectangle pieces <= n")
    parser.add_argument("--each", action="store_true", help="generates all PB files for every n rectangle pieces (same as --from 0 --to N*N)")
    parser.add_argument("--min", action="store_true", help="minimizing rectangle pieces")
    parser.add_argument("--max", action="store_true", help="maximizing rectangle pieces")
    '''
    parser.add_argument("--opt", choices=['0','1','2'], default=1, help="optimizing level for constraints (default=2)")
    parser.add_argument("--out", type=str, help="output PB file name.  - for standard output")

    args = parser.parse_args()
    if (args.opt == None):
        args.out = 1
    else:
        args.opt = int(args.opt)

#    if (args.each):
#        args.frm = 0
#        args.to = args.N * args.N //2
#
#    if (args.frm != None or args.to != None) and (args.nOC != None or args.min or args.max or args.out):
#        print("--each option is not compatible with --nOC, --min, --max, nor --out", file =sys.stderr)
#        exit()

#    if args.nOC != None:
#        m = re.match(r"([><]*[=]?)\s*(\d+)", args.nOC)
#        if not m:
#            print("possble argument of nOC: >n, >=n, =n, <n, or <=n\n", file=sys.stderr)
#            exit()
#        args.nOCOp = m.group(1)
#        args.nOCNum = int(m.group(2))

    return (args)

## 出力ファイル名の生成
def gen_filename(progName, args):
    resName = "{}-opt{}".format(progName, args.opt)

    return resName

## 主関数 MinBoard: サイズ１の枠を座標の集合で表現したもの
##        PrimTilePat: （入れるピースのtype番号と座標の集合の対）の集合
##              type番号: 0 は長方形、１以上はそれ以外の形
def gen_tiling_constraints(tilePat, Board, UsageText=""):
    # オプション取得
    args = get_args(UsageText)

    maxlenx = max({pat.xlen() for pat in tilePat})
    maxleny = max({pat.ylen() for pat in tilePat})
    # maxlen = max(maxlenx,maxleny)

    # 配置領域の設定
    D = [[False for y in range(Board.ylen() + maxleny)] for x in range(Board.xlen() + maxlenx)]
    setDomain(D, Board)

    M = Board.xlen()
    Mh = Board.ylen()
    # タイルオブジェクトの生成
    # T[i][j]: 基本タイルを(i,j)だけ平行移動したタイルの集合
    # H[x][y]: (x,y) を埋められるタイルの集合
    T = [[set() for y in range(Mh)] for x in range(M)]
    H = [[set() for y in range(Mh)] for x in range(M)]
    for i in range(M):
        for j in range(Mh):
            for pat in tilePat:
                m = {(i + x, j + y) for (x, y) in pat.cells}

                # mのうち、３マス以上 右側に入っていたら、Tに追加しない
                # 16: ggggg
                # 11: b b b
                #        b b
                if pat.type == 11 and len({(x, y) for (x, y) in m if 1 <= x }) >= 3:
                    continue

                # タイルがカバーするマスがすべて許可領域ならば
                # 使用可能なタイルとして登録
                #if not all([ x<M+maxlenx and y<Mh+maxleny for (x,y) in m ]):
                #    print("x")
                if all([D[x][y] for (x, y) in m]):
                    T[i][j].add(Tile(m, pat.type))       # 基本タイルを(i,j)だけ平行移動したタイルを追加
                    for (x,y) in m:
                        H[x][y].add(Tile(m, pat.type))   # (x,y)を埋められるタイルを追加

    if args.opt >=1:
        # 端に近いことから配置不能なタイルを調べて T, H から除去
        TD= [[set() for y in range(Mh)] for x in range(M)]  # 不要タイルの入れ物
        for i in range(M):
            for j in range(Mh):
                for tile in T[i][j]:
                    compatible = True
                    for (x,y) in tile.borders:
                        if not D[x][y]:
                            continue
                        # あるbordersについて、それを埋められるどのタイルも tile と重なるときは、このtileは利用不能
                        if all({ tile3.isoverlap(tile) for tile3 in H[x][y] }):
                            compatible = False
                            break
                    if not compatible:
                        # printConstr(pbOutStream, tileToExp({tile}), M, '=', 0)
                        TD[i][j].add(tile)      # 不要タイルに追加
        # 使えないタイルを T, H から取り除く
        for i in range(M):
            for j in range(Mh):
                if not D[i][j]:
                    continue
                for tile in TD[i][j]:
                    T[i][j].remove(tile)
                    for (x,y) in tile.cells:
                        H[x][y].remove(tile)

    # 出力ファイルの準備
    progName = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    fileNameBase = gen_filename(progName, args)
    if args.out == None or args.out != '-':
        if args.out != None:
            fname = args.out
        else:
            fname = "{}.pb".format(fileNameBase)
        pbOutStream = open(fname, 'w')
    else:
        pbOutStream = sys.stdout

    gen_basic_constraints(args, pbOutStream, M, Mh, D, T, H, maxlenx, maxleny, tilePat)

    if args.out == None or args.out != '-':
        pbOutStream.flush()
        os.fsync(pbOutStream.fileno())      # fname が書き込まれるのを待つ
        pbOutStream.close

def gen_basic_constraints(args, pbOutStream, M, Mh, D, T, H, maxlenx, maxleny, tilePat):

    Types = {tile.type for tile in tilePat}
    # print("Types: {}".format(Types))

    # 制約の生成： 各(i,j)に対して、それを埋めるタイルは一つだけ
    for i in range(M):
        for j in range(Mh):
            if D[i][j]:
                printConstr(pbOutStream, tilesToExp(H[i][j]), M, '=', 1)

    # 一個のピースは１回のみ使える
    Pce = [set() for type in Types]
    for i in range(M):
        for j in range(Mh):
            for tile in T[i][j]:
                Pce[tile.type-1].add(tile)
    for type in Types:
        printConstr(pbOutStream, tilesToExp(Pce[type-1]), M, '=', 1)

    if args.opt >=2:
        # 制約生成： 接している tile1 と tile2 に対して、隙間に他のピースが入らない場合を禁止
        for i in range(M):
            for j in range(Mh):
                for tile in T[i][j]:
                    neighbors = set()
                    for (k,l) in tile.borders:
                        if not D[k][l]:
                            continue
                        for tile2 in T[k][l]:
                            if tile.type == tile2.type:
                                continue
                            neighbors.add(tile2)
                    for tile2 in neighbors:
                        if tile < tile2 and (not tile.isoverlap(tile2)) and len(tile.borders & tile2.cells) > 1:
                            compatible = True
                            for (x,y) in tile.borders:
                                if not D[x][y] or tile2.contains((x,y)):
                                    continue
                                if all({ tile.isoverlap(tile3) or tile2.isoverlap(tile3) for tile3 in H[x][y]}):
                                    compatible = False
                                    break
                            if not compatible:
                                printConstr(pbOutStream, tilesToExp([tile, tile2]), M, '<=', 1)

# for JP fonts
fontsp = ' '
fonthl = '━'
# spaces used below is U+2002
cmapUtf = {(False, False, False, False): '  ', (False,  True, False,  True): '━━', ( True, False,  True, False): '┃ ',
           (False,  True,  True, False): '┏━', (False, False,  True,  True): '┓ ', ( True,  True, False, False): '┗━',
           ( True, False, False,  True): '┛ ', ( True,  True,  True, False): '┣━', ( True, False,  True,  True): '┫ ',
           (False,  True,  True,  True): '┳━', ( True,  True, False,  True): '┻━', ( True,  True,  True,  True): '╋━'}
cmapJp = {(False, False, False, False): ' ', (False,  True, False,  True): '━', ( True, False,  True, False): '┃',
          (False,  True,  True, False): '┏', (False, False,  True,  True): '┓', ( True,  True, False, False): '┗',
          ( True, False, False,  True): '┛', ( True,  True,  True, False): '┣', ( True, False,  True,  True): '┫',
          (False,  True,  True,  True): '┳', ( True,  True, False,  True): '┻', ( True,  True,  True,  True): '╋'}

cmapUtfExtra =  ['  ','──','━━','│ ','┃ ','┌─','┍━','┎─','┏━',
    '┐ ','┑ ','┒ ','┓ ','└─','┕━','┖─','┗━','┘ ','┙ ','┚ ','┛ ','├─','┝━','┞─','┟─',
    '┠─','┡━','┢━','┣━','┤ ','┥ ','┦ ','┧ ','┨ ','┩ ','┪ ','┫ ','┬─','┭─','┮━','┯━',
    '┰─','┱─','┲━','┳━','┴─','┵─','┶━','┷━','┸─','┹─','┺━','┻━','┼─','┽─','┾━','┿━',
    '╀─','╁─','╂─','╃─','╄━','╅─','╆━','╇━','╈━','╉─','╊━','╋━']
cmapJpExtra =   [' ','─','━','│','┃','┌','┍','┎','┏',
    '┐','┑','┒','┓','└','┕','┖','┗','┘','┙','┚','┛','├','┝','┞','┟',
    '┠','┡','┢','┣','┤','┥','┦','┧','┨','┩','┪','┫','┬','┭','┮','┯',
    '┰','┱','┲','┳','┴','┵','┶','┷','┸','┹','┺','┻','┼','┽','┾','┿',
    '╀','╁','╂','╃','╄','╅','╆','╇','╈','╉','╊','╋']
def listup(utfMode=False):
    if(utfMode):
        cmap = cmapUtfExtra
    else:
        cmap = cmapJpExtra
    for c in cmap:
        print("'{}'  ".format(c), end='')
    print('')

# (north, east, south, west)
def vec_to_char(p, utfMode=False):
    if(utfMode):
        ch = cmapUtf.get(p)
    else:
        ch = cmapJp.get(p)
    assert (ch != None), "{}".format(p)
    return ch

def drawTilesHex(pieces, out=sys.stdout):
    xmax = max(p.xmax for p in pieces)
    ymax = max(p.ymax for p in pieces)

    Bd = [[ '-' for y in range(ymax+1)] for x in range(xmax+1)]
    n = 0
    for p in pieces:
        for (x,y) in p.cells:
            Bd[x][y] = toSingleChar(p.type)

    for y in range(ymax+1):
        for x in range(xmax+1):
            print("{} ".format(Bd[x][y]), end='', file=out)
        n += 1
        print("{}{}".format("\n", " "*n), end='', file=out)
    print("\n")
    return


# Tileの集合を表示する
def draw_tiles(pieces, utfMode, out=sys.stdout):
    xmax = max(p.xmax for p in pieces)
    ymax = max(p.ymax for p in pieces)

    def within(x,y):
        return(0<=x and x<=xmax and 0<=y and y<=ymax)

    def add_north(di):
        (n, e, s, w) = di
        return(True,e,s,w)
    def add_east(di):
        (n, e, s, w) = di
        return(n,True,s,w)
    def add_south(di):
        (n, e, s, w) = di
        return(n,e,True,w)
    def add_west(di):
        (n, e, s, w) = di
        return(n,e,s,True)

    Bd = [[ (False,False,False,False) for y in range(ymax+2)] for x in range(xmax+2)]

    for p in pieces:
        for (x,y) in p.cells:
            if (not within(x-1,y)) or (not p.contains((x-1,y))):
                Bd[x][y] = add_south(Bd[x][y])
                Bd[x][y+1] = add_north(Bd[x][y+1])
            if (not within(x+1,y)) or (not p.contains((x+1,y))):
                Bd[x+1][y] = add_south(Bd[x+1][y])
                Bd[x+1][y+1] = add_north(Bd[x+1][y+1])
            if (not within(x,y-1)) or (not p.contains((x,y-1))):
                Bd[x][y] = add_east(Bd[x][y])
                Bd[x+1][y] = add_west(Bd[x+1][y])
            if (not within(x,y+1)) or (not p.contains((x,y+1))):
                Bd[x][y+1] = add_east(Bd[x][y+1])
                Bd[x+1][y+1] = add_west(Bd[x+1][y+1])

    for y in range(ymax+2):
        for x in range(xmax+2):
            print(vec_to_char(Bd[x][y], utfMode), end='', file=out)
        print('', file=out)
    return

#  converting a string p = "ABC((0,0),(0,1),(1,1))" to Tile object
extract_offset = re.compile(r'^[ ]*\[([+-]?\d+),[ ]*([+-]?\d+)\]')
decomop_cells  = re.compile(r'\((\d+),[ ]*(\d+)\)')
def strToTile(p):
    offset    = extract_offset.match(p)
    (ox,oy) = (0,0)
    if offset:
        (ox,oy) = ( int(offset.group(1)), int(offset.group(2)) )
    positions = decomop_cells.findall(p)
    return Tile( { (int(x)+ox,int(y)+oy) for (x,y) in positions } )

def intToVec(m, M):
    return (((m-1) % M, (m-1) // M))

# converting a string p = "ABC(2,3,7)", and M = 5
decomp_cellM = re.compile(r'(\d+)')
def strToTileM(p, M, type=0):
    positions = decomp_cellM.findall(p)
    x = { intToVec(int(m), M) for m in positions }
    return Tile(x, type)

atom = re.compile(r'[a-zA-Z]+([0-9]*)\[([0-9,()]+)\]')
pos = re.compile(r'\(([0-9]+),([0-9]+)\)')
# converting a string p = "P3[(0,1),(2,3)]" to object Tile({(0,1),(2,3)}, 3)
def variableToTile(str):
#    print("variableToTile: {}".format(str))
    t = int(atom.match(str).group(1))
    if t == '':
        type = 0
    else:
        type = int(t)
    position_list = pos.findall(atom.match(str).group(2))
#       print("{}".format(position_list))
    cls = {(int(x), int(y)) for (x, y) in position_list}
#       print("{}".format(cls))
    tile = Tile(cls, type)
    return (tile)
