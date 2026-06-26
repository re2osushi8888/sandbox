use rust_hello_world::greet::greet;

#[test]
fn greet_integrates_with_external_call() {
    let result = greet("Rust");
    assert!(result.contains("Rust"));
    assert!(result.starts_with("Hello"));
}
