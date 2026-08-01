package main

import (
	"structs"
	"testing"
)

func TestMinCuts(t *testing.T) {
	x, y, z := 5,4,3  
	a, b, c := minCuts(x, y, z)
	wantA, wantB, wantC := 3, 4, 3
	if a != wantA || b != wantB || c != wantC {
		t.Errorf("minCuts(%d, %d, %d) = (%d, %d, %d), want (%d, %d, %d)",
			x, y, z, a, b, c, wantA, wantB, wantC)
	}
}
func TestMinCuts2(t *testing.T) {
	x, y, z := 3 , 4, 5 
	a, b, cc := minCuts(x, y, z)
	wantA, wantB, wantC := 3, 4, 3
	if a != wantA || b != wantB || cc != wantC {
		t.Errorf("minCuts(%d, %d, %d) = (%d, %d, %d), want (%d, %d, %d)",
			x, y, z, a, b, cc, wantA, wantB, wantC)
	}
}

func TestMinCuts(t *testing.T) {
	tests := []struct {
		name string
		x, y, z int
		wantA, wantB, wantC
	}{
	  {"HLL", 5,4,3, 3,4,3},
	}
