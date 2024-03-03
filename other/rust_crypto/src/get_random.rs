
fn get_random() -> Result<u8, getrandom::Error> {
    let mut buf = [0u8; 1];
    getrandom::getrandom(&mut buf)?;
    Ok(buf[0])
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_random() {
        let _random_value = get_random();
    }
}
