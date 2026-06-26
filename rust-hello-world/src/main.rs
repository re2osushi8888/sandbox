use rust_hello_world::{greet::greet, math::add};

fn main() {
    let message = "world retsu";
    println!("{}", greet(message));
    println!("new {}", greet(message));





    println!("1 + 2 = {}", add(1, 2));
}
