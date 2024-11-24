package pentahex

//"github.com/oguri257/theStudy/pentahex/utils"

type TilePatSet struct {
	elements map[*PrimTilePat]struct{}
}

// NewCellSet は新しい CellSet を作成します
func NewTilePatSet() *TilePatSet {
	return &TilePatSet{
		elements: make(map[*PrimTilePat]struct{}),
	}
}

// Add はセットに要素を追加します
func (s *TilePatSet) Add(element *PrimTilePat) {
	s.elements[element] = struct{}{} // 空の struct{} を使用
}

func (s *TilePatSet) Elements() []*PrimTilePat {
	keys := make([]*PrimTilePat, 0, len(s.elements))
	for key := range s.elements {
		keys = append(keys, key)
	}
	return keys
}

// Remove はセットから要素を削除します
func (s *TilePatSet) Remove(element *PrimTilePat) {
	delete(s.elements, element)
}

func removeByValue(slice []*PrimTilePat, value *PrimTilePat) []*PrimTilePat {
	for i, v := range slice {
		if v == value {
			return append(slice[:i], slice[i+1:]...)
		}
	}
	return slice
}

// 制約生成で使用する構造体
type TileExp struct {
	coeff int
	tile  *PrimTilePat
}
