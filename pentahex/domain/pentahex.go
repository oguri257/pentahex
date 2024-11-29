package pentahex

import (
	"fmt"
	"sort"
	"strconv"
	"strings"

	"github.com/oguri257/theStudy/pentahex/utils"
)

// Tile構造体，Tileを扱う関数の定義
type PrimTilePat struct {
	id          int
	coordinates utils.CellSet
	xmin        int
	ymin        int
	xlen        int
	ylen        int
	borders     utils.CellSet
	group       int
}

func NewPrimTilePat(newid int, coordinates utils.CellSet) (*PrimTilePat, error) {
	if newid < 0 {
		return nil, fmt.Errorf("[entity] faild ad NewPrimTilePat(): require id > 0")
	}

	if coordinates.Size() != 5 {
		return nil, fmt.Errorf("[entity] faild ad NewPrimTilePat(): require coodinates are 5")
	}

	inf := 100
	min := -100
	xmin, ymin := inf, inf
	xmax, ymax := min, min
	left_count := 0
	for _, coord := range coordinates.Elements() {
		x, y := coord.X, coord.Y
		if x < xmin {
			xmin = x
		}
		if y < ymin {
			ymin = y
		}
		if x > xmax {
			xmax = x
		}
		if y > ymax {
			ymax = y
		}
		if x+y < 10 {
			left_count++
		}
	}
	xlen := xmax - xmin + 1
	ylen := ymax - ymin + 1
	// 自身の5マスに左側が3マス以上あればgroup1,そうでなければgroup2に分類する
	group := 1
	if left_count < 3 {
		group = 2
	}

	borders := utils.NewCellSet()
	for _, coord := range coordinates.Elements() {
		coord := coord
		x := coord.X
		y := coord.Y
		// x軸方向
		for i := x - 1; i <= x+1; i += 2 {
			coord := utils.NewCoord(i, y)
			if !coordinates.Contains(coord) {
				borders.Add(coord)
			}
		}
		// y軸方向
		for i := y - 1; i <= y+1; i += 2 {
			coord := utils.NewCoord(x, i)
			if !coordinates.Contains(coord) {
				borders.Add(coord)
			}
		}
	}

	return &PrimTilePat{
		id:          newid,
		coordinates: coordinates,
		xmin:        xmin,
		ymin:        ymin,
		xlen:        xlen,
		ylen:        ylen,
		borders:     *borders,
		group:       group,
	}, nil
}

func (p *PrimTilePat) contains(inx int, iny int) bool {
	for _, coord := range p.coordinates.Elements_type() {
		x, y := coord.X, coord.Y
		if x == inx && y == iny {
			return true
		}
	}
	return false
}

func (p *PrimTilePat) isnormalize() bool {
	if p.xmin == 0 && p.ymin == 0 {
		return true
	}
	return false
}

func (p *PrimTilePat) toVariales(M int) string {
	// Cells をソート
	sortedCells := p.coordinates.SortedCoords()

	// ソート済みセルを文字列に変換
	cellStrings := make([]string, len(sortedCells))
	for i, cell := range sortedCells {
		cellStrings[i] = fmt.Sprintf("(%d,%d)", cell.X, cell.Y)
	}

	// 結果をフォーマット
	return fmt.Sprintf("P%d[%s]", p.id, strings.Join(cellStrings, ","))
}

func (p *PrimTilePat) toVariales2(M int) string {
	res := make([]int, 0, 5)
	for _, coord := range p.coordinates.Elements_type() {
		x := coord.X
		y := coord.Y
		num := y*M + x + 1
		res = append(res, num)
	}
	sort.Ints(res)

	// カンマ区切りの文字列を生成
	var strValues []string
	for _, val := range res {
		strValues = append(strValues, strconv.Itoa(val))
	}

	// フォーマットされた文字列を返す
	return fmt.Sprintf("P%d(%s)", p.id, strings.Join(strValues, ","))
}

// 共通があるとtrue
func (p *PrimTilePat) isoverlap(in *PrimTilePat) bool {
	for _, p_coord := range p.coordinates.Elements_type() {
		for _, in_coord := range in.coordinates.Elements_type() {
			if p_coord.X == in_coord.X && p_coord.Y == in_coord.Y {
				return false
			}
		}
	}
	return true
}

func (p *PrimTilePat) normalize() error {
	//fmt.Printf("log at normalize():before %+v \n", p.coordinates.Elements_type())
	for _, coord := range p.coordinates.Elements() {
		coord.X = coord.X - p.xmin
		coord.Y = coord.Y - p.ymin
		if coord.X < 0 || coord.Y < 0 {
			return fmt.Errorf("faild at normalize(): result in [coord < 0]")
		}
	}
	//fmt.Printf("log at normalize():after %+v \n", p.coordinates.Elements_type())
	return nil
}

func (p *PrimTilePat) flip() (*PrimTilePat, error) {
	flip_coordinates := utils.NewCellSet()
	for _, coord := range p.coordinates.Elements() {
		x, y := coord.X, coord.Y
		new_coord := utils.NewCoord(x+y, -y)
		flip_coordinates.Add(new_coord)
	}

	flip_p, err := NewPrimTilePat(p.id, *flip_coordinates)
	if err != nil {
		return nil, fmt.Errorf("faild at flip(): by NewPrimTilePat")
	}
	flip_p.normalize()
	return flip_p, nil
}

func (p *PrimTilePat) rotate_60() (*PrimTilePat, error) {
	//fmt.Printf("log at rotate_60():before %+v \n", p.coordinates.Elements_type())
	rotate_coordinates := utils.NewCellSet()
	for _, coord := range p.coordinates.Elements() {
		x, y := coord.X, coord.Y
		new_coord := utils.NewCoord(-y, x+y)
		rotate_coordinates.Add(new_coord)
	}

	rotate_60_p, err := NewPrimTilePat(p.id, *rotate_coordinates)
	if err != nil {
		return nil, fmt.Errorf("faild at rotate_60(): by NewPrimTilePat")
	}
	rotate_60_p.normalize()
	//fmt.Printf("log at rotate_60():after %+v \n", p.coordinates.Elements_type())
	//fmt.Println(p.id, p.coordinates.SortedCoords(), rotate_60_p.coordinates.SortedCoords())
	return rotate_60_p, nil
}

func (p *PrimTilePat) rotate_180() (*PrimTilePat, error) {
	//fmt.Printf("log at rotate_180():before %+v \n", p.coordinates.Elements_type())
	rotate_coordinates := utils.NewCellSet()
	for _, coord := range p.coordinates.Elements() {
		x, y := coord.X, coord.Y
		new_coord := utils.NewCoord(-x, -y)
		rotate_coordinates.Add(new_coord)
	}

	rotate_180_p, err := NewPrimTilePat(p.id, *rotate_coordinates)
	if err != nil {
		return nil, fmt.Errorf("faild at rotate_180(): by NewPrimTilePat")
	}
	rotate_180_p.normalize()
	//fmt.Printf("log at rotate_180(:after %+v \n", p.coordinates.Elements_type())

	return rotate_180_p, nil
}

func (p *PrimTilePat) All_rotate() ([]*PrimTilePat, error) {
	tileset := make([]*PrimTilePat, 0, 2)
	r_tileset := make([]*PrimTilePat, 0, 2)
	rr_tileset := make([]*PrimTilePat, 0, 2)
	all_tileset := make([]*PrimTilePat, 0, 12)
	all_coord := utils.NewStringSet()

	original_tile := p
	flip_p, _ := p.flip()
	//x軸反転
	tileset = append(tileset, original_tile)
	flag := false
	for i := 0; i < 5; i++ {
		ori_x, ori_y := original_tile.coordinates.SortedCoords()[i].X, original_tile.coordinates.SortedCoords()[i].Y
		fli_x, fli_y := flip_p.coordinates.SortedCoords()[i].X, flip_p.coordinates.SortedCoords()[i].Y
		if ori_x != fli_x || ori_y != fli_y {
			flag = true
		}
	}
	if flag {
		tileset = append(tileset, flip_p)
	}

	// for _, i := range tileset {
	// 	fmt.Println(i.id, i.coordinates.SortedCoords())
	// }

	//元と反転タイルを60度回転した集合
	for _, tile := range tileset {
		tile_r, err := tile.rotate_60()
		if err != nil {
			return nil, err
		}
		flag := false
		for i := 0; i < 5; i++ {
			ori_x, ori_y := tile.coordinates.SortedCoords()[i].X, tile.coordinates.SortedCoords()[i].Y
			r_x, r_y := tile_r.coordinates.SortedCoords()[i].X, tile_r.coordinates.SortedCoords()[i].Y
			if ori_x != r_x || ori_y != r_y {
				flag = true
			}
		}
		if flag {
			r_tileset = append(r_tileset, tile_r)
		}
	}
	// for _, i := range r_tileset {
	// 	fmt.Println(i.id, i.coordinates.SortedCoords())
	// }

	//元と反転タイルを120度回転した集合
	for _, tile := range r_tileset {
		tile_rr, err := tile.rotate_60()
		if err != nil {
			return nil, err
		}
		flag := false
		for i := 0; i < 5; i++ {
			ori_x, ori_y := tile.coordinates.SortedCoords()[i].X, tile.coordinates.SortedCoords()[i].Y
			r_x, r_y := tile_rr.coordinates.SortedCoords()[i].X, tile_rr.coordinates.SortedCoords()[i].Y
			if ori_x != r_x || ori_y != r_y {
				flag = true
			}
		}
		if flag {
			rr_tileset = append(rr_tileset, tile_rr)
		}
	}
	// for _, i := range rr_tileset {
	// 	fmt.Println(i.id, i.coordinates.SortedCoords())
	// }

	//全てのオブジェクトとその反転の集合
	for _, tile := range tileset {
		// if tile.id == 11 {
		// 	fmt.Println("a", tile.id, tile.coordinates.SortedCoords())
		// }
		//元のタイルについて
		tile_str := tile.coordinates.SortedCoordsString()
		if !all_coord.Contains(tile_str) {
			all_coord.Add(tile_str)
			all_tileset = append(all_tileset, tile)
			// fmt.Println("OK Add")
			//fmt.Printf("log at allrotate: add original %+v \n", tile.coordinates.Elements_type())
		}
		//反転について
		tile_180, _ := tile.rotate_180()
		tile_r_str := tile_180.coordinates.SortedCoordsString()
		if !all_coord.Contains(tile_r_str) {
			all_coord.Add(tile_r_str)
			all_tileset = append(all_tileset, tile_180)
			// fmt.Println("OK Add")
			//fmt.Printf("log at allrotate: add original-180 %+v \n", tile.coordinates.Elements_type())
		}
		// if tile.id == 11 {
		// 	// fmt.Println("b", tile.id, tile_180.coordinates.SortedCoords())
		// }
	}

	for _, tile := range r_tileset {
		// if tile.id == 11 {
		// 	// fmt.Println("c", tile.id, tile.coordinates.SortedCoords())
		// }
		// fmt.Println(tile.id, tile.coordinates.SortedCoords())
		//元のタイルについて
		tile_str := tile.coordinates.SortedCoordsString()
		if !all_coord.Contains(tile_str) {
			all_coord.Add(tile_str)
			all_tileset = append(all_tileset, tile)
			// fmt.Println("OK Add")
			//fmt.Printf("log at allrotate: add r60 %+v \n", tile.coordinates.Elements_type())
		}
		//反転について
		tile_180, _ := tile.rotate_180()
		tile_r_str := tile_180.coordinates.SortedCoordsString()
		if !all_coord.Contains(tile_r_str) {
			all_coord.Add(tile_r_str)
			all_tileset = append(all_tileset, tile_180)
			// fmt.Println("OK Add")
			//fmt.Printf("log at allrotate: add r60-180 %+v \n", tile.coordinates.Elements_type())
		}
		// if tile.id == 11 {
		// 	fmt.Println("d", tile.id, tile_180.coordinates.SortedCoords())
		// }
	}

	// for _, tile := range rr_tileset {
	// 	if tile.id == 11 {
	// 		fmt.Println("aaaaa", tile.id, tile.coordinates.SortedCoords())
	// 	}
	// }
	for _, tile := range rr_tileset {
		// if tile.id == 11 {
		// 	fmt.Println("e", tile.id, tile.coordinates.SortedCoords())
		// }
		//元のタイルについて
		tile_str := tile.coordinates.SortedCoordsString()
		if !all_coord.Contains(tile_str) {
			all_coord.Add(tile_str)
			all_tileset = append(all_tileset, tile)
			fmt.Println("OK Add")
			//fmt.Printf("log at allrotate: add r120 %+v \n", tile.coordinates.Elements_type())
		}
		//反転について
		tile_180, _ := tile.rotate_180()
		tile_r_str := tile_180.coordinates.SortedCoordsString()
		if !all_coord.Contains(tile_r_str) {
			all_coord.Add(tile_r_str)
			all_tileset = append(all_tileset, tile_180)
			// fmt.Println("OK Add")
			//fmt.Printf("log at allrotate: add r120-180 %+v \n", tile.coordinates.Elements_type())
		}
		// if tile.id == 11 {
		// 	fmt.Println("f", tile.id, tile_180.coordinates.SortedCoords())
		// }
	}
	// for _, i := range all_tileset {
	// 	fmt.Println(i.id, i.coordinates.SortedCoords())
	// }

	return all_tileset, nil

}

func (p *PrimTilePat) toVariable() (string, error) {
	str := ""
	length := p.coordinates.Size()
	for i, coord := range p.coordinates.SortedCoords() {
		x, y := coord.X, coord.Y
		str += fmt.Sprintf("(%d,%d)", x, y)
		if i != length-1 {
			str += ", "
		}
	}

	return fmt.Sprintf("P%d{%s}", p.id, str), nil
}
