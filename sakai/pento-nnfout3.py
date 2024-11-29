import sys
import rev
import re
import time
import copy

from enum import Enum

nnfout_filename = sys.argv[1]
cnf_filename = sys.argv[2]

class NType(Enum):
    LIT   = 0    # リテラル
    OR    = 1    # OR
    AND   = 2    # AND

class Node(object):
    num=0  # 生成したノード数（次に割り当てるid番号）

    def __init__(self,type,lits=None,lit=None):
        self.type = type

        if type == NType.LIT:
            self.lit = lit
        else:
            self.children = lits

        self.id = Node.num
        Node.num += 1
        self.weight = None      ### 斜交いの最大数を求める際に使用する値
        self.branch = None      ### 0:左の子　1:右の子
        self.count=0            ### ノードが持つ解の個数
        #self.weight_list=[]
        self.odd_even=None
        self.max_branch = None


cor_table = {}      ###{id:[idに該当する元の変数番号]}
return_table = {}   ###{元の変数番号:変数情報}
a = []              ###a行の情報
L_A_O = []          ###L,A,O行の情報
or_stuck = []       ###[[id,LorR]]
started=False       ###関数next_answerで使用する変数
finish=False        ###関数next_answerで使用する変数
# l＿count=0          ###ファイル読み込みの際に各ノードにidを振るために使用する変数
node_list = []      ###各ノードを格納するリスト リストの番目とidが一致するようになっている
answer = []         ###リテラルの正負を格納するリスト　リテラルの絶対値がリストの番目と一致している
cache={}


def search(node): #ノードを辿っていく関数
    global or_stuck
    #print(node.id)
    if node.type==NType.LIT:
        if node.lit>0:
            answer[abs(node.lit)]=True
        elif node.lit<0:
            answer[abs(node.lit)]=False
        #リテラルを返して解リストを更新
    elif node.type==NType.AND:
        #自分の子供を順に見ていく
        for child in node.children:
            search(node_list[child])
    elif node.type==NType.OR:
        if node.branch == None:
            node.branch = 0
            or_stuck.append(node.id)
            search(node_list[node.children[0]])
        else:
            search(node_list[node.children[node.branch]])

def next_answer(): #順に解を出力するための関数
    global started
    global or_stuck
    global finish
    global answer_number

    if finish==True:
        return
    if started==False:
        search(node_list[-1])
    else:
        while(len(or_stuck)>0 and node_list[or_stuck[-1]].branch==1):
            node_list[or_stuck[-1]].branch = None
            or_stuck.pop()
        if (len(or_stuck)>0):
            node_list[or_stuck[-1]].branch = 1
            search(node_list[-1])
            #ans=show_answer()
            #print(ans)
            find_answer()
            answer_number += 1
        else:
            # print('no more answer')
            finish=True
    started=True
    #or_stuckの一番上を見る
    #(L) 左の子を見た場合の解を消す
    #    スタックを{id:R}に更新し右の子を見て解く
    #
    #(R) スタックから取り除いて新しいスタックを引数に繰り返す
    #
    #スタックから取り出したものがフラグであれば終了する
    #　　　orノードを見た場合に決まる解を保持する必要あり
    #     orノードの子がLIT->決まる解として保持
    #     orノードの子がAND->ANDが持つ子LITを全てorノードが持つ解として保持



koteians=''
for i in a:
    if i>0:
        koteians = koteians + ' ' + str(return_table.get(abs(i)))
    elif i<0:
        koteians = koteians + ' -' + str(return_table.get(abs(i)))


def find_answer(): #解のリテラル情報をみてハッシュへと登録する関数
    global cache

    ans=''
    area=[]
    tile=[]
    #answerはある解に対する全ての変数の割り当てを保存しているリスト
    for i in range(1,len(answer)):
        # i : ddnnf上の変数番号（id）
        #割り当てが真の変数に対する処理
        if answer[i]==True:
            #正リテラルの解を元の変数に戻す　originはリスト
            #ddnnf上の変数番号からcnf上の変数番号を探す　litはcnf上の変数番号
            lit = cor_table.get(i)
            if lit==None: #元の変数情報がない場合はパス
                continue
            #cnf上の変数から情報をとる処理
            for j in lit:
                #cnf上の変数番号からタイル情報を取り出す
                ans=ans+' '+str(return_table.get(j))
                #return_tableの　0番目：領域情報　1番目：タイル情報
                #変数が占める領域とタイルの種類をとる
                area+=return_table.get(j)[1]
                tile.append(return_table.get(j)[0])

            #ddnnf上でネガティブリテラルが解の場合の処理　今回は存在しないはず
            nolit = cor_table.get(-i)
            if nolit==None:
                continue
            for j in nolit:
                ans=ans+' -'+str(return_table.get(j))

        #割り当てが偽の変数に対する処理
        elif answer[i]==False:
            #負リテラルの解を元の変数に戻す　originはリスト
            #ddnnf上の変数番号からcnf上の変数番号を探す　litはcnf上の変数番号
            nolit = cor_table.get(-i)
            if nolit==None:#元の変数情報がない場合はパス
                continue
            #cnf上の変数から情報をとる処理
            for j in nolit:
                #cnf上の変数番号からタイル情報を取り出す
                ans=ans+' '+str(return_table.get(j))
                #return_tableの　0番目：領域情報　1番目：タイル情報
                #変数が占める領域とタイルの種類をとる
                area+=return_table.get(j)[1]
                tile.append(return_table.get(j)[0])

            #ddnnf上でネガティブリテラルが解の場合の処理　今回は存在しないはず
            lit = cor_table.get(i)#正リテラルの解を元の変数に戻す　originはリスト
            if lit==None:
                continue
            for j in lit:
                ans=ans+' -'+str(return_table.get(j))

    #ハッシュへの解の登録　求めた領域と使用タイルの情報を登録、及び数を加算
    area.sort()
    tile.sort()
    reg_hash(area,tile)

    return


left_ub_hash={}   #左上領域のハッシュ
left_hash={}      #左領域のハッシュ

name2index={                            4:0  ,  5:1  ,  6:3   ,   7:2 ,
            11:36 ,  12:37 ,  13:38 ,  14:4  , 15:5  ,  16:7  ,  17:6 ,  #18:11 ,　19:12 ,  20:13 ,
            21:39 ,  22:40 ,  23:41 ,  24:8  , 25:9  ,  26:11 ,  27:10 ,  #28:21 ,　29:22 ,  30:23 ,
            31:44 ,  32:43 ,  33:42 ,  34:15 , 35:14 ,  36:12 ,  37:13 ,  #38:31 ,　39:32 ,  40:33 ,
            41:47 ,  42:46 ,  43:45 ,  44:19 , 45:18 ,  46:16 ,  47:17 ,  #48:41 ,　49:42 ,  50:43 ,
                                       54:23 , 55:22 ,  56:20 ,  57:21,
            'P0':24,'P1':25,'P2':26,'P3':27,'P4':28,'P5':29,
            'P6':30,'P7':31,'P8':32,'P9':33,'P10':34,'P11':35  }

#タイルの形
#P0: #   P1:#  P2: #  P3: ##  P4: #   P5: ##    P6: #    P7: ##  P8: #   P9: #   P10:#  P11: #
#    ##     #     ##      ##      ##       #        ###      #       #       ##      #      ###
#   ##      #     #        #      #        ##       #        ##      ###      ##     #       #
#           ##    #               #                                                  #
#                                                                                    #

#それぞれの要素数
len_all_area = len(name2index) #48
len_mid_area = 24
len_tile_type = 12
len_left_area = 12

#name2index={
#            11: 0 ,  12: 1 ,  13: 2 ,
#            21: 3 ,  22: 4 ,  23: 5 ,
#            31: 8 ,  32: 7 ,  33: 6 ,
#            41:11 ,  42:10 ,  43:9 }

counter=0

#左側のタイル配置のみから占有領域とその解の数を求める関数
def reg_hash(area,tile):
    global left_ub_hash
    global name2index

    #key 端3行ずつを取り除いたバイナリ表現
    left_key=[False]*len_all_area

    #使用しているマスに対してインデックスを取得して、keyの値を決定
    #area_num : 領域のマス上での番号
    for area_num in area:
        if area_num in name2index:
            #マス上での番号を対応するインデックスへと変換
            index=name2index[area_num]
            #使用領域をTrueにする
            if name2index[area_num]!=None:
                left_key[index]=True

    #使用しているタイルに対してインデックスを取得して、keyの値を決定
    for tile_num in tile:
        #使用タイルを対応するインデックスへと変換
        index=name2index[tile_num]
        if index!=None:
            left_key[index]=True

    #左3行(left_ub_key)と中央4列(left_key)のデータを生成
    left_ub_key = left_key[ len_mid_area+len_tile_type : len_all_area+1 ]
    del left_key[ len_mid_area+len_tile_type : len_all_area+1 ]


    #辞書型のkeyにするためにtuple
    left_ub_key=tuple(left_ub_key)
    left_key=tuple(left_key)

    #二重辞書 { 左3列の領域 : { 中央4列とタイル : その数 } }
    #keyの数に応じてカウント
    if left_ub_key not in left_ub_hash:
        left_ub_hash[left_ub_key]={}
        left_ub_hash[left_ub_key][left_key]=1
    else:
        if left_key not in left_ub_hash[left_ub_key]:
            left_ub_hash[left_ub_key][left_key]=1
        else:
            left_ub_hash[left_ub_key][left_key]+=1


#左上の埋め方から左半分の埋め方と数を求める関数
def calculate_ub(left_ub_hash):
    global left_hash
    global counter

    for left_ub_key in left_ub_hash:
        #左上の埋め方に対し左下を探す
        buttom_key = list(map(lambda x: not x, left_ub_key))
        flip = 11 #11-i で上下反転位置になる
        loop = 6 #左3列を求めるためのループ回数
        for i in range(loop):
            i_key = buttom_key[i]
            buttom_key[i] = buttom_key[flip-i]
            buttom_key[flip-i] = i_key
        buttom_key = tuple(buttom_key)

        #相方がある場合
        if buttom_key in left_ub_hash:
            up_dict     = left_ub_hash[left_ub_key]
            buttom_dict = left_ub_hash[buttom_key]
        #相方がない場合
        else:
            continue

        #左側領域を生成する処理
        #左上を一つずつとる
        for up_list1 in up_dict:
            val_ub = up_dict[up_list1]
            up_list=list(up_list1)

            #左下を一つずつとる
            for buttom_list1 in buttom_dict:
                val_buttom = buttom_dict[buttom_list1]
                buttom_list=list(buttom_list1)
                flip = 23 #上下の位置入れ替えの定数
                loop = 12 #ループ処理回数
                for i in range(loop):
                    i_key = buttom_list[i]
                    buttom_list[i] = buttom_list[flip-i]
                    buttom_list[flip-i] = i_key
                #左側領域を生成できるか　できない場合はNoneが返ってくる
                left_key = check_double2(list(up_list),list(buttom_list))
                #left_key = check_double(list(up_list),list(buttom_list))
                if left_key == None:
                    continue
                else:
                    left_key = tuple(left_key)
                    val = val_ub * val_buttom

                    if left_key not in left_hash:
                        left_hash[left_key]=val
                    else:
                        left_hash[left_key]+=val
                        counter+=1

    return

#左上の埋め方から左半分の埋め方と数を求める関数
def calculate_ub_test(left_ub_hash):
    global left_hash
    global counter

    check = (True, True, False, True,
    True, True, False, False,
    True, True, False, False,
    False, False, True, True,
    False, False, False, True,
    False, False, True, True,
    False, True, True, True, True, True, False, True, False, False, False, False)

    for left_ub_key in left_ub_hash:
        #print('left_ub_key\n',left_ub_key)
        #左上の埋め方に対し左下を探す
        buttom_key = list(map(lambda x: not x, left_ub_key))
        flip = 11 #11-i で上下反転位置になる
        loop = 6 #左3列を求めるためのループ回数
        for i in range(loop):
            i_key = buttom_key[i]
            buttom_key[i] = buttom_key[flip-i]
            buttom_key[flip-i] = i_key
        buttom_key = tuple(buttom_key)
        #print('buttom_key\n',buttom_key)

        #相方がある場合
        if buttom_key in left_ub_hash:
            #print('find_pair')
            up_dict     = left_ub_hash[left_ub_key]
            #print('up_dict\n',up_dict)
            buttom_dict = left_ub_hash[buttom_key]
            #print('buttom_dict\n',buttom_dict)
        #相方がない場合
        else:
            continue

        #左側領域を生成する処理
        #左上を一つずつとる
        for up_list1 in up_dict:
            up_list=list(up_list1)
            #print('up_list1\n',up_list1)

            #左下を一つずつとる
            for buttom_list1 in buttom_dict:
                buttom_list=list(buttom_list1)
                #print('buttom_list1\n',buttom_list1)
                flip = 23 #上下の位置入れ替えの定数
                loop = 12 #ループ処理回数
                for i in range(loop):
                    i_key = buttom_list[i]
                    buttom_list[i] = buttom_list[flip-i]
                    buttom_list[flip-i] = i_key
                #print('flip buttom_list1\n',buttom_list1)
                #左側領域を生成できるか　できない場合はNoneが返ってくる
                left_key = check_double2(list(up_list),list(buttom_list))
                #left_key = check_double(list(up_list),list(buttom_list))
                if left_key == None:
                    continue
                else:
                    left_key = tuple(left_key)
                    #print('left_key\n',left_key)
                    if left_key == check:
                        for i in [2,6,10]:
                            i_val=up_list[i]
                            up_list[i]=up_list[i+1]
                            up_list[i+1]=i_val
                        for i in [12,16,20]:
                            i_val=up_list[i]
                            i1_val=up_list[i+1]
                            i2_val=up_list[i+2]
                            i3_val=up_list[i+3]
                            up_list[i]  =i3_val
                            up_list[i+1]=i2_val
                            up_list[i+2]=i_val
                            up_list[i+3]=i1_val
                        print(up_list)
                        for i in [2,6,10]:
                            i_val=buttom_list[i]
                            buttom_list[i]=up_list[i+1]
                            buttom_list[i+1]=i_val
                        for i in [12,16,20]:
                            i_val=buttom_list[i]
                            i1_val=buttom_list[i+1]
                            i2_val=buttom_list[i+2]
                            i3_val=buttom_list[i+3]
                            buttom_list[i]  =i3_val
                            buttom_list[i+1]=i2_val
                            buttom_list[i+2]=i_val
                            buttom_list[i+3]=i1_val
                        print(buttom_list)
                        print()

                    if left_key not in left_hash:
                        left_hash[left_key]=1
                    else:
                        left_hash[left_key]+=1
                        counter+=1

    return

#左上と左下から左の領域を生成する関数
def check_double2(up_list,buttom_list):
    #Trueの数を数えておく
    count_true1 = up_list.count(True)
    count_true2 = buttom_list.count(True)
    #2つのリストをorで統合
    result_list = [a or b for a, b in zip(up_list, buttom_list)]
    #Trueの数が減ったかどうか　減っていると被る位置がある
    count_true3 = result_list.count(True)

    check_index1=[1,3,5,7,9,11]
    check_index2=[12,14,16,18,20,22]
    if count_true3 == count_true1 + count_true2:
        for i in check_index1:
            if result_list[i] is True and result_list[i-1] is False:
                return None
            else:
                return result_list
        for i in check_index2:
            if result_list[i] is True and result_list[i+1] is False:
                return None
            else:
                return result_list

    else:
        return None

#t t t  t f t  f t f  f f t

#タイルが被るかの論理演算用関数
def custom_and(a, b):
    if a is True and b is True:
        return None
    elif a is True and b is False:
        return True
    elif a is False and b is True:
        return True
    elif a is False and b is False:
        return False

#左上と左下から左の領域を生成する関数
def check_double(up_list,buttom_list):
    #print(up_list)
    #print(buttom_list)
    #print()
    return_list = copy.deepcopy(up_list)
    flip = 23 #11-i で上下反転位置になる
    #使っているタイルから被りがないか確かめ、使用タイルを合わせる
    for i in range(len_mid_area,len_mid_area+len_tile_type):
        res_and=custom_and(return_list[i], buttom_list[i])
        if res_and==None:
            return None
        else:
            return_list[i]=res_and
    #マスに対する処理
    loop = 12 #ループ処理回数　要素数の半分
    for i in range(loop):
        #元の場所と比較するべき上下対象の位置の値
        i_val = buttom_list[flip-i]
        #上下対象の位置と比較するべき元の場所の値
        flip_val = buttom_list[i]
        #比較する場所の論理演算結果　埋まるかどうか
        #Noneの場合タイルが重なる　Trueの場合どちらかで埋まる　Falseの場合埋まらない
        res_and=custom_and(return_list[i],i_val)
        if res_and==None:
            return None
        else:
            return_list[i]=res_and
        res_and=custom_and(return_list[flip-i],flip_val)
        if res_and==None:
            return None
        else:
            return_list[flip-i]=res_and

    return return_list


#左領域のハッシュから答えを計算
def calculate_lr(left_hash):
    answer=0

    #左側領域を一つずつ確認
    for left_key in left_hash:
        left_val = left_hash[left_key]
        #反対側の相方を生成
        right_key = list(map(lambda x: not x, left_key))
        #左右対称にする処理
        flip_index=[0,1,4,5,8,9,12,13,16,17,20,21]
        for i in flip_index:
            i_key = right_key[i]
            right_key[i] = right_key[i+2]
            right_key[i+2] = i_key

        right_key = tuple(right_key)
        #相方が存在するならば答えとしてカウント
        if right_key in left_hash:
            right_val = left_hash[right_key]
            answer += left_val * right_val

    return answer


def show_answer(): #解のリテラル情報を出力する関数
    ans = 'show'
    area=[]
    tile=[]
    lit_list=[]
    for i in range(1,len(answer)):
        if answer[i]==True:
            lit = cor_table.get(i)#正リテラルの解を元の変数に戻す　originはリスト
            lit_list.append(lit)
            if lit==None:
                continue
            for j in lit:
                ans=ans+' '+str(return_table.get(j))
                area+=return_table.get(j)[1]
                tile.append(return_table.get(j)[0])
            nolit = cor_table.get(-i)
            if nolit==None:
                continue
            for j in nolit:
                ans=ans+' -'+str(return_table.get(j))

        elif answer[i]==False:
            nolit = cor_table.get(-i)
            if nolit==None:
                continue
            for j in nolit:
                ans=ans+' '+str(return_table.get(j))
                area+=return_table.get(j)[1]
                tile.append(return_table.get(j)[0])
            lit = cor_table.get(i)#正リテラルの解を元の変数に戻す　originはリスト
            if lit==None:
                continue
            for j in lit:
                ans=ans+' -'+str(return_table.get(j))
    #area.sort()
    #tile.sort()
    #return area, tile
    return lit_list
    return ans + ' ' + koteians


def modelcount(node): #ノードが持つ解の数を計算する関数
    if node.count > 0:
        return node.count

    if node.type==NType.LIT:
        node.count = 1
    elif node.type==NType.OR:
        node.count = modelcount(node_list[node.children[0]])
        node.count += modelcount(node_list[node.children[1]])
    elif node.type==NType.AND:
        node.count = 1
        for child in node.children:
            node.count *= modelcount(node_list[child])
    else:
        print("Error: illegal node")

    return node.count


atom  = re.compile(r'[a-zA-Z]+([0-9]*)\(([0-9,]+)\)')

def draw(tiles, utfMode, listMode):
    if(listMode):
        for t in tiles:
            print('{}'.format(t))
    else:
        rev.draw_tiles(tiles, utfMode)

def draw_answer(size): #解を描画する関数
    M = 6   # J型領域の幅
    tiles = set()
    for i in range(1,len(answer)):
        if answer[i]==True:
            lit = cor_table.get(i)#正リテラルの解を元の変数に戻す　originはリスト
            if lit==None:
                continue
            for j in lit:
                tile_str = str(return_table.get(j))
                (t, poss) = (atom.match(tile_str).group(1), atom.match(tile_str).group(2))
                if t == '':
                    type = 0
                else:
                    type = int(t)
                tile = rev.strToTileM(poss, M, type)
                tiles.add(tile)

        elif answer[i]==False:
            nolit = cor_table.get(-i)
            if nolit==None:
                continue
            for j in nolit:
                tile_str = str(return_table.get(j))
                (t, poss) = (atom.match(tile_str).group(1), atom.match(tile_str).group(2))
                if t == '':
                    type = 0
                else:
                    type = int(t)
                tile = rev.strToTileM(poss, M, type)
                tiles.add(tile)

    if (tiles != set()):
        draw(tiles, True, False)#ファイルに書き込むときは第二引数をFalseにしたほうが綺麗になる


###########################################################################################
###############################ファイル読み込み処理###########################################
###########################################################################################

nnf_start = time.time()

with open(nnfout_filename) as f:
    print('d-DNNFファイル読み込み中...')
    for line in f:
       line_block = line.split()
       if (line_block[0]=='v'):
           key = int(line_block[2])
           value = int(line_block[1])
           if key in cor_table:
               cor_table.get(key).append(value)
           else:
               cor_table[key] = [value]
       elif (line_block[0]=='p'):
           litcount=int(line_block[3])
       elif (line_block[0]=='a'):
           a = list(map(int,a[1:-1]))
       elif (line_block[0]=='L'):
           node_list.append(Node(NType.LIT,lit=int(line_block[1])))
       elif (line_block[0]=='A'):
           node_list.append(Node(NType.AND,lits=list(map(int,line_block[2:]))))
       elif (line_block[0]=='O'):
           node_list.append(Node(NType.OR,lits=list(map(int,line_block[3:]))))

for i in range(litcount+1):
    answer.append(None)

nnf_end = time.time()
print('nnf parse time:', nnf_end-nnf_start, 's')

cnf_start = time.time()

with open(cnf_filename) as f:
    print('PB変数とCNFファイルの対応情報を読み込み中...')
    for line in f:
        lineblock = line.split()
        if lineblock!=[]:
            if (lineblock[0]=='cv'):
                lineblock.pop(0)
                for i in lineblock:
                    var_block=i.split(':')
                    value=var_block[1].split('(')
                    value[1]=list(map(int, value[1].split(')')[0].split(',') ))
                    return_table[int(var_block[0])]=value

cnf_end = time.time()
print('cnf parse time', cnf_end-cnf_start, 's')

###########################################################################################
###############################ファイル読み込み処理終了########################################
###########################################################################################


###########################################################################################
#######################################メイン処理###########################################
###########################################################################################

answer_number=0


maketable_start = time.time()
#一度ddnnfを探索
modelcount(node_list[-1])
for i in range((node_list[-1].count-1)+1):
    next_answer()
maketable_end = time.time()
print('making table time', maketable_end-maketable_start, 's')

ans_start = time.time()

#左の領域を求める
calculate_ub(left_ub_hash)

#print('len(left_ub_hash)',len(left_ub_hash))
ans_ub_end = time.time()
print('calculate left pattern time', ans_ub_end-ans_start, 's')
#解の数を左の領域から求める
answer=calculate_lr(left_hash)

print('len(left_hash)',len(left_hash))
print(answer)
ans_end = time.time()
print('calculate answer time', ans_end-ans_start, 's')
exit()
