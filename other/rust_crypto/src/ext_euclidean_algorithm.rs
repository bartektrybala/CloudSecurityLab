
#[derive(Eq, PartialEq, Debug)]
struct BezoutCoefficients {
    s: i64,
    t: i64
}


fn ext_gcd_ea (a: &u64, b: &u64) -> BezoutCoefficients {
    let _r0 = *a;
    let _r1 = *b;
    BezoutCoefficients { s: 0, t: 1 }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_gcd_greater_number_first() {
        let a = 973;
        let b = 301;
        let expected_coefficients = BezoutCoefficients { s: 13, t: -42 };
        assert_eq!(ext_gcd_ea(&a, &b), expected_coefficients);
    }

    #[test]
    fn test_gcd_smaller_number_first() {
        let a = 301;
        let b = 973;
        let expected_coefficients = BezoutCoefficients { s: -42, t: 13 };
        assert_eq!(ext_gcd_ea(&b, &a), expected_coefficients);
    }

    #[test]
    fn test_gcd_large_numbers() {
        let a = 1846793222;
        let b = 1347382;
        let expected_coefficients = BezoutCoefficients { s: 171949, t: -235682418 };
        assert_eq!(ext_gcd_ea(&a, &b), expected_coefficients);
    }

    #[test]
    fn test_gcd_same_number() {
        let a = 100;
        let expected_coefficients = BezoutCoefficients { s: 0, t: 1 };
        assert_eq!(ext_gcd_ea(&a, &a), expected_coefficients);
    }
}