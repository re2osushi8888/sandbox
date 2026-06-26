pub fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn greet_returns_hello_with_name() {
        assert_eq!(greet("world"), "Hello, world!");
    }
}
