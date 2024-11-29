package main

import (
	"flag"
	"fmt"

	domain "github.com/oguri257/theStudy/pentahex/domain"
	"github.com/oguri257/theStudy/pentahex/utils"
)

func NewCoordinates(coord1 []int, coord2 []int, coord3 []int, coord4 []int, coord5 []int) utils.CellSet {
	// ステップ 1: Coord を作成
	coords := make([]*utils.Coord, 0, 5)
	coords = append(coords, utils.NewCoord(coord1[0], coord1[1]))
	coords = append(coords, utils.NewCoord(coord2[0], coord2[1]))
	coords = append(coords, utils.NewCoord(coord3[0], coord3[1]))
	coords = append(coords, utils.NewCoord(coord4[0], coord4[1]))
	coords = append(coords, utils.NewCoord(coord5[0], coord5[1]))

	// ステップ 2: CellSet を作成
	cellSet := utils.NewCellSet_in(coords)
	return *cellSet
}

func main() {
	tile_set := make([]*domain.PrimTilePat, 0, 12*22)
	tile1, _ := domain.NewPrimTilePat(1, NewCoordinates([]int{0, 0}, []int{1, 0}, []int{1, 1}, []int{1, 2}, []int{2, 0}))
	tile1_rotate, _ := tile1.All_rotate()
	tile_set = append(tile_set, tile1_rotate...)

	tile2, _ := domain.NewPrimTilePat(2, NewCoordinates([]int{0, 1}, []int{0, 3}, []int{1, 0}, []int{1, 1}, []int{1, 2}))
	tile2_rotate, _ := tile2.All_rotate()
	tile_set = append(tile_set, tile2_rotate...)

	tile3, _ := domain.NewPrimTilePat(3, NewCoordinates([]int{0, 0}, []int{1, 0}, []int{2, 0}, []int{2, 1}, []int{2, 2}))
	tile3_rotate, _ := tile3.All_rotate()
	tile_set = append(tile_set, tile3_rotate...)

	tile4, _ := domain.NewPrimTilePat(4, NewCoordinates([]int{0, 0}, []int{0, 3}, []int{1, 0}, []int{1, 1}, []int{1, 2}))
	tile4_rotate, _ := tile4.All_rotate()
	tile_set = append(tile_set, tile4_rotate...)

	tile5, _ := domain.NewPrimTilePat(5, NewCoordinates([]int{0, 3}, []int{1, 1}, []int{1, 2}, []int{1, 3}, []int{2, 0}))
	tile5_rotate, _ := tile5.All_rotate()
	tile_set = append(tile_set, tile5_rotate...)

	tile6, _ := domain.NewPrimTilePat(6, NewCoordinates([]int{0, 2}, []int{1, 0}, []int{1, 1}, []int{1, 2}, []int{2, 0}))
	tile6_rotate, _ := tile6.All_rotate()
	tile_set = append(tile_set, tile6_rotate...)

	tile7, _ := domain.NewPrimTilePat(7, NewCoordinates([]int{0, 4}, []int{1, 2}, []int{1, 3}, []int{2, 1}, []int{3, 0}))
	tile7_rotate, _ := tile7.All_rotate()
	tile_set = append(tile_set, tile7_rotate...)

	tile8, _ := domain.NewPrimTilePat(8, NewCoordinates([]int{0, 4}, []int{1, 3}, []int{2, 2}, []int{3, 0}, []int{3, 1}))
	tile8_rotate, _ := tile8.All_rotate()
	tile_set = append(tile_set, tile8_rotate...)

	tile9, _ := domain.NewPrimTilePat(9, NewCoordinates([]int{0, 0}, []int{0, 1}, []int{0, 2}, []int{1, 0}, []int{1, 1}))
	tile9_rotate, _ := tile9.All_rotate()
	tile_set = append(tile_set, tile9_rotate...)

	tile10, _ := domain.NewPrimTilePat(10, NewCoordinates([]int{0, 1}, []int{0, 2}, []int{1, 2}, []int{2, 0}, []int{2, 1}))
	tile10_rotate, _ := tile10.All_rotate()
	tile_set = append(tile_set, tile10_rotate...)

	tile11, _ := domain.NewPrimTilePat(11, NewCoordinates([]int{0, 3}, []int{1, 1}, []int{1, 2}, []int{2, 0}, []int{2, 1}))
	tile11_rotate, _ := tile11.All_rotate()
	tile_set = append(tile_set, tile11_rotate...)

	tile12, _ := domain.NewPrimTilePat(12, NewCoordinates([]int{0, 2}, []int{2, 1}, []int{2, 1}, []int{3, 0}, []int{4, 0}))
	tile12_rotate, _ := tile12.All_rotate()
	tile_set = append(tile_set, tile12_rotate...)

	tile13, _ := domain.NewPrimTilePat(13, NewCoordinates([]int{0, 3}, []int{1, 2}, []int{2, 0}, []int{2, 1}, []int{3, 1}))
	tile13_rotate, _ := tile13.All_rotate()
	tile_set = append(tile_set, tile13_rotate...)

	tile14, _ := domain.NewPrimTilePat(14, NewCoordinates([]int{0, 1}, []int{0, 2}, []int{1, 1}, []int{1, 2}, []int{2, 0}))
	tile14_rotate, _ := tile14.All_rotate()
	tile_set = append(tile_set, tile14_rotate...)

	tile15, _ := domain.NewPrimTilePat(15, NewCoordinates([]int{0, 0}, []int{1, 0}, []int{1, 1}, []int{2, 0}, []int{3, 0}))
	tile15_rotate, _ := tile15.All_rotate()
	tile_set = append(tile_set, tile15_rotate...)

	tile16, _ := domain.NewPrimTilePat(16, NewCoordinates([]int{0, 0}, []int{1, 0}, []int{2, 0}, []int{3, 0}, []int{4, 0}))
	tile16_rotate, _ := tile16.All_rotate()
	tile_set = append(tile_set, tile16_rotate...)

	tile17, _ := domain.NewPrimTilePat(17, NewCoordinates([]int{0, 0}, []int{0, 1}, []int{0, 2}, []int{1, 1}, []int{2, 0}))
	tile17_rotate, _ := tile17.All_rotate()
	tile_set = append(tile_set, tile17_rotate...)

	tile18, _ := domain.NewPrimTilePat(18, NewCoordinates([]int{0, 0}, []int{1, 0}, []int{1, 2}, []int{2, 0}, []int{2, 1}))
	tile18_rotate, _ := tile18.All_rotate()
	tile_set = append(tile_set, tile18_rotate...)

	tile19, _ := domain.NewPrimTilePat(19, NewCoordinates([]int{0, 0}, []int{0, 1}, []int{1, 0}, []int{2, 0}, []int{3, 0}))
	tile19_rotate, _ := tile19.All_rotate()
	tile_set = append(tile_set, tile19_rotate...)

	tile20, _ := domain.NewPrimTilePat(20, NewCoordinates([]int{0, 3}, []int{1, 3}, []int{2, 1}, []int{2, 2}, []int{3, 0}))
	tile20_rotate, _ := tile20.All_rotate()
	tile_set = append(tile_set, tile20_rotate...)

	tile21, _ := domain.NewPrimTilePat(21, NewCoordinates([]int{0, 3}, []int{1, 1}, []int{1, 2}, []int{2, 0}, []int{2, 2}))
	tile21_rotate, _ := tile21.All_rotate()
	tile_set = append(tile_set, tile21_rotate...)

	tile22, _ := domain.NewPrimTilePat(22, NewCoordinates([]int{0, 3}, []int{0, 4}, []int{1, 1}, []int{1, 2}, []int{2, 0}))
	tile22_rotate, _ := tile22.All_rotate()
	tile_set = append(tile_set, tile22_rotate...)

	// フラグを定義
	opt := flag.Int("opt", 0, "option")
	out := flag.String("out", "default", "fileout")
	// フラグをパース
	flag.Parse()
	M, Mh := 11, 10

	_, err := domain.Gen_constraint(tile_set, M, Mh, opt, out)
	if err != nil {
		fmt.Errorf("failed at gen_constraint")
		return
	}

	// ファイルをクローズする
	// defer file.Close()
	// f, err := os.Open(file.Name())
	// if err != nil {
	// 	fmt.Errorf("failed to open file: %w", err)
	// 	return
	// }
	// defer f.Close()

	// // ファイル内容を読み取り
	// _, err = io.Copy(os.Stdout, f)
	// if err != nil {
	// 	fmt.Errorf("failed to read file: %w", err)
	// 	return
	// }
	// return

}
