package utils

import (
	"fmt"
	"sort"
	"strconv"
)

// CellSet: 座標の集合
// Coord:   座標
type CellSet struct {
	elements map[*Coord]struct{}
}

type Coord struct {
	X int
	Y int
}

// stringSet: string型のSet
type StringSet struct {
	elements map[string]struct{}
}

// NewCellSet は新しい CellSet を作成します
func NewCellSet() *CellSet {
	return &CellSet{
		elements: make(map[*Coord]struct{}),
	}
}

func NewCellSet_in(coords []*Coord) *CellSet {
	cellSet := &CellSet{
		elements: make(map[*Coord]struct{}),
	}
	// coords の各要素を elements に追加
	for _, coord := range coords {
		cellSet.elements[coord] = struct{}{} // 空の struct{} を使用して、存在確認用のマップに追加
	}
	return cellSet
}

func NewCoord(in_x int, in_y int) *Coord {
	return &Coord{
		X: in_x,
		Y: in_y,
	}
}

// NewCellSet は新しい CellSet を作成します
func NewStringSet() StringSet {
	return StringSet{
		elements: make(map[string]struct{}),
	}
}

// Add はセットに要素を追加します
func (s *CellSet) Add(element *Coord) {
	s.elements[element] = struct{}{} // 空の struct{} を使用
}

// Remove はセットから要素を削除します
func (s *CellSet) Remove(element *Coord) {
	delete(s.elements, element)
}

// Contains はセットに要素が含まれているかを確認します
func (s *CellSet) Contains(element *Coord) bool {
	_, exists := s.elements[element]
	return exists
}

// Size はセットの要素数を返します
func (s *CellSet) Size() int {
	return len(s.elements)
}

// Elements はセットの全要素を返します
func (s *CellSet) Elements() []*Coord {
	keys := make([]*Coord, 0, len(s.elements))
	for key := range s.elements {
		keys = append(keys, key)
	}
	return keys
}

// Elements はセットの全要素を返します
func (s *CellSet) Elements_type() []Coord {
	keys := make([]Coord, 0, len(s.elements))
	for key := range s.elements {
		keys = append(keys, *key)
	}
	return keys
}

// Elements はセットの全x要素を返します
func (s *CellSet) Elements_x() []int {
	xs := make([]int, 0, len(s.elements))
	for coord := range s.elements {
		xs = append(xs, coord.X)
	}
	return xs
}

// Elements はセットの全y要素を返します
func (s *CellSet) Elements_y() []int {
	ys := make([]int, 0, len(s.elements))
	for coord := range s.elements {
		ys = append(ys, coord.Y)
	}
	return ys
}

// CellSet内のCoordをソートした全要素を返す関数
func (s *CellSet) SortedCoords() []Coord {
	// mapからsliceに変換
	coords := make([]Coord, 0, len(s.elements))
	for coord := range s.elements {
		coords = append(coords, *coord)
	}

	// CoordのX, Yを基準にソート
	sort.Slice(coords, func(i, j int) bool {
		if coords[i].X == coords[j].X {
			return coords[i].Y < coords[j].Y
		}
		return coords[i].X < coords[j].X
	})

	return coords
}

func (s *CellSet) SortedCoordsString() string {
	coord_slice := s.SortedCoords()
	str := ""
	for _, coord := range coord_slice {
		str += fmt.Sprintf("%s %s ", strconv.Itoa(coord.X), strconv.Itoa(coord.Y))
	}
	return str
}

// Add はセットに要素を追加します
func (s *StringSet) Add(element string) {
	s.elements[element] = struct{}{} // 空の struct{} を使用
}

// Remove はセットから要素を削除します
func (s *StringSet) Remove(element string) {
	delete(s.elements, element)
}

// Contains はセットに要素が含まれているかを確認します
func (s *StringSet) Contains(element string) bool {
	_, exists := s.elements[element]
	return exists
}

// ////////////////////////////////////////
// ////// IntSet: 整数を扱うSet ////////////
// ////////////////////////////////////////
type IntSet struct {
	elements map[int]struct{}
}

// NewCellSet は新しい CellSet を作成します
func NewIntSet() *IntSet {
	return &IntSet{
		elements: make(map[int]struct{}),
	}
}

// Add はセットに要素を追加します
func (s *IntSet) Add(element int) {
	s.elements[element] = struct{}{} // 空の struct{} を使用
}

// Size はセットの要素数を返します
func (s *IntSet) Size() int {
	return len(s.elements)
}

func (s *IntSet) Elements() []int {
	keys := make([]int, 0, len(s.elements))
	for key := range s.elements {
		keys = append(keys, key)
	}
	sort.Ints(keys)
	return keys
}
