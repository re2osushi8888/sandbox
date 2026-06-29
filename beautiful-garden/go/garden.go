package main

func minCuts(x int, y int, z int) (int, int, int) {
	// H -> L
	if x > y {
		// H -> L -> L
		if y > z {
			a := y - 1
		return a, y, z
		}
	}
	// L -> H
	if x < y {
		// L -> H -> H
		if y < z {
			c := y - 1
			return x,y,c
		}
	}
	return x, y, z
}
