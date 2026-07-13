use rust_survival::{average, parse_reading};

fn main() {
    let reading = parse_reading("workshop: 18.5").expect("the built-in example is valid");
    let values = vec![reading.value, 19.0, 19.5];
    let mean = average(&values).expect("the built-in vector is non-empty");
    println!("{} mean: {mean:.1}", reading.sensor);
}
