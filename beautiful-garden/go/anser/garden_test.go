package main

import "testing"

func TestMinCuts(t *testing.T) {
	tests := []struct {
		name  string
		input []int
		want  int
	}{
		// todo.md のケース
		{"already H,L,H", []int{5, 3, 5}, 0},
		{"H,L,L", []int{5, 4, 3}, 1},
		{"L,H,H", []int{3, 4, 5}, 1},
		{"H,L,H,H,H", []int{5, 4, 5, 6, 7}, 1},
		{"H,L,H,H,H,H", []int{5, 4, 5, 6, 7, 8}, 2},
		{"H,E,H", []int{3, 3, 4}, 1},
		{"H,E,E", []int{3, 3, 2}, 1},
		// エッジケース
		{"empty", []int{}, 0},
		{"single", []int{5}, 0},
		{"two already different asc", []int{3, 5}, 0},
		{"two already different desc", []int{5, 3}, 0},
		{"two same", []int{5, 5}, 1},
		{"already L,H,L", []int{3, 5, 3}, 0},
		{"all same", []int{3, 3, 3, 3}, 2},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := minCuts(tt.input)
			if got != tt.want {
				t.Errorf("minCuts(%v) = %d, want %d", tt.input, got, tt.want)
			}
		})
	}
}
