package main

func minCuts(heights []int) int {
	if len(heights) <= 1 {
		return 0
	}
	a := countCuts(heights, true)
	b := countCuts(heights, false)
	if a < b {
		return a
	}
	return b
}

// startHigh=true: 0番目がH, 1番目がL, ...のパターン
func countCuts(heights []int, startHigh bool) int {
	h := make([]int, len(heights))
	copy(h, heights)

	cut := make([]bool, len(heights))

	for i := 0; i < len(h)-1; i++ {
		iIsHigh := (i%2 == 0) == startHigh

		if iIsHigh {
			// H → L のペア: h[i] > h[i+1] であるべき
			if h[i] <= h[i+1] {
				cut[i+1] = true
				h[i+1] = h[i] - 1
			}
		} else {
			// L → H のペア: h[i] < h[i+1] であるべき
			if h[i] >= h[i+1] {
				cut[i] = true
				h[i] = h[i+1] - 1
			}
		}
	}

	total := 0
	for _, c := range cut {
		if c {
			total++
		}
	}
	return total
}
