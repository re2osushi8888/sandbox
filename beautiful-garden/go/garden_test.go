package main

import "testing"

func TestMinCuts(t *testing.T) {
	x, y, z := 3, 4, 5
	a, b, c := minCuts(x, y, z)
	wantA, wantB, wantC := 5, 4, 3
	if a != wantA || b != wantB || c != wantC {
		t.Errorf("minCuts(%d, %d, %d) = (%d, %d, %d), want (%d, %d, %d)",
			x, y, z, a, b, c, wantA, wantB, wantC)
	}
}
