

fn euclidean_algorithm(r1: &u64, r2: &u64) -> u64 {
    let mut _r1 = *r1;
    let mut _r2 = *r2;
    let mut reminder = r1 % r2;

    while reminder != 0 {
        _r1 = _r2;
        _r2 = reminder;
        reminder = _r1 % _r2;
    }
    _r2
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_gcd_greater_number_first() {
        let a = 27;
        let b = 21;
        let expected_result = 3;
        assert_eq!(euclidean_algorithm(&a, &b), expected_result);
    }

    #[test]
    fn test_gcd_smaller_number_first() {
        let a = 27;
        let b = 21;
        let expected_result = 3;
        assert_eq!(euclidean_algorithm(&b, &a), expected_result);
    }

    #[test]
    fn test_gcd_large_numbers() {
        let a = 8859935;
        let b = 1176735;
        let expected_result = 245;
        assert_eq!(euclidean_algorithm(&a, &b), expected_result);
    }

    #[test]
    fn test_gcd_same_number() {
        let a = 100;
        assert_eq!(euclidean_algorithm(&a, &a), a);
    }
}
