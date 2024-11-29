package pentahex

import (
	"fmt"
	"io"
	"os"

	//"github.com/oguri257/theStudy/pentahex/utils"
	"github.com/oguri257/theStudy/pentahex/utils"
)

// ファイル名を生成する関数
func genFilename(progName string, opt int) string {
	return fmt.Sprintf("%s-opt%d", progName, opt)
}

func printLinEx(writer io.Writer, tileExp []TileExp, M int) error {
	for _, exp := range tileExp {
		coeff := exp.coeff
		tile := exp.tile
		_, err := writer.Write([]byte(fmt.Sprintf("%d %s ", coeff, tile.toVariales(M))))
		if err != nil {
			return fmt.Errorf("failed at printLinEx")
		}

		// fmt.Printf("%d %s ", coeff, tile.toVariales(M))
	}
	return nil
}

func printConstr(writer io.Writer, tileExp []TileExp, M int, Operand string, num int) error {
	if len(tileExp) > 0 {
		err := printLinEx(writer, tileExp, M)
		if err != nil {
			return fmt.Errorf("failed at printLinEx in printConstr: %w", err)
		}
		_, err = writer.Write([]byte(fmt.Sprintf("%s %d;\n", Operand, num)))
		if err != nil {
			return fmt.Errorf("failed at printConstr: %w", err)
		}
		// fmt.Printf("%s %d;\n", Operand, num)
	}
	return nil
}

// def printConstr(out, exp, M, Op, num):
//     if exp != set():
//         printLinEx(out, exp, M)
//         print("{} {};".format(Op, num), file=out)

func tilesToExp(tile_set []*PrimTilePat, in_coeff int) ([]TileExp, error) {
	res := make([]TileExp, 0, len(tile_set))
	for _, in_tile := range tile_set {
		tileExp := TileExp{
			coeff: in_coeff,
			tile:  in_tile,
		}
		res = append(res, tileExp)
	}
	return res, nil
}

func Gen_constraint(tile_set []*PrimTilePat, M int, Mh int, opt *int, out *string) (*os.File, error) {

	// fmt.Println(tile_set, M, Mh, opt, out)
	maxlenx, maxleny := -99, -99
	for _, tile := range tile_set {
		if tile.xlen > maxlenx {
			maxlenx = tile.xlen
		}
		if tile.ylen > maxleny {
			maxleny = tile.ylen
		}
	}
	//配置領域の設定
	Dx, Dy := M+maxlenx, Mh+maxleny
	D := make([][]bool, Dx)
	for i := 0; i < Dx; i++ {
		D[i] = make([]bool, Dy)
	}
	// M×Mh の範囲を true に設定
	for i := 0; i < M; i++ {
		for j := 0; j < Mh; j++ {
			D[i][j] = true
		}
	}

	// T と H を [][]PrimTilePat のスライスとして定義
	T := make([][]*TilePatSet, M)
	H := make([][]*TilePatSet, M)
	for i := 0; i < M; i++ {
		T[i] = make([]*TilePatSet, Mh)
		H[i] = make([]*TilePatSet, Mh)
		for j := 0; j < Mh; j++ {
			T[i][j] = NewTilePatSet()
			H[i][j] = NewTilePatSet()
		}
	}

	for i := 0; i < M; i++ {
		for j := 0; j < Mh; j++ {
			for _, pat := range tile_set {
				move_tile := *utils.NewCellSet()
				pat_coord := pat.coordinates.Elements_type()
				for _, coord := range pat_coord {
					newcoord := utils.NewCoord(i+coord.X, j+coord.Y)
					move_tile.Add(newcoord)
				}

				// タイルがカバーするマスがすべて許可領域ならば
				// 使用可能なタイルとして登録
				flag := true
				for _, coord := range move_tile.Elements_type() {
					if !D[coord.X][coord.Y] {
						flag = false
					}
				}
				// T[i][j]: 基本タイルを(i,j)だけ平行移動したタイルの集合
				// H[x][y]: (x,y) を埋められるタイルの集合

				// Tに追加
				if flag {
					newPrimTilePat, _ := NewPrimTilePat(pat.id, move_tile)
					T[i][j].Add(newPrimTilePat)

					// Hに追加
					for _, coord := range move_tile.Elements_type() {
						H[coord.X][coord.Y].Add(newPrimTilePat)
					}
				}
			}
		}
	}

	if *opt >= 1 {
		// 不要なタイル入れを生成
		TD := make([][]*TilePatSet, M)
		for i := 0; i < M; i++ {
			TD[i] = make([]*TilePatSet, Mh)
			for j := 0; j < Mh; j++ {
				TD[i][j] = NewTilePatSet()
			}
		}

		// 端に近いことから配置不能なタイルを調べて T, H から除去
		for i := 0; i < M; i++ {
			for j := 0; j < Mh; j++ {
				for _, tile := range T[i][j].Elements() {
					compatible := true
					for _, coord := range tile.coordinates.Elements_type() {
						x, y := coord.X, coord.Y
						if !D[x][y] {
							continue
						}
						// あるbordersについて、それを埋められるどのタイルも tile と重なるときは、このtileは利用不能
						for _, tile_H := range H[x][y].Elements() {
							if !tile.isoverlap(tile_H) {
								continue
							}
							compatible = false
							break
						}
					}
					if !compatible {
						TD[i][j].Add(tile)
					}
				}
			}
		}

		// 使えないタイルを取り除く
		for i := 0; i < M; i++ {
			for j := 0; j < Mh; j++ {
				if !D[i][j] {
					continue
				}
				for _, tile := range TD[i][j].Elements() {
					T[i][j].Remove(tile)
					for _, coord := range tile.coordinates.Elements_type() {
						x, y := coord.X, coord.Y
						H[x][y].Remove(tile)
					}
				}
			}
		}
	}

	progName := "pentahex"
	fileNameBase := genFilename(progName, *opt)
	var pbOutStream *os.File
	var err error

	if *out == "" || *out != "-" {
		if *out != "" {
			pbOutStream, err = os.Create(*out)
		} else {
			pbOutStream, err = os.Create(fmt.Sprintf("%s.pb", fileNameBase))
		}
		if err != nil {
			fmt.Println("Error creating file:", err)
			return nil, err
		}
	} else {
		pbOutStream = os.Stdout
	}

	// ここで出力内容をpbOutStreamに書き込み
	err = gen_basic_constraints(pbOutStream, M, Mh, *opt, D, T, H, tile_set)
	// 例: _, err = pbOutStream.WriteString("出力内容")
	if err != nil {
		fmt.Println("Error writing to file:", err)
	}

	// ファイルを閉じる
	if *out == "" || *out != "-" {
		pbOutStream.Sync()
		pbOutStream.Close()
	}
	return pbOutStream, err
}

func gen_basic_constraints(pbOutStream *os.File, M int, Mh int, opt int, D [][]bool, T [][]*TilePatSet, H [][]*TilePatSet, tilePat []*PrimTilePat) error {
	typeSet := utils.NewIntSet()
	for _, tile := range tilePat {
		typeSet.Add(tile.id)
	}

	// 制約の生成： 各(i,j)に対して、それを埋めるタイルは一つだけ
	for i := 0; i < M; i++ {
		for j := 0; j < Mh; j++ {
			if D[i][j] {
				tileExp, err := tilesToExp(H[i][j].Elements(), 1)
				if err != nil {
					fmt.Errorf("failed at tilesToExp() in gen_basic_constraints: %w", err)
				}
				printConstr(pbOutStream, tileExp, M, "=", 1)
			}
		}
	}

	peaces := make([]*TilePatSet, typeSet.Size())
	// 各要素を NewTilePatSet で初期化
	for i := range peaces {
		peaces[i] = NewTilePatSet() // 各 TilePatSet を初期化
	}
	for i := 0; i < M; i++ {
		for j := 0; j < Mh; j++ {
			for _, tile := range T[i][j].Elements() {
				peaces[tile.id-1].Add(tile)
			}
		}
	}

	for _, p := range typeSet.Elements() {
		tileExp, err := tilesToExp(peaces[p-1].Elements(), 1)
		if err != nil {
			fmt.Errorf("failed at tilesToExp in gen_basic_constraint")
		}
		printConstr(pbOutStream, tileExp, M, "=", 1)
	}

	if opt >= 2 {
		for i := 0; i < M; i++ {
			for j := 0; j < Mh; j++ {
				for _, tile := range T[i][j].Elements() {
					var neibors []*PrimTilePat
					for _, coord := range tile.borders.Elements_type() {
						k, l := coord.X, coord.Y
						if k < 0 || l < 0 {
							continue
						}
						if !D[k][l] {
							continue
						}
						for _, tile2 := range T[k][l].Elements() {
							if tile.id == tile2.id {
								continue
							}
							neibors = append(neibors, tile2)
						}
					}
					for _, tile2 := range neibors {
						if lt(tile, tile2) && !(tile.isoverlap(tile2)) && (len_overlap(tile.borders, tile2.coordinates) > 1) {
							compatible := true
							for _, coord := range tile.borders.Elements_type() {
								x, y := coord.X, coord.Y
								if x < 0 || y < 0 {
									continue
								}
								if !D[x][y] || tile2.contains(x, y) {
									continue
								}
								for _, tile3 := range H[x][y].Elements() {
									if !tile.isoverlap(tile3) && !tile2.isoverlap(tile3) {
										continue
									}
									compatible = false
									break
								}
							}
							if !compatible {
								tileExp, err := tilesToExp([]*PrimTilePat{tile, tile2}, 1)
								if err != nil {
									fmt.Errorf("failed at tilesToExp in gen_basic_constraint")
								}
								err = printConstr(pbOutStream, tileExp, M, "<=", 1)
								if err != nil {
									fmt.Errorf("failed at printConstr in gen_basic_constraint")
								}
							}
						}
					}
				}
			}
		}
	}
	return nil
}

func lt(tile1 *PrimTilePat, tile2 *PrimTilePat) bool {
	tile1_coords := tile1.coordinates.SortedCoords()
	tile2_coords := tile2.coordinates.SortedCoords()
	for i := 0; i < 5; i++ {
		x1, y1 := tile1_coords[i].X, tile1_coords[i].Y
		x2, y2 := tile2_coords[i].X, tile2_coords[i].Y
		// x座標で判定
		if x1 < x2 {
			return true
		}
		if x1 > x2 {
			return false
		}

		// x座標が同じならy座標で判定
		if y1 < y2 {
			return true
		}
		if y1 > y2 {
			return false
		}
	}
	return false
}

func len_overlap(coords1 utils.CellSet, coords2 utils.CellSet) int {
	res := 0
	for _, coord1 := range coords1.Elements_type() {
		for _, coord2 := range coords2.Elements_type() {
			if coord1.X == coord2.X && coord1.Y == coord2.Y {
				res += 1
			}
		}
	}
	return res
}
