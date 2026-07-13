fn print_label(label: &str) {
    println!("{label}");
}

fn main() {
    let label = String::from("sensor-a");
    print_label(&label);
    print_label(&label);
}
