package hello

import "testing"

func TestHello(t *testing.T) {
	result := "Hello, Go!"
	if result != "Hello, Go!" {
		t.Errorf("got %s", result)
	}
}
